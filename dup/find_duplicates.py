import os
import hashlib
import re
import pandas as pd
import streamlit as st
import logging
from collections import defaultdict
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to remove __pycache__ folders
def remove_pycache_folders(folder_path):
    for root, dirs, _ in os.walk(folder_path, topdown=False):
        for dir_name in dirs:
            if dir_name == "__pycache__":
                dir_to_remove = os.path.join(root, dir_name)
                try:
                    #os.rmdir(dir_to_remove)
                    os.system(f"rm -rf {dir_to_remove}")
                    logging.info(f"Removed __pycache__ folder: {dir_to_remove}")
                except Exception as e:
                    logging.error(f"Error removing __pycache__ folder {dir_to_remove}: {e}")

# Function to get file size and modification time
def get_file_info(file_path):
    try:
        file_info = os.stat(file_path)
        return {
            "size": file_info.st_size,
            "modified": datetime.fromtimestamp(file_info.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        logging.error(f"Error getting file info for {file_path}: {e}")
        return {}

# Function to compute SHA256 hash
def get_file_hash(file_path):
    hash_sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):  # Read in chunks for large files
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except Exception as e:
        logging.error(f"Error calculating hash for {file_path}: {e}")
        return ""

# Function to find duplicate files based on selected criteria
def find_duplicates_in_folder(folder_path, use_name, use_size, use_date, use_hash):
    #file_pattern = re.compile(r"^(.*?)( \(\d+\))?(\.[^.]+)$")
    file_pattern = re.compile(r"^(.*?)(\s*\(\d+\)\s*)*(\.[^.]+)$")

    potential_duplicates = defaultdict(list)

    # Walk through files in directory (including subfolders)
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            if file_name.startswith("."):
                continue
            # Skip files with basename "Screenshot"
            if file_name.startswith("Screenshot"):
                continue
            match = file_pattern.match(file_name)
            if match:
                base_name, _, ext = match.groups()
                file_path = os.path.join(root, file_name)
                file_info = get_file_info(file_path)
                if file_info:
                    # Construct the key based on selected criteria
                    file_key = (root, base_name, ext)
                    if use_size:
                        file_key += (file_info["size"],)
                    if use_date:
                        file_key += (file_info["modified"],)

                    potential_duplicates[file_key].append(file_path)

    result = []
    # For each group with more than one file, confirm duplicates with hash if enabled
    for group in potential_duplicates.values():
        if len(group) > 1:
            if use_hash:
                # Calculate hash for each file in the group
                hash_map = {}
                for file_path in group:
                    file_hash = get_file_hash(file_path)
                    if file_hash:
                        if file_hash in hash_map:
                            hash_map[file_hash].append(file_path)
                        else:
                            hash_map[file_hash] = [file_path]

                # Only keep groups where all files have the same hash
                for hash_group in hash_map.values():
                    if len(hash_group) > 1:
                        hash_group.sort(key=lambda f: len(os.path.basename(f)))  # Shortest filename is main file
                        main_file = hash_group[0]
                        for dup in hash_group[1:]:
                            result.append((main_file, dup))
            else:
                # If not using hash, consider all files in the group as duplicates
                group.sort(key=lambda f: len(os.path.basename(f)))  # Shortest filename is main file
                main_file = group[0]
                for dup in group[1:]:
                    result.append((main_file, dup))

    return result

# Main Streamlit Application
def main():
    # Set wide layout with a fixed width of 1850px
    st.set_page_config(layout="wide")

    # Custom CSS to force grid width to 1850px
    st.markdown(
        """
        <style>
            [data-testid="stTable"] {
                max-width: 1850px !important;
                margin: auto;
            }
            [data-testid="stTable"] td:nth-child(3) { /* Right-align duplicate file name column */
                text-align: right !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("Duplicate File Finder in Same Folder")

    folder_path = st.text_input("Enter the folder path:", "")
    use_name = st.checkbox("Use Name", value=True)
    use_size = st.checkbox("Use Size", value=True)
    use_date = st.checkbox("Use Date", value=True)
    use_hash = st.checkbox("Use Hash", value=True)

    # Use session state to store duplicate groups
    if 'duplicate_groups' not in st.session_state:
        st.session_state.duplicate_groups = []

    if folder_path and os.path.isdir(folder_path):
        logging.info(f"Scanning folder: {folder_path}")

        # Remove __pycache__ folders before scanning for duplicates
        remove_pycache_folders(folder_path)

        # Ensure at least one criterion is selected
        if not (use_name or use_size or use_date or use_hash):
            st.error("Please select at least one criterion for duplicate detection.")
        else:
            st.session_state.duplicate_groups = find_duplicates_in_folder(folder_path, use_name, use_size, use_date, use_hash)

            if st.session_state.duplicate_groups:
                # Prepare data for the grid:
                # Each row represents one duplicate file and includes the main file name from its group.
                data = []
                main_files = {}

                for main_file, dup_file in st.session_state.duplicate_groups:
                    if main_file not in main_files:
                        main_files[main_file] = []
                    main_files[main_file].append(dup_file)

                for main_file, duplicates in main_files.items():
                    main_info = get_file_info(main_file)
                    relative_main_path = main_file.replace(folder_path, "")
                    data.append({
                        "Select": False,
                        "Main File Name": os.path.basename(main_file),
                        "Duplicate File Name": "",
                        "File Path": relative_main_path,
                        "Size (bytes)": main_info["size"],
                        "Modified Date": main_info["modified"]
                    })
                    for dup_file in duplicates:
                        dup_info = get_file_info(dup_file)
                        relative_dup_path = dup_file.replace(folder_path, "")

                        data.append({
                            "Select": True,  # Auto-select duplicate files
                            "Main File Name": "",
                            "Duplicate File Name": os.path.basename(dup_file),
                            "File Path": relative_dup_path,
                            "Size (bytes)": dup_info["size"],
                            "Modified Date": dup_info["modified"]
                        })

                df = pd.DataFrame(data)

                # Display interactive table with checkbox selection
                edited_df = st.data_editor(
                    df,
                    column_config={"Select": st.column_config.CheckboxColumn()},
                    key="file_table"
                )

                # Compute the total number of duplicate file groups (unique main files)
                total_groups = len(main_files)

                # Get selected files from the grid
                selected_files = edited_df[edited_df["Select"] == True]["File Path"].tolist()

                st.markdown(f"**Total Duplicate File Groups:** {total_groups}")
                st.markdown(f"**Total Selected Files for Deletion:** {len(selected_files)}")

                if selected_files:
                    st.warning(f"{len(selected_files)} files selected for deletion!")
                    if st.button("Delete Selected Files"):
                        for file in selected_files:
                            full_path = os.path.join(folder_path, file.lstrip(os.sep))
                            logging.info(f"Attempting to delete: {full_path}")
                            try:
                                os.remove(full_path)
                                logging.info(f"Deleted: {file}")
                                st.success(f"Deleted: {file}")
                            except Exception as e:
                                logging.error(f"Error deleting {file}: {e}")
                                st.error(f"Error deleting {file}: {e}")
                        # Re-evaluate duplicates after deletion
                        st.session_state.duplicate_groups = find_duplicates_in_folder(folder_path, use_name, use_size, use_date, use_hash)
                else:
                    st.info("Select files to delete.")
            else:
                st.success("No duplicate files found.")
    else:
        st.warning("Please enter a valid directory path.")

# Run the Streamlit app
if __name__ == "__main__":
    main()
