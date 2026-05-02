import subprocess
from pathlib import Path
from typing import Optional, List, Tuple

def batch_write_mp4_title_desc_from_filename(
    folder: str,
    title_suffix: str,                    # 你指定要拼接的那段文本
    description: Optional[str] = None,
    keywords: Optional[List[str]] = None,
    exts: Tuple[str, ...] = (".mp4", ".m4v", ".mov"),
    recursive: bool = True,
    dry_run: bool = False,
) -> None:
    folder_path = Path(folder)
    pattern = "**/*" if recursive else "*"
    files = [p for p in folder_path.glob(pattern) if p.suffix.lower() in exts]

    kw_semicolon = ";".join(keywords) if keywords else None

    for p in files:
        base_name = p.stem  # 文件名（不含扩展名）
        title_value = f"{base_name}{title_suffix}"

        cmd = ["exiftool", "-overwrite_original"]

        # QuickTime Player 可见：Title
        cmd.append(f"-QuickTime:Title={title_value}")

        # 你说可见的 description：ItemList:Description（可选）
        if description is not None:
            cmd.append(f"-ItemList:Description={description}")
            cmd.append(f"-XMP-dc:Description={description}")

        # keywords（可选）
        if kw_semicolon is not None:
            cmd.append(f"-ItemList:Keywords={kw_semicolon}")
            cmd.append(f"-XMP-dc:Subject={kw_semicolon}")

        cmd.append(str(p))

        if dry_run:
            print(" ".join(cmd))
            continue

        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode == 0:
            print(f"[OK] {p.name} -> Title='{title_value}'")
        else:
            print(f"[FAIL] {p}\n{r.stderr}")

if __name__ == "__main__":
    batch_write_mp4_title_desc_from_filename(
        folder="01",
        title_suffix="© 2026 wqncwzxqt",
        description="© 2026 wqncwzxqt",
        keywords=["© 2026 wqncwzxqt"],
        recursive=True,
        dry_run=False,   # 先改 True 预演也行
    )