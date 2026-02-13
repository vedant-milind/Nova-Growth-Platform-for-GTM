"""Feedback Loops - Part 5: Delivery → Sales and Profile enrichment."""

import streamlit as st

def render():
    st.subheader("Feedback Loops")
    st.markdown("Two key loops that improve future decisions.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 1. Delivery → Sales")
        st.markdown("""
        **Triggers:**
        - Weekly delivery sync with Account Lead
        - Project milestone completion
        - Client feedback (positive or negative)
        - Scope change or risk identified

        **How it improves decisions:**
        - Sales learns what works in delivery (use cases, timing, client readiness)
        - Early warning on at-risk accounts
        - Better qualification for future opportunities
        """)

    with col2:
        st.markdown("#### 2. Profile Enrichment")
        st.markdown("""
        **Triggers:**
        - Every client touch (meeting, delivery update, proposal)
        - Quarterly account review
        - Opportunity closed (won or lost)

        **How it improves decisions:**
        - Profile stays current; no stale assumptions
        - AI signals updated as client evolves
        - Decision history informs similar clients
        """)

    st.divider()
    st.markdown("#### Feedback Capture (Simulated)")
    feedback_type = st.selectbox("Feedback type", ["Delivery → Sales", "Profile enrichment"])
    feedback_text = st.text_area("What did we learn?")
    if st.button("Log feedback"):
        st.success("Feedback logged. In production, this would update the Client Profile and notify Sales.")
