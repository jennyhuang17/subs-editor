"""
用法: python process.py <文件夹> <开始集数> <结束集数>

流程:
  1. 若目录中存在 .ass 文件，询问是否转换为 .srt
     转换时按排序顺序与集数对应，输出 <文件夹名><集数>.srt
  2. 按集数范围查找精确命名的 <文件夹名><集数>.srt，找不到则报错退出
  3. 生成台词 CSV
"""

import csv
import os
import re
import sys


# ── ASS → SRT 转换 ────────────────────────────────────────────────────────────

# ASS Dialogue 格式: Dialogue: Layer,Start,End,Style,Actor,MarginL,MarginR,MarginV,Effect,Text
DIALOGUE_RE = re.compile(
    r'Dialogue: \d,'
    r'(?P<start>\d+:\d{2}:\d{2}\.\d{2}),'
    r'(?P<end>\d+:\d{2}:\d{2}\.\d{2}),'
    r'[^,]*,[^,]*,[^,]*,[^,]*,[^,]*,[^,]*,'
    r'(?P<text>[^\n]*)'
)
ASS_OVERRIDE_RE = re.compile(r'\{[^}]*\}')


def ass_to_srt(ass_path, srt_path):
    with open(ass_path, 'r', encoding='utf-8') as f:
        content = f.read()

    matches = list(DIALOGUE_RE.finditer(content))
    if not matches:
        print(f"警告: {ass_path} 中未匹配到对话行，跳过转换")
        return False

    with open(srt_path, 'w', encoding='utf-8') as f:
        for i, m in enumerate(matches, 1):
            # ASS 时间格式 H:MM:SS.cc → SRT 格式 HH:MM:SS,mmm（补零对齐）
            start = '0' + m.group('start').replace('.', ',') + '0'
            end   = '0' + m.group('end').replace('.', ',') + '0'
            text  = ASS_OVERRIDE_RE.sub('', m.group('text')).strip()
            f.write(f"{i}\n{start} --> {end}\n{text}\n\n")

    print(f"转换: {os.path.basename(ass_path)} → {os.path.basename(srt_path)}")
    return True


def convert_ass_files(directory, ep_start, ep_end):
    """
    只转换指定集数范围内的纯数字 .ass 文件。

    支持：
    1.ass
    01.ass
    10.ass

    转换后保留同样的纯数字名字：
    1.ass  -> 1.srt
    01.ass -> 01.srt
    10.ass -> 10.srt
    """
    ass_name_re = re.compile(r'^(\d+)\.ass$')

    ass_map = {}

    for filename in os.listdir(directory):
        match = ass_name_re.match(filename)
        if not match:
            continue

        epno = int(match.group(1))
        ass_map[epno] = filename

    for epno in range(ep_start, ep_end + 1):
        ass_file = ass_map.get(epno)

        if not ass_file:
            print(f"警告: 未找到第 {epno} 集对应的 .ass 文件，跳过转换")
            continue

        srt_name = os.path.splitext(ass_file)[0] + '.srt'

        ass_to_srt(
            os.path.join(directory, ass_file),
            os.path.join(directory, srt_name),
        )


# ── 生成 CSV ──────────────────────────────────────────────────────────────────

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


def find_srt(directory, epno):
    """
    查找纯数字命名的 .srt 文件。

    支持：
    1.srt
    01.srt
    10.srt
    """
    srt_name_re = re.compile(r'^(\d+)\.srt$')
    matches = []

    for filename in os.listdir(directory):
        match = srt_name_re.match(filename)
        if not match:
            continue

        if int(match.group(1)) == epno:
            matches.append(filename)

    return sorted(matches)


def generate_csv(directory, folder_name, ep_start, ep_end):
    all_rows = []
    missing = []

    for epno in range(ep_start, ep_end + 1):
        candidates = find_srt(directory, epno)
        if not candidates:
            missing.append(str(epno))
            continue
        if len(candidates) > 1:
            print(f"警告: 第 {epno} 集匹配到多个文件: {', '.join(candidates)}，使用 {candidates[0]}")
        srt_name = candidates[0]
        print(f"读取: {srt_name}")
        all_rows.extend(read_srt(os.path.join(directory, srt_name), epno))

    if missing:
        print(f"错误: 以下集数未找到对应的 SRT 文件: {', '.join(missing)}")
        sys.exit(1)

    if ep_start == ep_end:
        output_csv = os.path.join(directory, f"{folder_name}{ep_start:02d}.csv")
    else:
        output_csv = os.path.join(directory, f"{folder_name}{ep_start:02d}-{ep_end:02d}.csv")

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

    directory   = sys.argv[1].rstrip('/\\')
    ep_start    = int(sys.argv[2])
    ep_end      = int(sys.argv[3])
    folder_name = os.path.basename(directory)

    # 步骤 1：按需从 ASS 转换为 SRT
    answer = input("是否从 .ass 转换为 .srt？[y/N] ").strip().lower()
    if answer == 'y':
        convert_ass_files(directory, ep_start, ep_end)
        
    # 步骤 2+3：精确查找 SRT 并生成 CSV
    generate_csv(directory, folder_name, ep_start, ep_end)
