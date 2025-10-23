import os
import streamlit as st

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
        st.success(f"Found {len(matching_files)} files:")
        files_row = ", ".join([f"{i + 1}:{file}" for i, file in enumerate(matching_files)])
        st.write(files_row)

        # Select a file to open
        file_choice = st.number_input(
            "Enter the file number to open (0 to search new words):",
            min_value=0,
            max_value=len(matching_files),
            step=1
        )

        if file_choice != 0:
            file_to_open = os.path.join(folder_path, matching_files[file_choice - 1])

            st.markdown("### " + "="*50)
            st.markdown("### " + "="*50)
            st.markdown("### " + "="*50)
            st.markdown(f"**FILE {file_choice}: {matching_files[file_choice - 1]}**")
            st.markdown("### " + "="*50)
            st.markdown("### " + "="*50)
            st.markdown("### " + "="*50)

            with open(file_to_open, "r", encoding="utf-8") as f:
                content = f.read()

            # Show first 1000 characters
            st.text(content[:1000])

            # Button to show full document
            if st.button("Show full document"):
                st.text(content)

            st.markdown("### " + "="*50)
            st.markdown("### " + "="*50)
            st.markdown("### " + "="*50)
            st.markdown(f"**END OF FILE {file_choice}**")
            st.markdown("### " + "="*50)
            st.markdown("### " + "="*50)
            st.markdown("### " + "="*50)
