import os
import re
from collections import defaultdict

# Define the path to the folder containing mp3 files
folder_path = '赵盼儿'  # Replace with the actual folder path
output_file_path = '赵盼儿16-40.txt'  # The path of the output text file

# Define a regular expression to match the episode number and the title
file_pattern = re.compile(r'(\d{2})-(\d{3}) (.+)\.mp3')

# Create a dictionary to store episode titles grouped by episode number
episodes = defaultdict(list)

# List all files in the directory
for filename in os.listdir(folder_path):
    if filename.endswith('.mp3'):
        match = file_pattern.match(filename)
        if match:
            episode_number = match.group(1)  # Extract the episode number
            title = match.group(3)  # Extract the title
            episodes[episode_number].append((filename, "◦ "+title))

# Write the sorted output to the text file
with open(output_file_path, 'w', encoding='utf-8') as output_file:
    for episode_number in sorted(episodes.keys()):
        output_file.write(episode_number + '\n')
        # Sort titles by the original filename
        for _, title in sorted(episodes[episode_number], key=lambda x: x[0]):
            output_file.write(title + '\n')
        output_file.write('\n')  # Add a blank line between episodes
