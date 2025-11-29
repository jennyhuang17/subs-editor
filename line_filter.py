import re

def extract_lines(input_file, pattern, output_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    extracted_lines = []
    for line in lines:
        # 用正则匹配代替原先的 search_strings
        if re.search(pattern, line) or line.strip().isdigit() or line.strip() == "":
            extracted_lines.append(line)

    # 写入输出文件
    with open(output_file, 'w', encoding='utf-8') as file:
        file.writelines(extracted_lines)

# 示例使用
input_file = 'output-txt/山河枕.txt'
output_file = 'output-txt/楚瑜.txt'
pattern = r'【8?1】'
extract_lines(input_file, pattern, output_file)
