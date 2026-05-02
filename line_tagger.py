"""
根据已有台词本（txt）自动标记 CSV 中的角色列。

支持两种 txt 格式：
  - 纯台词模式：txt 里只有目标角色的台词，所有匹配行标记为 --role 值（默认 "q"）
  - 混合模式：txt 里包含目标角色台词（普通行）和第三方角色台词（括号格式）
              括号格式：（角色名：台词内容）
              普通行标记为 --role，括号行标记为括号内的角色名

用法：
  python line_tagger.py <集数/文件前缀> [--role 角色名] [--n 窗口大小] [--min_score 最低分]

示例：
  # 纯台词模式（txt 只有目标角色）
  python line_tagger.py 乐嫣01 --role 乐嫣

  # 混合模式（txt 含第三方括号行）
  python line_tagger.py 10 --role 1

输入文件：<ep>.csv  +  <ep>.txt
输出文件：<ep>_marked.csv
"""

import argparse
import re
import pandas as pd
from collections import defaultdict


# ── 文本归一化 ────────────────────────────────────────────────────────────────

def normalize_text(s: str) -> str:
    if s is None:
        return ""
    s = str(s)
    s = re.sub(r"\s+", "", s)
    s = re.sub(r"[^0-9A-Za-z一-鿿]+", "", s)
    return s


def should_ignore_line(line: str) -> bool:
    line = line.strip()
    if not line:
        return True
    if re.match(r"(?i)^EP\d+\b", line):   # EPxx 集数行
        return True
    if re.match(r"^\d+\-\d+\b", line):    # 4-01 编号行
        return True
    return False


# ── 解析括号格式第三方台词：（角色名：台词） ──────────────────────────────────

def parse_parenthetical(line: str):
    """返回 (role_name, content) 或 None"""
    m = re.match(r"^[（(]\s*(.+?)\s*[）)]\s*$", line.strip())
    if not m:
        return None
    inner = m.group(1)
    if "：" in inner:
        parts = inner.split("：", 1)
    elif ":" in inner:
        parts = inner.split(":", 1)
    else:
        return None
    role, content = parts[0].strip(), parts[1].strip()
    return (role, content) if role and content else None


# ── 读取 txt，输出 token 列表（含标签）────────────────────────────────────────

