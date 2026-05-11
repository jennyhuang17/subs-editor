"""
Lightweight local web UI for generating dialogue TXT and role-marked SRT files.

Run:
    python web_app.py
"""

from __future__ import annotations

import os
import re
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", tempfile.mkdtemp(prefix="subs_editor_mpl_"))
import pandas as pd


COLUMNS = ["编号", "时间戳", "台词", "角色", "集数"]
HEADER_MARKERS = set(COLUMNS)


@dataclass
class FormatConfig:
    output_name: str
    main_markers: set[str]
    txt_main_prefix: str
    txt_other_prefix: str
    txt_line_separator: str
    txt_split_separator: str
    txt_episode_header: str
    clean_txt_line_spaces: bool
    srt_main_prefix: str
    srt_other_prefix: str


def _uploaded_path(file_obj) -> str | None:
    if file_obj is None:
        return None
    if isinstance(file_obj, str):
        return file_obj
    return getattr(file_obj, "name", None)


def infer_output_name(file_obj) -> str:
    path = _uploaded_path(file_obj)
    if not path:
        return ""
    return Path(path).stem


def _read_csv(path: str) -> pd.DataFrame:
    raw = pd.read_csv(path, header=None, dtype=str, keep_default_na=False)
    if raw.empty:
        raise ValueError("CSV 是空的。")

    first_row = [str(value).strip() for value in raw.iloc[0].tolist()]
    has_header = HEADER_MARKERS.issubset(set(first_row))

    if has_header:
        df = pd.read_csv(path, dtype=str, keep_default_na=False)
    else:
        if raw.shape[1] < len(COLUMNS):
            raise ValueError("CSV 至少需要 5 列：编号、时间戳、台词、角色、集数。")
        df = raw.iloc[:, : len(COLUMNS)].copy()
        df.columns = COLUMNS

    missing = [column for column in COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"CSV 缺少列：{', '.join(missing)}")

    df = df[COLUMNS].copy()
    for column in COLUMNS:
        df[column] = df[column].astype(str).fillna("").str.strip()
    return df


def _parse_episode_filter(value: str) -> set[str] | None:
    value = (value or "").strip()
    if not value:
        return None

    episodes: set[str] = set()
    for part in re.split(r"[,，\s]+", value):
        if not part:
            continue
        match = re.fullmatch(r"(?:EP)?(\d+)\s*[-~至]\s*(?:EP)?(\d+)", part, re.I)
        if match:
            start, end = int(match.group(1)), int(match.group(2))
            if start > end:
                start, end = end, start
            episodes.update(f"EP{i:02d}" for i in range(start, end + 1))
            continue

        match = re.fullmatch(r"(?:EP)?(\d+)", part, re.I)
        if match:
            episodes.add(f"EP{int(match.group(1)):02d}")
            continue

        episodes.add(part.upper() if part.upper().startswith("EP") else part)

    return episodes


def _parse_markers(value: str) -> set[str]:
    return {item for item in re.split(r"[,，\s]+", value.strip()) if item}


def _safe_name(value: str) -> str:
    value = (value or "").strip()
    value = re.sub(r'[\\/:*?"<>|]+', "-", value)
    value = value.strip(" .")
    return value or "subs-output"


def _is_main_role(role: str, markers: set[str]) -> bool:
    if not markers:
        return False
    if role in markers:
        return True
    return _is_split_main_role(role) and role[1] in markers


def _is_split_main_role(role: str) -> bool:
    return len(role) >= 2 and role.startswith(("n", "9"))


def _display_role_for_txt(role: str) -> str:
    if _is_split_main_role(role):
        return role[1:]
    return role


def _format_prefix(template: str, role: str) -> str:
    return template.format(role=role)


def _line_text(text: str, clean_spaces: bool) -> str:
    if clean_spaces:
        return re.sub(r"\s+", "", text)
    return text.strip()


def _index_value(value: str) -> int | None:
    try:
        return int(float(value))
    except ValueError:
        return None


def _split_timestamp(value: str) -> tuple[str, str]:
    if " --> " not in value:
        raise ValueError(f"时间戳格式不正确：{value}")
    start_time, end_time = value.split(" --> ", 1)
    return start_time, end_time


def _same_group(previous: pd.Series, current: pd.Series) -> bool:
    previous_index = _index_value(previous["编号"])
    current_index = _index_value(current["编号"])
    if previous_index is not None and current_index is not None:
        consecutive = current_index - previous_index == 1
    else:
        consecutive = True
    return previous["角色"] == current["角色"] and consecutive


