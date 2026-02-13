"""SQLAlchemy models for the Flask application."""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# User roles: CEO and Strategy Lead have full access; Employees need explicit permission for confidential info
ROLE_CEO = "ceo"
ROLE_STRATEGY_LEAD = "strategy_lead"
ROLE_EMPLOYEE = "employee"
ROLES = [ROLE_CEO, ROLE_STRATEGY_LEAD, ROLE_EMPLOYEE]

# Kanban stages and ownership
KANBAN_STAGES = ["qualified_lead", "discovery", "proposal", "contract", "kickoff"]
STAGE_OWNERS = {
    "qualified_lead": "Sales",
    "discovery": "Sales",
    "proposal": "Sales",
    "contract": "Operations",
    "kickoff": "Delivery",
}
AI_READINESS_THRESHOLD = 50  # Min score to move Proposal -> Contract

# Lead conversion funnel (California government prospects)
LEAD_STAGES = ["new", "contacted", "qualified", "negotiation", "converted", "lost"]


class User(UserMixin, db.Model):
    """User account for authentication and role-based access."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), default=ROLE_EMPLOYEE)  # ceo, strategy_lead, employee
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_full_access(self):
        """CEO and Strategy Lead see all confidential info."""
        return self.role in (ROLE_CEO, ROLE_STRATEGY_LEAD)


class Lead(db.Model):
    """California government prospect before conversion to client."""

    __tablename__ = "leads"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    department = db.Column(db.String(200), default="")  # e.g. "Dept of Public Services"
    contact_info = db.Column(db.String(500), default="")
    status = db.Column(db.String(50), default="new")  # new, contacted, qualified, negotiation, converted, lost
    notes = db.Column(db.Text, default="")
    converted_to_client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_contacted_at = db.Column(db.DateTime, nullable=True)

    converted_client = db.relationship("Client", backref=db.backref("source_lead", uselist=False))


class ClientPermission(db.Model):
    """Grants an employee access to confidential client data."""

    __tablename__ = "client_permissions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)
    granted_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    granted_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", foreign_keys=[user_id])
    client = db.relationship("Client", backref=db.backref("permissions", lazy="dynamic"))
    granted_by = db.relationship("User", foreign_keys=[granted_by_id])


class Client(db.Model):
    """Client Account Profile (CAP) model."""

    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    legacy_systems = db.Column(db.String(500), default="")  # Comma-separated
    ai_readiness_score = db.Column(db.Integer, default=50)  # 1-100
    last_delivery_update = db.Column(db.DateTime, default=datetime.utcnow)
    revenue = db.Column(db.Float, default=0.0)  # Total (legacy)
    services_revenue = db.Column(db.Float, default=0.0)
    ai_product_revenue = db.Column(db.Float, default=0.0)
    trust_level = db.Column(db.Integer, default=50)  # 1-100 for Trust-Revenue matrix
    data_foundation_service_active = db.Column(db.Boolean, default=False)  # Guardrail
    engagement_start_date = db.Column(db.DateTime, nullable=True)  # For 6+ months check
    use_case_documented = db.Column(db.Boolean, default=False)
    delivery_capacity_confirmed = db.Column(db.Boolean, default=False)
    prior_pilot_success = db.Column(db.Boolean, default=False)
    budget_confirmed = db.Column(db.Boolean, default=False)
    handoff_checklist_complete = db.Column(db.Boolean, default=False)
    guardrail_flags = db.Column(db.Text, default="[]")  # JSON array of violated guardrails
    # LLM analysis output (JSON stored as text)
    ai_use_cases = db.Column(db.Text, default="[]")
    technical_blockers = db.Column(db.Text, default="[]")
    key_stakeholders = db.Column(db.Text, default="[]")
    delivery_notes = db.Column(db.Text, default="")  # Services view - embedded team notes
    problem_priority = db.Column(db.Text, default="")  # For AI enrichment
    analysis_updated_at = db.Column(db.DateTime, nullable=True)
    # Assignment & approval
    assigned_to_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)  # Employee working on client
    approver_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)  # Responsible for approval
    ai_feature_request = db.Column(db.Text, default="")  # What AI feature the client wants to build
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    assigned_to = db.relationship("User", foreign_keys=[assigned_to_id])
    approver = db.relationship("User", foreign_keys=[approver_id])

    def __repr__(self):
        return f"<Client {self.name}>"


class ClientReview(db.Model):
    """Tracks who has reviewed a client application."""

    __tablename__ = "client_reviews"

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)
    reviewed_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    reviewed_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text, default="")

    client = db.relationship("Client", backref=db.backref("reviews", lazy="dynamic", order_by="ClientReview.reviewed_at.desc()"))
    reviewed_by = db.relationship("User", foreign_keys=[reviewed_by_id])


class Opportunity(db.Model):
    """Pipeline opportunity for Lead-to-Delivery Kanban."""

    __tablename__ = "opportunities"

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)
    name = db.Column(db.String(200), default="")  # e.g. "Process Automation Pilot"
    stage = db.Column(db.String(50), default="qualified_lead")
    primary_owner = db.Column(db.String(50), default="Sales")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    client = db.relationship("Client", backref=db.backref("opportunities", lazy="dynamic"))


class RiskFlag(db.Model):
    """Risk flags raised by Delivery Team - triggers Strategic Intervention alerts."""

    __tablename__ = "risk_flags"

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)
    project_name = db.Column(db.String(200), default="")
    message = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(20), default="high")  # low, medium, high, critical
    acknowledged = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    client = db.relationship("Client", backref=db.backref("risk_flags", lazy="dynamic"))

    def __repr__(self):
        return f"<RiskFlag {self.id} client={self.client_id}>"


class PipelineTicket(db.Model):
    """Ticket for pipeline mistakes - raised when someone commits an error on a record."""

    __tablename__ = "pipeline_tickets"

    id = db.Column(db.Integer, primary_key=True)
    opportunity_id = db.Column(db.Integer, db.ForeignKey("opportunities.id"), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved = db.Column(db.Boolean, default=False)

    opportunity = db.relationship("Opportunity", backref=db.backref("tickets", lazy="dynamic"))
    created_by = db.relationship("User", foreign_keys=[created_by_id])
