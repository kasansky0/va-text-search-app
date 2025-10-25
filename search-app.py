import os
import re
import random
import streamlit as st
from datetime import datetime

# -----------------------------
# Streamlit Config
# -----------------------------
st.set_page_config(
    page_title="BVA Finder Pro",
    page_icon="🔍",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# -----------------------------
# Session ID
# -----------------------------
if "client_id" not in st.session_state:
    st.session_state.client_id = f"{random.randint(1000000000,9999999999)}.{random.randint(1000000000,9999999999)}"

# -----------------------------
# Google Sheet Logging
# -----------------------------
def log_to_sheet(session_id, search_term, document_viewed):
    try:
        if "gcp_service_account" not in st.secrets:
            return
        import gspread
        from google.oauth2.service_account import Credentials
        SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
        SERVICE_ACCOUNT_INFO = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
        gs_client = gspread.authorize(creds)
        SHEET_KEY = "1siHLnL8t1OZMvbrALNrgMp9w54IhtlSTgeGqMXSt7JA"
        sheet = gs_client.open_by_key(SHEET_KEY).sheet1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([timestamp, search_term, session_id, document_viewed])
    except:
        pass

# -----------------------------
# Modern Blue-Grey Theme
# -----------------------------
st.markdown("""<style>
html, body, [class*="stAppViewContainer"], [class*="stApp"], 
[data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    background-color: #f6f7f9 !important;
    color: #1c1e21 !important;
}
[data-testid="stHeader"], [data-testid="stToolbar"] {
    background-color: #ffffff !important;
    color: #1c1e21 !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
}
.centered-text {
    text-align: center;
    color: #1877f2 !important;
    font-weight: bold;
    margin-bottom: 8px;
}
.sub-title {
    text-align: center;
    color: #555555;
    font-size: 16px;
    margin-bottom: 25px;
}
.search-result {
    border: 1px solid #d0d7de;
    border-radius: 10px;
    padding: 18px;
    margin-bottom: 30px;
    background-color: #ffffff;
    text-align: left;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}
.search-result:nth-child(even) {
    background-color: #f0f4f9;
}
mark {
    background-color: #ffe58f;
    color: #000000;
    padding: 0 3px;
    border-radius: 3px;
}
div.stTextInput > label > div {
    color: #1877f2 !important;
    font-weight: bold;
    font-size: 16px;
}
div.stTextInput input {
    border: 2px solid #1877f2 !important;
    border-radius: 6px !important;
    padding: 10px !important;
    width: 100% !important;
    font-size: 16px !important;
    color: #000000 !important;
    background-color: #ffffff !important;
    caret-color: #1877f2 !important;
}
div.stTextInput input::placeholder {
    color: #888888 !important;
}
div.stButton > button {
    background-color: #1877f2 !important;
    color: white !important;
    border-radius: 6px !important;
    border: none !important;
    padding: 8px 18px !important;
    font-size: 15px !important;
    cursor: pointer !important;
}
div.stButton > button:hover {
    background-color: #145dbf !important;
}
.footer-text {
    font-size: 11px;
    color: #555555;
    text-align: center;
    margin-top: 40px;
    line-height: 1.5;
}
</style>""", unsafe_allow_html=True)

# -----------------------------
# Header
# -----------------------------
st.markdown('<h1 class="centered-text">BVA Finder Pro</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Quickly search and explore BVA documents for conditions and claims information.</p>', unsafe_allow_html=True)

# -----------------------------
# Folders with text files
# -----------------------------
folders = [f"document{i}" for i in range(1, 8)]
existing_folders = [f for f in folders if os.path.exists(f)]
if not existing_folders:
    st.error("No folders found! Make sure the folders document1..document7 exist.")
    st.stop()

# -----------------------------
# Cache all files in memory
# -----------------------------
@st.cache_data(show_spinner=False)
def load_all_documents(folders):
    documents = []
    for folder in folders:
        for filename in os.listdir(folder):
            if filename.endswith(".txt"):
                file_path = os.path.join(folder, filename)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    documents.append((filename, content))
                except Exception:
                    pass
    return documents

all_documents = load_all_documents(existing_folders)

# -----------------------------
# Search Input
# -----------------------------
search_input = st.text_input(
    "🔍 Enter the condition you are looking for",
    value="",
    placeholder="Knee, Sleep apnea, Migraines"
)

# -----------------------------
# Search Logic
# -----------------------------
if search_input:
    search_phrase = search_input.strip()
    if not search_phrase:
        st.warning("Please enter a valid phrase to search.")
    else:
        log_to_sheet(st.session_state.client_id, search_phrase, "")
        words = search_phrase.split()
        phrases_to_try = [" ".join(words[:len(words)-i]) for i in range(len(words)) if " ".join(words[:len(words)-i])]

        matching_files = []
        used_phrase = None

        for phrase in phrases_to_try:
            temp_matches = []
            pattern = re.compile(re.escape(phrase), re.IGNORECASE)
            for file_name, content in all_documents:
                matches = pattern.findall(content)
                if matches:
                    temp_matches.append((file_name, len(matches), content))
            if temp_matches:
                matching_files = temp_matches
                used_phrase = phrase
                break

        if not matching_files:
            st.warning("No files found with the given or related phrase.")
        else:
            if used_phrase != search_phrase:
                st.info(f'No exact matches found for "{search_phrase}". Showing results for "{used_phrase}".')

            st.markdown(
                f'<div class="search-result"><strong>Found {len(matching_files)} file(s)</strong></div>',
                unsafe_allow_html=True
            )

            for idx, (file_name, match_count, content) in enumerate(matching_files, 1):
                clean_name = file_name.replace(".txt", "")
                match = re.search(re.escape(used_phrase), content, re.IGNORECASE)
                snippet_text = ""
                if match:
                    start = max(0, match.start() - 300)
                    end = min(len(content), match.end() + 700)
                    snippet_text = content[start:end]

                snippet_text = snippet_text[:1000]
                snippet = re.sub(
                    re.escape(used_phrase),
                    lambda m: f"<mark>{m.group(0)}</mark>",
                    snippet_text,
                    flags=re.IGNORECASE
                )

                header_text = f'<b>#{idx} {clean_name}</b> — <mark>{match_count} match{"es" if match_count != 1 else ""}</mark><br>'
                header_text += '<small style="color:#555;">Click “Show Full Document” to read the entire file.</small>'

                snippet_html = f"{header_text}<br><br>{snippet}" if snippet else f"{header_text}<br><i>No snippet available.</i>"
                st.markdown(f'<div class="search-result">{snippet_html}</div>', unsafe_allow_html=True)

                if st.button(f"Show Full Document: #{idx} {clean_name}", key=f"{file_name}"):
                    log_to_sheet(st.session_state.client_id, used_phrase, clean_name)
                    full_content = re.sub(
                        re.escape(used_phrase),
                        lambda m: f"<mark>{m.group(0)}</mark>",
                        content,
                        flags=re.IGNORECASE
                    )
                    st.markdown(f'<div class="search-result">{full_content}</div>', unsafe_allow_html=True)

# -----------------------------
# Footer
# -----------------------------
st.markdown("""
<div class="footer-text">
Disclaimer: This site indexes and displays excerpts from publicly available U.S. government documents (VA.gov).<br>
No personal or private information is uploaded or stored.<br>
This tool is for informational use only and not a substitute for legal or medical advice.
</div>
""", unsafe_allow_html=True)
