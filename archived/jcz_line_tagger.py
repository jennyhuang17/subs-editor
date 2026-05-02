import re
import pandas as pd
from collections import defaultdict


def normalize_text(s: str) -> str:
    """归一化：去空白和标点，仅保留中英文数字"""
    if s is None:
        return ""
    s = str(s)
    s = re.sub(r"\s+", "", s)
    s = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]+", "", s)
    return s


def should_ignore_line(line: str) -> bool:
    """
    忽略：
    1) EPxx 开头行，如 EP04 / ep01
    2) 数字-数字 开头行，如 4-01、12-3
    """
    line = line.strip()
    if not line:
        return True
    if re.match(r"(?i)^EP\d+\b", line):
        return True
    if re.match(r"^\d+\-\d+\b", line):
        return True
    return False


def parse_parenthetical_mention(line: str):
    """
    解析格式：
      （角色名：台词...）
    返回 (role_name, content_after_colon) 或 None

    兼容：
    - 全角括号（ ）
    - 半角括号 ( )
    - 全角冒号 ：
    - 半角冒号 :
    """
    s = line.strip()

    # 允许全角/半角括号包裹
    m = re.match(r"^[（(]\s*(.+?)\s*[）)]\s*$", s)
    if not m:
        return None
    inner = m.group(1)

    # 找到第一个冒号（全角或半角）
    if "：" in inner:
        parts = inner.split("：", 1)
    elif ":" in inner:
        parts = inner.split(":", 1)
    else:
        return None

    role = parts[0].strip()
    content = parts[1].strip()

    if not role or not content:
        return None

    return role, content


