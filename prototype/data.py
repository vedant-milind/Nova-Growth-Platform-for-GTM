"""
Data models and session state for the prototype.
"""

import json
from pathlib import Path
import streamlit as st

# Default demo client (Part 4 example)
DEMO_CLIENT = {
    "id": "CA-PS-001",
    "name": "California Department of Public Services",
    "sector": "Public Sector",
    "size": "Mid-sized",
    "region": "California",
    "relationship": "Existing consulting client",
    "systems": ["Legacy ERP", "Custom case management", "Spreadsheet-based reporting"],
    "ai_readiness": "Defining priorities",
    "opportunities": [
        {"id": "OPP-001", "type": "Hybrid", "description": "Process automation pilot", "stage": "Proposal"}
    ],
    "profile_sections": {
        "client_overview": {"mandatory": True, "updated": "periodically"},
        "current_engagement": {"mandatory": True, "updated": "continuous"},
        "ai_opportunity_signals": {"mandatory": False, "updated": "continuous"},
        "decision_history": {"mandatory": False, "updated": "continuous"}
    }
}

# Flow stages with ownership
FLOW_STAGES = [
    {"id": "lead", "name": "Lead / Account", "owner": "Sales", "contributors": ["Marketing"], "approval": None},
    {"id": "opportunity", "name": "Qualified Opportunity", "owner": "Sales", "contributors": ["Delivery", "Operations"], "approval": "Opportunity Review"},
    {"id": "proposal", "name": "Proposal", "owner": "Sales", "contributors": ["Delivery", "Operations"], "approval": "Pricing Review"},
    {"id": "contract", "name": "Contract", "owner": "Operations", "contributors": ["Sales", "Legal"], "approval": "Legal"},
    {"id": "delivery", "name": "Delivery Kickoff", "owner": "Delivery", "contributors": ["Operations", "Client"], "approval": "Delivery Lead"}
]

# Guardrails
GUARDRAILS = [
    {"id": 1, "title": "Services First for New Relationships", "description": "For clients with no prior delivery relationship, services engagement must precede product pilots."},
    {"id": 2, "title": "Product Readiness Signal", "description": "Product can be proposed when: (a) client has 6+ months engagement, (b) use case is documented, (c) delivery capacity is confirmed."},
    {"id": 3, "title": "Pilot Before Scale", "description": "AI products start as pilots (3–6 months) unless client has prior successful pilot with us."},
    {"id": 4, "title": "Handoff Checklist", "description": "Sales → Operations handoff requires: signed opportunity brief, confirmed scope, and delivery availability."},
    {"id": 5, "title": "Trust Preservation", "description": "Never propose product that could undermine existing services trust. Escalate conflicts to Account Lead."}
]


def get_session_data():
    """Initialize or retrieve session state data."""
    if "clients" not in st.session_state:
        st.session_state.clients = [DEMO_CLIENT]
    if "opportunities" not in st.session_state:
        st.session_state.opportunities = []
    return st.session_state


def save_client(client: dict):
    """Add or update a client."""
    if "clients" not in st.session_state:
        st.session_state.clients = []
    existing = next((c for c in st.session_state.clients if c.get("id") == client.get("id")), None)
    if existing:
        idx = st.session_state.clients.index(existing)
        st.session_state.clients[idx] = client
    else:
        st.session_state.clients.append(client)


