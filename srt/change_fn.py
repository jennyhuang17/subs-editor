import os

def truncate_filenames(folder_path):
    try:
        # List all files in the folder
        files = os.listdir(folder_path)

        for file in files:
            # Split the filename and its extension
            file_name, file_extension = os.path.splitext(file)

            # Truncate the filename to the first 4 characters
            if len(file_name) > 4:
                new_file_name = file_name[:4] + file_extension

                # Generate full file paths
                old_file_path = os.path.join(folder_path, file)
                new_file_path = os.path.join(folder_path, new_file_name)

                # Rename the file
                os.rename(old_file_path, new_file_path)
                print(f'Renamed: "{file}" -> "{new_file_name}"')

        print("File renaming completed.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Specify the folder path (update this path as needed)
sub_folder_path = "乔菲"
truncate_filenames(sub_folder_path)