import csv
import re

def srt_to_csv(srt_filename, csv_filename, episode):
    # Regular expression pattern to match SRT file format
    pattern = re.compile(r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.*?)\n\n', re.DOTALL)
    
    with open(srt_filename, 'r', encoding='utf-8') as srt_file:
        srt_content = srt_file.read()

    # Find all matches in the SRT content
    matches = pattern.findall(srt_content)

    with open(csv_filename, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        
        # # Write header
        # csv_writer.writerow(['Index', 'Timestamp', 'Line'])
        
        for match in matches:
            index = match[0]
            timestamp = f"{match[1]} --> {match[2]}"
            line = match[3].replace('\n', ' ')
            csv_writer.writerow([index, timestamp, line, episode])

    print(f"Successfully converted {srt_filename} to {csv_filename}")

# Example usage
for i in range(2,3):
    srt_to_csv('苍兰诀 第'+str(i) + '集_简体中文.srt', '苍兰诀'+str(i)+'.csv', 'EP'+str(i))
