"""Client Account Profile - Part 1: Design and capture client information."""

import streamlit as st
from data import get_session_data, save_client, DEMO_CLIENT

# Profile section definitions (from Part 1 design)
PROFILE_SECTIONS = [
    {
        "name": "Client Overview",
        "fields": ["Organization name", "Sector", "Size", "Region", "Key contacts"],
        "why": "Shared understanding of who the client is; avoids duplication across teams.",
        "mandatory": True,
        "update": "Periodically (quarterly or when major changes)"
    },
    {
        "name": "Current Engagement",
        "fields": ["Active projects", "Delivery team", "Contract end dates", "Relationship tenure"],
        "why": "Drives services expansion and handoff decisions.",
        "mandatory": True,
        "update": "Continuous (updated as delivery progresses)"
    },
    {
        "name": "Systems & Constraints",
        "fields": ["Legacy systems", "Compliance requirements", "Technical constraints"],
        "why": "Informs product fit and implementation approach.",
        "mandatory": False,
        "update": "Periodically"
    },
    {
        "name": "AI Opportunity Signals",
        "fields": ["Expressed interest", "Use cases discussed", "Pilot readiness"],
        "why": "Guides when and how to introduce AI products.",
        "mandatory": False,
        "update": "Continuous"
    },
    {
        "name": "Decision History",
        "fields": ["Services vs product choices", "Why pilots were proposed", "Outcomes"],
        "why": "Improves future qualification and avoids repeated mistakes.",
        "mandatory": False,
        "update": "Continuous"
    }
]


def render():
    get_session_data()
    st.subheader("Client Account Profile")
    st.markdown("Design a profile that supports both services and AI product sales. Focus on information that drives decisions.")

    tab1, tab2, tab3 = st.tabs(["📋 Section Design", "➕ Create / Edit Profile", "📖 View Profiles"])

    with tab1:
        st.markdown("#### Profile Section Definitions")
        for section in PROFILE_SECTIONS:
            with st.expander(f"**{section['name']}** {'(Mandatory)' if section['mandatory'] else '(Optional)'}"):
                st.write("**Information captured:**", ", ".join(section["fields"]))
                st.write("**Why it matters:**", section["why"])
                st.write("**Update cadence:**", section["update"])

    with tab2:
        st.markdown("#### Create or Edit Client Profile")
        client_id = st.text_input("Client ID", value="CA-PS-002", help="e.g. CA-PS-001")
        name = st.text_input("Organization Name", value="")
        sector = st.selectbox("Sector", ["Public Sector", "Healthcare", "Education", "Other"])
        size = st.selectbox("Size", ["Small", "Mid-sized", "Large"])
        region = st.text_input("Region", value="California")
        relationship = st.selectbox("Relationship", ["New lead", "Existing consulting client", "Product pilot client"])
        ai_readiness = st.selectbox("AI Readiness", ["Not yet discussed", "Defining priorities", "Use cases identified", "Pilot ready"])
        systems = st.text_area("Systems (comma-separated)", value="", placeholder="Legacy ERP, Custom systems, ...")

        if st.button("Save Profile"):
            client = {
                "id": client_id,
                "name": name or "Unnamed Client",
                "sector": sector,
                "size": size,
                "region": region,
                "relationship": relationship,
                "systems": [s.strip() for s in systems.split(",") if s.strip()] if systems else [],
                "ai_readiness": ai_readiness,
                "opportunities": []
            }
            save_client(client)
            st.success("Profile saved.")

    with tab3:
        st.markdown("#### Existing Profiles")
        for client in st.session_state.clients:
            with st.expander(f"**{client.get('name')}** ({client.get('id')})"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Sector:**", client.get("sector"))
                    st.write("**Size:**", client.get("size"))
                    st.write("**Relationship:**", client.get("relationship"))
                with col2:
                    st.write("**AI Readiness:**", client.get("ai_readiness"))
                    st.write("**Systems:**", ", ".join(client.get("systems", [])) or "—")
