import os
import streamlit as st
import re

# Folder with your txt files (inside your repo)
folder_path = "documents"

# Check if folder exists
if not os.path.exists(folder_path):
    st.error(f"Error: Folder not found at {folder_path}")
    st.stop()

st.title("VA Text Search App")
st.write("Search through your documents for specific keywords.")

# Text input for keywords
search_input = st.text_input("Enter words to search for (comma or space separated)")

if search_input:
    # Prepare search keywords
    search_keywords = [kw.strip() for kw in search_input.replace(",", " ").split()]
    search_keywords_lower = [kw.lower() for kw in search_keywords]

    # Find matching files
    matching_files = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            # Case-insensitive check
            if any(kw.lower() in content.lower() for kw in search_keywords):
                matching_files.append(filename)

    # Show results
    if not matching_files:
        st.warning("No files found with the given keywords.")
    else:
        st.success(f"Found {len(matching_files)} files:")

        # Show all matching files
        for idx, file_name in enumerate(matching_files, 1):
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            st.markdown(f"### {idx}: {file_name}")

            # Highlight search keywords in the first 1000 chars
            snippet = content[:1000]
            for kw in search_keywords:
                snippet = re.sub(f"({re.escape(kw)})", r'<mark>\1</mark>', snippet, flags=re.IGNORECASE)

            st.markdown(snippet, unsafe_allow_html=True)

            # Button to show full content with highlighted keywords
            if st.button(f"Show full document: {file_name}", key=file_name):
                full_content = content
                for kw in search_keywords:
                    full_content = re.sub(f"({re.escape(kw)})", r'<mark>\1</mark>', full_content, flags=re.IGNORECASE)
                st.markdown(full_content, unsafe_allow_html=True)
