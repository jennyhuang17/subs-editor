import re

def ass_to_srt(ass_file, srt_file):
    with open(ass_file, 'r', encoding='utf-8') as f:
        ass_content = f.read()

    # Regular expression to match Dialogue lines in .ass format
    dialogue_regex = r'Dialogue: \d,(?P<start>\d+:\d+:\d+\.\d+),(?P<end>\d+:\d+:\d+\.\d+),[^,]*,,[^,]*,[^,]*,[^,]*,,(?P<text>[^\n]*)'
    dialogue_lines = re.finditer(dialogue_regex, ass_content)

    # Open the output .srt file for writing
    with open(srt_file, 'w', encoding='utf-8') as f:
        count = 1
        for match in dialogue_lines:
            start_time = match.group('start')
            end_time = match.group('end')
            text = match.group('text').strip()

            # Format start and end times into HH:MM:SS,mmm (milliseconds)
            start_time_formatted = f"{start_time.replace('.',',')}"
            end_time_formatted = f"{end_time.replace('.',',')}"

            # Write subtitle index
            f.write(f"{count}\n")

            # Write subtitle timing
            f.write(f"0{start_time_formatted}0 --> 0{end_time_formatted}0\n")

            # Write subtitle text
            f.write(f"{text}\n\n")

            count += 1

    print(f"Conversion completed: {ass_file} -> {srt_file}")

# Example usage:
for i in range(34, 35):
    epno = f"{i:02}"
    ass_file = f"{'暗河传/'}{epno}.ass"
    srt_file = f"{'暗河传/'}{epno}.srt"
    ass_to_srt(ass_file, srt_file)
