# Changelog

## 2026-05-03

### `srt/process.py`

**删除**
- 移除 `rename_files` 函数，不再自动修改 SRT 文件名

**修复**
- `DIALOGUE_RE` 原要求 Actor/Effect 字段为空（`,,`），遇到有角色名的 ASS 文件时零匹配，静默生成空 SRT；改为 `[^,]*` 兼容任意字段内容
- 新增 `ASS_OVERRIDE_RE`，转换时剥除字幕中的 `{...}` 特效标签
- SRT 查找改用精确集数匹配 `(?<!\d){epno}(?!\d)`，避免 ep05 被误匹配为 ep15；找不到对应集数时报错退出

**新增**
- 启动时检测目录中的 `.ass` 文件，存在则提示 `是否转换为 .srt？[y/N]`，用户确认后才执行转换

### `menu.py`

**修改**
- 移除 `rename_files` 的 import 和调用
- 预处理字幕步骤改为：检测 `.ass` 文件 → 用 `questionary.confirm` 询问是否转换 → 确认后调用 `convert_ass_files` → 调用 `generate_csv`
