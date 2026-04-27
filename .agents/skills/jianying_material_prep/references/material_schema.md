# Jianying 输入素材包结构

## 推荐目录

```text
jianying-package/
├── asset-manifest.json
├── storyboard.json
├── subtitles.srt
├── voiceover.txt
├── bgm-notes.md
└── edit-brief.md
```

## 1. `asset-manifest.json`

作用：列出所有可供剪映流程使用的媒体资产。

推荐字段：

```json
{
  "title": "预告片 v1.0",
  "aspect_ratio": "9:16",
  "source_dir": "资源/社交分享/预告片/分镜头",
  "assets": [
    {
      "id": "shot-01-video",
      "shot": "01",
      "type": "video",
      "path": "资源/社交分享/预告片/分镜头/01.mp4",
      "role": "main"
    },
    {
      "id": "shot-01-image",
      "shot": "01",
      "type": "image",
      "path": "资源/社交分享/预告片/分镜头/01.png",
      "role": "poster"
    }
  ]
}
```

字段建议：

- `id`：稳定唯一标识
- `shot`：镜头编号
- `type`：`video` / `image` / `audio`
- `path`：仓库内相对路径
- `role`：`main` / `poster` / `share` / `bgm` / `voiceover`

## 2. `storyboard.json`

作用：把素材、字幕、口播和建议时长绑定到镜头级条目。

推荐字段：

```json
[
  {
    "shot": "01",
    "asset_ref": "shot-01-video",
    "subtitle": "2056年，人类快灭绝了。",
    "voiceover": "2056年，人类快灭绝了。",
    "suggested_duration_sec": 3.0,
    "notes": "引擎室送行，冷白工业光"
  }
]
```

这是本项目推荐的编辑前素材结构。

## 3. `subtitles.srt`

作用：供后续 `import_srt()` 或人工导入。

标准格式示例：

```srt
1
00:00:00,000 --> 00:00:03,000
2056年，人类快灭绝了。
```

## 4. `voiceover.txt`

作用：保留口播顺序，后续可做人声录制、TTS 或对拍。

推荐格式：

```text
[01] 2056年，人类快灭绝了。
[02] 他们把最后一个工程师，送进了时间通道。
```

## 与外部 `jianying-editor` 的对接点

- 媒体导入层要使用绝对路径，这一步由后续执行脚本转换
- 文字层可以直接吃 `subtitles.srt`
- 若走其 `movie_commentary_builder.py`，需要再转换成更扁平的数组：

```json
[
  {
    "start": "00:00",
    "duration": 3.0,
    "text": "2056年，人类快灭绝了。"
  }
]
```

因此本 skill 的定位是：先把项目内部资产标准化，再按具体剪映脚本的需要做二次转换。
