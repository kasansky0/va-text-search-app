import os
import re
import random
import streamlit as st
from datetime import datetime

# -----------------------------
# Streamlit App Config
# -----------------------------
st.set_page_config(
    page_title="VA Condition Search",
    page_icon="🔍",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# -----------------------------
# Session ID for tracking users
# -----------------------------
if "client_id" not in st.session_state:
    st.session_state.client_id = f"{random.randint(1000000000,9999999999)}.{random.randint(1000000000,9999999999)}"

# -----------------------------
# Logging Function (reads secrets at runtime)
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
# Search Logic + Logging
# -----------------------------
if search_input:
    search_phrase = search_input.strip()
    if not search_phrase:
        st.warning("Please enter a valid phrase to search.")
    else:
        log_to_sheet(st.session_state.client_id, search_phrase, "")

        matching_files = []
        for filename in os.listdir(folder_path):
            if filename.endswith(".txt"):
                with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as f:
                    content = f.read()
                matches = re.findall(re.escape(search_phrase), content, flags=re.IGNORECASE)
                if matches:
                    matching_files.append((filename, len(matches)))

        if not matching_files:
            st.warning("No files found with the given phrase.")
        else:
            st.markdown(
                f'<div class="search-result-blue"><strong>Found {len(matching_files)} file(s):</strong></div>',
                unsafe_allow_html=True
            )

            for idx, (file_name, match_count) in enumerate(matching_files, 1):
                clean_name = file_name.replace(".txt", "")
                with open(os.path.join(folder_path, file_name), "r", encoding="utf-8") as f:
                    content = f.read()

                # Create snippet around first match
                match = re.search(re.escape(search_phrase), content, re.IGNORECASE)
                if match:
                    start = max(0, match.start() - 300)
                    end = min(len(content), match.end() + 700)
                    snippet_text = content[start:end]
                else:
                    snippet_text = ""

                # Trim snippet to 1000 characters
                snippet_text = snippet_text[:1000]

                # Highlight matches
                snippet = re.sub(
                    re.escape(search_phrase),
                    lambda m: f"<mark>{m.group(0)}</mark>",
                    snippet_text,
                    flags=re.IGNORECASE
                )

                # Count matches in snippet
                matches_in_snippet = len(re.findall(re.escape(search_phrase), snippet_text, flags=re.IGNORECASE))

                # Header text: always show full document info
                header_text = f'<b><mark>#{idx} {clean_name} — {match_count} match{"es" if match_count != 1 else ""} found</mark></b><br>'
                if match_count > matches_in_snippet:
                    header_text += '<b><mark>Click "Show Full Document" to see all matches.</mark></b>'
                else:
                    header_text += '<b><mark>Click "Show Full Document" to read the full document.</mark></b>'

                snippet_html = f"{header_text}<br><br>{snippet}" if snippet else f"{header_text}<br><i>No snippet available.</i>"

                # Determine snippet box color
                box_class = "search-result-blue" if idx % 2 != 0 else "search-result-green"

                # Display snippet
                st.markdown(
                    f'<div class="{box_class}"><p>{snippet_html}</p></div>',
                    unsafe_allow_html=True
                )

                # Full document button
                if st.button(f"Show full document: #{idx} {clean_name}", key=file_name):
                    log_to_sheet(st.session_state.client_id, search_phrase, clean_name)
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
