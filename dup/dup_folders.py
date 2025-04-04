import os
import re
import pandas as pd
import streamlit as st
import logging
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to find duplicate folders based on name pattern
def find_duplicate_folders(folder_path):
    # Updated regex to match patterns like '(copy 1)', '(copy 2)', etc.
    folder_pattern = re.compile(r"^(.*?)( \(\d+\)| \(\w+ \d+\))?$")
    #folder_pattern = re.compile(r"^(.*?)( \(\d+\)| \(\w+ \d+\))*(\.[^.]+)?$")

    
    potential_duplicates = defaultdict(list)

    # Walk through directories in the specified folder
    for root, dirs, _ in os.walk(folder_path, topdown=True):
        for dir_name in dirs:
            match = folder_pattern.match(dir_name)
            if match:
                base_name = match.group(1)
                folder_key = (root, base_name)
                potential_duplicates[folder_key].append(dir_name)

    result = []
    # For each group with more than one folder, consider them as duplicates
    for (root, base_name), group in potential_duplicates.items():
        if len(group) > 1:
            group.sort()  # Sort to maintain a consistent order
            main_folder = group[0]
            for dup in group[1:]:
                result.append((os.path.join(root, main_folder), os.path.join(root, dup)))

    return result

# Function to remove a folder with dual redundant method
def remove_folder(folder_path):
    try:
        os.rmdir(folder_path)
        logging.info(f"Removed folder using os.rmdir(): {folder_path}")
    except Exception as e:
        logging.warning(f"os.rmdir() failed: {e}. Trying os.system('rm -rf')...")
        try:
            os.system(f'rm -rf "{folder_path}"')
            logging.info(f"Removed folder using os.system('rm -rf'): {folder_path}")
        except Exception as ex:
            logging.error(f"Failed to remove folder {folder_path}: {ex}")
            raise ex

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
            [data-testid="stTable"] td:nth-child(3) { /* Right-align duplicate folder name column */
                text-align: right !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("Duplicate Folder Finder in Same Parent Directory")

    folder_path = st.text_input("Enter the folder path:", "")

    # Use session state to store duplicate groups
    if 'duplicate_groups' not in st.session_state:
        st.session_state.duplicate_groups = []

    if folder_path and os.path.isdir(folder_path):
        logging.info(f"Scanning folder: {folder_path}")

        st.session_state.duplicate_groups = find_duplicate_folders(folder_path)

        if st.session_state.duplicate_groups:
            # Prepare data for the grid:
            # Each row represents one duplicate folder and includes the main folder name from its group.
            data = []
            main_folders = {}

            for main_folder, dup_folder in st.session_state.duplicate_groups:
                if main_folder not in main_folders:
                    main_folders[main_folder] = []
                main_folders[main_folder].append(dup_folder)

            for main_folder, duplicates in main_folders.items():
                data.append({
                    "Select": False,
                    "Main Folder Name": os.path.basename(main_folder),
                    "Duplicate Folder Name": "",
                    "Folder Path": main_folder
                })
                for dup_folder in duplicates:
                    data.append({
                        "Select": True,  # Auto-select duplicate folders
                        "Main Folder Name": "",
                        "Duplicate Folder Name": os.path.basename(dup_folder),
                        "Folder Path": dup_folder
                    })

            df = pd.DataFrame(data)

            # Display interactive table with checkbox selection
            edited_df = st.data_editor(
                df,
                column_config={"Select": st.column_config.CheckboxColumn()},
                key="folder_table"
            )

            # Compute the total number of duplicate folder groups (unique main folders)
            total_groups = len(main_folders)

            # Get selected folders from the grid
            selected_folders = edited_df[edited_df["Select"] == True]["Folder Path"].tolist()

            st.markdown(f"**Total Duplicate Folder Groups:** {total_groups}")
            st.markdown(f"**Total Selected Folders for Deletion:** {len(selected_folders)}")

            if selected_folders:
                st.warning(f"{len(selected_folders)} folders selected for deletion!")
                if st.button("Delete Selected Folders"):
                    for folder in selected_folders:
                        logging.info(f"Attempting to delete: {folder}")
                        try:
                            remove_folder(folder)
                            st.success(f"Deleted: {folder}")
                        except Exception as e:
                            logging.error(f"Error deleting {folder}: {e}")
                            st.error(f"Error deleting {folder}: {e}")
                    # Re-evaluate duplicates after deletion
                    st.session_state.duplicate_groups = find_duplicate_folders(folder_path)
            else:
                st.info("Select folders to delete.")
        else:
            st.success("No duplicate folders found.")
    else:
        st.warning("Please enter a valid directory path.")

# Run the Streamlit app
if __name__ == "__main__":
    main()
