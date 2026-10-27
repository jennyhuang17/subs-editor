import pandas as pd
from pathlib import Path


def csv_to_srt_by_episode(csv_file, output_dir="srt_output"):
    df = pd.read_csv(csv_file, header=None)

    Path(output_dir).mkdir(exist_ok=True)

    for episode, group in df.groupby(4):
        srt_file = Path(output_dir) / f"{episode}.srt"

        with open(srt_file, "w", encoding="utf-8") as f:
            for _, row in group.iterrows():
                f.write(f"{row[0]}\n")
                f.write(f"{row[1]}\n")
                f.write(f"{row[2]}\n\n")

        print(f"已生成: {srt_file}")


if __name__ == "__main__":
    csv_to_srt_by_episode("input-csv/长安.csv")