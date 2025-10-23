import os

# Folder with your txt files
folder_path = "documents"

# Check if folder exists
if not os.path.exists(folder_path):
    print(f"Error: Folder not found at {folder_path}")
    exit(1)

def search_and_browse():
    while True:
        # Ask user for keywords to search
        search_input = input("\nEnter words to search for (comma or space separated, or '0' to exit): ")
        if search_input.strip() == "0":
            print("Exiting program...")
            break

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
            print("No files found with the given keywords.")
            continue

        while True:
            # Print all matching files in one row
            print(f"\nFound {len(matching_files)} files:")
            print(", ".join([f"{i + 1}:{file}" for i, file in enumerate(matching_files)]))

            choice = input("\nEnter the file number to open (or '0' to search new words): ")
            if choice.isdigit():
                choice = int(choice)
                if choice == 0:
                    break  # Go back to search new words
                elif 1 <= choice <= len(matching_files):
                    file_to_open = os.path.join(folder_path, matching_files[choice - 1])

                    # Print 3 lines above the file
                    print("\n" + "=" * 50)
                    print("=" * 50)
                    print("=" * 50)
                    print(f"FILE {choice}: {matching_files[choice - 1]}")
                    print("=" * 50)
                    print("=" * 50)
                    print("=" * 50 + "\n")

                    with open(file_to_open, "r", encoding="utf-8") as f:
                        content = f.read()
                        # Show only first 1000 characters initially
                        print(content[:1000])

                    # Ask user if they want to see the full document
                    see_all = input("\nType 'all' to see the whole document, or press Enter to continue to file list: ").strip().lower()
                    if see_all == 'all':
                        print("\n" + content + "\n")

                    # Print 3 lines below the file
                    print("\n" + "=" * 50)
                    print("=" * 50)
                    print("=" * 50)
                    print(f"END OF FILE {choice}")
                    print("=" * 50)
                    print("=" * 50)
                    print("=" * 50 + "\n")
                else:
                    print("Invalid file number.")
            else:
                print("Please enter a valid number.")

# Run the search and browse function
search_and_browse()