def _filter_rows(df: pd.DataFrame, episodes: str, role_nonempty_only: bool) -> pd.DataFrame:
    filtered = df.copy()
    episode_filter = _parse_episode_filter(episodes)
    if episode_filter:
        filtered = filtered[filtered["集数"].str.upper().isin(episode_filter)]
    if role_nonempty_only:
        filtered = filtered[filtered["角色"].str.strip() != ""]
    return filtered.reset_index(drop=True)


def _generate_txt(df: pd.DataFrame, config: FormatConfig) -> str:
    parts: list[str] = []
    for episode, episode_rows in df.groupby("集数", sort=False):
        if config.txt_episode_header:
            parts.append(config.txt_episode_header.format(episode=episode, ep=episode[-2:]))
            parts.append("\n")

        previous = None
        for _, row in episode_rows.iterrows():
            role = row["角色"]
            display_role = _display_role_for_txt(role)
            prefix = (
                config.txt_main_prefix
                if _is_main_role(role, config.main_markers)
                else _format_prefix(config.txt_other_prefix, display_role)
            )
            text = _line_text(row["台词"], config.clean_txt_line_spaces)

            if previous is None:
                parts.extend([prefix, text])
            elif _same_group(previous, row):
                parts.extend([config.txt_line_separator, text])
            else:
                if config.txt_split_separator and _is_split_main_role(role):
                    parts.extend(["\n\n", config.txt_split_separator, "\n", prefix, text])
                else:
                    parts.extend(["\n", prefix, text])
            previous = row

        parts.append("\n\n")
    return "".join(parts).rstrip() + "\n"


def _generate_srt_blocks(episode_rows: pd.DataFrame, config: FormatConfig) -> str:
    blocks: list[tuple[str, str, str]] = []
    current_lines: list[str] = []
    first_time = ""
    previous = None

    for _, row in episode_rows.iterrows():
        role = row["角色"]
        prefix = (
            config.srt_main_prefix
            if _is_main_role(role, config.main_markers)
            else _format_prefix(config.srt_other_prefix, role)
        )
        text = f"{prefix}{row['台词'].strip()}"

        if previous is None:
            first_time = row["时间戳"]
            current_lines = [text]
        elif _same_group(previous, row):
            current_lines.append(row["台词"].strip())
        else:
            start_time, _ = _split_timestamp(first_time)
            _, end_time = _split_timestamp(previous["时间戳"])
            blocks.append((start_time, end_time, " ".join(current_lines)))
            first_time = row["时间戳"]
            current_lines = [text]
        previous = row

    if previous is not None:
        start_time, _ = _split_timestamp(first_time)
        _, end_time = _split_timestamp(previous["时间戳"])
        blocks.append((start_time, end_time, " ".join(current_lines)))

    output: list[str] = []
    for index, (start_time, end_time, text) in enumerate(blocks, start=1):
        output.extend([str(index), "\n", f"{start_time} --> {end_time}", "\n", text, "\n\n"])
    return "".join(output)


def _write_outputs(df: pd.DataFrame, config: FormatConfig) -> tuple[str, str]:
    output_dir = Path(tempfile.mkdtemp(prefix="subs_editor_"))
    txt_path = output_dir / f"{config.output_name}.txt"
    zip_path = output_dir / f"{config.output_name}-srt.zip"

    txt_path.write_text(_generate_txt(df, config), encoding="utf-8")

    srt_root = output_dir / config.output_name
    srt_root.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for episode, episode_rows in df.groupby("集数", sort=False):
            ep_suffix = episode[-2:] if len(episode) >= 2 else episode
            srt_path = srt_root / f"{config.output_name}{ep_suffix}.srt"
            srt_path.write_text(_generate_srt_blocks(episode_rows, config), encoding="utf-8")
            archive.write(srt_path, arcname=f"{config.output_name}/{srt_path.name}")

    return str(txt_path), str(zip_path)


def preview_csv(file_obj, episodes, role_nonempty_only):
    path = _uploaded_path(file_obj)
    if not path:
        return pd.DataFrame(columns=COLUMNS), "请先上传 CSV。"

    try:
        df = _read_csv(path)
        filtered = _filter_rows(df, episodes, role_nonempty_only)
    except Exception as exc:
        return pd.DataFrame(columns=COLUMNS), f"读取失败：{exc}"

    summary = (
        f"原始 {len(df)} 行，筛选后 {len(filtered)} 行；"
        f"集数：{', '.join(filtered['集数'].drop_duplicates().tolist()) or '无'}。"
    )
    return filtered.head(30), summary


