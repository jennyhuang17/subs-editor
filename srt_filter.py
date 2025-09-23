def extract_srt_lines(input_file, output_file, keyword):
    """
    Extracts subtitle blocks containing the keyword from an SRT file
    and saves them into a new SRT file with proper numbering.
    """

    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Split into blocks separated by blank lines
    blocks = content.strip().split("\n\n")

    extracted_blocks = []
    counter = 1

    for block in blocks:
        if keyword.lower() in block.lower():  # case-insensitive match
            lines = block.split("\n")
            # Replace first line with new numbering
            lines[0] = str(counter)
            counter += 1
            extracted_blocks.append("\n".join(lines))

    # Join blocks with double newlines
    new_content = "\n\n".join(extracted_blocks)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"Done! Extracted {len(extracted_blocks)} blocks to {output_file}")


# Example usage
ep_start = 27
ep_end = 28
ep_name = "赴山海"
char_name = "李沉舟"

for i in range(ep_start, ep_end+1):
    input_path = "output-text/srt/"+ep_name+"/"+ep_name+"_"+str(i)+".srt"
    output_path = "output-text/srt/"+ep_name+"/"+char_name+"_"+str(i)+".srt"
    extract_srt_lines(input_path, output_path, "【"+char_name)