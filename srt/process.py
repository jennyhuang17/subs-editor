"""
用法: python process.py <文件夹> <开始集数> <结束集数>

流程:
  1. 把文件夹内的 .ass 或 .srt 文件按文件名排序，重命名为 <文件夹名><集数>.ass/.srt
  2. 如果有 .ass 文件，转换成 .srt
  3. 生成台词 CSV
"""

import csv
import os
import re
import sys


# ── 1. 重命名 ────────────────────────────────────────────────────────────────

def rename_files(directory, folder_name, ep_start, ep_end):
    episode_range = range(ep_start, ep_end + 1)

    for ext in ('.ass', '.srt'):
        files = sorted(f for f in os.listdir(directory) if f.endswith(ext))
        if not files:
            continue

        if len(files) != len(episode_range):
            print(f"警告: 找到 {len(files)} 个 {ext} 文件，但集数范围是 {len(episode_range)} 集，请确认")

        for filename, epno in zip(files, episode_range):
            new_name = f"{folder_name}{epno:02d}{ext}"
            if filename == new_name:
                continue
            src = os.path.join(directory, filename)
            dst = os.path.join(directory, new_name)
            os.rename(src, dst)
            print(f"重命名: {filename} → {new_name}")


# ── 2. ASS → SRT 转换 ────────────────────────────────────────────────────────

DIALOGUE_RE = re.compile(
    r'Dialogue: \d,(?P<start>\d+:\d+:\d+\.\d+),(?P<end>\d+:\d+:\d+\.\d+),'
    r'[^,]*,,[^,]*,[^,]*,[^,]*,,(?P<text>[^\n]*)'
)

def ass_to_srt(ass_path, srt_path):
    with open(ass_path, 'r', encoding='utf-8') as f:
        content = f.read()

    with open(srt_path, 'w', encoding='utf-8') as f:
        for i, m in enumerate(DIALOGUE_RE.finditer(content), 1):
            start = m.group('start').replace('.', ',')
            end   = m.group('end').replace('.', ',')
            text  = m.group('text').strip()
            f.write(f"{i}\n0{start}0 --> 0{end}0\n{text}\n\n")

    print(f"转换: {ass_path} → {srt_path}")


def convert_ass_files(directory, folder_name, ep_start, ep_end):
    for epno in range(ep_start, ep_end + 1):
        ass_path = os.path.join(directory, f"{folder_name}{epno:02d}.ass")
        srt_path = os.path.join(directory, f"{folder_name}{epno:02d}.srt")
        if os.path.exists(ass_path):
            ass_to_srt(ass_path, srt_path)


# ── 3. 生成 CSV ──────────────────────────────────────────────────────────────

SRT_BLOCK_RE = re.compile(
    r'(\d+)\n'
    r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n'
    r'(.*?)(?=\n{2,}|\Z)',
    re.DOTALL
)

def read_srt(file_path, episode_number):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    rows = []
    for m in SRT_BLOCK_RE.findall(content):
        rows.append({
            '编号':  m[0],
            '时间戳': f"{m[1]} --> {m[2]}",
            '台词':  m[3].replace('\n', ' ').strip(),
            '角色':  '',
            '集数':  f'EP{episode_number:02d}',
        })
    return rows


def generate_csv(directory, folder_name, ep_start, ep_end):
    all_rows = []
    episode_re = re.compile(rf'{re.escape(folder_name)}(\d{{2}})\.srt$')

    filenames = sorted(f for f in os.listdir(directory) if episode_re.search(f))
    for filename in filenames:
        epno = int(episode_re.search(filename).group(1))
        if ep_start <= epno <= ep_end:
            print(f"读取: {filename}")
            all_rows.extend(read_srt(os.path.join(directory, filename), epno))

    if ep_start == ep_end:
        output_csv = os.path.join(directory, f"台词本{ep_start:02d}.csv")
    else:
        output_csv = os.path.join(directory, f"台词本{ep_start:02d}-{ep_end:02d}.csv")

    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['编号', '时间戳', '台词', '角色', '集数'])
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"CSV 已生成: {output_csv}")


# ── 入口 ─────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("用法: python process.py <文件夹> <开始集数> <结束集数>")
        sys.exit(1)

    directory = sys.argv[1].rstrip('/\\')
    ep_start  = int(sys.argv[2])
    ep_end    = int(sys.argv[3])
    folder_name = os.path.basename(directory)  # 取最后一层目录名

    rename_files(directory, folder_name, ep_start, ep_end)
    convert_ass_files(directory, folder_name, ep_start, ep_end)
    generate_csv(directory, folder_name, ep_start, ep_end)