def generate_files(
    file_obj,
    output_name,
    episodes,
    role_nonempty_only,
    main_markers,
    txt_main_prefix,
    txt_other_prefix,
    txt_line_separator,
    txt_split_separator,
    txt_episode_header,
    clean_txt_line_spaces,
    srt_main_prefix,
    srt_other_prefix,
):
    path = _uploaded_path(file_obj)
    if not path:
        raise ValueError("请先上传 CSV。")

    df = _filter_rows(_read_csv(path), episodes, role_nonempty_only)
    if df.empty:
        raise ValueError("筛选后没有可生成的台词行。")

    safe_output_name = _safe_name(output_name or Path(path).stem)

    config = FormatConfig(
        output_name=safe_output_name,
        main_markers=_parse_markers(main_markers),
        txt_main_prefix=txt_main_prefix,
        txt_other_prefix=txt_other_prefix,
        txt_line_separator=txt_line_separator,
        txt_split_separator=txt_split_separator,
        txt_episode_header=txt_episode_header,
        clean_txt_line_spaces=clean_txt_line_spaces,
        srt_main_prefix=srt_main_prefix,
        srt_other_prefix=srt_other_prefix,
    )
    txt_path, zip_path = _write_outputs(df, config)
    preview = _generate_txt(df, config)
    summary = (
        f"已生成 {len(df)} 行。请检查预览后，用下载按钮手动保存 TXT / SRT ZIP。"
    )
    return txt_path, zip_path, preview, summary


def create_demo():
    import gradio as gr

    with gr.Blocks(title="subs-editor web") as demo:
        gr.Markdown("# subs-editor")
        gr.Markdown("上传 CSV，筛选角色非空台词，生成台词本和按集拆分的 SRT。")

        with gr.Row():
            csv_file = gr.File(label="CSV 文件", file_types=[".csv"])
            with gr.Column():
                output_name = gr.Textbox(label="输出名称", placeholder="例如 山河枕11-15")
                episodes = gr.Textbox(label="集数筛选", placeholder="留空为全部；例如 11-15 或 EP11,EP12")
                role_nonempty_only = gr.Checkbox(label="只处理角色非空行", value=True)
                main_markers = gr.Textbox(label="主角 marker", value="q e", placeholder="例如 q e")

        with gr.Accordion("高级设置", open=False):
            with gr.Row():
                txt_main_prefix = gr.Textbox(label="台词本：主角前缀", value="- ")
                txt_other_prefix = gr.Textbox(label="台词本：其他角色前缀模板", value="【{role}】")
            with gr.Row():
                txt_line_separator = gr.Textbox(label="台词本：连续台词连接符", value=" ")
                txt_split_separator = gr.Textbox(label="台词本：n/9 切换分隔符", value="❖")
            txt_episode_header = gr.Textbox(label="台词本：每集标题模板", value="{ep}")
            clean_txt_line_spaces = gr.Checkbox(label="台词本：清理每句台词内部空格", value=True)
            with gr.Row():
                srt_main_prefix = gr.Textbox(label="SRT：主角前缀", value="")
                srt_other_prefix = gr.Textbox(label="SRT：其他角色前缀模板", value="【{role}】")

        with gr.Row():
            preview_button = gr.Button("预览 CSV")
            generate_button = gr.Button("生成 TXT / SRT", variant="primary")

        status = gr.Textbox(label="状态", lines=2, interactive=False)
        preview_table = gr.Dataframe(label="筛选预览", headers=COLUMNS, interactive=False)
        txt_preview = gr.Textbox(label="台词本预览", lines=16, interactive=False)

        with gr.Row():
            txt_download = gr.DownloadButton(label="下载台词本 TXT", value=None)
            srt_download = gr.DownloadButton(label="下载 SRT ZIP", value=None)

        preview_button.click(
            preview_csv,
            inputs=[csv_file, episodes, role_nonempty_only],
            outputs=[preview_table, status],
        )
        csv_file.change(
            infer_output_name,
            inputs=[csv_file],
            outputs=[output_name],
        )
        generate_button.click(
            generate_files,
            inputs=[
                csv_file,
                output_name,
                episodes,
                role_nonempty_only,
                main_markers,
                txt_main_prefix,
                txt_other_prefix,
                txt_line_separator,
                txt_split_separator,
                txt_episode_header,
                clean_txt_line_spaces,
                srt_main_prefix,
                srt_other_prefix,
            ],
            outputs=[txt_download, srt_download, txt_preview, status],
        )

    return demo


if __name__ == "__main__":
    os.environ.setdefault("XDG_CACHE_HOME", tempfile.mkdtemp(prefix="subs_editor_cache_"))
    demo = create_demo()
    demo.launch(server_name="127.0.0.1", server_port=7860)
