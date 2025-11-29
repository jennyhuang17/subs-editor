import csv

def mark_character_in_csv(input_file, output_file):
    # Read the CSV file
    with open(input_file, mode='r', encoding='utf-8') as infile:
        csvreader = csv.reader(infile)
        rows = list(csvreader)

    # Initialize the previous character
    previous_character = None

    # Loop through each row and mark the character
    for row in rows:
        line = row[2]  # The 'line' is in the 3rd column (index 2)

        # Check if the line starts with the "【" symbol
        if line.startswith('【'):
            row[3] = ''  # Leave the character value empty
            previous_character = None  # Reset the previous character
        elif '：' in line:
            # Extract the character name (text before the "：" symbol)
            character_name = line.split('：')[0]

            # Check if the character name is valid (no more than 3 characters)
            if len(character_name) < 4:
                row[3] = character_name  # Update the character column with the valid name
                previous_character = character_name  # Update previous character
            else:
                row[3] = previous_character if previous_character else 'Unknown'  # Use previous character
        else:
            # If no character name is found, use the previous character
            if previous_character:
                row[3] = previous_character  # Update the character column
            else:
                row[3] = 'Unknown'  # If there's no previous character, set to 'Unknown'

    # Write the updated data to a new CSV file
    with open(output_file, mode='w', encoding='utf-8', newline='') as outfile:
        csvwriter = csv.writer(outfile)
        csvwriter.writerows(rows)

    print(f"Processed CSV saved as {output_file}")


# Example usage
input_file = '黑2.csv'  # Your input CSV file
output_file = '黑2_标记.csv'  # Your output CSV file
mark_character_in_csv(input_file, output_file)
