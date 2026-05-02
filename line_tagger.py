import re, sys
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
    1) EPxx 开头行，如 EP04
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


def load_txt_tokens(txt_path: str):
    """按空格/换行拆 token"""
    tokens = []
    with open(txt_path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if should_ignore_line(line):
                continue
            parts = re.split(r"\s+", line)
            for p in parts:
                p_norm = normalize_text(p)
                if p_norm:
                    tokens.append(p_norm)
    return tokens


def build_csv_units(df: pd.DataFrame, dialogue_col="台词"):
    """
    把每一行台词做归一化，并额外构建“2行拼接”“3行拼接”用于容忍
    txt 一个 token 覆盖 csv 连续多行 的情况。
    """
    lines = df[dialogue_col].fillna("").astype(str).tolist()
    norm = [normalize_text(x) for x in lines]
    n = len(norm)

    units = []
    # 1行
    for i in range(n):
        if norm[i]:
            units.append((i, i, norm[i]))
    # 2行拼接
    for i in range(n - 1):
        c = norm[i] + norm[i + 1]
        if c:
            units.append((i, i + 1, c))
    # 3行拼接
    for i in range(n - 2):
        c = norm[i] + norm[i + 1] + norm[i + 2]
        if c:
            units.append((i, i + 2, c))

    return norm, units


def index_units(units):
    """
    建倒排索引：text -> [(start,end), ...]
    """
    inv = defaultdict(list)
    for s, e, t in units:
        inv[t].append((s, e))
    return inv


def exists_near(inv, token, center_row, n):
    """
    token 是否在 center_row 的 ±n 行内出现（按 unit 的 start/end 判断）
    """
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
    在候选中选最优：
    - 先做上下文打分：前1/2 token、后1/2 token 是否在 ±n 出现
    - 再偏向时间顺序（start >= last_anchor）
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


def mark_by_anchor_window(
    csv_path: str,
    txt_path: str,
    out_path: str,
    dialogue_col: str = "台词",
    role_col: str = "角色",
    n: int = 20,
    min_context_score: int = 1,   # 至少命中1个上下文锚点才标记；可调成0更宽松
):
    df = pd.read_csv(csv_path, encoding="utf-8-sig")

    # 确保角色列是字符串类型，避免 float <-> str 的 dtype 警告
    df[role_col] = df[role_col].astype("string")
    df[role_col] = df[role_col].fillna("")  # 保持空字符串

    if dialogue_col not in df.columns:
        raise ValueError(f"CSV缺少列：{dialogue_col}，现有列：{list(df.columns)}")
    if role_col not in df.columns:
        df[role_col] = ""

    tokens = load_txt_tokens(txt_path)
    _, units = build_csv_units(df, dialogue_col=dialogue_col)
    inv = index_units(units)

    marked_rows = set()
    last_anchor = -1
    matched_tokens = 0

    for i, tok in enumerate(tokens):
        cands = inv.get(tok, [])
        if not cands:
            # 这块找不到，跳过
            continue

        best, score = choose_best_candidate(cands, inv, tokens, i, n=n, last_anchor=last_anchor)
        if best is None:
            continue

        # 上下文校验不过就跳过（你要求“没有找到就跳过，查下一块”）
        if score < min_context_score:
            continue

        s, e = best
        for r in range(s, e + 1):
            marked_rows.add(r)

        last_anchor = max(last_anchor, e)
        matched_tokens += 1

    for r in marked_rows:
        df.at[r, role_col] = "q"

    df.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"输出文件: {out_path}")
    print(f"txt token总数: {len(tokens)}")
    print(f"成功匹配token数: {matched_tokens}")
    print(f"被标记csv行数: {len(marked_rows)}")


if __name__ == "__main__":
    ep = sys.argv[1]
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
        min_context_score=1,  # 如果还漏很多，可改成0
    )
