# research_dashboard.py (updated with Conference and Book Tabs)
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

status_options = ["Idea", "Submitted", "Under Review", "Approved", "Sanctioned", "Completed", "Rejected"]

journal_indexing = ["Scopus", "SCI", "Web of Science", "Non-Scopus"]

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

def get_pdf_download(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    col_width = pdf.w / (len(df.columns) + 1)
    row_height = pdf.font_size * 1.5
    for col in df.columns:
        pdf.cell(col_width, row_height, str(col), border=1)
    pdf.ln(row_height)
    for i in range(len(df)):
        for col in df.columns:
            value = str(df.iloc[i][col])
            pdf.cell(col_width, row_height, value[:25], border=1)
        pdf.ln(row_height)
    output = BytesIO()
    pdf.output(output)
    output.seek(0)
    return output

def get_now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def create_form(tab, year):
    st.subheader(f"Add New {tab} Entry")
    df_path = f"data/{tab.lower().replace(' ', '_')}_{year}.csv"
    df = load_data(df_path)

    with st.form(f"form_{tab}"):
        faculty = st.selectbox("Faculty Name", ["Select Faculty"] + faculty_list)
        if faculty == "Select Faculty":
            st.warning("Please select a faculty name before submitting.")
        title = st.text_input(f"{tab} Title")
        status = st.selectbox("Status", status_options)
        status_date = st.date_input("Status Date", datetime.today())

        if tab == "Journal Publications":
            journal_name = st.text_input("Journal Name")
            indexing = st.selectbox("Indexing", journal_indexing)
            issn = st.text_input("ISSN Number")
            doi = st.text_input("DOI Number")
        elif tab == "Research Projects":
            agency = st.text_input("Funding Agency")
            amount = st.number_input("Sanctioned Amount (₹)", min_value=0.0)
            role = st.selectbox("Role", ["PI", "Co-PI"])
            duration = st.number_input("Project Duration (Months)", min_value=1)
        elif tab == "Consultancy Projects":
            client = st.text_input("Client/Agency Name")
            amount = st.number_input("Consultancy Amount (₹)", min_value=0.0)
        elif tab == "Patents":
            patent_type = st.selectbox("Patent Type", ["Provisional", "Complete", "Design", "Copyright"])
            inventors = st.multiselect("Inventors", faculty_list)
            application_no = st.text_input("Patent Application Number")
            filing_date = st.date_input("Filing Date")
        elif tab == "Project Ideas":
            description = st.text_area("Idea Description")
        elif tab == "Conference":
            conf_name = st.text_input("Conference Name")
            location = st.text_input("Location")
            level = st.selectbox("Level", ["National", "International"])
            presentation_type = st.selectbox("Presentation Type", ["Oral", "Poster"])
        elif tab == "Book / Book Chapter":
            book_chap_type = st.selectbox("Entry Type", ["Book", "Book Chapter"])
            book_title = st.text_input("Book Title")
            chapter_title = st.text_input("Chapter Title (if any)")
            publisher = st.text_input("Publisher")
            isbn = st.text_input("ISBN")

        remarks = st.text_area("Remarks (Optional)")
        doc_upload = st.file_uploader("Upload Supporting Document (PDF/DOCX)", type=["pdf", "docx"])
        submit = st.form_submit_button("Submit")

    if submit:
        duplicate_check = df[
            (df["Faculty"] == faculty) &
            (df["Academic Year"] == year) &
            (df[f"{tab} Title"] == title)
        ]
        if not duplicate_check.empty:
            st.warning("Duplicate entry found. This record already exists.")
        else:
            doc_name = upload_file(doc_upload, tab.lower().split()[0])
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
        if tab == "Journal Publications":
            row.update({"Journal Name": journal_name, "Indexing": indexing, "ISSN": issn, "DOI": doi})
        elif tab == "Research Projects":
            row.update({"Agency": agency, "Amount": amount, "Role": role, "Duration": duration})
        elif tab == "Consultancy Projects":
            row.update({"Client": client, "Amount": amount})
        elif tab == "Patents":
            row.update({"Patent Type": patent_type, "Inventors": ", ".join(inventors), "Application No": application_no, "Filing Date": filing_date.strftime("%Y-%m-%d")})
        elif tab == "Project Ideas":
            row.update({"Description": description})
        elif tab == "Conference":
            row.update({"Conference Name": conf_name, "Location": location, "Level": level, "Presentation Type": presentation_type})
        elif tab == "Book / Book Chapter":
            row.update({"Entry Type": book_chap_type, "Book Title": book_title, "Chapter Title": chapter_title, "Publisher": publisher, "ISBN": isbn})

        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
        save_data(df, df_path)
        st.success(f"{tab} entry submitted successfully!")

    if is_admin:
        st.markdown("### Admin: Upload CSV Data")
        uploaded_csv = st.file_uploader("Upload CSV File to Import Data", type=["csv"], key=f"admin_csv_{tab}")
        if uploaded_csv:
            uploaded_df = pd.read_csv(uploaded_csv)
            df = pd.concat([df, uploaded_df], ignore_index=True)
            save_data(df, df_path)
            st.success("CSV data uploaded and merged successfully!")

    if not df.empty:
        st.markdown(f"### {tab} Records")
        st.dataframe(df)
        st.download_button("Download Excel", get_excel_download(df, f"{tab.lower().replace(' ', '_')}_{year}.xlsx"), file_name=f"{tab.lower().replace(' ', '_')}_{year}.xlsx")
        st.download_button("Download PDF", get_pdf_download(df), file_name=f"{tab.lower().replace(' ', '_')}_{year}.pdf")

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
    all_dataframes = []
    for year in academic_years:
        for tab in ["journal", "research", "consultancy", "patent", "ideas", "conference", "book"]:
            df_path = f"data/{tab}_{year}.csv"
            if os.path.exists(df_path):
                df = load_data(df_path)
                df["Academic Year"] = year
                df["Type"] = tab.capitalize()
                all_dataframes.append(df)

    if all_dataframes:
        all_data = pd.concat(all_dataframes, ignore_index=True)
        selected_year = st.selectbox("Filter by Academic Year", academic_years, index=2)
        selected_faculty = st.selectbox("Filter by Faculty", ["All"] + faculty_list)
        filtered = all_data[all_data["Academic Year"] == selected_year]
        selected_type = st.selectbox("Filter by Entry Type", ["All"] + sorted(all_data["Type"].unique()))
        selected_status = st.selectbox("Filter by Status", ["All"] + sorted(all_data["Status"].dropna().unique()))
        if selected_type != "All":
            filtered = filtered[filtered["Type"] == selected_type]
        if selected_status != "All":
            filtered = filtered[filtered["Status"] == selected_status]
        if selected_faculty != "All":
            filtered = filtered[filtered["Faculty"] == selected_faculty]
        st.dataframe(filtered)
        st.download_button("Download All Records (Excel)", get_excel_download(filtered, f"department_dashboard_{selected_year}.xlsx"), file_name=f"department_dashboard_{selected_year}.xlsx")
        st.download_button("Download PDF", get_pdf_download(filtered), file_name=f"department_dashboard_{selected_year}.pdf")
        chart = alt.Chart(filtered).mark_bar().encode(x="Faculty", y="count()", color="Type").properties(width=900, height=400)
        st.altair_chart(chart)
    else:
        st.info("No data available yet for Department Dashboard.")
