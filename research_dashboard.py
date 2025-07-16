# research_dashboard.py
import streamlit as st
import pandas as pd
import os
from datetime import datetime
import altair as alt

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
tabs = st.tabs([
    "📄 Journal Publications",
    "📁 Research Projects",
    "💼 Consultancy Projects",
    "🧠 Patents",
    "🚀 Project Ideas",
    "📊 Department Dashboard"
])

# 1. JOURNAL PUBLICATIONS TAB
with tabs[0]:
    st.subheader("📄 Journal Publications")
    year = st.selectbox("Select Academic Year", academic_years, index=2, key="journal_year")
    filename = f"data/journals_{year}.csv"
    df = load_data(filename)

    with st.form("journal_form"):
        col1, col2 = st.columns(2)
        faculty = col1.selectbox("Faculty Name", faculty_list)
        journal_name = col2.text_input("Journal Name")
        col3, col4 = st.columns(2)
        indexing = col3.selectbox("Indexing", ["Scopus", "SCI", "WoS", "Non-Indexed"])
        status = col4.selectbox("Status", ["Started Writing", "Writing Completed", "Journal Identified", "Manuscript Submitted", "Under Process", "Under Review", "Published"])
        col5, col6 = st.columns(2)
        doi = col5.text_input("DOI Number")
        issn = col6.text_input("ISSN Number")
        first_page = st.file_uploader("Upload First Page PDF", type=["pdf"])

        submitted = st.form_submit_button("Submit")
        if submitted:
            file_uploaded = upload_file(first_page, "journal") if first_page else ""
            new_entry = pd.DataFrame([[faculty, journal_name, indexing, status, doi, issn, file_uploaded]],
                                      columns=["Faculty", "Journal Name", "Indexing", "Status", "DOI", "ISSN", "First Page PDF"])
            df = pd.concat([df, new_entry], ignore_index=True)
            save_data(df, filename)
            st.success("Journal entry submitted.")

    st.markdown("### 📋 Submitted Journal Entries")
    st.dataframe(df)

# Placeholder for other tabs to be implemented in the next update
with tabs[1]:
    st.subheader("📁 Research Projects")
    st.info("Form under development. Coming up in next update!")

with tabs[2]:
    st.subheader("💼 Consultancy Projects")
    st.info("Form under development. Coming up in next update!")

with tabs[3]:
    st.subheader("🧠 Patents")
    st.info("Form under development. Coming up in next update!")

with tabs[4]:
    st.subheader("🚀 Project Ideas")
    st.info("Form under development. Coming up in next update!")

# 6. DEPARTMENT-WIDE DASHBOARD
with tabs[5]:
    st.subheader("📊 Department-Wide Research Overview")

    for year in academic_years:
        st.markdown(f"### 📅 Academic Year: {year}")

        # Journals
        journal_path = f"data/journals_{year}.csv"
        if os.path.exists(journal_path):
            st.markdown("**📄 Journal Publications**")
            df_journal = pd.read_csv(journal_path)
            st.dataframe(df_journal)
            chart = alt.Chart(df_journal).mark_bar().encode(
                x="Status",
                y="count()",
                color="Status",
                tooltip=["Status", "count()"]
            ).properties(title="Journal Publication Status")
            st.altair_chart(chart, use_container_width=True)

        # Research Projects
        res_path = f"data/research_{year}.csv"
        if os.path.exists(res_path):
            st.markdown("**📁 Research Projects**")
            df_research = pd.read_csv(res_path)
            st.dataframe(df_research)
            chart = alt.Chart(df_research).mark_bar().encode(
                x="Status",
                y="count()",
                color="Status",
                tooltip=["Status", "count()"]
            ).properties(title="Research Project Status")
            st.altair_chart(chart, use_container_width=True)

        # Consultancy Projects
        con_path = f"data/consultancy_{year}.csv"
        if os.path.exists(con_path):
            st.markdown("**💼 Consultancy Projects**")
            df_consult = pd.read_csv(con_path)
            st.dataframe(df_consult)
            chart = alt.Chart(df_consult).mark_bar().encode(
                x="Status",
                y="count()",
                color="Status",
                tooltip=["Status", "count()"]
            ).properties(title="Consultancy Project Status")
            st.altair_chart(chart, use_container_width=True)

        # Patents
        pt_path = f"data/patents_{year}.csv"
        if os.path.exists(pt_path):
            st.markdown("**🧠 Patents**")
            df_patents = pd.read_csv(pt_path)
            st.dataframe(df_patents)
            chart = alt.Chart(df_patents).mark_bar().encode(
                x="Status",
                y="count()",
                color="Status",
                tooltip=["Status", "count()"]
            ).properties(title="Patent Filing Status")
            st.altair_chart(chart, use_container_width=True)

        # Project Ideas
        idea_path = f"data/project_ideas_{year}.csv"
        if os.path.exists(idea_path):
            st.markdown("**🚀 Project Ideas**")
            df_ideas = pd.read_csv(idea_path)
            st.dataframe(df_ideas)
            chart = alt.Chart(df_ideas).mark_bar().encode(
                x="Status",
                y="count()",
                color="Status",
                tooltip=["Status", "count()"]
            ).properties(title="Project Idea Development Status")
            st.altair_chart(chart, use_container_width=True)

    st.info("All data shown above is read-only. For any changes, please contact the admin.")
