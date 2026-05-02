# subs-editor

字幕处理 → 角色标注 → 生成台词本/字幕 → 截取音频的工具链。

---

## 完整流程

```
原始字幕（ass/srt）
      ↓  srt/process.py
   CSV 文件（角色列为空）
      ↓  line_tagger.py（可选，自动预标注）
      ↓  手动在 Excel/Numbers 填写角色列
      ↓  保存到 input-csv/
      ↓  subs_generator.py
  台词本（txt）+ 带角色字幕（srt）
      ↓  降噪音频保存到 input-audio/
      ↓  audio_cutter.py
  按台词切割的音频片段（已自动打 artist 标签）
```

---

## 主流程脚本

### `srt/process.py` — 字幕预处理

把下载的字幕转换成 CSV，供后续标注。  
自动完成：**重命名 → ass 转 srt → 生成 CSV**，三步一条命令。

```bash
python srt/process.py <文件夹> <开始集数> <结束集数>
```

**示例**
```bash
# 文件夹内有乱码命名的 .ass 文件，处理第 1-40 集
python srt/process.py 暗河传 1 40

# 文件夹内已经是 .srt 文件，只生成 CSV
python srt/process.py 山河枕 5 10
```

**输出**
- 重命名后的文件：`暗河传01.ass`、`暗河传01.srt` …
- CSV：`暗河传/台词本01-40.csv`

> 重命名按文件名字母排序后依次分配集数。如果下载文件顺序有问题，手动调整一下再跑。

---

### `line_tagger.py` — 自动预标注角色（可选）

有其他来源的台词本时，用它把角色列预先填好，再去人工校对。  
支持**纯台词模式**和**混合模式**，用 `--role` 参数区分。

```bash
python line_tagger.py <集数/文件前缀> [--role 角色名] [--n 窗口] [--min_score 分数]
```

**输入文件**：`<ep>.csv` + `<ep>.txt`  
**输出文件**：`<ep>_marked.csv`

#### 纯台词模式
txt 里只有目标角色的台词，所有匹配行标记为 `--role` 值。

```bash
# 乐嫣01.csv + 乐嫣01.txt → 乐嫣01_marked.csv，匹配行标记为"乐嫣"
python line_tagger.py 乐嫣01 --role 乐嫣
```

#### 混合模式
txt 里同时包含目标角色（普通行）和第三方角色（括号格式）。  
括号格式：`（角色名：台词内容）`

```bash
# 10.csv + 10.txt → 10_marked.csv
# 普通行标记为"1"，括号行标记为括号内角色名
python line_tagger.py 10 --role 1
```

txt 示例（混合模式）：
```
你今日气色不错
（慕声：是吗，我觉得还好）
改日再叙
（慕声：好，一言为定）
```

#### 参数说明
| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--role` | `q` | 目标角色标签 |
| `--n` | `20` | 上下文窗口大小（行数），越大越准但越慢 |
| `--min_score` | `1` | 最低上下文匹配分，改成 `0` 更宽松（可能误标） |
| `--max_concat` | `3` | 最多拼接几行做匹配，txt 分行较碎时可调大 |

---

### `subs_generator.py` — 生成台词本和字幕

读取 `input-csv/<文件名>.csv`，生成：
- `output-txt/<文件名>.txt`：按角色分组的台词本
- `output-srt/<文件名>/`：带角色标注的 srt 字幕

```bash
python subs_generator.py <文件名>
```

**示例**
```bash
python subs_generator.py 乐嫣        # 读取 input-csv/乐嫣.csv
python subs_generator.py 山河枕01-10  # 读取 input-csv/山河枕01-10.csv
```

---

### `audio_cutter.py` — 截取音频并标记 artist

按 srt 时间戳从降噪音频中截取每句台词，截取完后自动给所有片段打 artist 元数据标签。

**使用前**：修改文件底部的配置区：

```python
drama             = "水龙吟"     # 剧名，与文件夹名一致
episode_start     = 35
episode_end       = 40
start_time_adjust = -0.4         # 起始时间偏移（秒），负数 = 提前
end_time_adjust   =  0.4         # 结束时间偏移（秒），正数 = 延后
artist_name       = "lnlychee"   # 写入 mp3 元数据的 artist 字段
```

**目录结构要求**
```
output-srt/<剧名>/<剧名><集数>.srt
input-audio/<剧名><集数>.mp3
output-audio/<剧名><集数>/   ← 输出到这里
```

```bash
python audio_cutter.py
```

---

## 偶尔使用

### `postprocess.py` — 音频后处理

整合了两个操作，经常一起用。

#### filter — 按正则过滤台词文件

多角色台词混合输出时，从整体 txt 里提取单个角色的部分。

```bash
python postprocess.py filter <输入文件> <输出文件> <正则表达式>
```

**示例**
```bash
# 从山河枕全集台词本里提取编号含【1】或【81】的行（某角色标注符）
python postprocess.py filter output-txt/山河枕.txt output-txt/楚瑜.txt "【8?1】"

# 提取包含"慕声"的行
python postprocess.py filter 全剧.txt 慕声.txt "慕声"
```

#### reorder — 音频文件重新编号

手动整理出某角色的音频文件后，重新生成连续序号。

```bash
python postprocess.py reorder <音频根文件夹>
```

**示例**
```bash
# 整理后的乐嫣音频重新编号（处理所有子文件夹）
python postprocess.py reorder output-audio/乐嫣

# 典型场景：先 filter 筛行 → 手动挑选音频 → reorder 重编号
```

原命名 `01-020 台词内容.mp3` → 重编后 `01-003 台词内容.mp3`

---

## 存档脚本

以下脚本为一次性或低频使用，保存在 `archived/` 备查。

| 文件 | 功能 | 备注 |
|------|------|------|
| `archived/artist_tagger.py` | 修改 mp3 文件的 artist 元数据 | 已整合进 audio_cutter.py |
| `archived/line_filter.py` | 按正则过滤 txt 行 | 已整合进 postprocess.py filter |
| `archived/reorder-file.py` | mp3 重新编号 | 已整合进 postprocess.py reorder |
| `archived/line_merger.py` | 合并 srt 中的多行字幕为单行 | 偶尔用于预处理特殊字幕 |
| `archived/srt_filter.py` | 交互式按角色提取 srt 片段 | 被 subs_generator.py 取代 |
| `archived/srt_to_txt.py` | 将 srt 文件夹转为单个 txt | 按需使用 |
| `archived/tcb.py` | 交互式提取单角色 srt | 被 subs_generator.py 取代 |
| `archived/get-filename.py` | 导出 mp3 文件名列表到 txt | 按需使用 |
| `archived/test.py` | 同上（另一版本） | 按需使用 |

### `srt/` 存档

| 文件 | 功能 | 备注 |
|------|------|------|
| `srt/youku_asstosrt.py` | youku .ass 转 .srt | 已整合进 srt/process.py |
| `srt/change_fn.py` | 截断文件名至前 4 个字符 | 一次性工具，硬编码 |
| `srt/char-marker.py` | 从 `角色：台词` 格式自动标记 CSV | 一次性工具，硬编码 |
| `srt/xml2srt.py` | 特定 XML 格式转 srt | 偶尔用于非常规字幕来源 |

---

## 参考

- [如何从 mkv 视频中提取字幕](docs/how-to-extract-srt.md)
