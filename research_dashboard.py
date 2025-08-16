# research_dashboard.py
# Persistent storage via Google Sheets + Admin edit + year handling fixes

import os
from datetime import datetime

import streamlit as st
import pandas as pd
import altair as alt

# Optional import kept if you later add PDF exports
from fpdf import FPDF  # noqa: F401

# ---------- Google Sheets libraries ----------
import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import set_with_dataframe, get_as_dataframe

# -------------------- APP SETUP -------------------- #
st.set_page_config(page_title="Research Dashboard", layout="wide")
st.title("\U0001F393 Civil Engineering Research Dashboard")

# -------------------- AUTH -------------------- #
admin_users = {"admin@mit.edu": "mitresearch2025"}
admin_email = st.sidebar.text_input("\U0001F4E7 Admin Email")
admin_password = st.sidebar.text_input("\U0001F512 Admin Password", type="password")
is_admin = admin_users.get(admin_email) == admin_password

# -------------------- CONSTANTS -------------------- #
academic_years = ["2025–26", "2026–27", "2027–28"]
DEFAULT_YEAR = "2025–26"

# Local (temporary on cloud) folders for uploads
upload_dirs = {
    "journal": "uploads/journals/",
    "research": "uploads/research/",
    "consultancy": "uploads/consultancy/",
    "patent": "uploads/patents/",
    "ideas": "uploads/ideas/",           # <- correct mapping for Project Ideas
    "conference": "uploads/conference/",
    "book": "uploads/book/"
}
for p in upload_dirs.values():
    os.makedirs(p, exist_ok=True)

# Upload tab -> folder key map
UPLOAD_KEY = {
    "Journal Publications": "journal",
    "Research Projects": "research",
    "Consultancy Projects": "consultancy",
    "Patents": "patent",
    "Project Ideas": "ideas",            # <- fixed
    "Conference": "conference",
    "Book / Book Chapter": "book",
}

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
    "Prof. Sagar K. Sonawane",
]

status_dict = {
    "Journal Publications": ["Started Writing", "Journal Identifying", "Manuscript Submitted", "In Process", "Under Review", "Accepted", "Published"],
    "Research Projects": ["Idea", "Submitted", "In Process of Approval", "Approved", "In Process", "Completed"],
    "Consultancy Projects": ["Idea Stage", "Submitted", "Approved", "Sanctioned", "In Process", "Completed"],
    "Patents": ["Filed", "Published", "Granted"],
    "Project Ideas": [
        "Drafted", "Submitted", "Under Review", "Implemented",
        "S.Y Mini Project", "T.Y Mini Project", "B.Tech Project",
        "M.Tech TRE", "M.Tech STR", "Ph.D."
    ],
    "Conference": ["Submitted", "Accepted", "Presented"],
    "Book / Book Chapter": ["Proposal Submitted", "Accepted", "In Press", "Published"],
}

journal_indexing = ["Scopus", "SCI", "Web of Science", "Non-Scopus"]
scopus_quartiles = ["Q1", "Q2", "Q3", "Q4"]

def get_now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# -------------------- GOOGLE SHEETS BACKEND -------------------- #
USE_GSHEETS = True  # Keep True on Streamlit Cloud

def _gs_client():
    creds = Credentials.from_service_account_info(
        dict(st.secrets["gcp_service_account"]),
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ],
    )
    return gspread.authorize(creds)

def _open_sheet(client):
    return client.open_by_key(st.secrets["GSHEET_ID"])

def _ws_name(tab: str, year: str) -> str:
    # Worksheet title "Tab__Year" (replace '/' so it's a valid title)
    return f"{tab.replace('/', '-') }__{year}"

def base_columns(tab: str) -> list[str]:
    title_col = f"{tab} Title"
    cols = ["Faculty", "Academic Year", title_col, "Status", "Status Date",
            "Remarks", "Uploaded File", "Submitted On", "Updated On"]
    if tab == "Journal Publications":
        cols += ["ISSN", "DOI", "Volume", "Issue", "Date of Publication", "Indexing", "Scopus Quartile"]
    return cols

