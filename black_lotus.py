import pandas as pd
import numpy as np

def csv_to_txt(new_fname, subs_arr, replacements=None):
    csv_to_txt_list, idx_ls, name_ls = [list() for i in range(3)]

    for row in range(subs_arr.shape[0]):
        idx_ls.append(subs_arr[row][0]) 
        name_ls.append(subs_arr[row][3])
        char_name = '【' + str(subs_arr[row][3]) + '】' 

        if row == 0:
            csv_to_txt_list.append(str(subs_arr[row][2]))
        else:
            diff = idx_ls[row] - idx_ls[row-1]
            # Removed the condition checking for special characters
            if name_ls[row] == name_ls[row-1] and diff == 1:
                csv_to_txt_list.append('，')
            else:
                csv_to_txt_list.append('\n')
            csv_to_txt_list.append(str(subs_arr[row][2]))

    # Perform replacements if any
    if replacements:
        csv_to_txt_list = [replace_text(str(line), replacements) for line in csv_to_txt_list]

    # Write to file
    ftxt = 'output-text/txt/' + new_fname + '.txt'
    with open(ftxt, 'w') as f1:
        csv_to_txt_list = ''.join(csv_to_txt_list)
        f1.write(csv_to_txt_list)
    print(new_fname + ' 台词本已生成！')


def replace_text(text, replacements):
    """
    Performs replacements in a given text string based on the provided replacements dictionary.
    :param text: The text to modify.
    :param replacements: A dictionary of string replacements.
    :return: The modified text after all replacements.
    """
    if replacements:
        for old_str, new_str in replacements.items():
            text = text.replace(old_str, new_str)
    return text

def csv_to_compressed_srt(new_fname, subs_arr, replacements=None):
    idx_ls, name_ls, line_ls, csv_to_srt_combined_list = [list() for i in range(4)]
    count = 0
    time_start = ''

    for row in range(subs_arr.shape[0]):
        idx_ls.append(subs_arr[row][0])
        name_ls.append(subs_arr[row][3])
        char_name = '【' + str(subs_arr[row][3]) + '】'

        if row == 0:
            count = count + 1
            csv_to_srt_combined_list.append(str(count))
            line_ls.append(str(subs_arr[row][2]))
            time_start = subs_arr[row][1]

        else:
            diff = idx_ls[row] - idx_ls[row-1]
            # Removed the condition checking for special characters
            if name_ls[row] == name_ls[row-1] and diff == 1:
                line_ls.append(str(subs_arr[row][2]))
            else:
                t_new_split = time_start.split()
                t_end_split = subs_arr[row-1][1].split()
                t_new_split[2] = t_end_split[2]
                csv_to_srt_combined_list.append(' '.join(t_new_split))
                csv_to_srt_combined_list.append('，'.join(line_ls))

                count = count + 1
                csv_to_srt_combined_list.append(str(count))
                line_ls = [str(subs_arr[row][2])]
                time_start = subs_arr[row][1]
            
            if row == (subs_arr.shape[0] - 1):
                t_new_split = time_start.split()
                t_end_split = subs_arr[row][1].split()
                t_new_split[2] = t_end_split[2]
                csv_to_srt_combined_list.append(' '.join(t_new_split))
                csv_to_srt_combined_list.append('，'.join(line_ls))

    # Perform replacements if any
    if replacements:
        csv_to_srt_combined_list = [replace_text(str(line), replacements) for line in csv_to_srt_combined_list]

    # Write to file
    np_list = np.array(csv_to_srt_combined_list)
    n = 3
    m = int(len(csv_to_srt_combined_list)/n)
    np_list_new = np_list.reshape(m,n)

    combined_srt_list = list()
    for x in range(np_list_new.shape[0]):
        for y in range(np_list_new.shape[1]):
            if y == 2:
                new_line = np_list_new[x][y].replace("】 ", "】").replace("-】", "】")
                np_list_new[x][y] = new_line
            combined_srt_list.extend([np_list_new[x][y],'\n'])
        combined_srt_list.append('\n')

    fsrt = 'output-text/srt/' + new_fname + '.srt'
    with open(fsrt, 'w') as f2:
        csv_to_srt_list = ''.join(combined_srt_list)
        f2.write(csv_to_srt_list)
    print(new_fname + ' 字幕文件（整合）已生成！')



# Function to process replacements in files (if needed)
def find_and_replace_in_file(file_path, replacements):
    """
    Reads the file at `file_path`, performs replacements of strings based on the 
    `replacements` dictionary, and writes the modified content back to the file.
    
    :param file_path: The path of the file to modify.
    :param replacements: A dictionary where keys are the strings to be replaced, 
                         and values are the new strings.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Perform all replacements
    for old_str, new_str in replacements.items():
        content = content.replace(old_str, new_str)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Replacements completed in {file_path}")


# Main code execution

fname = "黑2"

input_fpath = 'input-csv/' + fname + '.csv'
input_csv = pd.read_csv(input_fpath, header=None)
subs_arr = np.array(input_csv)

# Example replacements dictionary
replacements_ls = {
    'nan，': '',
    '？，': '？',
    '！，': '！',
    '—，': '—',
    '…，': '…',
    '。，': '。',
    '：，': '：',
}



# Get the unique episode numbers
episode_numbers = np.unique(subs_arr[:, 4])

for episode in episode_numbers:
    episode_mask = subs_arr[:, 4] == episode
    episode_subs_arr = subs_arr[episode_mask]
    
    episode_fname = f"{fname}_{str(episode[-2:])}"
    
    # Generate TXT and SRT files with replacements
    csv_to_txt(episode_fname, episode_subs_arr, replacements=replacements_ls)
    csv_to_compressed_srt(episode_fname, episode_subs_arr, replacements=replacements_ls)

    # If additional replacement is needed after file generation
    # txt_file_path = f'output-text/txt/{episode_fname}.txt'
    # srt_file_path = f'output-text/srt/{episode_fname}.srt'
    
    # find_and_replace_in_file(txt_file_path, replacements_txt)
    # find_and_replace_in_file(srt_file_path, replacements_srt)
