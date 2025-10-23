import os
import streamlit as st
import re

# Folder with your txt files (inside your repo)
folder_path = "documents"

# Check if folder exists
if not os.path.exists(folder_path):
    st.error(f"Error: Folder not found at {folder_path}")
    st.stop()

# CSS styling
st.markdown(
    """
    <style>
    .centered-text { text-align: center; }
    .search-result {
        border: 2px solid #007BFF;  /* Blue border */
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        background-color: #f9f9f9;
        text-align: left;
        font-family: Arial, sans-serif;
        word-wrap: break-word;
    }
    mark { background-color: #FFFF00; color: black; }

    /* Style Streamlit input box */
    div.stTextInput > label > div {
        color: #007BFF;
        font-weight: bold;
    }
    div.stTextInput > div > input {
        border: 2px solid #007BFF;
        border-radius: 5px;
        padding: 8px;
        width: 100%;
        font-size: 16px;
    }
    </style>
    """, unsafe_allow_html=True
)

# Header
st.markdown('<h1 class="centered-text">VA Disability Search</h1>', unsafe_allow_html=True)

# Search input with magnifying glass emoji
search_input = st.text_input("🔍 Enter the condition you are looking for")

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
            # Show "Found X files" in blue-framed box
            st.markdown(f"""
                <div class="search-result">
                    <strong>Found {len(matching_files)} files:</strong>
                </div>
            """, unsafe_allow_html=True)

            for idx, file_name in enumerate(matching_files, 1):
                file_path = os.path.join(folder_path, file_name)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Highlight first 1000 characters
                snippet = re.sub(
                    re.escape(search_phrase),
                    lambda m: f"<mark>{m.group(0)}</mark>",
                    content[:1000],
                    flags=re.IGNORECASE
                )

                html_content = f"""
                <div class="search-result">
                    <h4>{idx}: {file_name}</h4>
                    <p>{snippet}</p>
                </div>
                """
                st.markdown(html_content, unsafe_allow_html=True)

                # Button to show full content
                if st.button(f"Show full document: {file_name}", key=file_name):
                    full_content = re.sub(
                        re.escape(search_phrase),
                        lambda m: f"<mark>{m.group(0)}</mark>",
                        content,
                        flags=re.IGNORECASE
                    )
                    st.markdown(f'<div class="search-result">{full_content}</div>', unsafe_allow_html=True)
