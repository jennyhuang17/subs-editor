import pandas as pd
import re
from pathlib import Path


def extract_episode(ep_value):
    """
    支持:
    1 -> 01
    EP01 -> 01
    ep1 -> 01
    Episode12 -> 12
    """
    ep_str = str(ep_value).strip()

    match = re.search(r'(\d+)', ep_str)
    if match:
        return match.group(1).zfill(2)

    return ep_str


def csv_to_txt(csv_file, txt_file):
    # 无表头读取
    df = pd.read_csv(csv_file, header=None)

    # 第3列是台词，第5列是集数
    text_col = 2
    episode_col = 4

    output_lines = []

    # 按集数分组（保持原顺序）
    current_ep = None

    for _, row in df.iterrows():
        episode = extract_episode(row[episode_col])
        subtitle = str(row[text_col]).strip()

        if not subtitle or subtitle.lower() == "nan":
            continue

        if episode != current_ep:
            if current_ep is not None:
                output_lines.append("")  # 集数之间空一行

            output_lines.append(episode)
            current_ep = episode

        output_lines.append(subtitle)

    with open(txt_file, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))

    print(f"输出完成: {txt_file}")


if __name__ == "__main__":
    csv_to_txt(
        csv_file="input-csv/长安.csv",
        txt_file="output-txt/长安.txt"
    )