def _ensure_worksheet(sh, ws_title: str, cols: list[str]):
    try:
        ws = sh.worksheet(ws_title)
    except gspread.exceptions.WorksheetNotFound:
        ws = sh.add_worksheet(title=ws_title, rows=2000, cols=max(26, len(cols)))
        empty = pd.DataFrame(columns=cols)
        set_with_dataframe(ws, empty, include_index=False, resize=True)
    return ws

def load_df(tab: str, year: str) -> pd.DataFrame:
    cols = base_columns(tab)
    if USE_GSHEETS:
        client = _gs_client()
        sh = _open_sheet(client)
        ws = _ensure_worksheet(sh, _ws_name(tab, year), cols)
        df = get_as_dataframe(ws, evaluate_formulas=True, header=0)
        if df is None:
            return pd.DataFrame(columns=cols)
        df = df.dropna(how="all")
        # Ensure all expected columns exist
        for c in cols:
            if c not in df.columns:
                df[c] = ""
        # Preserve column order
        df = df[cols]
        return df
    else:
        # Fallback to local CSV (non-persistent on cloud)
        path = f"data/{tab.replace(' ', '_').replace('/', '-')}_{year}.csv"
        if os.path.exists(path):
            return pd.read_csv(path)
        return pd.DataFrame(columns=cols)

def save_df(tab: str, year: str, df: pd.DataFrame):
    cols = base_columns(tab)
    df = df.copy()
    for c in cols:
        if c not in df.columns:
            df[c] = ""
    df = df[cols]
    if USE_GSHEETS:
        client = _gs_client()
        sh = _open_sheet(client)
        ws = _ensure_worksheet(sh, _ws_name(tab, year), cols)
        set_with_dataframe(ws, df, include_index=False, resize=True)
    else:
        path = f"data/{tab.replace(' ', '_').replace('/', '-')}_{year}.csv"
        df.to_csv(path, index=False)

