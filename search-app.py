import os
import streamlit as st
import re

# -----------------------------
# Force Light Mode in App Config
# -----------------------------
st.set_page_config(
    page_title="VA Condition Search",
    page_icon="🔍",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Force Streamlit light theme
st.markdown(
    """
    <style>
    /* Override global dark theme */
    html, body, [class*="stAppViewContainer"], [class*="stApp"], [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }

    /* Hide dark mode top bar (header) */
    [data-testid="stHeader"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        box-shadow: none !important;
    }

    /* Force Streamlit toolbar (if any) to white */
    [data-testid="stToolbar"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }

    /* Centered Header */
    .centered-text {
        text-align: center;
        color: #000000 !important;
        font-weight: bold;
        margin-bottom: 20px;
    }

    /* Search result boxes */
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

    /* Highlight text */
    mark {
        background-color: #FFFF00;
        color: #000000;
        padding: 0 2px;
        border-radius: 2px;
    }

    /* Input label */
    div.stTextInput > label > div {
        color: #007BFF !important;
        font-weight: bold;
        font-size: 16px;
    }

    /* Search input box */
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

    /* Button */
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

    /* Footer */
    .footer-text {
        font-size: 10px;
        color: gray;
        text-align: center;
        margin-top: 30px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

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
search_input = st.text_input("🔍 Enter the condition you are looking for")

# -----------------------------
# Search Logic
# -----------------------------
if search_input:
    search_phrase = search_input.strip()
    if not search_phrase:
        st.warning("Please enter a valid phrase to search.")
    else:
        matching_files = []
        for filename in os.listdir(folder_path):
            if filename.endswith(".txt"):
                file_path = os.path.join(folder_path, filename)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                if search_phrase.lower() in content.lower():
                    matching_files.append(filename)

        if not matching_files:
            st.warning("No files found with the given phrase.")
        else:
            st.markdown(f"""
                <div class="search-result-blue">
                    <strong>Found {len(matching_files)} file(s):</strong>
                </div>
            """, unsafe_allow_html=True)

            for idx, file_name in enumerate(matching_files, 1):
                file_path = os.path.join(folder_path, file_name)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                snippet = re.sub(
                    re.escape(search_phrase),
                    lambda m: f"<mark>{m.group(0)}</mark>",
                    content[:1000],
                    flags=re.IGNORECASE
                )

                box_class = "search-result-blue" if idx % 2 != 0 else "search-result-green"

                html_content = f"""
                <div class="{box_class}">
                    <h4>{idx}: {file_name}</h4>
                    <p>{snippet}</p>
                </div>
                """
                st.markdown(html_content, unsafe_allow_html=True)

                if st.button(f"Show full document: {file_name}", key=file_name):
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
st.markdown(
    """
    <div class="footer-text">
    Disclaimer: This site indexes and displays excerpts from publicly available U.S. government documents (VA.gov).
    No personal or private information is uploaded or stored. This tool is for informational use only and not a
    substitute for legal or medical advice.
    </div>
    """,
    unsafe_allow_html=True
)
