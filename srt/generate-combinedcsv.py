import csv
import os
import re
import sys

def read_srt_file(file_path, episode_number):
    content = []

    # 改进后的正则：允许最后一句没有 \n\n
    pattern = re.compile(
        r'(\d+)\n'
        r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n'
        r'(.*?)(?=\n{2,}|\Z)',
        re.DOTALL
    )

    # 读取 SRT 文件
    with open(file_path, 'r', encoding='utf-8') as srt_file:
        srt_content = srt_file.read()

    # 匹配字幕块
    matches = pattern.findall(srt_content)
    for match in matches:
        index = match[0]
        timestamp = f"{match[1]} --> {match[2]}"
        line = match[3].replace('\n', ' ').strip()
        content.append({
            '编号': index,
            '时间戳': timestamp,
            '台词': line,
            '角色': '',
            '集数': f'EP{episode_number:02}'
        })

    return content

# Directory containing the .srt files
srt_directory = sys.argv[1]

# Specify range of the episode
ep_start, ep_end = int(sys.argv[2]), int(sys.argv[3])+1
episode_range = range(ep_start, ep_end)

# Output csv file name
if ep_end - ep_start == 1:
    output_csv = f'{srt_directory}台词本{ep_start}.csv'
else:
    output_ep_end = ep_end - 1
    output_csv = f'{srt_directory}台词本{ep_start}-{output_ep_end}.csv'

# Regex pattern to extract the episode number from the filename
episode_pattern = re.compile(r'(\d{2})\.srt$')

# List to hold all the content from all .srt files
all_content = []

# Get and sort filenames
filenames = [f for f in os.listdir(srt_directory) if episode_pattern.search(f)]
filenames.sort()

# Iterate over all .srt files in the directory
for filename in filenames:
    match = episode_pattern.search(filename)
    if match:
        episode_number = int(match.group(1))
        if episode_number in episode_range:
            print(episode_number)
            file_path = os.path.join(srt_directory, filename)
            all_content.extend(read_srt_file(file_path, episode_number))

# Write the unified CSV file
with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['编号', '时间戳', '台词', '角色', '集数']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for row in all_content:
        writer.writerow(row)

print(f'Unified CSV file created: {output_csv}')
