# research_dashboard.py
import streamlit as st
import pandas as pd
import os
from datetime import datetime
import altair as alt
from io import BytesIO

# -------------------- SETUP -------------------- #
st.set_page_config(page_title="Research Dashboard", layout="wide")
st.title("\U0001F393 Civil Engineering Research Dashboard")

# Admin access control
admin_password = st.sidebar.text_input("\U0001F512 Admin Password (for edit access)", type="password")
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
    "ideas": "uploads/ideas/"
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

def get_excel_download(df, filename):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return output

# -------------------- TABS -------------------- #
tabs = st.tabs([
    "\U0001F4C4 Journal Publications",
    "\U0001F4C1 Research Projects",
    "\U0001F4BC Consultancy Projects",
    "\U0001F9E0 Patents",
    "\U0001F680 Project Ideas",
    "\U0001F4CA Department Dashboard"
])

# 1. JOURNAL PUBLICATION TAB
with tabs[0]:
    st.subheader("📄 Journal Publications")
    st.markdown("Enter details of your journal papers below.")
    with st.form("journal_form"):
        year = st.selectbox("Academic Year", academic_years, index=2)
        faculty = st.selectbox("Faculty Name", faculty_list)
        journal_name = st.text_input("Journal Name")
        indexing = st.selectbox("Indexing", ["Scopus", "SCI", "WoS", "Non-Scopus"])
        doi = st.text_input("DOI Number")
        issn = st.text_input("ISSN Number")
        status = st.selectbox("Publication Status", [
            "Started Writing", "Writing Completed", "Journal Identified", "Manuscript Submitted",
            "Under Process", "Under Review", "Published"
        ])
        pdf_file = st.file_uploader("Upload First Page PDF", type=["pdf"])
        submit = st.form_submit_button("Submit")

        if submit:
            filename = f"data/journals_{year}.csv"
            df = load_data(filename)
            new_row = pd.DataFrame.from_dict([{
                "Faculty": faculty,
                "Journal": journal_name,
                "Indexing": indexing,
                "DOI": doi,
                "ISSN": issn,
                "Status": status,
                "PDF": upload_file(pdf_file, "journal")
            }])
            df = pd.concat([df, new_row], ignore_index=True)
            save_data(df, filename)
            st.success("Journal entry added successfully!")

# 2. RESEARCH PROJECT TAB
with tabs[1]:
    st.subheader("📁 Research Projects")
    st.markdown("Enter research project details.")
    with st.form("research_form"):
        year = st.selectbox("Academic Year", academic_years, index=2, key="research_year")
        faculty = st.selectbox("Faculty Name", faculty_list, key="research_faculty")
        project_title = st.text_input("Project Title")
        submitted_to = st.text_input("Submitted to (Organization/Agency)")
        status = st.selectbox("Project Status", ["Submitted", "Approved", "Scanned", "In Process", "Completed"])
        upload_file_proj = st.file_uploader("Upload Project File (if any)", type=["pdf", "docx"])
        submit = st.form_submit_button("Submit Project")

        if submit:
            filename = f"data/research_{year}.csv"
            df = load_data(filename)
            new_row = pd.DataFrame.from_dict([{
                "Faculty": faculty,
                "Project Title": project_title,
                "Submitted To": submitted_to,
                "Status": status,
                "File": upload_file(upload_file_proj, "research")
            }])
            df = pd.concat([df, new_row], ignore_index=True)
            save_data(df, filename)
            st.success("Research project submitted.")

# 3. CONSULTANCY PROJECT TAB
with tabs[2]:
    st.subheader("💼 Consultancy Projects")
    st.markdown("Enter consultancy project details.")
    with st.form("consultancy_form"):
        year = st.selectbox("Academic Year", academic_years, index=2, key="cons_year")
        faculty = st.selectbox("Faculty Name", faculty_list, key="cons_faculty")
        project_title = st.text_input("Project Title")
        client = st.text_input("Client/Industry/Organization")
        status = st.selectbox("Status", ["Started", "In Progress", "Documentation", "Completed"])
        cost = st.number_input("Project Cost (in ₹)", min_value=0)
        upload_file_cons = st.file_uploader("Upload File (if any)", type=["pdf", "docx"])
        submit = st.form_submit_button("Submit Consultancy")

        if submit:
            filename = f"data/consultancy_{year}.csv"
            df = load_data(filename)
            new_row = pd.DataFrame.from_dict([{
                "Faculty": faculty,
                "Project Title": project_title,
                "Client": client,
                "Status": status,
                "Cost": cost,
                "File": upload_file(upload_file_cons, "consultancy")
            }])
            df = pd.concat([df, new_row], ignore_index=True)
            save_data(df, filename)
            st.success("Consultancy project entry added.")

