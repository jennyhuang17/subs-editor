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

input_file = 'output-txt/百花杀.txt'
extract_configs = {
    '女': (r'【[qwert]】', 'output-txt/百花杀（女）.txt'),
    '男': (r'【[asdfg]】', 'output-txt/百花杀（男）.txt'),
}

for name, (pattern, output_file) in extract_configs.items():
    extract_lines(input_file, pattern, output_file)
    print(f"✅已提取{name}台词本：{output_file}")
