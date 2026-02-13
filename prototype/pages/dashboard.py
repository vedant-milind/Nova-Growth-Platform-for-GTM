"""Dashboard - Overview of clients, opportunities, and pipeline."""

import streamlit as st
from data import get_session_data, FLOW_STAGES

def render():
    get_session_data()
    clients = st.session_state.clients
    opportunities = [opp for c in clients for opp in c.get("opportunities", [])]

    st.subheader("Dashboard")
    st.markdown("Overview of clients, opportunities, and pipeline stages.")

    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Clients", len(clients))
    with col2:
        st.metric("Active Opportunities", len(opportunities))
    with col3:
        in_proposal = len([o for o in opportunities if o.get("stage") in ["Proposal", "Contract"]])
        st.metric("In Proposal/Contract", in_proposal)
    with col4:
        st.metric("Flow Stages", len(FLOW_STAGES))

    st.divider()

    # Client list
    st.subheader("Clients")
    for client in clients:
        with st.expander(f"**{client.get('name', 'Unknown')}** — {client.get('sector', '')} | {client.get('id', '')}"):
            st.write(f"**Relationship:** {client.get('relationship', 'N/A')}")
            st.write(f"**AI Readiness:** {client.get('ai_readiness', 'N/A')}")
            opps = client.get("opportunities", [])
            if opps:
                st.write("**Opportunities:**")
                for o in opps:
                    st.write(f"- {o.get('description', '')} ({o.get('stage', '')})")
            else:
                st.write("No active opportunities.")

    st.divider()
    st.caption("Use the sidebar to navigate to Client Profile, Lead-Delivery Flow, Guardrails, and more.")
