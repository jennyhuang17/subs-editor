import re
import os

def parse_srt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    pattern = re.compile(r'(\d+)\s+(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\s+(.*?)\s*(?=\d+\s+\d{2}:\d{2}:\d{2},\d{3} -->|\Z)', re.S)
    matches = pattern.findall(content)
    
    subtitles = []
    for match in matches:
        subtitles.append({
            'index': int(match[0]),
            'start': match[1],
            'end': match[2],
            'text': match[3].strip()
        })
    
    return subtitles

def compress_subtitles(subtitles):
    compressed_subtitles = []
    i = 0
    
    while i < len(subtitles):
        current_subtitle = subtitles[i]
        start_time = current_subtitle['start']
        end_time = current_subtitle['end']
        text = current_subtitle['text']
        
        while i + 1 < len(subtitles) and subtitles[i + 1]['text'] == text:
            end_time = subtitles[i + 1]['end']
            i += 1
        
        compressed_subtitles.append({
            'start': start_time,
            'end': end_time,
            'text': text
        })
        i += 1
    
    return compressed_subtitles

def format_srt(subtitles):
    srt_content = []
    for i, subtitle in enumerate(subtitles, 1):
        srt_content.append(f"{i}")
        srt_content.append(f"{subtitle['start']} --> {subtitle['end']}")
        srt_content.append(subtitle['text'])
        srt_content.append("")  # SRT files need a blank line after each subtitle
    
    return "\n".join(srt_content)

def write_srt(file_path, srt_content):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(srt_content)

def compress_srt_file(input_path, output_path):
    subtitles = parse_srt(input_path)
    compressed_subtitles = compress_subtitles(subtitles)
    formatted_srt = format_srt(compressed_subtitles)
    write_srt(output_path, formatted_srt)

# # Example usage:
# input_srt = 'input.srt'
# output_srt = 'output.srt'
# compress_srt_file(input_srt, output_srt)

current_folder = os.getcwd()
for filename in os.listdir(current_folder):
    if filename.endswith('.srt'):
        compress_srt_file(filename,'new_'+filename)
