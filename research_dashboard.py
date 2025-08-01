# research_dashboard.py (Updated with Dashboard Graphs and Error Fixes)
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

data_dir = "data"
os.makedirs(data_dir, exist_ok=True)

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
    "Select Your Name",
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
    "Project Ideas": ["Drafted", "Submitted", "Under Review", "Assigned to S.Y. Mini Project", "Assigned to T.Y. Mini Project", "Assigned to B.Tech. Project", "Implemented"],
    "Conference": ["Submitted", "Accepted", "Presented"],
    "Book / Book Chapter": ["Proposal Submitted", "Accepted", "In Press", "Published"]
}

journal_indexing = ["Scopus", "SCI", "Web of Science", "Non-Scopus"]

def get_now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def load_data(filename, tab):
    if os.path.exists(filename):
        return pd.read_csv(filename)
    else:
        title_col = f"{tab} Title"
        base_cols = ["Faculty", "Academic Year", title_col, "Status", "Status Date", "Remarks", "Uploaded File", "Submitted On", "Updated On"]
        return pd.DataFrame(columns=base_cols)

def save_data(df, filename):
    df.to_csv(filename, index=False)

def create_form(tab, year):
    st.subheader(f"{tab} - {year}")
    df_path = f"{data_dir}/{tab.lower().replace(' ', '_')}_{year}.csv"
    df = load_data(df_path, tab)

    with st.form(f"form_{tab}"):
        faculty = st.selectbox("Faculty Name", faculty_list)
        title = st.text_input(f"{tab} Title")
        status = st.selectbox("Status", status_dict.get(tab, []))
        status_date = st.date_input("Status Date", datetime.today())
        remarks = st.text_area("Remarks (Optional)")
        doc = st.file_uploader("Upload Document", type=["pdf", "docx"])
        submit = st.form_submit_button("Submit")

    if submit:
        if faculty and title:
            duplicate = df[(df["Faculty"] == faculty) & (df["Academic Year"] == year) & (df[f"{tab} Title"] == title)]
            if not duplicate.empty:
                st.warning("This entry already exists.")
            else:
                doc_name = ""
                if doc:
                    folder_key = tab.lower().split()[0]
                    filepath = os.path.join(upload_dirs[folder_key], doc.name)
                    with open(filepath, "wb") as f:
                        f.write(doc.getbuffer())
                    doc_name = doc.name
                row = {
                    "Faculty": faculty,
                    "Academic Year": year,
                    f"{tab} Title": title,
                    "Status": status,
                    "Status Date": status_date.strftime("%Y-%m-%d"),
                    "Remarks": remarks,
                    "Uploaded File": doc_name,
                    "Submitted On": get_now(),
                    "Updated On": get_now()
                }
                df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
                save_data(df, df_path)
                st.success("Entry submitted successfully!")
        else:
            st.error("Please fill all required fields.")

    if not df.empty:
        st.markdown("### All Records")
        st.dataframe(df)

# -------------------- TABS -------------------- #
tabs = st.tabs([
    "\U0001F4C4 Journal Publications",
    "\U0001F4C1 Research Projects",
    "\U0001F4BC Consultancy Projects",
    "\U0001F9E0 Patents",
    "\U0001F680 Project Ideas",
    "\U0001F4E2 Conference",
    "\U0001F4D6 Book / Book Chapter",
    "\U0001F4CA Department Dashboard"
])

with tabs[0]:
    create_form("Journal Publications", current_year)
with tabs[1]:
    create_form("Research Projects", current_year)
with tabs[2]:
    create_form("Consultancy Projects", current_year)
with tabs[3]:
    create_form("Patents", current_year)
with tabs[4]:
    create_form("Project Ideas", current_year)
with tabs[5]:
    create_form("Conference", current_year)
with tabs[6]:
    create_form("Book / Book Chapter", current_year)
with tabs[7]:
    st.subheader("\U0001F4CA Department Dashboard Overview")
    all_data = []
    for tab in status_dict:
        for year in academic_years:
            df_path = f"{data_dir}/{tab.lower().replace(' ', '_')}_{year}.csv"
            if os.path.exists(df_path):
                df = pd.read_csv(df_path)
                df["Type"] = tab
                df["Academic Year"] = year
                all_data.append(df)

    if all_data:
        combined = pd.concat(all_data, ignore_index=True)
        st.dataframe(combined)
        chart = alt.Chart(combined).mark_bar().encode(
            x=alt.X("Faculty:N", sort="-y"),
            y="count()",
            color="Type:N",
            tooltip=["Faculty", "Type", "count()"]
        ).properties(width=900, height=400)
        st.altair_chart(chart)
    else:
        st.info("No data available yet for Department Dashboard.")
