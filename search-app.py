import os
import re
import random
import requests
import streamlit as st

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
# Google Analytics Configuration
# -----------------------------
GA_MEASUREMENT_ID = "G-4LPXYWL47V"          # Your GA4 Measurement ID
GA_API_SECRET = "9-w9pPt_RFqr2ZXUho8Tpw"   # Your GA4 Measurement Protocol API Secret

# Generate GA4-compatible client ID per session
if "client_id" not in st.session_state:
    st.session_state.client_id = f"{random.randint(1000000000,9999999999)}.{random.randint(1000000000,9999999999)}"

def send_ga_event(event_name, event_params=None):
    """Send server-side event to Google Analytics 4 without showing banners"""
    payload = {
        "client_id": st.session_state.client_id,
        "events": [
            {
                "name": event_name,
                "params": {
                    "page_location": "https://your-streamlit-app-name.streamlit.app",
                    "page_title": "VA Condition Search",
                    **(event_params or {})
                }
            }
        ]
    }
    url = f"https://www.google-analytics.com/mp/collect?measurement_id={GA_MEASUREMENT_ID}&api_secret={GA_API_SECRET}"
    try:
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        if response.status_code != 204:
            # Only log to console if it fails
            print(f"GA event FAILED ({response.status_code}): {response.text}")
    except Exception as e:
        print(f"GA event exception: {e}")

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
# Search Logic + Analytics Events
# -----------------------------
if search_input:
    search_phrase = search_input.strip()
    if not search_phrase:
        st.warning("Please enter a valid phrase to search.")
    else:
        send_ga_event("search", {"event_category": "interaction", "event_label": search_phrase})

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
                    send_ga_event("view_document", {"event_category": "interaction", "event_label": file_name})
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
