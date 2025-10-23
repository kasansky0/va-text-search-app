import os
import streamlit as st
import random

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
    search_keywords = [kw.strip().lower() for kw in search_input.replace(",", " ").split()]

    # Find matching files
    matching_files = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().lower()
            if any(kw in content for kw in search_keywords):
                matching_files.append(filename)

    # Show results
    if not matching_files:
        st.warning("No files found with the given keywords.")
    else:
        st.success(f"Found {len(matching_files)} files. Showing 10 random files:")

        # Pick 10 random files (or all if less than 10)
        display_files = random.sample(matching_files, min(10, len(matching_files)))

        for idx, file_name in enumerate(display_files, 1):
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            st.markdown(f"### {idx}: {file_name}")
            st.text(content[:1000])  # show first 1000 characters

            # Button to show full content
            if st.button(f"Show full document: {file_name}", key=file_name):
                st.text(content)
