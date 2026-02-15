import streamlit as st
import pandas as pd
import os
import subprocess

# Ensure playwright browsers are installed
try:
    import playwright
except ImportError:
    subprocess.run(["pip", "install", "playwright"])

@st.cache_resource
def install_playwright():
    subprocess.run(["playwright", "install", "chromium"])

install_playwright()

from database import get_all_leads, update_lead_status, delete_lead, get_daily_summary, init_db
from scraper import RealEstateScraper
from database import save_lead
from scheduler import start_scheduler
import datetime

# Page configuration
st.set_page_config(page_title="Real Estate Lead Intelligence", page_icon="🏠", layout="wide")

# Initialize DB and Scheduler
init_db()

@st.cache_resource
def init_scheduler():
    return start_scheduler()

# We don't necessarily want to start the scheduler on every rerun,
# but @st.cache_resource ensures it only runs once per session/restart.
scheduler = init_scheduler()

st.title("🏠 Real Estate AI Lead Intelligence")

# Sidebar for automation and info
st.sidebar.header("Automation")
if st.sidebar.button("Run Scraper Now"):
    with st.spinner("Scraping new leads..."):
        scraper = RealEstateScraper()
        leads = scraper.run()
        for lead in leads:
            save_lead(lead)
    st.sidebar.success(f"Found and processed {len(leads)} leads!")
    st.rerun()

summary = get_daily_summary()
st.sidebar.subheader("Daily Summary")
st.sidebar.write(f"**Total Leads:** {summary['total']}")
st.sidebar.write(f"**Sellers:** {summary['sellers']}")
st.sidebar.write(f"**Buyers:** {summary['buyers']}")
st.sidebar.write(f"**Avg Score:** {summary['avg_score']:.2f}")

# Filters
st.subheader("Filter Leads")
col1, col2, col3 = st.columns(3)
with col1:
    intent_filter = st.selectbox("Intent Type", ["All", "Seller", "Buyer"])
with col2:
    status_filter = st.selectbox("Status", ["All", "New", "Contacted", "Closed"])
with col3:
    location_filter = st.text_input("Location")

filters = {}
if intent_filter != "All":
    filters["intent_type"] = intent_filter
if status_filter != "All":
    filters["status"] = status_filter
if location_filter:
    filters["location"] = location_filter

# Fetch leads
leads = get_all_leads(filters)

if not leads:
    st.info("No leads found matching the filters.")
else:
    # Display leads in a table-like structure using columns
    for lead in leads:
        with st.container():
            c1, c2, c3, c4, c5 = st.columns([1, 4, 2, 2, 2])

            # Score
            score = lead['lead_score']
            color = "red" if score >= 80 else "orange" if score >= 50 else "green"
            c1.markdown(f"### :{color}[{score}]")

            # Info
            with c2:
                st.markdown(f"**{lead['post_title']}**")
                st.caption(f"📍 {lead['location']} | 💰 ${lead['price'] or 'N/A'}")
                st.caption(f"{lead['source_platform']} | {lead['timestamp']}")

            # Intent
            c3.write(f"**{lead['intent_type']}**")

            # Contact
            with c4:
                st.write(f"📞 {lead['phone'] or 'N/A'}")
                st.write(f"📧 {lead['email'] or 'N/A'}")

            # Actions
            with c5:
                new_status = st.selectbox("Status", ["New", "Contacted", "Closed"], index=["New", "Contacted", "Closed"].index(lead['status']), key=f"status_{lead['id']}")
                if new_status != lead['status']:
                    update_lead_status(lead['id'], new_status)
                    st.rerun()

                if st.button("Delete", key=f"del_{lead['id']}"):
                    delete_lead(lead['id'])
                    st.rerun()

            st.divider()

# Optional: Add a CSS override for better styling
st.markdown("""
<style>
    [data-testid="stMetricValue"] {
        font-size: 24px;
    }
</style>
""", unsafe_allow_html=True)
