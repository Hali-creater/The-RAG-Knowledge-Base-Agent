import streamlit as st
import pandas as pd
import os
import subprocess
from database import get_all_leads, update_lead, delete_lead, get_daily_summary, init_db, export_to_csv
from scraper import RealEstateScraper
from database import save_lead
from scheduler import start_scheduler
import datetime

# Page configuration
st.set_page_config(page_title="Lead Intelligence Engine", page_icon="🔎", layout="wide")

# Ensure playwright browsers are installed
@st.cache_resource
def install_playwright():
    subprocess.run(["playwright", "install", "chromium"])

install_playwright()

# Initialize DB and Scheduler
init_db()

@st.cache_resource
def init_scheduler():
    return start_scheduler()

scheduler = init_scheduler()

st.title("🔎 Multi-Source Real Estate Lead Intelligence")

# Sidebar
st.sidebar.header("Control Center")
if st.sidebar.button("🚀 Run Scraper Now"):
    with st.spinner("Monitoring sources (Reddit, Craigslist, Google)..."):
        scraper = RealEstateScraper()
        leads = scraper.run_all()
        for lead in leads:
            save_lead(lead)
    st.sidebar.success(f"Scrape Complete!")
    st.rerun()

summary = get_daily_summary()
st.sidebar.subheader("Today's Overview")
st.sidebar.metric("Total Leads", summary['total'])
st.sidebar.write(f"Sellers: {summary['sellers']} | Buyers: {summary['buyers']}")

# CSV Export
all_leads = get_all_leads()
if all_leads:
    csv_data = export_to_csv(all_leads)
    st.sidebar.download_button(
        label="📥 Download CSV Export",
        data=csv_data,
        file_name=f"leads_export_{datetime.date.today()}.csv",
        mime="text/csv"
    )

# Filters
st.subheader("Filter & Analyze")
f1, f2, f3, f4 = st.columns(4)
with f1:
    source_f = st.selectbox("Source", ["All", "Reddit", "Craigslist", "Google"])
with f2:
    type_f = st.selectbox("Type", ["All", "Seller", "Buyer", "Investor"])
with f3:
    level_f = st.selectbox("Intent Level", ["All", "High Intent", "Medium Intent", "Low Intent"])
with f4:
    status_f = st.selectbox("Status", ["All", "New", "Contacted", "Closed", "Ignored"])

filters = {}
if source_f != "All": filters["source"] = source_f
if type_f != "All": filters["lead_type"] = type_f
if level_f != "All": filters["intent_level"] = level_f
if status_f != "All": filters["status"] = status_f

# Fetch and display
leads = get_all_leads(filters, sort_by="intent_score", sort_order="DESC")

if not leads:
    st.info("No leads found. Run the scraper to collect data.")
else:
    for lead in leads:
        with st.container():
            c1, c2, c3, c4 = st.columns([1, 4, 3, 2])

            # Score
            score = lead['intent_score']
            color = "red" if "High" in lead['intent_level'] else "orange" if "Medium" in lead['intent_level'] else "green"
            c1.markdown(f"### :{color}[{score}]")
            c1.caption(lead['intent_level'])

            # Info
            with c2:
                st.markdown(f"**[{lead['title']}]({lead['url']})**")
                st.caption(f"{lead['source']} | {lead['lead_type']} | {lead['location']} | {lead['created_at']}")
                # Notes
                new_notes = st.text_area("Internal Notes", value=lead['notes'], key=f"notes_{lead['id']}", height=68)
                if new_notes != lead['notes']:
                    update_lead(lead['id'], {"notes": new_notes})

            # Contact
            with c3:
                st.write(f"📞 {lead['phone'] or '---'}")
                st.write(f"📧 {lead['email'] or '---'}")
                st.write(f"Status: **{lead['status']}**")

            # Actions
            with c4:
                new_status = st.selectbox("Set Status", ["New", "Contacted", "Closed", "Ignored"],
                                         index=["New", "Contacted", "Closed", "Ignored"].index(lead['status']),
                                         key=f"status_{lead['id']}")
                if new_status != lead['status']:
                    update_lead(lead['id'], {"status": new_status})
                    st.rerun()

                if st.button("🗑 Delete", key=f"del_{lead['id']}"):
                    delete_lead(lead['id'])
                    st.rerun()

            st.divider()
