---
name: jianying_material_prep
description: 为《长生不死》的预告片、短视频和解说视频整理可喂给 jianying-editor 的标准输入素材。适用于把现有分镜、字幕、口播、BGM 和媒体文件收口为 asset manifest、storyboard、SRT 和 voiceover 文本，但不直接执行剪映自动化。
---

# Jianying Material Prep Skill

此 Skill 是 `jianying-editor` 的前置轻量层。

目标不是直接剪片，而是把项目里现有的分镜图、视频片段、字幕文案和口播思路，整理成一套稳定、可复用、可交接的输入素材包。

## 何时使用

- 用户要为 `资源/社交分享/预告片/` 整理剪映自动化输入
- 用户已经有分镜头、文案或字幕，但不想直接接入重型剪映 Skill
- 用户要生成 `asset-manifest.json`、`storyboard.json`、`subtitles.srt`、`voiceover.txt`
- 用户要先做“标准素材包”，以后再交给 `jianying-editor` 或人工进剪映

## 工作边界

- 只整理输入素材，不创建剪映草稿，不调用外部剪映 API
- 优先复用现有目录：`资源/社交分享/预告片/`
- 输出内容默认落到目标目录下的 `jianying-package/`
- 若已有镜头编号，保持原编号，不重排
- 视频剪辑逻辑、转场、滤镜、关键帧仍留给后续剪映流程处理

## 标准流程

### 1. 读取现有素材

优先检查：

- `资源/社交分享/预告片/README.md`
- `资源/社交分享/预告片/video-prompts.md`
- `资源/社交分享/预告片/分镜头/`
- `资源/社交分享/预告片/分镜头/分享/`

### 2. 明确输出包

默认输出 4 类文件：

- `asset-manifest.json`
- `storyboard.json`
- `subtitles.srt`
- `voiceover.txt`

必要时再补：

- `bgm-notes.md`
- `edit-brief.md`

### 3. 生成或更新骨架

优先用脚本：

```bash
python .agents/skills/jianying_material_prep/scripts/init_package.py \
  --source "资源/社交分享/预告片/分镜头" \
  --out "资源/社交分享/预告片/jianying-package" \
  --title "预告片 v1.0"
```

脚本会：

- 扫描 `png/mp4/jpg/jpeg/webp/mp3/wav/m4a`
- 生成素材清单
- 为每个镜头生成 storyboard 占位条目
- 初始化空的 `subtitles.srt` 与 `voiceover.txt`

### 4. 补齐内容

根据 `video-prompts.md` 把以下信息补进包里：

- 镜头顺序
- 每镜头字幕
- 每镜头口播
- BGM 建议
- 时长建议

## 输出约束

- `asset-manifest.json` 中的 `path` 一律写仓库内相对路径
- `storyboard.json` 保留镜头编号、素材引用、字幕、口播、建议时长
- `subtitles.srt` 用标准 SRT 格式
- `voiceover.txt` 按镜头顺序逐条记录

## 参考资料

- 素材包结构与字段说明：`references/material_schema.md`
- 外部 `jianying-editor` 对媒体和字幕的要求：
  - 绝对路径由后续执行层负责转换
  - 字幕可走 `import_srt()`
  - 媒体素材建议按比例区分横竖屏

