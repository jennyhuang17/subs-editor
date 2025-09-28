import os
import re

def srt_to_txt(srt_file):
    """读取单个srt文件，返回字幕台词列表"""
    with open(srt_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    subtitles = []
    for line in lines:
        line = line.strip()
        if not line or line.isdigit() or '-->' in line:
            continue
        subtitles.append(line)
    return subtitles

def merge_srt_folder(folder, output_file):
    all_texts = []

    # 获取文件夹下的所有 .srt 文件，并排序
    srt_files = sorted([f for f in os.listdir(folder) if f.endswith('.srt')])

    for srt_file in srt_files:
        # 从文件名中提取集数 A_01.srt -> 01
        match = re.match(r'.*(\d{2})\.srt$', srt_file)
        if not match:
            continue
        episode_num = match.group(1)

        # 读取字幕内容
        subtitles = srt_to_txt(os.path.join(folder, srt_file))

        if subtitles:
            all_texts.append(episode_num)       # 在开头写入集数
            all_texts.extend(subtitles)         # 加入字幕
            all_texts.append("")                # 每集之间空一行

    # 写入输出文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(all_texts).strip())   # 去掉最后多余空行

if __name__ == "__main__":
    input_folder = "output-text/srt/光渊"
    output_file = "output-text/txt/光渊.txt"
    merge_srt_folder(input_folder, output_file)
