"""
subs-editor 交互式菜单
用法: python menu.py
"""

import os
import sys

try:
    import questionary
    from questionary import Style
except ImportError:
    print("请先安装依赖: pip install questionary")
    sys.exit(1)

# 把 srt/ 子目录加入路径，方便 import process.py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "srt"))

STYLE = Style([
    ("qmark",       "fg:#5f819d bold"),
    ("question",    "bold"),
    ("answer",      "fg:#5f819d bold"),
    ("pointer",     "fg:#5f819d bold"),
    ("highlighted", "fg:#5f819d bold"),
    ("selected",    "fg:#5f819d"),
])


def ask(prompt, default=None):
    return questionary.text(prompt, default=str(default) if default is not None else "", style=STYLE).ask()

def select(prompt, choices):
    return questionary.select(prompt, choices=choices, style=STYLE).ask()

def clear():
    os.system("clear" if os.name == "posix" else "cls")

def header():
    print("═" * 32)
    print("      subs-editor 工具菜单")
    print("═" * 32)
    print()


# ── 各功能 ────────────────────────────────────────────────────────────────────

def run_process():
    print("\n── 预处理字幕 ──\n")
    folder    = ask("字幕文件夹名（srt/ 下的子文件夹）：")
    ep_start  = ask("开始集数：", "1")
    ep_end    = ask("结束集数：", ep_start)

    from process import convert_ass_files, generate_csv
    folder = folder.rstrip("/\\")
    if not folder.startswith("srt/") and not folder.startswith("srt\\"):
        folder = os.path.join("srt", folder)
    folder_name = os.path.basename(folder)
    ep_start, ep_end = int(ep_start), int(ep_end)

    print()
    ass_files = sorted(f for f in os.listdir(folder) if f.endswith('.ass'))
    if ass_files:
        print(f"发现 {len(ass_files)} 个 .ass 文件: {', '.join(ass_files)}")
        if questionary.confirm("是否转换为 .srt？", default=False, style=STYLE).ask():
            convert_ass_files(folder, folder_name, ep_start, ep_end)

    generate_csv(folder, folder_name, ep_start, ep_end)


def run_line_tagger():
    print("\n── 自动标注角色 ──\n")
    ep        = ask("文件前缀（如 乐嫣01，对应 乐嫣01.csv + 乐嫣01.txt）：")
    role      = ask("目标角色标签：", "q")
    n         = ask("上下文窗口大小：", "20")
    min_score = ask("最低匹配分（0=宽松  1=严格）：", "1")

    from line_tagger import mark_by_anchor_window
    print()
    mark_by_anchor_window(
        csv_path          = f"{ep}.csv",
        txt_path          = f"{ep}.txt",
        out_path          = f"{ep}_marked.csv",
        target_label      = role,
        n                 = int(n),
        min_context_score = int(min_score),
    )


def run_subs_generator():
    print("\n── 生成台词本 / 字幕 ──\n")
    file_name = ask("文件名（对应 input-csv/<文件名>.csv）：")
    pattern   = ask("主要角色标注（如 qw，留空则跳过）：") or None

    import subsgen as sg
    print()
    sg.write_srt(file_name, pattern)
    sg.write_txt(file_name, pattern)


def run_audio_cutter():
    print("\n── 截取音频 ──\n")
    drama      = ask("剧名：")
    ep_start   = ask("开始集数：", "1")
    ep_end     = ask("结束集数：", ep_start)
    start_adj  = ask("起始时间偏移（秒，负数=提前）：", "-0.4")
    end_adj    = ask("结束时间偏移（秒，正数=延后）：", "0.4")
    artist     = ask("Artist 标签：", "lnlychee")

    from audio_cutter import srt_to_audio_segments
    print()
    srt_to_audio_segments(
        drama, int(ep_start), int(ep_end),
        float(start_adj), float(end_adj), artist
    )


def run_postprocess():
    print("\n── 后处理 ──\n")
    action = select("选择操作：", [
        "filter  — 按正则过滤台词文件",
        "reorder — 音频重新编号",
    ])

    if action.startswith("filter"):
        input_file  = ask("输入文件：")
        output_file = ask("输出文件：")
        pattern     = ask("正则表达式（如 乐嫣、【8?1】）：")
        from postprocess import filter_lines
        print()
        filter_lines(input_file, output_file, pattern)
    else:
        folder = ask("音频根文件夹：")
        from postprocess import reorder_mp3
        print()
        reorder_mp3(folder)


# ── 主菜单 ────────────────────────────────────────────────────────────────────

CHOICES = [
    ("1. 预处理字幕       srt/process.py",      run_process),
    ("2. 自动标注角色     line_tagger.py",       run_line_tagger),
    ("3. 生成台词本/字幕  subs_generator.py",    run_subs_generator),
    ("4. 截取音频         audio_cutter.py",      run_audio_cutter),
    ("5. 后处理           postprocess.py",       run_postprocess),
    ("── 退出", None),
]

LABELS   = [c[0] for c in CHOICES]
HANDLERS = {c[0]: c[1] for c in CHOICES}

def main():
    while True:
        clear()
        header()
        choice = select("请选择功能：", LABELS)

        if choice is None or HANDLERS[choice] is None:
            clear()
            break

        print()
        try:
            HANDLERS[choice]()
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"\n错误: {e}")

        input("\n按 Enter 返回菜单...")


if __name__ == "__main__":
    main()