def load_txt_items(txt_path: str):
    """
    读取 txt，输出 items 列表：
    items = [{"tok": <normalized token>, "label": "1" 或 角色名}, ...]
    """
    items = []
    with open(txt_path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if should_ignore_line(line):
                continue

            mention = parse_parenthetical_mention(line)
            if mention:
                role, content = mention
                # 冒号后的内容按空白切 token
                parts = re.split(r"\s+", content)
                for p in parts:
                    p_norm = normalize_text(p)
                    if p_norm:
                        items.append({"tok": p_norm, "label": role})
                continue

            # 普通行：按空白切 token，标记为 "1"
            parts = re.split(r"\s+", line)
            for p in parts:
                p_norm = normalize_text(p)
                if p_norm:
                    items.append({"tok": p_norm, "label": "1"})

    return items


def build_csv_units(df: pd.DataFrame, dialogue_col="台词", max_concat_lines=3):
    """
    为了容忍 txt 的一个 token 覆盖 csv 连续多行（无空格拼接），
    构建 1~max_concat_lines 行拼接的 unit：
      unit: (start_row, end_row, normalized_text)
    """
    lines = df[dialogue_col].fillna("").astype(str).tolist()
    norm = [normalize_text(x) for x in lines]
    n = len(norm)

    units = []
    for k in range(1, max_concat_lines + 1):
        for i in range(n - k + 1):
            combined = "".join(norm[i:i + k])
            if combined:
                units.append((i, i + k - 1, combined))

    return norm, units


def index_units(units):
    """倒排索引：text -> [(start,end), ...]"""
    inv = defaultdict(list)
    for s, e, t in units:
        inv[t].append((s, e))
    return inv


def exists_near(inv, token, center_row, n):
    """token 是否在 center_row 的 ±n 行内出现"""
    if token not in inv:
        return False
    lo = center_row - n
    hi = center_row + n
    for s, e in inv[token]:
        if e >= lo and s <= hi:
            return True
    return False


def choose_best_candidate(cands, inv, tokens, t_idx, n, last_anchor):
    """
    候选选择：
    - 上下文打分：前1/2 token、后1/2 token 是否在 ±n 出现
    - 再偏向顺序（start >= last_anchor）
    """
    best = None
    best_score = -1
    best_penalty = float("inf")

    prev1 = tokens[t_idx - 1] if t_idx - 1 >= 0 else None
    prev2 = tokens[t_idx - 2] if t_idx - 2 >= 0 else None
    next1 = tokens[t_idx + 1] if t_idx + 1 < len(tokens) else None
    next2 = tokens[t_idx + 2] if t_idx + 2 < len(tokens) else None

    for s, e in cands:
        center = (s + e) // 2
        score = 0

        if prev1 and exists_near(inv, prev1, center, n): score += 1
        if prev2 and exists_near(inv, prev2, center, n): score += 1
        if next1 and exists_near(inv, next1, center, n): score += 1
        if next2 and exists_near(inv, next2, center, n): score += 1

        # 顺序惩罚：越不倒退越好
        penalty = 0 if s >= last_anchor else (last_anchor - s + 1)

        if (score > best_score) or (score == best_score and penalty < best_penalty):
            best_score = score
            best_penalty = penalty
            best = (s, e)

    return best, best_score


def merge_role_cell(old_val: str, new_label: str) -> str:
    """
    合并写入“角色”列的策略：
    - 如果 new_label 是具体角色名：优先级高于 "1"
    - 如果 old 是空：直接写 new
    - 如果 old 是 "1" 且 new 是角色名：覆盖为角色名
    - 如果 old 是角色名且 new 也是角色名且不同：用 '|' 追加
    - 如果 new 是 "1"：仅在 old 为空时写入
    """
    old = "" if pd.isna(old_val) else str(old_val).strip()
    new = str(new_label).strip()

    if not old:
        return new

    if new == "1":
        return old  # 已经有内容就不被 1 覆盖

    # new 是角色名
    if old == "1":
        return new

    # old 也是角色名：若不同则追加
    if old == new:
        return old
    # 去重追加
    parts = set(old.split("|"))
    parts.add(new)
    return "|".join(sorted(parts))


def mark_by_anchor_window(
    csv_path: str,
    txt_path: str,
    out_path: str,
    dialogue_col: str = "台词",
    role_col: str = "角色",
    n: int = 20,
    min_context_score: int = 1,
    max_concat_lines: int = 3,
):
    df = pd.read_csv(csv_path, encoding="utf-8-sig")

    if dialogue_col not in df.columns:
        raise ValueError(f"CSV缺少列：{dialogue_col}，现有列：{list(df.columns)}")
    if role_col not in df.columns:
        df[role_col] = ""

    items = load_txt_items(txt_path)  # [{"tok":..., "label":...}]
    tokens = [it["tok"] for it in items]

    _, units = build_csv_units(df, dialogue_col=dialogue_col, max_concat_lines=max_concat_lines)
    inv = index_units(units)

    last_anchor = -1
    matched_items = 0
    marked_rows = 0

    for i, it in enumerate(items):
        tok = it["tok"]
        label = it["label"]

        cands = inv.get(tok, [])
        if not cands:
            continue

        best, score = choose_best_candidate(cands, inv, tokens, i, n=n, last_anchor=last_anchor)
        if best is None:
            continue
        if score < min_context_score:
            continue

        s, e = best
        for r in range(s, e + 1):
            # 只对非空台词行写标记（避免把空行也染色）
            if normalize_text(df.at[r, dialogue_col]):
                df.at[r, role_col] = merge_role_cell(df.at[r, role_col], label)
                marked_rows += 1

        last_anchor = max(last_anchor, e)
        matched_items += 1

    df.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"输出文件: {out_path}")
    print(f"txt token总数: {len(items)}")
    print(f"成功匹配token数: {matched_items}")
    print(f"写入标记次数(行级): {marked_rows}")


if __name__ == "__main__":
    ep = "10"
    csv_path = f"{ep}.csv"
    txt_path = f"{ep}.txt"
    out_path = f"{ep}_marked.csv"

    mark_by_anchor_window(
        csv_path=csv_path,
        txt_path=txt_path,
        out_path=out_path,
        dialogue_col="台词",
        role_col="角色",
        n=20,
        min_context_score=0,   # 漏太多可改 0
        max_concat_lines=5,    # 若 txt token 常跨多行，可加到 4~5
    )