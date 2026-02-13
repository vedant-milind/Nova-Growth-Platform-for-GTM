"""Incentive Alignment - Part 6: Tensions and mechanisms."""

import streamlit as st

def render():
    st.subheader("Incentive Alignment")
    st.markdown("Identify tensions and propose simple mechanisms to keep incentives aligned.")

    st.markdown("#### Likely Tension: Sales Speed vs Delivery Readiness")
    st.markdown("""
    **The tension:** Sales is incentivized to close deals quickly. Delivery needs time to confirm capacity, 
    understand scope, and avoid overcommitment. Rushing handoffs can damage trust and delivery quality.
    """)

    st.divider()
    st.markdown("#### Proposed Mechanism")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Process**")
        st.markdown("""
        - Mandatory **handoff checklist** before contract signing
        - Delivery Lead must confirm capacity and scope understanding
        - No contract without Delivery sign-off
        """)

    with col2:
        st.markdown("**Metric**")
        st.markdown("""
        - Track **time from proposal to delivery kickoff**
        - Target: ≤2 weeks for standard engagements
        - Flag outliers for review (too fast = rushed; too slow = bottleneck)
        """)

    with col3:
        st.markdown("**Policy**")
        st.markdown("""
        - Sales commission tied to **successful delivery kickoff**, not just contract signature
        - Shared accountability: both Sales and Delivery own client satisfaction
        """)

    st.divider()
    st.info("Avoid complex compensation redesigns. Use process, metric, and policy to align behavior.")
