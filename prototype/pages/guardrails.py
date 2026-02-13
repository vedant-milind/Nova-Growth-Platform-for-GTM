"""Guardrails - Part 3: Services vs AI Product guardrails."""

import streamlit as st
from data import GUARDRAILS

def render():
    st.subheader("Services vs AI Product Guardrails")
    st.markdown("Rules that maintain delivery quality, preserve trust, and encourage scalable product adoption.")

    for g in GUARDRAILS:
        st.markdown(f"#### {g['id']}. {g['title']}")
        st.write(g["description"])
        st.divider()

    st.markdown("#### Decision Helper")
    st.markdown("Use this checklist when qualifying an opportunity:")
    services_first = st.checkbox("Client has 6+ months prior engagement with us")
    use_case_doc = st.checkbox("Use case is documented")
    delivery_ready = st.checkbox("Delivery capacity is confirmed")
    prior_pilot = st.checkbox("Client has prior successful pilot with us")

    if services_first and use_case_doc and delivery_ready:
        if prior_pilot:
            st.success("✅ Product can be proposed at scale (pilot not required).")
        else:
            st.warning("⚠️ Start with a 3–6 month pilot before full rollout.")
    elif not services_first:
        st.error("❌ Services engagement should come first. Do not propose product yet.")
    else:
        st.info("🔍 Gather more information before proposing product.")
