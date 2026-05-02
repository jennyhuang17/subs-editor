"""
音频后处理工具，提供两个子命令：

  filter  —— 从 txt 文件中按正则提取符合条件的行
  reorder —— 对音频文件夹内的 mp3 重新顺序编号

用法：
  python postprocess.py filter <输入文件> <输出文件> <正则表达式>
  python postprocess.py reorder <音频根文件夹>
"""

import os
import re
import sys


def filter_lines(input_file: str, output_file: str, pattern: str):
    """
    保留匹配 pattern 的行，以及纯数字行和空行（维持 srt 结构）。
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    kept = [
        line for line in lines
        if re.search(pattern, line) or line.strip().isdigit() or line.strip() == ""
    ]

    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(kept)

    print(f"过滤完成: {input_file} → {output_file}  ({len(kept)}/{len(lines)} 行保留)")


def reorder_mp3(root_folder: str):
    """
    对 root_folder 下每个子文件夹里的 mp3 按文件名排序后重新编号。
    原命名格式：<集数>-<旧序号> <内容>.mp3
    新命名格式：<集数>-<新三位序号> <内容>.mp3
    """
    for folder in sorted(os.listdir(root_folder)):
        subfolder_path = os.path.join(root_folder, folder)
        if not os.path.isdir(subfolder_path):
            continue

        mp3_files = sorted(f for f in os.listdir(subfolder_path) if f.endswith(".mp3"))
        if not mp3_files:
            continue

        print(f"处理: {subfolder_path}")
        for idx, filename in enumerate(mp3_files, start=1):
            parts = filename.split(" ", 1)
            if len(parts) < 2:
                print(f"  跳过（格式不符）: {filename}")
                continue
            header, content = parts
            episode = header.split("-")[0]
            new_name = f"{episode}-{idx:03d} {content}"
            if filename == new_name:
                continue
            os.rename(
                os.path.join(subfolder_path, filename),
                os.path.join(subfolder_path, new_name)
            )
            print(f"  {filename} → {new_name}")

    print("重命名完成")


# ── 入口 ──────────────────────────────────────────────────────────────────────

USAGE = """\
用法:
  python postprocess.py filter <输入文件> <输出文件> <正则表达式>
  python postprocess.py reorder <音频根文件夹>

示例:
  python postprocess.py filter 山河枕.txt 楚瑜.txt "【8?1】"
  python postprocess.py reorder 乐嫣降噪音频包
"""

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(USAGE)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "filter":
        if len(sys.argv) != 5:
            print("用法: python postprocess.py filter <输入文件> <输出文件> <正则表达式>")
            sys.exit(1)
        filter_lines(sys.argv[2], sys.argv[3], sys.argv[4])

    elif cmd == "reorder":
        if len(sys.argv) != 3:
            print("用法: python postprocess.py reorder <音频根文件夹>")
            sys.exit(1)
        reorder_mp3(sys.argv[2])

    else:
        print(f"未知命令: {cmd}")
        print(USAGE)
        sys.exit(1)
