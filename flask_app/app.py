"""
Flask application - Client → Opportunity → Delivery System
Operations Manager Dashboard with auth, leads, and role-based access.
"""

from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from config import Config
from models import (
    db, User, Client, RiskFlag, Opportunity, Lead, ClientPermission, PipelineTicket, ClientReview,
    KANBAN_STAGES, STAGE_OWNERS, AI_READINESS_THRESHOLD, LEAD_STAGES,
    ROLE_CEO, ROLE_STRATEGY_LEAD, ROLE_EMPLOYEE,
)
from services.priority_score import calculate_priority_score
from services.llm_analyzer import analyze_delivery_notes
from services.guardrails import validate_deal, get_guardrail_violations_for_clients, GUARDRAIL_DEFINITIONS
from services.auth_utils import can_view_confidential, can_grant_permissions


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager = LoginManager(app)
    login_manager.login_view = "login"
    login_manager.login_message = "Please log in to access this page."

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.template_filter("fromjson")
    def fromjson_filter(s):
        import json
        if not s:
            return []
        try:
            return json.loads(s) if isinstance(s, str) else s
        except Exception:
            return []

    @app.context_processor
    def inject_guardrails():
        clients = Client.query.all() if db else []
        violations = get_guardrail_violations_for_clients(clients)
        return {
            "guardrail_violations": violations,
            "can_grant_permissions": can_grant_permissions() if current_user.is_authenticated else False,
        }

    with app.app_context():
        db.create_all()
        try:
            from migrate_db import migrate
            migrate()
        except Exception:
            pass
        _seed_if_empty()
        _ensure_opportunities()
        _seed_users_if_empty()
        _seed_leads_if_empty()

    # --- Auth routes ---

    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        return redirect(url_for("login"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        if request.method == "POST":
            email = (request.form.get("email") or "").strip().lower()
            password = request.form.get("password") or ""
            user = User.query.filter_by(email=email).first()
            if user and user.check_password(password):
                login_user(user, remember=request.form.get("remember") == "on")
                next_url = request.args.get("next") or url_for("dashboard")
                return redirect(next_url)
            flash("Invalid email or password.", "danger")
        return render_template("login.html")

    @app.route("/signup", methods=["GET", "POST"])
    def signup():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        if request.method == "POST":
            email = (request.form.get("email") or "").strip().lower()
            password = request.form.get("password") or ""
            full_name = (request.form.get("full_name") or "").strip()
            if not email or not password or not full_name:
                flash("Email, password, and full name are required.", "danger")
            elif User.query.filter_by(email=email).first():
                flash("An account with this email already exists.", "danger")
            else:
                user = User(email=email, full_name=full_name, role=ROLE_EMPLOYEE)
                user.set_password(password)
                db.session.add(user)
                db.session.commit()
                login_user(user)
                flash("Account created. Welcome!", "success")
                return redirect(url_for("dashboard"))
        return render_template("signup.html")

    @app.route("/logout", methods=["GET", "POST"])
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("login"))

    # --- Protected routes ---

    @app.route("/dashboard")
    @login_required
    def dashboard():
        clients = Client.query.all()
        has_full = current_user.has_full_access()
        total_revenue = sum(c.revenue or 0 for c in clients) if has_full else 0
        services_revenue = sum(getattr(c, "services_revenue", 0) or 0 for c in clients) if has_full else 0
        ai_revenue = sum(getattr(c, "ai_product_revenue", 0) or 0 for c in clients) if has_full else 0
        if has_full and services_revenue == 0 and ai_revenue == 0:
            services_revenue = total_revenue * 0.7
            ai_revenue = total_revenue * 0.3
        revenue_velocity = _compute_revenue_velocity(clients) if has_full else 0
        account_health = _compute_account_health(clients)
        unack_flags = RiskFlag.query.filter_by(acknowledged=False).count()
        trust_revenue_matrix = _build_trust_revenue_matrix(clients, has_full)
        guardrail_violations = get_guardrail_violations_for_clients(clients)
        client_perms = {c.id: can_view_confidential(c) for c in clients}
        return render_template(
            "dashboard.html",
            clients=clients,
            revenue_velocity=revenue_velocity,
            account_health=account_health,
            total_revenue=total_revenue,
            services_revenue=services_revenue,
            ai_revenue=ai_revenue,
            unack_risk_flags=unack_flags,
            trust_revenue_matrix=trust_revenue_matrix,
            guardrail_violations=guardrail_violations,
            can_view_confidential=has_full,
            client_perms=client_perms,
        )

    @app.route("/clients")
    @login_required
    def clients():
        clients = Client.query.all()
        rows = []
        for c in clients:
            can_see = can_view_confidential(c)
            priority = calculate_priority_score(
                (c.revenue or 0) if can_see else 0,
                c.ai_readiness_score or 0,
                c.last_delivery_update or datetime.utcnow(),
            )
            days = _days_since(c.last_delivery_update)
            rows.append({
                "client": c,
                "priority_score": priority,
                "days_since_update": days,
                "can_view_confidential": can_see,
            })
        rows.sort(key=lambda x: x["priority_score"], reverse=True)
        return render_template("clients.html", rows=rows)

    @app.route("/client-health")
    @login_required
    def client_health():
        clients = Client.query.all()
        health_data = []
        for c in clients:
            can_see = can_view_confidential(c)
            days = _days_since(c.last_delivery_update)
            risk_count = c.risk_flags.filter_by(acknowledged=False).count()
            ok, warnings = validate_deal(c)
            health_score = min(100, (c.ai_readiness_score or 0) - (risk_count * 10) - int(days / 7))
            health_data.append({
                "client": c,
                "health_score": max(0, health_score),
                "days_since_update": days,
                "risk_count": risk_count,
                "guardrail_ok": ok,
                "guardrail_warnings": warnings,
                "can_view_confidential": can_see,
            })
        health_data.sort(key=lambda x: x["health_score"])
        return render_template("client_health.html", health_data=health_data)

    @app.route("/leads")
    @login_required
    def leads():
        all_leads = Lead.query.order_by(Lead.updated_at.desc()).all()
        by_stage = {s: [] for s in LEAD_STAGES}
        for lead in all_leads:
            if lead.status in by_stage:
                by_stage[lead.status].append(lead)
        converted = Lead.query.filter(Lead.converted_to_client_id.isnot(None)).count()
        return render_template(
            "leads.html",
            leads=all_leads,
            by_stage=by_stage,
            stages=LEAD_STAGES,
            converted_count=converted,
        )

    @app.route("/leads/add", methods=["GET", "POST"])
    @login_required
    def lead_add():
        if request.method == "POST":
            lead = Lead(
                name=request.form.get("name", "").strip(),
                department=request.form.get("department", ""),
                contact_info=request.form.get("contact_info", ""),
                status=request.form.get("status", "new"),
                notes=request.form.get("notes", ""),
            )
            db.session.add(lead)
            db.session.commit()
            flash("Lead added.", "success")
            return redirect(url_for("leads"))
        return render_template("lead_form.html", lead=None, stages=LEAD_STAGES)

    @app.route("/leads/<int:id>/edit", methods=["GET", "POST"])
    @login_required
    def lead_edit(id):
        lead = Lead.query.get_or_404(id)
        if request.method == "POST":
            lead.name = request.form.get("name", "").strip()
            lead.department = request.form.get("department", "")
            lead.contact_info = request.form.get("contact_info", "")
            lead.status = request.form.get("status", lead.status)
            lead.notes = request.form.get("notes", "")
            if request.form.get("last_contacted") == "on":
                lead.last_contacted_at = datetime.utcnow()
            db.session.commit()
            flash("Lead updated.", "success")
            return redirect(url_for("leads"))
        return render_template("lead_form.html", lead=lead, stages=LEAD_STAGES)

    @app.route("/leads/<int:id>/convert", methods=["POST"])
    @login_required
    def lead_convert(id):
        if not can_grant_permissions():
            flash("Only CEO or Strategy Lead can convert leads.", "danger")
            return redirect(url_for("leads"))
        lead = Lead.query.get_or_404(id)
        if lead.converted_to_client_id:
            flash("Lead already converted.", "info")
            return redirect(url_for("leads"))
        c = Client(
            name=lead.name,
            legacy_systems=lead.notes or "",
            ai_readiness_score=50,
            revenue=0,
            services_revenue=0,
            ai_product_revenue=0,
            trust_level=50,
            engagement_start_date=datetime.utcnow(),
            last_delivery_update=datetime.utcnow(),
        )
        db.session.add(c)
        db.session.commit()
        lead.status = "converted"
        lead.converted_to_client_id = c.id
        db.session.commit()
        opp = Opportunity(client_id=c.id, name="New opportunity", stage="qualified_lead", primary_owner="Sales")
        db.session.add(opp)
        db.session.commit()
        flash(f"Lead converted to client: {c.name}", "success")
        return redirect(url_for("client_detail", id=c.id))

    @app.route("/client/<int:id>/permissions", methods=["GET", "POST"])
    @login_required
    def client_permissions(id):
        if not can_grant_permissions():
            flash("Only CEO or Strategy Lead can manage permissions.", "danger")
            return redirect(url_for("client_detail", id=id))
        client = Client.query.get_or_404(id)
        if request.method == "POST":
            user_id = request.form.get("user_id", type=int)
            action = request.form.get("action")
            if action == "grant" and user_id:
                existing = ClientPermission.query.filter_by(user_id=user_id, client_id=id).first()
                if not existing:
                    perm = ClientPermission(user_id=user_id, client_id=id, granted_by_id=current_user.id)
                    db.session.add(perm)
                    db.session.commit()
                    flash("Access granted.", "success")
            elif action == "revoke" and user_id:
                ClientPermission.query.filter_by(user_id=user_id, client_id=id).delete()
                db.session.commit()
                flash("Access revoked.", "success")
            return redirect(url_for("client_permissions", id=id))
        employees = User.query.filter(User.role == ROLE_EMPLOYEE).all()
        granted = ClientPermission.query.filter_by(client_id=id).all()
        granted_ids = {p.user_id for p in granted}
        return render_template("client_permissions.html", client=client, employees=employees, granted_ids=granted_ids)

    @app.route("/analyze-account/<int:id>", methods=["GET", "POST"])
    @login_required
    def analyze_account(id):
        client = Client.query.get_or_404(id)
        if not can_view_confidential(client):
            flash("You do not have access to analyze this account.", "danger")
            return redirect(url_for("clients"))
        if request.method == "POST":
            notes = request.form.get("delivery_notes") or client.delivery_notes or ""
            if not notes.strip():
                return jsonify({"error": "No delivery notes provided"}), 400
            result = analyze_delivery_notes(notes, app.config.get("OPENAI_API_KEY"))
            client.ai_use_cases = _to_json(result.get("potential_ai_use_cases", []))
            client.technical_blockers = _to_json(result.get("technical_blockers", []))
            client.key_stakeholders = _to_json(result.get("key_stakeholders", []))
            client.delivery_notes = notes
            client.analysis_updated_at = datetime.utcnow()
            db.session.commit()
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify(result)
            return redirect(url_for("client_detail", id=id))
        return render_template("analyze_account.html", client=client)

    @app.route("/client/<int:id>")
    @login_required
    def client_detail(id):
        client = Client.query.get_or_404(id)
        can_see = can_view_confidential(client)
        view = request.args.get("view", "services")
        ok, guardrail_warnings = validate_deal(client)
        priority = calculate_priority_score(
            (client.revenue or 0) if can_see else 0,
            client.ai_readiness_score or 0,
            client.last_delivery_update or datetime.utcnow(),
        )
        reviews = list(client.reviews.limit(10).all())
        users = User.query.all()
        return render_template(
            "client_detail.html",
            client=client,
            priority_score=priority,
            cap_view=view,
            guardrail_warnings=guardrail_warnings,
            can_view_confidential=can_see,
            reviews=reviews,
            users=users,
        )

    @app.route("/client/<int:id>/edit", methods=["GET", "POST"])
    @login_required
    def client_edit(id):
        client = Client.query.get_or_404(id)
        if not can_grant_permissions():
            flash("Only CEO or Strategy Lead can edit client assignment.", "danger")
            return redirect(url_for("client_detail", id=id))
        if request.method == "POST":
            client.assigned_to_id = request.form.get("assigned_to_id", type=int) or None
            client.approver_id = request.form.get("approver_id", type=int) or None
            client.ai_feature_request = (request.form.get("ai_feature_request") or "").strip()
            db.session.commit()
            flash("Client updated.", "success")
            return redirect(url_for("client_detail", id=id))
        users = User.query.all()
        return render_template("client_edit.html", client=client, users=users)

    @app.route("/api/client/<int:id>/review", methods=["POST"])
    @login_required
    def api_client_review(id):
        """Mark client as reviewed by current user."""
        client = Client.query.get_or_404(id)
        if not can_view_confidential(client):
            return jsonify({"ok": False, "error": "Access denied"}), 403
        data = request.get_json() or {}
        notes = (data.get("notes") or "").strip()
        review = ClientReview(client_id=id, reviewed_by_id=current_user.id, notes=notes)
        db.session.add(review)
        db.session.commit()
        return jsonify({"ok": True, "id": review.id})

    @app.route("/client/add", methods=["GET", "POST"])
    @login_required
    def client_add():
        if not can_grant_permissions():
            flash("Only CEO or Strategy Lead can add clients directly.", "danger")
            return redirect(url_for("clients"))
        if request.method == "POST":
            rev = float(request.form.get("revenue", 0))
            svc = float(request.form.get("services_revenue", rev * 0.7))
            ai = float(request.form.get("ai_product_revenue", rev * 0.3))
            assigned = request.form.get("assigned_to_id", type=int) or None
            approver = request.form.get("approver_id", type=int) or None
            ai_feature = (request.form.get("ai_feature_request") or "").strip()
            c = Client(
                name=request.form.get("name"),
                legacy_systems=request.form.get("legacy_systems", ""),
                ai_readiness_score=int(request.form.get("ai_readiness_score", 50)),
                revenue=rev,
                services_revenue=svc,
                ai_product_revenue=ai,
                trust_level=int(request.form.get("trust_level", 50)),
                data_foundation_service_active=request.form.get("data_foundation_service_active") == "on",
                use_case_documented=request.form.get("use_case_documented") == "on",
                delivery_capacity_confirmed=request.form.get("delivery_capacity_confirmed") == "on",
                prior_pilot_success=request.form.get("prior_pilot_success") == "on",
                handoff_checklist_complete=request.form.get("handoff_checklist_complete") == "on",
                engagement_start_date=datetime.utcnow(),
                last_delivery_update=datetime.utcnow(),
                assigned_to_id=assigned,
                approver_id=approver,
                ai_feature_request=ai_feature,
            )
            db.session.add(c)
            db.session.commit()
            opp = Opportunity(client_id=c.id, name="New opportunity", stage="qualified_lead", primary_owner="Sales")
            db.session.add(opp)
            db.session.commit()
            return redirect(url_for("clients"))
        users = User.query.all()
        return render_template("client_form.html", client=None, users=users)

    @app.route("/risk-flag/add", methods=["GET", "POST"])
    @login_required
    def add_risk_flag():
        if request.method == "POST":
            client_id = request.form.get("client_id", type=int)
            client = Client.query.get_or_404(client_id)
            if not can_view_confidential(client):
                flash("You do not have access to add risk flags for this client.", "danger")
                return redirect(url_for("clients"))
            msg = request.form.get("message", "").strip()
            if not msg:
                return jsonify({"error": "Message required"}), 400
            rf = RiskFlag(
                client_id=client_id,
                project_name=request.form.get("project_name", ""),
                message=msg,
                severity=request.form.get("severity", "high"),
            )
            db.session.add(rf)
            db.session.commit()
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify({"id": rf.id, "client": client.name, "message": msg})
            return redirect(url_for("dashboard"))
        clients = [c for c in Client.query.all() if can_view_confidential(c)]
        return render_template("add_risk_flag.html", clients=clients)

    @app.route("/api/alerts")
    @login_required
    def api_alerts():
        flags = RiskFlag.query.filter_by(acknowledged=False).order_by(RiskFlag.created_at.desc()).all()
        return jsonify([{
            "id": f.id, "client_id": f.client_id, "client_name": f.client.name,
            "project_name": f.project_name, "message": f.message, "severity": f.severity,
            "created_at": f.created_at.isoformat() if f.created_at else None,
        } for f in flags])

    @app.route("/api/alerts/<int:id>/acknowledge", methods=["POST"])
    @login_required
    def api_acknowledge(id):
        flag = RiskFlag.query.get_or_404(id)
        flag.acknowledged = True
        db.session.commit()
        return jsonify({"ok": True})

    @app.route("/validate_deal/<int:client_id>")
    @login_required
    def validate_deal_route(client_id):
        client = Client.query.get_or_404(client_id)
        ok, warnings = validate_deal(client)
        return jsonify({"ok": ok, "warnings": warnings})

    @app.route("/kanban")
    @login_required
    def kanban():
        opportunities = Opportunity.query.all()
        by_stage = {s: [] for s in KANBAN_STAGES}
        for o in opportunities:
            if o.stage in by_stage:
                by_stage[o.stage].append(o)
        return render_template(
            "kanban.html",
            stages=KANBAN_STAGES,
            stage_owners=STAGE_OWNERS,
            by_stage=by_stage,
            ai_threshold=AI_READINESS_THRESHOLD,
        )

    @app.route("/api/pipeline-ticket", methods=["POST"])
    @login_required
    def api_pipeline_ticket():
        """Create a ticket for a pipeline mistake."""
        data = request.get_json() or {}
        opp_id = data.get("opportunity_id", type=int)
        message = (data.get("message") or "").strip()
        if not opp_id or not message:
            return jsonify({"ok": False, "error": "Opportunity and message required"}), 400
        opp = Opportunity.query.get_or_404(opp_id)
        ticket = PipelineTicket(
            opportunity_id=opp_id,
            message=message,
            created_by_id=current_user.id,
        )
        db.session.add(ticket)
        db.session.commit()
        return jsonify({"ok": True, "id": ticket.id})

    @app.route("/api/opportunity/<int:id>/move", methods=["POST"])
    @login_required
    def api_opportunity_move(id):
        opp = Opportunity.query.get_or_404(id)
        data = request.get_json() or {}
        new_stage = data.get("stage")
        user_role = data.get("user_role", "Sales")
        if new_stage not in KANBAN_STAGES:
            return jsonify({"ok": False, "error": "Invalid stage"}), 400
        if opp.stage == "proposal" and new_stage == "contract":
            score = opp.client.ai_readiness_score or 0
            if score < AI_READINESS_THRESHOLD:
                return jsonify({"ok": False, "error": f"Quality Gate: AI Readiness Score must be ≥{AI_READINESS_THRESHOLD}. Current: {score}."}), 400
        required_owner = STAGE_OWNERS.get(new_stage, "Sales")
        if user_role != required_owner:
            return jsonify({"ok": False, "error": f"Decision Authority required. Primary Owner for this stage is {required_owner}."}), 403
        opp.stage = new_stage
        opp.primary_owner = required_owner
        db.session.commit()
        return jsonify({"ok": True, "stage": new_stage})

    @app.route("/guardrails")
    @login_required
    def guardrails():
        clients = Client.query.all()
        violations = get_guardrail_violations_for_clients(clients)
        return render_template("guardrails.html", definitions=GUARDRAIL_DEFINITIONS, violations=violations)

    @app.route("/client/<int:id>/toggle-cap")
    @login_required
    def client_cap(id):
        return redirect(url_for("client_detail", id=id, view=request.args.get("view", "services")))

    return app


def _compute_revenue_velocity(clients):
    total = 0
    for c in clients:
        days = _days_since(c.last_delivery_update)
        if days > 0 and (c.revenue or 0) > 0:
            total += (c.revenue or 0) / days
    return round(total, 2)


def _compute_account_health(clients):
    if not clients:
        return 0
    return round(sum(c.ai_readiness_score or 0 for c in clients) / len(clients), 1)


def _build_trust_revenue_matrix(clients, include_revenue=True):
    high_trust_low_ai, low_trust_high_ai, high_trust_high_ai, low_trust_low_ai = [], [], [], []
    for c in clients:
        trust = getattr(c, "trust_level", 50) or 50
        ai_pct = 0
        rev = (c.revenue or 0) if include_revenue else 0
        if rev > 0:
            ai_rev = getattr(c, "ai_product_revenue", 0) or 0
            ai_pct = (ai_rev / rev) * 100
        high_trust, high_ai = trust >= 60, ai_pct >= 30
        entry = {"id": c.id, "name": c.name, "trust": trust, "ai_pct": round(ai_pct, 1)}
        if high_trust and not high_ai:
            high_trust_low_ai.append(entry)
        elif not high_trust and high_ai:
            low_trust_high_ai.append(entry)
        elif high_trust and high_ai:
            high_trust_high_ai.append(entry)
        else:
            low_trust_low_ai.append(entry)
    return {
        "high_trust_low_ai": high_trust_low_ai,
        "low_trust_high_ai": low_trust_high_ai,
        "high_trust_high_ai": high_trust_high_ai,
        "low_trust_low_ai": low_trust_low_ai,
    }


def _days_since(dt):
    if not dt:
        return 0
    return max((datetime.utcnow() - dt).total_seconds() / 86400, 0.1)


def _to_json(obj):
    import json
    return json.dumps(obj) if not isinstance(obj, str) else obj


def _seed_if_empty():
    if Client.query.first():
        return
    now = datetime.utcnow()
    clients_data = [
        ("California Dept of Public Services", "Legacy ERP, Custom case management", 65, 120000, 84000, 36000, 75, False, now - timedelta(days=200), False, False, False),
        ("State Health Authority", "Mainframe, Spreadsheet reporting", 45, 85000, 85000, 0, 40, False, now - timedelta(days=100), False, False, False),
        ("Regional Education Agency", "Student information system, Paper forms", 80, 200000, 120000, 80000, 85, True, now - timedelta(days=400), True, True, True),
    ]
    for name, legacy, ai, rev, svc, ai_rev, trust, data_found, eng_start, use_case, delivery_ok, prior_pilot in clients_data:
        c = Client(
            name=name, legacy_systems=legacy, ai_readiness_score=ai, revenue=rev,
            services_revenue=svc, ai_product_revenue=ai_rev, trust_level=trust,
            data_foundation_service_active=data_found, engagement_start_date=eng_start,
            use_case_documented=use_case, delivery_capacity_confirmed=delivery_ok,
            prior_pilot_success=prior_pilot,
            last_delivery_update=now - timedelta(days=5 if "California" in name else (14 if "Health" in name else 2)),
        )
        db.session.add(c)
    db.session.commit()
    for c in Client.query.all():
        if c.opportunities.count() == 0:
            stage = "proposal" if "California" in c.name else ("discovery" if "Health" in c.name else "qualified_lead")
            db.session.add(Opportunity(client_id=c.id, name=(c.name[:20] + "...") if len(c.name) > 20 else c.name, stage=stage, primary_owner=STAGE_OWNERS.get(stage, "Sales")))
    db.session.commit()


def _seed_users_if_empty():
    vedant = User.query.filter_by(email="vedantmilindathavale@gmail.com").first()
    if vedant:
        vedant.full_name = "Vedant Athavale (Strategy)"
        vedant.role = ROLE_STRATEGY_LEAD
        vedant.set_password("qwerty")
        db.session.commit()
    else:
        vedant = User(email="vedantmilindathavale@gmail.com", full_name="Vedant Athavale (Strategy)", role=ROLE_STRATEGY_LEAD)
        vedant.set_password("qwerty")
        db.session.add(vedant)
        db.session.commit()

    if User.query.count() > 1:
        return
    for email, pw, name, role in [
        ("ceo@novaera.com", "ceo123", "CEO", ROLE_CEO),
        ("employee@novaera.com", "employee123", "Sample Employee", ROLE_EMPLOYEE),
    ]:
        if User.query.filter_by(email=email).first():
            continue
        u = User(email=email, full_name=name, role=role)
        u.set_password(pw)
        db.session.add(u)
    db.session.commit()


def _seed_leads_if_empty():
    if Lead.query.first():
        return
    ca_gov_depts = [
        "Dept of Public Services", "State Health Authority", "Regional Education Agency",
        "Dept of Transportation", "Dept of Corrections", "Dept of Motor Vehicles",
        "Dept of Water Resources", "Dept of Parks & Recreation", "Dept of Finance",
        "Dept of General Services", "Dept of Technology", "Dept of Human Resources",
        "Dept of Social Services", "Dept of Child Support", "Dept of Aging",
        "Dept of Veterans Affairs", "Dept of Housing", "Dept of Consumer Affairs",
        "Dept of Insurance", "Dept of Tax & Fee Administration", "Franchise Tax Board",
        "Employment Development Dept", "Dept of Industrial Relations",
        "Dept of Food & Agriculture", "Dept of Forestry", "Cal Fire",
        "Dept of Fish & Wildlife", "State Lands Commission", "Coastal Commission",
        "Air Resources Board", "Energy Commission", "Public Utilities Commission",
        "Dept of Justice", "Dept of Public Health", "Dept of Health Care Services",
        "Dept of State Hospitals", "Dept of Developmental Services",
        "Dept of Rehabilitation", "Dept of Education", "Community Colleges",
        "University of California", "California State University",
        "Dept of Alcoholic Beverage Control", "Dept of Cannabis Control",
        "Board of Equalization", "State Controller", "State Treasurer",
        "Secretary of State", "Attorney General", "Governor's Office",
    ]
    clients_by_name = {c.name: c.id for c in Client.query.all()}
    for dept in ca_gov_depts[:50]:
        name = f"California {dept}"
        client_id = clients_by_name.get(name) or clients_by_name.get(dept)
        status = "converted" if client_id else "new"
        lead = Lead(name=name, department=dept, status=status, converted_to_client_id=client_id, notes="CA government - AI operations opportunity")
        db.session.add(lead)
    db.session.commit()


def _ensure_opportunities():
    for c in Client.query.all():
        if c.opportunities.count() == 0:
            db.session.add(Opportunity(client_id=c.id, name=(c.name[:20] + "...") if len(c.name) > 20 else c.name, stage="qualified_lead", primary_owner="Sales"))
    db.session.commit()


app = create_app()
