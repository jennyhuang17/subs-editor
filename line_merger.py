import re

# 将srt文件中的多行台词合并到一行

def merge_lines(srt_filename, output_srt_filename):
    # Regular expression pattern to match SRT file format
    pattern = re.compile(r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.*?)(?=\n\d+\n|\Z)', re.DOTALL)
    
    with open(srt_filename, 'r', encoding='utf-8') as srt_file:
        srt_content = srt_file.read()

    # Find all matches in the SRT content
    matches = pattern.findall(srt_content)

    with open(output_srt_filename, 'w', encoding='utf-8') as output_file:
        for match in matches:
            index = match[0]
            timestamp = f"{match[1]} --> {match[2]}"
            line = ' '.join(match[3].splitlines())
            
            output_file.write(f"{index}\n")
            output_file.write(f"{timestamp}\n")
            output_file.write(f"{line}\n\n")

    print(f"Successfully compressed lines in {srt_filename} and saved to {output_srt_filename}")

# Example usage
merge_lines('output-text/05.srt', 'output-text/长相思二05.srt')
