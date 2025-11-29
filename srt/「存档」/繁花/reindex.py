import os
import re

def reindex_srt_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        
    # Split content into blocks (a block is separated by two newlines)
    blocks = content.strip().split('\n\n')
    
    reindexed_blocks = []
    index = 1
    
    for block in blocks:
        lines = block.split('\n')
        # Replace the first line (the index) with the new index
        lines[0] = str(index)
        reindexed_blocks.append('\n'.join(lines))
        index += 1
    
    # Join the reindexed blocks with double newline separation
    reindexed_content = '\n\n'.join(reindexed_blocks)
    
    # Write the reindexed content back to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(reindexed_content)

def reindex_all_srt_files_in_folder(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.srt'):
                file_path = os.path.join(root, file)
                reindex_srt_file(file_path)
                print(f'Reindexed: {file_path}')

# Use the current directory
current_directory = os.getcwd()
reindex_all_srt_files_in_folder(current_directory)
