import re

def extract_lines(input_file, search_strings, output_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    extracted_lines = []
    for line in lines:
        # Check for the search string or lines containing digits or empty lines
        if any(search_string in line for search_string in search_strings) or line.strip().isdigit() or line.strip() == "":
            extracted_lines.append(line)

    # Write the extracted lines to the output file
    with open(output_file, 'w', encoding='utf-8') as file:
        file.writelines(extracted_lines)

# Example usage
input_file = 'output-text/txt/光渊.txt'  # Replace with your input file name
output_file = 'output-text/txt/裴溯.txt'  # Replace with your desired output file name
search_strings = ["【裴溯", "裴溯相关", "裴溯】"]  # Replace with your desired search string
extract_lines(input_file, search_strings, output_file)