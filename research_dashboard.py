# research_dashboard.py
import streamlit as st
import pandas as pd
import os
from datetime import datetime

# -------------------- SETUP -------------------- #
st.set_page_config(page_title="Research Dashboard", layout="wide")
st.title("🎓 Civil Engineering Research Dashboard")

# Admin access control
admin_password = st.sidebar.text_input("🔐 Admin Password (for edit access)", type="password")
is_admin = admin_password == "mitresearch2025"

# Academic Year Options
academic_years = ["2023–24", "2024–25", "2025–26"]
current_year = "2025–26"

# Folder setup
upload_dirs = {
    "journal": "uploads/journals/",
    "research": "uploads/research/",
    "consultancy": "uploads/consultancy/",
    "patent": "uploads/patents/",
}
for path in upload_dirs.values():
    os.makedirs(path, exist_ok=True)

# Faculty List
faculty_list = [
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

# Utility functions
def load_data(filename):
    return pd.read_csv(filename) if os.path.exists(filename) else pd.DataFrame()

def save_data(df, filename):
    df.to_csv(filename, index=False)

def upload_file(uploaded_file, folder):
    if uploaded_file:
        file_path = os.path.join(upload_dirs[folder], uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return uploaded_file.name
    return ""

# -------------------- TABS -------------------- #
tabs = st.tabs(["📄 Journal Publications", "📁 Research Projects", "💼 Consultancy Projects", "🧠 Patents", "🚀 Project Ideas"])

# 1. JOURNAL PUBLICATIONS
with tabs[0]:
    st.subheader("📄 Journal Publications")
    year = st.selectbox("Select Academic Year", academic_years, index=2, key="jr_year")
    journal_file = f"data/journals_{year}.csv"
    df = load_data(journal_file)

    with st.form("journal_form"):
        col1, col2 = st.columns(2)
        with col1:
            faculty = st.selectbox("Faculty Name", faculty_list)
            title = st.text_input("Journal Title")
            journal_type = st.selectbox("Journal Type", ["Scopus", "SCI", "WoS", "Non-Scopus"])
            doi = st.text_input("DOI Number")
        with col2:
            issn = st.text_input("ISSN Number")
            status = st.selectbox("Status", ["Started Writing", "Writing Completed", "Journal Identified", "Manuscript Submitted", "Under Process", "Under Review", "Published"])
            upload = st.file_uploader("Upload First Page PDF", type=["pdf"])

        submitted = st.form_submit_button("Save Journal Entry")
        if submitted:
            filename = upload_file(upload, "journal")
            new_entry = pd.DataFrame([[faculty, title, journal_type, doi, issn, status, filename, year, datetime.today()]],
                columns=["Faculty", "Title", "Type", "DOI", "ISSN", "Status", "File", "Year", "Date"])
            df = pd.concat([df, new_entry], ignore_index=True)
            save_data(df, journal_file)
            st.success("Journal entry saved successfully!")

    st.markdown("### 📊 Journal Records")
    st.dataframe(df)

# 2. RESEARCH PROJECTS
with tabs[1]:
    st.subheader("📁 Research Projects")
    year = st.selectbox("Select Academic Year", academic_years, index=2, key="rs_year")
    project_file = f"data/research_{year}.csv"
    df = load_data(project_file)

    with st.form("research_form"):
        faculty = st.selectbox("Faculty Name", faculty_list)
        title = st.text_input("Project Title")
        submitted_to = st.text_input("Submitted To (Org/Industry/MIT)")
        status = st.selectbox("Project Status", ["Idea", "Submitted", "Approved", "Scanned", "In Process", "Completed"])
        cost = st.text_input("Estimated/Approved Cost (INR)")
        upload = st.file_uploader("Upload Proposal (PDF)", type=["pdf"])

        submitted = st.form_submit_button("Save Research Project")
        if submitted:
            filename = upload_file(upload, "research")
            new_entry = pd.DataFrame([[faculty, title, submitted_to, status, cost, filename, year, datetime.today()]],
                columns=["Faculty", "Title", "Submitted To", "Status", "Cost", "File", "Year", "Date"])
            df = pd.concat([df, new_entry], ignore_index=True)
            save_data(df, project_file)
            st.success("Research project saved!")

    st.dataframe(df)

# 3. CONSULTANCY PROJECTS
with tabs[2]:
    st.subheader("💼 Consultancy Projects")
    year = st.selectbox("Select Academic Year", academic_years, index=2, key="cs_year")
    file_path = f"data/consultancy_{year}.csv"
    df = load_data(file_path)

    with st.form("consultancy_form"):
        faculty = st.selectbox("Faculty Name", faculty_list)
        title = st.text_input("Project Title")
        client = st.text_input("Client / Industry")
        status = st.selectbox("Status", ["Started", "In Progress", "Completed"])
        cost = st.text_input("Revenue / Cost (INR)")
        upload = st.file_uploader("Upload Work Order (PDF)", type=["pdf"])

        submitted = st.form_submit_button("Save Consultancy Project")
        if submitted:
            filename = upload_file(upload, "consultancy")
            new_entry = pd.DataFrame([[faculty, title, client, status, cost, filename, year, datetime.today()]],
                columns=["Faculty", "Title", "Client", "Status", "Cost", "File", "Year", "Date"])
            df = pd.concat([df, new_entry], ignore_index=True)
            save_data(df, file_path)
            st.success("Consultancy record saved!")

    st.dataframe(df)

# 4. PATENTS
with tabs[3]:
    st.subheader("🧠 Patent Details")
    year = st.selectbox("Select Academic Year", academic_years, index=2, key="pt_year")
    file_path = f"data/patents_{year}.csv"
    df = load_data(file_path)

    with st.form("patent_form"):
        faculty = st.selectbox("Faculty Name", faculty_list)
        title = st.text_input("Invention Title")
        app_no = st.text_input("Application Number")
        patent_type = st.selectbox("Patent Type", ["National", "International"])
        status = st.selectbox("Patent Status", ["Drafting", "Filed", "Published", "Granted"])
        upload = st.file_uploader("Upload Patent Document (PDF)", type=["pdf"])

        submitted = st.form_submit_button("Save Patent")
        if submitted:
            filename = upload_file(upload, "patent")
            new_entry = pd.DataFrame([[faculty, title, app_no, patent_type, status, filename, year, datetime.today()]],
                columns=["Faculty", "Title", "App No", "Type", "Status", "File", "Year", "Date"])
            df = pd.concat([df, new_entry], ignore_index=True)
            save_data(df, file_path)
            st.success("Patent record saved!")

    st.dataframe(df)

# 5. PROJECT IDEAS
with tabs[4]:
    st.subheader("🚀 Project Ideas")
    year = st.selectbox("Select Academic Year", academic_years, index=2, key="pi_year")
    file_path = f"data/project_ideas_{year}.csv"
    df = load_data(file_path)

    with st.form("project_idea_form"):
        faculty = st.selectbox("Faculty Name", faculty_list)
        title = st.text_input("Project Idea Title")
        status = st.selectbox("Status", ["Idea Only", "Work Started", "Assigned as Project"])
        assigned_to = st.selectbox("Assigned To", ["", "S.Y", "T.Y", "F.Y", "M.Tech Transportation", "M.Tech Structural", "Ph.D"])
        domain = st.text_input("Domain / Type")

        submitted = st.form_submit_button("Save Project Idea")
        if submitted:
            new_entry = pd.DataFrame([[faculty, title, status, assigned_to, domain, year, datetime.today()]],
                columns=["Faculty", "Title", "Status", "Assigned To", "Domain", "Year", "Date"])
            df = pd.concat([df, new_entry], ignore_index=True)
            save_data(df, file_path)
            st.success("Project idea saved!")

    st.dataframe(df)
