import pandas as pd
import numpy as np
import os
import eyed3

def generate_txt(input_csv):

    # Create three new lists
    new_txt_output, indexes, names = [list() for i in range(3)]

    # Iterate through csv rows in format [index, time, line, character, episode]
    for row in range(input_csv.shape[0]):

        indexes.append(input_csv[row][0]) 
        names.append(input_csv[row][3])
        line = str(input_csv[row][2])
        changed_name = f"◦ 【{input_csv[row][3]}】".replace("-", "")

        if row == 0:
            new_txt_output.extend([changed_name, line])
        else:
            # Calculate the difference between the current and previous indexes
            # If yes, check if the two lines are said by the same person
            row_diff = indexes[row] - indexes[row - 1]
            same_group = names[row] == names[row - 1] and row_diff == 1

            # Append a customized divider if this and previous rows are consistent
            # Else, start a new line
            if same_group:
                new_txt_output.append('，')
            else:
                new_txt_output.extend(['\n', changed_name])
            
            # Append the current line to the output
            new_txt_output.append(line)

    txt_output = ''.join(new_txt_output)
    return txt_output

def generate_srt(input_csv):

    csv_indexes, names, current_line, output_srt = [list() for i in range(4)]
    srt_index = 1
    first_line_time = ""

    # Initialize necessary variables
    for row in range(input_csv.shape[0]):
        csv_indexes.append(input_csv[row][0])
        names.append(input_csv[row][3])
        changed_name = f"【{input_csv[row][3]}】".replace("-", "")

        # For the first row, initialize the SRT index and time information
        if row == 0:
            output_srt.append(str(srt_index))
            current_line.extend([changed_name, str(input_csv[row][2])])
            first_line_time = input_csv[row][1]

        else:
            # Calculate the difference between the current and previous index
            index_diff = csv_indexes[row] - csv_indexes[row-1]
            same_group = names[row] == names[row-1] and index_diff == 1

            # Handle continuous lines (same group)
            if same_group:
                current_line.extend(["，", str(input_csv[row][2])])
            else:
                # Write the previous line to the output
                start_time = first_line_time.split(" --> ")[0]
                end_time = input_csv[row-1][1].split(" --> ")[1]
                output_srt.append(f"{start_time} --> {end_time}")
                output_srt.append(''.join(current_line))

                # Increment the SRT index and start a new line
                srt_index += 1
                output_srt.append(str(srt_index))

                # Prepare the current line for the new entry
                current_line = [changed_name, str(input_csv[row][2])]
                first_line_time = input_csv[row][1]

        # Last line
        if row == (input_csv.shape[0] - 1):
            start_time = first_line_time.split(" --> ")[0]
            end_time = input_csv[row][1].split(" --> ")[1]
            output_srt.append(f"{start_time} --> {end_time}")
            output_srt.append(''.join(current_line))


    np_list = np.array(output_srt)
    n = 3
    m = int(len(output_srt)/n)
    reshaped_np_list = np_list.reshape(m,n)
    new_output_srt = []

    # Iterate through the reshaped NumPy array
    for row in reshaped_np_list:
        for col_value in row:
            # Append the value and a newline
            new_output_srt.extend([col_value, '\n'])
        # Add an extra newline after each row
        new_output_srt.append('\n')

    srt_output = ''.join(new_output_srt)
    return srt_output


def write_srt(file_name):
    # Open the csv file
    srt_folder_path = os.path.join("output-text/srt/", file_name)
    original_csv = pd.read_csv(f"input-csv/{file_name}.csv", header=None)
    csv_array = np.array(original_csv)

    if not os.path.exists(srt_folder_path):
        os.makedirs(srt_folder_path)

    # Get the unique episode numbers
    episode_numbers = np.unique(csv_array[:, 4])
    for episode in episode_numbers:
        episode_mask = csv_array[:, 4] == episode
        episode_input_csv = csv_array[episode_mask]
        episode_file_name = f"{file_name}_{str(episode[-2:])}.srt"

        # generate_txt(episode_file_name, episode_input_csv)
        new_srt_output = generate_srt(episode_input_csv)
        with open(os.path.join(srt_folder_path, episode_file_name), "w") as f_srt:
            f_srt.write(new_srt_output)
        print(f"已生成整合字幕：{episode_file_name}")

def write_txt(file_name):
    output_file_name = f"{file_name}.txt"
    original_csv = pd.read_csv(f"input-csv/{file_name}.csv", header=None)
    csv_array = np.array(original_csv)
    txt_output = []

    # Get the unique episode numbers
    episode_numbers = np.unique(csv_array[:, 4])
    for episode in episode_numbers:
        episode_mask = csv_array[:, 4] == episode
        episode_input_csv = csv_array[episode_mask]
        new_txt_output = generate_txt(episode_input_csv)
        txt_output.extend([str(episode[-2:]), "\n", new_txt_output, "\n\n"])

    with open(os.path.join("output-text/txt", output_file_name), "w") as f_txt:
        f_txt.write("".join(txt_output))
    print(f"已生成台词本：{file_name}.txt")
    

	
def update_artist_metadata(folder_path, artist_name):
    """
    Updates the artist metadata for all MP3 files in the given folder and its sub-folders.

    :param folder_path: Path to the folder containing MP3 files.
    :param artist_name: The artist name to set in the metadata.
    """
    try:
        # Check if the folder exists
        if not os.path.isdir(folder_path):
            print(f"Error: The folder '{folder_path}' does not exist.")
            return

        # Walk through the folder and its sub-folders
        for root, _, files in os.walk(folder_path):
            for file_name in files:
                # Process only MP3 files
                if file_name.endswith('.mp3'):
                    file_path = os.path.join(root, file_name)
                    audiofile = eyed3.load(file_path)

                    if audiofile is None:
                        print(f"Warning: Could not load '{file_path}'. Skipping.")
                        continue

                    # Update the artist tag
                    if audiofile.tag is None:
                        audiofile.initTag()
                    audiofile.tag.artist = artist_name
                    audiofile.tag.save()

                    print(f"Updated artist metadata for: {file_path}")

        print("Metadata update completed.")

    except Exception as e:
        print(f"An error occurred: {e}")