def load_txt_items(txt_path: str, target_label: str):
    """
    返回 [{"tok": <归一化文本>, "label": <角色标签>}, ...]
    普通行 → target_label；括号行 → 括号内角色名
    """
    items = []
    with open(txt_path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if should_ignore_line(line):
                continue
            mention = parse_parenthetical(line)
            if mention:
                role, content = mention
                for p in re.split(r"\s+", content):
                    tok = normalize_text(p)
                    if tok:
                        items.append({"tok": tok, "label": role})
            else:
                for p in re.split(r"\s+", line):
                    tok = normalize_text(p)
                    if tok:
                        items.append({"tok": tok, "label": target_label})
    return items


# ── 构建 CSV 匹配单元（支持 1~max_concat 行拼接）────────────────────────────

def build_csv_units(df: pd.DataFrame, dialogue_col="台词", max_concat=3):
    lines = df[dialogue_col].fillna("").astype(str).tolist()
    norm = [normalize_text(x) for x in lines]
    n = len(norm)
    units = []
    for k in range(1, max_concat + 1):
        for i in range(n - k + 1):
            combined = "".join(norm[i:i + k])
            if combined:
                units.append((i, i + k - 1, combined))
    return norm, units


def index_units(units):
    inv = defaultdict(list)
    for s, e, t in units:
        inv[t].append((s, e))
    return inv


# ── 上下文打分 + 最优候选选择 ────────────────────────────────────────────────

def exists_near(inv, token, center, n):
    if token not in inv:
        return False
    lo, hi = center - n, center + n
    return any(e >= lo and s <= hi for s, e in inv[token])


def choose_best(cands, inv, tokens, t_idx, n, last_anchor):
    prev = [tokens[t_idx - i] if t_idx - i >= 0 else None for i in (1, 2)]
    nxt  = [tokens[t_idx + i] if t_idx + i < len(tokens) else None for i in (1, 2)]
    context = [x for x in prev + nxt if x]

    best, best_score, best_penalty = None, -1, float("inf")
    for s, e in cands:
        center  = (s + e) // 2
        score   = sum(1 for c in context if exists_near(inv, c, center, n))
        penalty = 0 if s >= last_anchor else (last_anchor - s + 1)
        if score > best_score or (score == best_score and penalty < best_penalty):
            best, best_score, best_penalty = (s, e), score, penalty
    return best, best_score


# ── 合并角色列（多标签时用 | 拼接）──────────────────────────────────────────

def merge_role(old_val, new_label: str, target_label: str) -> str:
    old = "" if pd.isna(old_val) else str(old_val).strip()
    new = new_label.strip()
    if not old:
        return new
    if new == target_label:
        return old                   # 已有具体角色名，不被目标标签覆盖
    if old == target_label:
        return new                   # 具体角色名优先于目标标签
    if old == new:
        return old
    parts = set(old.split("|"))
    parts.add(new)
    return "|".join(sorted(parts))


# ── 主函数 ────────────────────────────────────────────────────────────────────

def mark_by_anchor_window(csv_path, txt_path, out_path,
                           target_label="q", dialogue_col="台词", role_col="角色",
                           n=20, min_context_score=1, max_concat=3):
    df = pd.read_csv(csv_path, encoding="utf-8-sig")
    if dialogue_col not in df.columns:
        raise ValueError(f"CSV 缺少列：{dialogue_col}")
    if role_col not in df.columns:
        df[role_col] = ""
    df[role_col] = df[role_col].astype("string").fillna("")

    items  = load_txt_items(txt_path, target_label)
    tokens = [it["tok"] for it in items]
    _, units = build_csv_units(df, dialogue_col=dialogue_col, max_concat=max_concat)
    inv = index_units(units)

    last_anchor   = -1
    matched_items = 0
    marked_rows   = 0

    for i, it in enumerate(items):
        tok, label = it["tok"], it["label"]
        cands = inv.get(tok, [])
        if not cands:
            continue
        best, score = choose_best(cands, inv, tokens, i, n=n, last_anchor=last_anchor)
        if best is None or score < min_context_score:
            continue
        s, e = best
        for r in range(s, e + 1):
            if normalize_text(df.at[r, dialogue_col]):
                df.at[r, role_col] = merge_role(df.at[r, role_col], label, target_label)
                marked_rows += 1
        last_anchor = max(last_anchor, e)
        matched_items += 1

    df.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"输出: {out_path}")
    print(f"txt token 总数: {len(items)}  |  匹配成功: {matched_items}  |  标记行数: {marked_rows}")


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="根据台词本 txt 自动标记 CSV 角色列",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python line_tagger.py 乐嫣01 --role 乐嫣          # 纯台词模式
  python line_tagger.py 10 --role 1                 # 混合模式（txt 含括号行）
  python line_tagger.py 赴山海05 --role q --n 30    # 加大上下文窗口
        """
    )
    parser.add_argument("ep", help="集数/文件前缀，读取 <ep>.csv 和 <ep>.txt")
    parser.add_argument("--role",      default="q",  help="目标角色标签（默认 q）")
    parser.add_argument("--n",         type=int, default=20,  help="上下文窗口大小（默认 20）")
    parser.add_argument("--min_score", type=int, default=1,   help="最低上下文匹配分（默认 1，改 0 更宽松）")
    parser.add_argument("--max_concat",type=int, default=3,   help="最多拼接几行做匹配（默认 3）")
    args = parser.parse_args()

    mark_by_anchor_window(
        csv_path   = f"{args.ep}.csv",
        txt_path   = f"{args.ep}.txt",
        out_path   = f"{args.ep}_marked.csv",
        target_label     = args.role,
        n                = args.n,
        min_context_score= args.min_score,
        max_concat       = args.max_concat,
    )
