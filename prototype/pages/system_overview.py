"""System Overview - Part 7: End-to-end explanation and artifacts."""

import streamlit as st
from data import FLOW_STAGES, GUARDRAILS

def render():
    st.subheader("System Overview")
    st.markdown("How the system works end-to-end, key design decisions, tradeoffs, and next steps.")

    st.markdown("#### End-to-End Flow")
    st.markdown("""
    1. **Lead/Account** → Client Account Profile created or enriched (Overview, Current Engagement)
    2. **Opportunity** → Use case qualified; services vs product decided; AI signals captured
    3. **Proposal** → Scope confirmed; delivery capacity checked; proposal developed
    4. **Contract** → Legal sign-off; Operations owns handoff
    5. **Delivery Kickoff** → Profile handed to Delivery; feedback loops begin
    """)

    st.markdown("#### Key Design Decisions")
    st.markdown("""
    - **Profile over CRM schema:** Focus on practical information that drives decisions, not exhaustive fields
    - **Mandatory vs optional:** Only Overview and Current Engagement are mandatory; rest scales with need
    - **Services first:** Guardrails enforce services before product for new relationships
    - **Handoff checklist:** Prevents Sales → Delivery handoff without capacity confirmation
    - **Feedback loops:** Delivery → Sales and continuous profile enrichment keep the system current
    """)

    st.markdown("#### Tradeoffs Accepted")
    st.markdown("""
    - **Simplicity over completeness:** Some edge cases not fully modeled; judgment required
    - **Lean tooling:** No heavy CRM; spreadsheets or lightweight tools suffice for 10–30 people
    - **Trust over automation:** Human judgment valued; guardrails guide, not replace, decisions
    """)

    st.markdown("#### If Organization Doubled in Size")
    st.markdown("""
    - Formalize Client Account Profile in a lightweight CRM or Notion/Airtable
    - Add stage-specific dashboards (e.g., pipeline by stage, by owner)
    - Introduce Account Lead role explicitly; clarify ownership
    - Consider AI-assisted profile enrichment and opportunity qualification (Bonus)
    """)

    st.divider()
    st.markdown("#### Quick Reference")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Flow stages**")
        for s in FLOW_STAGES:
            st.write(f"- {s['name']} ({s['owner']})")
    with col2:
        st.markdown("**Guardrails**")
        for g in GUARDRAILS:
            st.write(f"- {g['title']}")
