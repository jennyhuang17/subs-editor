import os
import re

def write_mp3_filenames_to_txt(folder_path, output_file):
    with open(output_file, 'w') as txt_file:
        # Get all sub-folders in the given folder, sorted alphabetically
        sub_folders = sorted([f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))])

        # Process each sub-folder
        for sub_folder_name in sub_folders:
            sub_folder_path = os.path.join(folder_path, sub_folder_name)
            
            # Write the sub-folder name
            txt_file.write(f"{sub_folder_name}\n")
                
            # Get all .mp3 files in the sub-folder, sorted by name
            mp3_files = sorted([f for f in os.listdir(sub_folder_path) if f.endswith('.mp3')])

            # Write each mp3 file name without the .mp3 suffix and without the leading number prefix
            for mp3_file in mp3_files:
                # Remove the leading numbers and space (e.g., "01-170 ")
                cleaned_name = re.sub(r'^\d+[-\d]*\s', '', mp3_file[:-4])  # Remove numbers and '-'
                txt_file.write(f"  - {cleaned_name}\n")  # Write cleaned file name

def extract_files_with_strings(folder_path, target_strings):
    """
    Extracts mp3 file names that contain any of the target strings under each sub-folder.
    
    Args:
        folder_path (str): Path to the main folder containing sub-folders.
        target_strings (list): List of strings to match within the file names.
        
    Returns:
        dict: A dictionary with sub-folder names as keys and list of matched file names as values.
    """
    matched_files = {}

    # Get all sub-folders in the given folder, sorted alphabetically
    sub_folders = sorted([f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))])

    # Process each sub-folder
    for sub_folder_name in sub_folders:
        sub_folder_path = os.path.join(folder_path, sub_folder_name)

        # Get all .mp3 files in the sub-folder, sorted by name
        mp3_files = sorted([f for f in os.listdir(sub_folder_path) if f.endswith('.mp3')])

        # Filter files based on target strings
        matching_files = []
        for mp3_file in mp3_files:
            cleaned_name = re.sub(r'^\d+[-\d]*\s', '', mp3_file[:-4])  # Remove numbers and '-'
            if any(target_string in cleaned_name for target_string in target_strings):
                matching_files.append(cleaned_name)

        if matching_files:
            matched_files[sub_folder_name] = matching_files

    return matched_files

def write_matched_files_to_txt(matched_files, target_string, output_folder):
    """
    Writes the matched files to a text file with a specific filename format.

    Args:
        matched_files (dict): A dictionary with sub-folder names as keys and list of matched file names as values.
        target_string (str): The target string used to filter the filenames.
        output_folder (str): The folder where the output file will be saved.
    """
    output_file = os.path.join(output_folder, f"黑2_{target_string}.txt")
    
    with open(output_file, 'w') as txt_file:
        for sub_folder, files in matched_files.items():
            txt_file.write(f"{sub_folder}\n")
            for file in files:
                txt_file.write(f"  - {file}\n")

# Usage examples
folder_path = "乐嫣降噪音频包（共777条）"  # Replace with the path to your main folder
output_folder = "乐嫣降噪音频包（共777条）"   # Replace with the folder where the output files will be saved
write_mp3_filenames_to_txt(folder_path, os.path.join(output_folder, "乐嫣.txt"))

# List of target strings to search for
target_strings = ["凌妙妙：", "慕声：", "慕瑶：", "柳拂衣："]  # Replace with the target strings you are looking for

# Process each target string separately
for target_string in target_strings:
    matched_files = extract_files_with_strings(folder_path, [target_string])
    write_matched_files_to_txt(matched_files, target_string, output_folder)