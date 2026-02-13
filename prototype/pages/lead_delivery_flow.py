"""Lead to Delivery Flow - Part 2: End-to-end process design."""

import streamlit as st
from data import get_session_data, FLOW_STAGES

# Stage details with entry criteria
STAGE_DETAILS = {
    "lead": {
        "purpose": "Capture new lead or existing account; create initial Client Account Profile.",
        "entry_criteria": "Lead identified or account flagged for expansion.",
        "profile_action": "Create or enrich Client Account Profile (Overview, Current Engagement)"
    },
    "opportunity": {
        "purpose": "Qualify opportunity; decide services vs product vs hybrid.",
        "entry_criteria": "Identified need, budget signal, and decision-maker access.",
        "profile_action": "Add AI Opportunity Signals; document use case"
    },
    "proposal": {
        "purpose": "Develop proposal; confirm scope, pricing, and delivery capacity.",
        "entry_criteria": "Opportunity approved; scope agreed; delivery availability confirmed.",
        "profile_action": "Update Decision History; document proposal approach"
    },
    "contract": {
        "purpose": "Finalize contract; legal and compliance sign-off.",
        "entry_criteria": "Proposal accepted; terms negotiated.",
        "profile_action": "Profile used for handoff; no new sections"
    },
    "delivery": {
        "purpose": "Kickoff delivery; handoff from sales/ops to delivery team.",
        "entry_criteria": "Contract signed; delivery team assigned.",
        "profile_action": "Profile handed to delivery; feedback loop begins"
    }
}


def render():
    get_session_data()
    st.subheader("Lead to Delivery Flow")
    st.markdown("End-to-end process from Lead/Account → Qualified Opportunity → Proposal → Contract → Delivery Kickoff.")

    st.markdown("#### Visual Flow")
    # Visual pipeline
    stages_display = " → ".join([s["name"] for s in FLOW_STAGES])
    st.markdown(f"**{stages_display}**")

    st.divider()

    st.markdown("#### Stage Details")
    for i, stage in enumerate(FLOW_STAGES):
        sid = stage["id"]
        details = STAGE_DETAILS.get(sid, {})
        with st.expander(f"**{i+1}. {stage['name']}** — Owner: {stage['owner']}"):
            st.write("**Purpose:**", details.get("purpose", "—"))
            st.write("**Entry criteria:**", details.get("entry_criteria", "—"))
            st.write("**Profile action:**", details.get("profile_action", "—"))
            st.write("**Primary owner:**", stage["owner"])
            st.write("**Contributors:**", ", ".join(stage["contributors"]))
            if stage.get("approval"):
                st.write("**Approval point:**", stage["approval"])

    st.divider()
    st.markdown("#### Handoff Points")
    st.info("""
    - **Sales → Operations:** At Opportunity qualification (when scope is confirmed)
    - **Operations → Delivery:** At Contract signing (when delivery kickoff is scheduled)
    - **Profile enrichment:** Continuous; Sales and Delivery both contribute
    """)