# 4. PATENTS TAB
with tabs[3]:
    st.subheader("🧠 Patents")
    st.markdown("Enter patent details.")
    with st.form("patent_form"):
        year = st.selectbox("Academic Year", academic_years, index=2, key="patent_year")
        faculty = st.selectbox("Faculty Name", faculty_list, key="patent_faculty")
        title = st.text_input("Patent Title")
        status = st.selectbox("Status", ["Filed", "Published", "Granted", "Under Process"])
        domain = st.text_input("Technical Domain")
        file_upload = st.file_uploader("Upload Patent File (if any)", type=["pdf"])
        submit = st.form_submit_button("Submit Patent")

        if submit:
            filename = f"data/patents_{year}.csv"
            df = load_data(filename)
            new_row = pd.DataFrame.from_dict([{
                "Faculty": faculty,
                "Title": title,
                "Domain": domain,
                "Status": status,
                "File": upload_file(file_upload, "patent")
            }])
            df = pd.concat([df, new_row], ignore_index=True)
            save_data(df, filename)
            st.success("Patent entry submitted.")

# 5. PROJECT IDEAS TAB
with tabs[4]:
    st.subheader("🚀 Project Ideas")
    st.markdown("Enter new or ongoing research/project ideas.")
    with st.form("idea_form"):
        year = st.selectbox("Academic Year", academic_years, index=2, key="idea_year")
        faculty = st.selectbox("Faculty Name", faculty_list, key="idea_faculty")
        idea = st.text_area("Project Idea Title")
        status = st.selectbox("Status", ["Idea", "Started", "Given to Student"])
        assigned_to = st.selectbox("Assigned To (if any)", ["", "S.Y", "T.Y", "F.Y", "M.Tech - Structural", "M.Tech - Transportation", "Ph.D"])
        submit = st.form_submit_button("Submit Idea")

        if submit:
            filename = f"data/ideas_{year}.csv"
            df = load_data(filename)
            new_row = pd.DataFrame.from_dict([{
                "Faculty": faculty,
                "Idea": idea,
                "Status": status,
                "Assigned To": assigned_to
            }])
            df = pd.concat([df, new_row], ignore_index=True)
            save_data(df, filename)
            st.success("Project idea submitted.")

# 6. DEPARTMENT DASHBOARD TAB
with tabs[5]:
    st.subheader("📊 Department-Wide Research Overview")
    selected_year = st.selectbox("Select Academic Year", academic_years, index=2, key="dashboard_year")

    # Load all data
    journal_df = load_data(f"data/journals_{selected_year}.csv")
    research_df = load_data(f"data/research_{selected_year}.csv")
    consultancy_df = load_data(f"data/consultancy_{selected_year}.csv")
    patent_df = load_data(f"data/patents_{selected_year}.csv")
    ideas_df = load_data(f"data/ideas_{selected_year}.csv")

    st.markdown("### 📘 Journal Publications Summary")
    if not journal_df.empty:
        st.dataframe(journal_df)
        chart = alt.Chart(journal_df).mark_bar().encode(
            x='Status',
            y='count()',
            color='Status'
        ).properties(width=600)
        st.altair_chart(chart)

    st.markdown("### 📈 Research Projects Summary")
    if not research_df.empty:
        st.dataframe(research_df)
        chart = alt.Chart(research_df).mark_bar().encode(
            x='Status',
            y='count()',
            color='Status'
        ).properties(width=600)
        st.altair_chart(chart)

    st.markdown("### 💼 Consultancy Summary")
    if not consultancy_df.empty:
        st.dataframe(consultancy_df)
        chart = alt.Chart(consultancy_df).mark_bar().encode(
            x='Status',
            y='count()',
            color='Status'
        ).properties(width=600)
        st.altair_chart(chart)

    st.markdown("### 🧠 Patents Summary")
    if not patent_df.empty:
        st.dataframe(patent_df)
        chart = alt.Chart(patent_df).mark_bar().encode(
            x='Status',
            y='count()',
            color='Status'
        ).properties(width=600)
        st.altair_chart(chart)

    st.markdown("### 🚀 Project Ideas Summary")
    if not ideas_df.empty:
        st.dataframe(ideas_df)
        chart = alt.Chart(ideas_df).mark_bar().encode(
            x='Status',
            y='count()',
            color='Status'
        ).properties(width=600)
        st.altair_chart(chart)

    st.success("All department-wide data and summaries are visible above.")