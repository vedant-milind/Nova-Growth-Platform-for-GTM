"""Example Walkthrough - Part 4: Hypothetical client scenario."""

import streamlit as st
from data import DEMO_CLIENT, get_session_data

def render():
    get_session_data()
    client = DEMO_CLIENT

    st.subheader("Example Walkthrough")
    st.markdown("**Hypothetical client:** Existing consulting client, multiple legacy systems, mid-sized California public-sector org, interested in AI but still defining priorities.")

    steps = [
        ("1. Client Account Profile Created", [
            "Overview: California Dept of Public Services, mid-sized, public sector",
            "Current Engagement: Active consulting project, embedded team",
            "Systems: Legacy ERP, custom case management, spreadsheet reporting",
            "AI Signals: Interest expressed; priorities being defined"
        ]),
        ("2. Opportunity Identified", [
            "Use case: Process automation for case management workflows",
            "Trigger: Client asked about automation during quarterly review",
            "Qualification: 6+ months engagement ✓, use case emerging ✓"
        ]),
        ("3. Services vs Product vs Hybrid", [
            "Decision: **Hybrid** — Services first to refine use case, then product pilot",
            "Rationale: Client still defining priorities; services engagement builds trust before product"
        ]),
        ("4. Delivery Begins", [
            "Phase 1: 2-month discovery (services) to document workflows and pain points",
            "Phase 2: 3-month automation pilot (product) based on discovery",
            "Handoff: Sales → Operations at proposal; Operations → Delivery at contract"
        ])
    ]

    for title, items in steps:
        with st.expander(title, expanded=True):
            for item in items:
                st.write(f"- {item}")

    st.divider()
    st.markdown("#### Demo Client Profile")
    st.json({k: v for k, v in client.items() if k != "profile_sections"})
