"""
Operations Manager Performance Task - Client → Opportunity → Delivery System
Streamlit prototype for Services and AI Platform (California Public Sector context)
"""

import streamlit as st

st.set_page_config(
    page_title="Client → Opportunity → Delivery System",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for cleaner look
st.markdown("""
<style>
    .main-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #1e3a5f;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 0.95rem;
        color: #5a6c7d;
        margin-bottom: 2rem;
    }
    .stMetric {
        background-color: #f8fafc;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3b82f6;
    }
    .stage-card {
        padding: 1rem;
        border-radius: 0.5rem;
        background: #f1f5f9;
        margin: 0.5rem 0;
        border-left: 4px solid #64748b;
    }
    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">Client → Opportunity → Delivery System</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Services & AI Platform | California Public Sector</p>', unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("📋 Navigation")
page = st.sidebar.radio(
    "Go to",
    [
        "🏠 Dashboard",
        "👤 Client Account Profile",
        "🔄 Lead to Delivery Flow",
        "🛡️ Guardrails",
        "📖 Example Walkthrough",
        "🔄 Feedback Loops",
        "⚖️ Incentive Alignment",
        "📄 System Overview"
    ],
    label_visibility="collapsed"
)

# Route to pages
if page == "🏠 Dashboard":
    from pages import dashboard
    dashboard.render()
elif page == "👤 Client Account Profile":
    from pages import client_profile
    client_profile.render()
elif page == "🔄 Lead to Delivery Flow":
    from pages import lead_delivery_flow
    lead_delivery_flow.render()
elif page == "🛡️ Guardrails":
    from pages import guardrails
    guardrails.render()
elif page == "📖 Example Walkthrough":
    from pages import example_walkthrough
    example_walkthrough.render()
elif page == "🔄 Feedback Loops":
    from pages import feedback_loops
    feedback_loops.render()
elif page == "⚖️ Incentive Alignment":
    from pages import incentive_alignment
    incentive_alignment.render()
elif page == "📄 System Overview":
    from pages import system_overview
    system_overview.render()
