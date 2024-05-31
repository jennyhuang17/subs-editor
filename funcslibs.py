import csv
import pandas as pd

# Convert SRT to CSV
def srt_to_csv(input_file, output_file):
    with open(input_file, 'r') as f:
        lines = f.readlines()

    subtitles = []
    subtitle = {'index': None, 'start_time': None, 'end_time': None, 'text': ''}
    for line in lines:
        line = line.strip()
        if line.isdigit():
            # 新的字幕索引
            if subtitle['index'] is not None:
                subtitles.append(subtitle)
                subtitle = {'index': None, 'start_time': None, 'end_time': None, 'text': ''}
            subtitle['index'] = int(line)
        elif ' --> ' in line:
            # 时间戳
            start_time, end_time = line.split(' --> ')
            subtitle['start_time'] = start_time.strip()
            subtitle['end_time'] = end_time.strip()
        elif line.strip() == '':
            # 空行，表示字幕结束
            subtitles.append(subtitle)
            subtitle = {'index': None, 'start_time': None, 'end_time': None, 'text': ''}
        else:
            # 字幕文本
            subtitle['text'] += line + ' '

    # 写入CSV文件
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['index', 'start_time', 'end_time', 'text']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for subtitle in subtitles:
            writer.writerow(subtitle)
            
# Conver CSV to SRT
def csv_to_srt(csv_file, srt_file):
    # Read the CSV file
    df = pd.read_csv(csv_file)
    
    # Open the SRT file for writing
    with open(srt_file, 'w') as file:
        for index, row in df.iterrows():
            # Write the index
            file.write(f"{row['index']}\n")
            
            # Write the time format in SRT style
            file.write(f"{row['start_time']} --> {row['end_time']}\n")
            
            # Write the subtitle text
            file.write(f"{row['text']}\n")
            
            # Write a blank line to separate subtitles
            file.write("\n")

# Reorganize CSV based on characters
def process_csv(input_file, output_file):
    with open(input_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
    
    new_rows = []
    i = 0
    
    while i < len(rows):
        current_row = rows[i]
        character = current_row['character']
        start_time = current_row['start_time']
        end_time = current_row['end_time']
        text = f"【{character}】{current_row['text']}"
        index = int(current_row['index'])
        
        # Check for grouping adjacent rows
        while (i + 1 < len(rows) and
               rows[i + 1]['character'] == character and
               int(rows[i + 1]['index']) == index + 1):
            next_row = rows[i + 1]
            end_time = next_row['end_time']
            text += ' ' + next_row['text']
            index = int(next_row['index'])
            i += 1
        
        new_rows.append({
            'index': len(new_rows),
            'start_time': start_time,
            'end_time': end_time,
            'text': text,
            'character': character
        })
        i += 1
    
    # Write the processed rows to a new CSV file
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['index', 'start_time', 'end_time', 'text']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for row in new_rows:
            writer.writerow({
                'index': row['index'],
                'start_time': row['start_time'],
                'end_time': row['end_time'],
                'text': row['text']
            })