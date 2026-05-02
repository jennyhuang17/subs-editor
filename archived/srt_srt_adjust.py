import re

TIME_LINE_RE = re.compile(
    r"(?P<start>\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(?P<end>\d{2}:\d{2}:\d{2},\d{3})"
)

def srt_time_to_ms(t: str) -> int:
    """'HH:MM:SS,mmm' -> milliseconds (int)"""
    hh, mm, rest = t.split(":")
    ss, mmm = rest.split(",")
    return (int(hh) * 3600 + int(mm) * 60 + int(ss)) * 1000 + int(mmm)

def ms_to_srt_time(ms: int) -> str:
    """milliseconds (int) -> 'HH:MM:SS,mmm'"""
    if ms < 0:
        ms = 0
    hh = ms // 3600000
    ms %= 3600000
    mm = ms // 60000
    ms %= 60000
    ss = ms // 1000
    mmm = ms % 1000
    return f"{hh:02d}:{mm:02d}:{ss:02d},{mmm:03d}"

def parse_srt_blocks(srt_text: str):
    """
    Split SRT into blocks separated by blank lines.
    Return a list of blocks, each block is a list of lines.
    """
    # 保留原始换行风格：先统一用 \n 处理
    srt_text = srt_text.replace("\r\n", "\n").replace("\r", "\n")
    raw_blocks = srt_text.strip().split("\n\n")
    blocks = [b.split("\n") for b in raw_blocks if b.strip()]
    return blocks

def extract_times(block_lines):
    """
    From one subtitle block, find time line and return (start_ms, end_ms, time_line_index).
    If not found, return (None, None, None).
    """
    for idx, line in enumerate(block_lines):
        m = TIME_LINE_RE.search(line)
        if m:
            start_ms = srt_time_to_ms(m.group("start"))
            end_ms = srt_time_to_ms(m.group("end"))
            return start_ms, end_ms, idx
    return None, None, None

def replace_time_line(original_line: str, new_start_ms: int, new_end_ms: int) -> str:
    """Replace the time portion in a line with updated times."""
    new_start = ms_to_srt_time(new_start_ms)
    new_end = ms_to_srt_time(new_end_ms)
    # 直接用正则把 start/end 替换掉
    return TIME_LINE_RE.sub(f"{new_start} --> {new_end}", original_line)

def adjust_gaps(blocks, threshold_seconds: float):
    """
    If gap between block i end and block i+1 start is smaller than threshold,
    extend both to the midpoint.
    """
    threshold_ms = int(threshold_seconds * 1000)

    # 先把每个 block 的时间信息取出来，方便后面改
    info = []
    for b in blocks:
        s, e, time_idx = extract_times(b)
        info.append([s, e, time_idx])  # 用 list 是因为要修改

    # 逐对处理相邻字幕
    for i in range(len(blocks) - 1):
        s1, e1, idx1 = info[i]
        s2, e2, idx2 = info[i + 1]

        # 如果某个 block 没有时间行，跳过
        if s1 is None or s2 is None:
            continue

        gap = s2 - e1

        # 只处理“有间隔”的情况，且间隔小于阈值
        if 0 < gap < threshold_ms:
            mid = e1 + gap // 2
            # 更新前一条 end，后一条 start
            info[i][1] = mid
            info[i + 1][0] = mid

    # 把修改后的时间写回 blocks
    for i in range(len(blocks)):
        s, e, time_idx = info[i]
        if s is None:
            continue
        original_time_line = blocks[i][time_idx]
        blocks[i][time_idx] = replace_time_line(original_time_line, s, e)

    return blocks

def write_srt_blocks(blocks) -> str:
    """Join blocks back to SRT text."""
    return "\n\n".join("\n".join(lines) for lines in blocks) + "\n"

def main():
    input_path = input("Input .srt path: ").strip()
    output_path = input("Output .srt path (e.g. out.srt): ").strip()
    threshold_seconds = float(input("Threshold seconds (e.g. 0.4): ").strip())

    with open(input_path, "r", encoding="utf-8-sig") as f:
        text = f.read()

    blocks = parse_srt_blocks(text)
    new_blocks = adjust_gaps(blocks, threshold_seconds)
    out_text = write_srt_blocks(new_blocks)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(out_text)

    print("Done! Wrote:", output_path)

if __name__ == "__main__":
    main()