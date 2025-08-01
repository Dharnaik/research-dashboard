# research_dashboard.py (updated with Conference and Book Tabs, and custom status per tab)
import streamlit as st
import pandas as pd
import os
from datetime import datetime
import altair as alt
from io import BytesIO
from fpdf import FPDF

# -------------------- SETUP -------------------- #
st.set_page_config(page_title="Research Dashboard", layout="wide")
st.title("\U0001F393 Civil Engineering Research Dashboard")

admin_password = st.sidebar.text_input("\U0001F512 Admin Password (for edit access)", type="password")
is_admin = admin_password == "mitresearch2025"

academic_years = ["2023–24", "2024–25", "2025–26"]
current_year = "2025–26"

upload_dirs = {
    "journal": "uploads/journals/",
    "research": "uploads/research/",
    "consultancy": "uploads/consultancy/",
    "patent": "uploads/patents/",
    "ideas": "uploads/ideas/",
    "conference": "uploads/conference/",
    "book": "uploads/book/"
}
for path in upload_dirs.values():
    os.makedirs(path, exist_ok=True)

faculty_list = [
    "Prof. Dr. Yuvaraj L. Bhirud",
    "Prof. Dr. Satish B. Patil",
    "Prof. Abhijeet A. Galatage",
    "Prof. Dr. Rajshekhar G. Rathod",
    "Prof. Avinash A. Rakh",
    "Prof. Achyut A. Deshmukh",
    "Prof. Dr. Amit S. Dharnaik",
    "Prof. Hrishikesh  U Mulay",
    "Prof. Gauri S. Desai",
    "Prof. Bhagyashri D. Patil",
    "Prof. Sagar K. Sonawane"
]

status_dict = {
    "Journal Publications": ["Started Writing", "Journal Identifying", "Manuscript Submitted", "In Process", "Under Review", "Accepted", "Published"],
    "Research Projects": ["Idea", "Submitted", "In Process of Approval", "Approved", "In Process", "Completed"],
    "Consultancy Projects": ["Idea Stage", "Submitted", "Approved", "Sanctioned", "In Process", "Completed"],
    "Patents": ["Filed", "Published", "Granted"],
    "Project Ideas": ["Drafted", "Submitted", "Under Review", "Implemented"],
    "Conference": ["Submitted", "Accepted", "Presented"],
    "Book / Book Chapter": ["Proposal Submitted", "Accepted", "In Press", "Published"]
}

journal_indexing = ["Scopus", "SCI", "Web of Science", "Non-Scopus"]

def load_data(filename):
    if os.path.exists(filename):
        return pd.read_csv(filename)
    else:
        base_columns = ["Faculty", "Academic Year", f"{filename.split('/')[-1].replace('_2025–26.csv','').replace('_',' ').title()} Title", "Status", "Status Date", "Remarks", "Uploaded File", "Submitted On", "Updated On"]
        return pd.DataFrame(columns=base_columns)

def save_data(df, filename):
    df.to_csv(filename, index=False)

# ... rest of code remains unchanged from previous version ...
