def filter_lines(input_file, output_file, search_strings):
    with open('output-text/'+ input_file + '.txt', 'r') as infile:
        lines = infile.readlines()
    
    filtered_lines = []
    for line in lines:
        if any(search_string in line for search_string in search_strings):
            filtered_lines.append(line)
    
    with open('output-text/' + output_file + '.txt', 'w') as outfile:
        outfile.writelines(filtered_lines)

def main():
    input_file = input("Enter the input file name: ")
    output_file = input("Enter the output file name: ")

    search_strings = []
    while True:
        search_string = input("Enter a string to search for (or press Enter to finish): ")
        if not search_string:
            break
        search_strings.append(search_string)
    
    filter_lines(input_file, output_file, search_strings)
    print(f"Filtered lines have been written to {output_file}")

if __name__ == "__main__":
    main()
