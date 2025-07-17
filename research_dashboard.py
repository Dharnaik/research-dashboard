# research_dashboard.py
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

def get_pdf_download(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    col_width = pdf.w / (len(df.columns) + 1)
    row_height = pdf.font_size * 1.5

    # Header
    for col in df.columns:
        pdf.cell(col_width, row_height, str(col), border=1)
    pdf.ln(row_height)

    # Rows
    for i in range(len(df)):
        for col in df.columns:
            value = str(df.iloc[i][col])
            pdf.cell(col_width, row_height, value[:25], border=1)
        pdf.ln(row_height)

    output = BytesIO()
    pdf.output(output)
    output.seek(0)
    return output

# Timestamp
def get_now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# -------------------- TABS -------------------- #
tabs = st.tabs([
    "\U0001F4C4 Journal Publications",
    "\U0001F4C1 Research Projects",
    "\U0001F4BC Consultancy Projects",
    "\U0001F9E0 Patents",
    "\U0001F680 Project Ideas",
    "\U0001F4CA Department Dashboard"
])

# Tab Templates
def create_tab(tab_name, field_label):
    with st.container():
        st.subheader(f"Add {tab_name} Entry")
        selected_year = st.selectbox("Select Academic Year", academic_years, index=2, key=f"{tab_name.lower()}_year")
        df_path = f"data/{tab_name.lower()}_{selected_year}.csv"
        df = load_data(df_path)

        with st.form(f"{tab_name.lower()}_form"):
            faculty = st.selectbox("Faculty Name", faculty_list, key=f"faculty_{tab_name}")
            title = st.text_input(f"{field_label} Title")
            status = st.selectbox("Status", ["Idea Stage", "Submitted", "Approved", "Sanctioned", "In Process", "Completed"])
            doc_upload = st.file_uploader("Upload Supporting Document (Optional)", type=["pdf", "docx"])
            submit = st.form_submit_button("Submit")

        timestamp = get_now()

        if submit:
            duplicate = df[(df['Faculty'] == faculty) & (df[f'{field_label} Title'] == title)]
            if not duplicate.empty:
                st.warning(f"This {tab_name.lower()} already exists. You can only update the status.")
                if is_admin:
                    new_status = st.selectbox("Update Status", ["Idea Stage", "Submitted", "Approved", "Sanctioned", "In Process", "Completed"], key=f"update_{tab_name}_status")
                    df.loc[(df['Faculty'] == faculty) & (df[f'{field_label} Title'] == title), 'Previous Status'] = df.loc[(df['Faculty'] == faculty) & (df[f'{field_label} Title'] == title), 'Status']
                    df.loc[(df['Faculty'] == faculty) & (df[f'{field_label} Title'] == title), 'Status'] = new_status
                    df.loc[(df['Faculty'] == faculty) & (df[f'{field_label} Title'] == title), 'Updated On'] = timestamp
                    save_data(df, df_path)
                    st.success(f"{tab_name} status updated successfully!")
            else:
                doc_name = upload_file(doc_upload, tab_name.lower())
                new_row = pd.DataFrame([{
                    "Faculty": faculty,
                    f"{field_label} Title": title,
                    "Status": status,
                    "Previous Status": "-",
                    "Uploaded File": doc_name,
                    "Submitted On": timestamp,
                    "Updated On": timestamp
                }])
                df = pd.concat([df, new_row], ignore_index=True)
                save_data(df, df_path)
                st.success(f"{tab_name} submitted successfully!")

        if not df.empty:
            st.markdown(f"### {tab_name} Records")
            st.dataframe(df)
            st.download_button("Download Excel", get_excel_download(df, f"{tab_name.lower()}_{selected_year}.xlsx"), file_name=f"{tab_name.lower()}_{selected_year}.xlsx")
            st.download_button("Download PDF", get_pdf_download(df), file_name=f"{tab_name.lower()}_{selected_year}.pdf")

# Apply to all tabs
with tabs[0]:
    create_tab("Journal Publications", "Journal")

with tabs[1]:
    create_tab("Research Projects", "Research")

with tabs[2]:
    create_tab("Consultancy Projects", "Consultancy")

with tabs[3]:
    create_tab("Patents", "Patent")

with tabs[4]:
    create_tab("Project Ideas", "Idea")

# Dashboard Tab
with tabs[5]:
    st.subheader("\U0001F4CA Department Dashboard Overview")
    all_dataframes = []
    for year in academic_years:
        for tab in ["journal", "research", "consultancy", "patent", "ideas"]:
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
        if selected_faculty != "All":
            filtered = filtered[filtered["Faculty"] == selected_faculty]

        st.dataframe(filtered)

        st.download_button("Download All Records (Excel)", get_excel_download(filtered, f"department_dashboard_{selected_year}.xlsx"), file_name=f"department_dashboard_{selected_year}.xlsx")
        st.download_button("Download PDF", get_pdf_download(filtered), file_name=f"department_dashboard_{selected_year}.pdf")

        chart = alt.Chart(filtered).mark_bar().encode(
            x="Faculty",
            y="count()",
            color="Type"
        ).properties(width=900, height=400)
        st.altair_chart(chart)
    else:
        st.info("No data available yet for Department Dashboard.")