# -------------------- UI: FORM PER TAB -------------------- #
def create_form(tab: str):
    st.subheader(tab)

    # Unique key per tab for this selectbox
    year_selected = st.selectbox(
        "Academic Year",
        academic_years,
        index=academic_years.index(DEFAULT_YEAR),
        key=f"year_{tab}"
    )
    df = load_df(tab, year_selected)

    with st.form(f"form_{tab}"):
        faculty = st.selectbox(
            "Faculty Name",
            faculty_list,
            index=0,
            key=f"faculty_{tab}"
        )
        title = st.text_input(
            f"{tab} Title",
            key=f"title_{tab}"
        )
        status = st.selectbox(
            "Status",
            status_dict.get(tab, []),
            key=f"status_{tab}"
        )
        status_date = st.date_input(
            "Status Date",
            datetime.today(),
            key=f"status_date_{tab}"
        )

        # Journal extras (only if Published)
        issn = doi = volume = issue = pub_date = quartile = indexing = ""
        if tab == "Journal Publications" and status == "Published":
            issn = st.text_input("ISSN Number", key=f"issn_{tab}")
            doi = st.text_input("DOI Number", key=f"doi_{tab}")
            volume = st.text_input("Volume", key=f"volume_{tab}")
            issue = st.text_input("Issue", key=f"issue_{tab}")
            pub_date = st.date_input(
                "Date of Publication",
                datetime.today(),
                key=f"pubdate_{tab}"
            ).strftime("%Y-%m-%d")
            indexing = st.selectbox("Indexing", journal_indexing, key=f"indexing_{tab}")
            if indexing == "Scopus":
                quartile = st.selectbox("Scopus Quartile", scopus_quartiles, key=f"quartile_{tab}")

        remarks = st.text_area("Remarks (Optional)", key=f"remarks_{tab}")
        doc = st.file_uploader(
            "Upload Document (optional; cloud storage is temporary)",
            type=["pdf", "docx"],
            key=f"doc_{tab}"
        )

        submit = st.form_submit_button("Submit", use_container_width=True)

    if submit:
        if faculty == "Select Your Name" or not title or not status:
            st.error("Please fill all required fields (Faculty, Title, Status).")
        else:
            title_col = f"{tab} Title"
            duplicate = df[
                (df["Faculty"] == faculty) &
                (df["Academic Year"] == year_selected) &
                (df[title_col] == title)
            ]
            if not duplicate.empty:
                st.warning("This entry already exists for the selected academic year.")
            else:
                # Save uploaded doc to a temporary local folder (note: not permanent on free cloud)
                doc_name = ""
                if doc is not None:
                    folder_key = UPLOAD_KEY.get(tab, tab.lower().split()[0])
                    filepath = os.path.join(upload_dirs[folder_key], doc.name)
                    with open(filepath, "wb") as f:
                        f.write(doc.getbuffer())
                    doc_name = doc.name

                row = {
                    "Faculty": faculty,
                    "Academic Year": year_selected,
                    title_col: title,
                    "Status": status,
                    "Status Date": status_date.strftime("%Y-%m-%d"),
                    "Remarks": remarks,
                    "Uploaded File": doc_name,
                    "Submitted On": get_now(),
                    "Updated On": get_now(),
                }
                if tab == "Journal Publications" and status == "Published":
                    row.update({
                        "ISSN": issn,
                        "DOI": doi,
                        "Volume": volume,
                        "Issue": issue,
                        "Date of Publication": pub_date,
                        "Indexing": indexing,
                        "Scopus Quartile": quartile,
                    })

                df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
                save_df(tab, year_selected, df)
                st.success("Entry submitted successfully!")
                st.info("Tip: For permanent file storage, paste a Google Drive link in Remarks or integrate Drive uploads later.")

    # Display & Admin edit
    if not df.empty:
        st.markdown("### All Records")
        st.dataframe(df, use_container_width=True)

        if is_admin:
            st.markdown("#### Edit Mode (Admin Only)")
            row_indices = df.index.tolist()
            if row_indices:
                row_to_edit = st.selectbox(
                    "Select Row Index to Update",
                    row_indices,
                    key=f"edit_index_{tab}"
                )
                if st.button("Update Selected Row Status to: Completed", key=f"admin_update_{tab}"):
                    df.at[row_to_edit, "Status"] = "Completed"
                    df.at[row_to_edit, "Updated On"] = get_now()
                    save_df(tab, year_selected, df)
                    st.success("Status updated by Admin!")


# -------------------- TABS -------------------- #
tabs = st.tabs([
    "\U0001F4C4 Journal Publications",
    "\U0001F4C1 Research Projects",
    "\U0001F4BC Consultancy Projects",
    "\U0001F9E0 Patents",
    "\U0001F680 Project Ideas",
    "\U0001F4E2 Conference",
    "\U0001F4D6 Book / Book Chapter",
    "\U0001F4CA Department Dashboard",
])

with tabs[0]:
    create_form("Journal Publications")
with tabs[1]:
    create_form("Research Projects")
with tabs[2]:
    create_form("Consultancy Projects")
with tabs[3]:
    create_form("Patents")
with tabs[4]:
    create_form("Project Ideas")
with tabs[5]:
    create_form("Conference")
with tabs[6]:
    create_form("Book / Book Chapter")
with tabs[7]:
    st.subheader("\U0001F4CA Department Dashboard Overview")

    all_frames = []
    for tab_name in status_dict:
        for year in academic_years:
            tmp = load_df(tab_name, year)
            if not tmp.empty:
                tmp = tmp.copy()
                tmp["Type"] = tab_name
                tmp["Academic Year"] = year
                all_frames.append(tmp)

    if all_frames:
        combined = pd.concat(all_frames, ignore_index=True)
        st.dataframe(combined, use_container_width=True)

        chart = alt.Chart(combined).mark_bar().encode(
            x=alt.X("Faculty:N", sort="-y"),
            y="count()",
            color="Type:N",
            tooltip=["Faculty", "Type", "count()"]
        ).properties(width=900, height=420)
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("No data available yet for Department Dashboard.")

