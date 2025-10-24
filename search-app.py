import os
import re
import random
import streamlit as st
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# -----------------------------
# Force Light Mode in App Config
# -----------------------------
st.set_page_config(
    page_title="VA Condition Search",
    page_icon="🔍",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# -----------------------------
# Session ID for tracking
# -----------------------------
if "client_id" not in st.session_state:
    st.session_state.client_id = f"{random.randint(1000000000,9999999999)}.{random.randint(1000000000,9999999999)}"

# -----------------------------
# Google Sheets Setup
# -----------------------------
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

SERVICE_ACCOUNT_INFO = {
  "type": "service_account",
  "project_id": "vasearchlogger",
  "private_key_id": "af33a5e53b5393a04a168eadaed33b6aee186a67",
  "private_key": "-----BEGIN PRIVATE KEY-----\\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDER0T+bNukJfU3\\nTGrvsMukLcBoy0yy1t1v+H+2ON+HQYWlf07W875eyT+EhlOMpot2BU0kRQ8xi7zG\\n5ljGj4RE0jKAvXA4SIq30hu+a8EqhDdFHr4lBjgszYpyJIkAoz4LjAA5vNjVQSv+\\n7ujcvGF0AuHIcoNX8JLmnD0oazwuXADUWY8zIKg2ocEpQAuAtPb0tNn1Zf90XCvS\\nzLI3rn2/jGTu9T4RUAJMgi+YRpKz6dM9Irr0n2vfxths8rK06BIEzbc4Kru1lXBl\\nZKFTsmpQ2iHGFpIuFjvZrf8TezijuK1ia+rKNaPb878SKMNPFaPQJXChZpbFLPzt\\nRcuE7ZkvAgMBAAECggEAAMCeLDBMYOOlNrjwhGXBi8ufVUiOr89xYOrRKf2D0rNS\\ngJJJwfOETKqnnkDH/xSCMnwZgTHX46QPrEN0clJ6v+X4Jwj5sV3N0tqJ8inUAmkT\\nTxD3QEqPAk6p9fCUX6Pw0oFtbWq1sqw9CeeejYbKfcOjCAEbZCZNoTRSlQHSQzBo\\nGgLSZoykz6FBF1/Q99IAVrK9YEHWl1ele2yhOKDlNo3KtZAnjZiwyixBs+FkX6gV\\nTxoqNHZ8yTTXfqVEHAGOAw7NZIiIe+Ib5AhAyCAXB6wJltpsn+lBhVc9TduCDvde\\n2nNzEIK5MejZwmKgvlEPxk1GizkpJ6bsIuSpysFBqQKBgQDnEv+Ds/a0Z6w+73FA\\ncFwLz7RL4VFAA9iJuclJ5pXlkeXDxlMfSe7KuGb29UrX5g/5tbfCI7JB6aWWlCMQ\\nJomuFG5lYyBvyhh7A0SziK9nn6oy1IwKr4wybQmunxCv08ZMBiNR+B+5Zaet1cHQ\\nfD9S5MwdDoWwrI9u07Y2B5eyUwKBgQDZc2bjmFN7BYicVGEC/nzfReF1bOYhC4JX\\njlEckJ9P/Y2ODekyhusfPsgKpHlGLBWjO788Ki0F7IUSZLCQNE4RdiqCCLvAAtat\\nEzLcc75LyLSjA9Xukkn34LMxSQIZPhQKV/uMHZcGqolX9RAFBXvvHDnYTWdjMCyD\\nPvMqCUnaNQKBgFEaD+hPz7T99iyYqa0uQoA6xFMln/jR4LxmIsn3ToEmtfgCscX3\\nkwI/upPPABfKvaytJPPUx4nu0ZmKIMxYWlZpAV5AbnAOBI2YVhKVVMsP9RKmGwjd\\nGF3Se2V4msi7kYu5U8g/SBMwJKwUrFPaZ/dWKnXAVRfvWOBTGk7YV1vVAoGAYDA6\\nLScullamTXDN0QM9vY4t40GesrNintRncNlQf5PLUDE7HIyt6Q5ecsa6lp3dnG1L\\ndJO7gslTPAWqTL+2YOcCeq7eTltzFvBNKVNRtDg+H3YM5hF0AuA0o/KFqSDawJCW\\nxy43pk09n9jZkz8PyX+U3ueueiPPLOdlrQyazJkCgYBRW3u+SNBswQ/3K9/GrO1f\\nUSD180J029IpA0IrnVTSQbCHK+9oV7sjapXdJb+st95oMpxtM7DBqq0dru3ypLR3\\nyYqH6lhb+3fOaRMuLDdvbP9hX/W0MNTs7TUwQk4/a8m0wnO6SmlIgiKF5j6rtBAX\\nPpGwSqXMCp/kCpGyhQ+rSQ==\\n-----END PRIVATE KEY-----\\n",
  "client_email": "streamlit-logger@vasearchlogger.iam.gserviceaccount.com",
  "client_id": "110380397944810111696",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/streamlit-logger%40vasearchlogger.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

# Fix key formatting for deployed environment
SERVICE_ACCOUNT_INFO["private_key"] = SERVICE_ACCOUNT_INFO["private_key"].replace("\\n", "\n")

SHEET_KEY = "1Hhlezm78LIA4Dudt9fHlSTyoSmsOYKAk8_HXO5uUsLc"

# Initialize Google Sheets client
creds = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
gs_client = gspread.authorize(creds)
sheet = gs_client.open_by_key(SHEET_KEY).sheet1  # first worksheet

# -----------------------------
# Logging function with error handling
# -----------------------------
def log_to_sheet(session_id, search_term, document_viewed):
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([timestamp, session_id, search_term, document_viewed])
    except Exception as e:
        st.error(f"Logging to Google Sheets failed: {e}")

# -----------------------------
# CSS Styling
# -----------------------------
st.markdown("""
<style>
html, body, [class*="stAppViewContainer"], [class*="stApp"], 
[data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    background-color: #FFFFFF !important;
    color: #000000 !important;
}
[data-testid="stHeader"] {
    background-color: #FFFFFF !important;
    color: #000000 !important;
    box-shadow: none !important;
}
[data-testid="stToolbar"] {
    background-color: #FFFFFF !important;
    color: #000000 !important;
}
.centered-text {
    text-align: center;
    color: #000000 !important;
    font-weight: bold;
    margin-bottom: 20px;
}
.search-result-blue {
    border: 2px solid #007BFF;
    border-radius: 10px;
    padding: 15px;
    margin-bottom: 15px;
    background-color: #E6F0FF;
    text-align: left;
    color: #000000;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}
.search-result-green {
    border: 2px solid #28A745;
    border-radius: 10px;
    padding: 15px;
    margin-bottom: 15px;
    background-color: #E6FFE6;
    text-align: left;
    color: #000000;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}
mark {
    background-color: #FFFF00;
    color: #000000;
    padding: 0 2px;
    border-radius: 2px;
}
div.stTextInput > label > div {
    color: #007BFF !important;
    font-weight: bold;
    font-size: 16px;
}
div.stTextInput input {
    border: 2px solid #007BFF !important;
    border-radius: 5px !important;
    padding: 10px !important;
    width: 100% !important;
    font-size: 16px !important;
    color: #000000 !important;
    background-color: #FFFFFF !important;
    caret-color: #000000 !important;
}
div.stTextInput input::placeholder {
    color: #888888 !important;
    opacity: 1 !important;
}
div.stButton > button {
    background-color: #007BFF !important;
    color: white !important;
    border-radius: 5px !important;
    border: none !important;
    padding: 8px 16px !important;
    font-size: 14px !important;
    cursor: pointer !important;
    transition: background-color 0.2s !important;
}
div.stButton > button:hover {
    background-color: #0056b3 !important;
}
.footer-text {
    font-size: 10px;
    color: gray;
    text-align: center;
    margin-top: 30px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Header
# -----------------------------
st.markdown('<h1 class="centered-text">VA Condition Search</h1>', unsafe_allow_html=True)

# -----------------------------
# Folder containing text files
# -----------------------------
folder_path = "documents"
if not os.path.exists(folder_path):
    st.error(f"Error: Folder not found at {folder_path}")
    st.stop()

# -----------------------------
# Search Input
# -----------------------------
search_input = st.text_input(
    "🔍 Enter the condition you are looking for",
    value="",
    placeholder="Knee, Sleep apnea, Migraines"
)

# -----------------------------
# Search Logic + Google Sheets Logging
# -----------------------------
if search_input:
    search_phrase = search_input.strip()
    if not search_phrase:
        st.warning("Please enter a valid phrase to search.")
    else:
        log_to_sheet(st.session_state.client_id, search_phrase, "")  # log search only

        matching_files = []
        for filename in os.listdir(folder_path):
            if filename.endswith(".txt"):
                with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as f:
                    content = f.read()
                if search_phrase.lower() in content.lower():
                    matching_files.append(filename)

        if not matching_files:
            st.warning("No files found with the given phrase.")
        else:
            st.markdown(f'<div class="search-result-blue"><strong>Found {len(matching_files)} file(s):</strong></div>', unsafe_allow_html=True)

            for idx, file_name in enumerate(matching_files, 1):
                with open(os.path.join(folder_path, file_name), "r", encoding="utf-8") as f:
                    content = f.read()

                snippet = re.sub(
                    re.escape(search_phrase),
                    lambda m: f"<mark>{m.group(0)}</mark>",
                    content[:1000],
                    flags=re.IGNORECASE
                )

                box_class = "search-result-blue" if idx % 2 != 0 else "search-result-green"

                st.markdown(f'<div class="{box_class}"><h4>#{idx} {file_name}</h4><p>{snippet}</p></div>', unsafe_allow_html=True)

                if st.button(f"Show full document: #{idx} {file_name}", key=file_name):
                    log_to_sheet(st.session_state.client_id, search_phrase, file_name)  # log doc viewed
                    full_content = re.sub(
                        re.escape(search_phrase),
                        lambda m: f"<mark>{m.group(0)}</mark>",
                        content,
                        flags=re.IGNORECASE
                    )
                    st.markdown(f'<div class="{box_class}">{full_content}</div>', unsafe_allow_html=True)

# -----------------------------
# Footer
# -----------------------------
st.markdown("""
<div class="footer-text">
Disclaimer: This site indexes and displays excerpts from publicly available U.S. government documents (VA.gov).
No personal or private information is uploaded or stored. This tool is for informational use only and not a
substitute for legal or medical advice.
</div>
""", unsafe_allow_html=True)
