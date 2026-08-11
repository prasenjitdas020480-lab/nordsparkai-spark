import streamlit as st

from core.config import LEADS_FILE
from core.storage import load_leads


st.set_page_config(
    page_title="NordSparkAI Admin Dashboard",
    page_icon="📊",
    layout="wide",
)

st.title("📊 NordSparkAI Admin Dashboard")
st.caption("Manage demo requests and customer leads.")

leads = load_leads()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("📋 Total Leads", len(leads))

with col2:
    st.metric("🆕 New Today", len(leads))

with col3:
    st.metric("📅 Demo Requests", len(leads))

if not leads:
    st.info("No leads have been received yet.")
else:
    st.dataframe(
        leads,
        use_container_width=True,
        hide_index=True,
    )
    if LEADS_FILE.exists():
       with LEADS_FILE.open("rb") as file:
          st.download_button(
             label="⬇️ Download Leads CSV",
             data=file,
             file_name="nordsparkai_leads.csv",
             mime="text/csv",
        )