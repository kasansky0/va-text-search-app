import os
import streamlit as st
import re

# Folder with your txt files (inside your repo)
folder_path = "documents"

# Check if folder exists
if not os.path.exists(folder_path):
    st.error(f"Error: Folder not found at {folder_path}")
    st.stop()

st.title("VA Disability Search App")
st.write("Search through the documents for specific health condition or phrase.")

# Text input for phrases
search_input = st.text_input("Enter condition/body part or exact phrase to search for")

if search_input:
    search_phrase = search_input.strip()
    if not search_phrase:
        st.warning("Please enter a valid phrase to search.")
    else:
        # Find matching files
        matching_files = []
        for filename in os.listdir(folder_path):
            if filename.endswith(".txt"):
                file_path = os.path.join(folder_path, filename)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                # Case-insensitive exact phrase search
                if search_phrase.lower() in content.lower():
                    matching_files.append(filename)

        # Show results
        if not matching_files:
            st.warning("No files found with the given phrase.")
        else:
            st.success(f"Found {len(matching_files)} files:")

            for idx, file_name in enumerate(matching_files, 1):
                file_path = os.path.join(folder_path, file_name)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                st.markdown(f"### {idx}: {file_name}")

                # Highlight search phrase in the first 1000 chars
                snippet = content[:1000]
                snippet = re.sub(f"({re.escape(search_phrase)})", r'<mark>\1</mark>', snippet, flags=re.IGNORECASE)
                st.markdown(snippet, unsafe_allow_html=True)

                # Button to show full content with highlighted phrase
                if st.button(f"Show full document: {file_name}", key=file_name):
                    full_content = re.sub(f"({re.escape(search_phrase)})", r'<mark>\1</mark>', content, flags=re.IGNORECASE)
                    st.markdown(full_content, unsafe_allow_html=True)
