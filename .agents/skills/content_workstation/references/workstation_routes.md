# Content Workstation 路由表

## 任务类别 -> skill -> 默认落盘

| 类别 | 主 skill | 常见附加 skill | 默认落盘 |
|---|---|---|---|
| `chapter` | `novel_creator` | `copy_editor`, `site_optimizer` | `docs/content/chapters/{zh,en}/` |
| `copyedit` | `copy_editor` | 视情况无 | 原目标 Markdown |
| `profile-art` | `setting_art_generator` | `costume_designer`, `docs_ui_optimizer` | `资源/源图/图鉴/` 与 `docs/images/characters/` |
| `scene-art` | `illustration_generator` | `costume_designer` | `资源/插图/` 或 `docs/images/chapters/` |
| `costume` | `costume_designer` | `setting_art_generator`, `illustration_generator` | `资源/服装设定/` |
| `docs-ui` | `docs_ui_optimizer` | `site_optimizer` | `docs/` |
| `publish` | `site_optimizer` | `docs_ui_optimizer`, `novel_creator` | `docs/data/` 与发布产物 |
| `social-video` | `jianying_material_prep` | `illustration_generator` | `资源/社交分享/预告片/` |
| `research` | `prose_collector` | 无 | `资料/02_范文/` |

## 组合任务模板

### 1. 正文写作并发布

```text
novel_creator
-> copy_editor（若用户要求审校）
-> site_optimizer（发布审计）
```

### 2. 角色图鉴更新并同步站点

```text
costume_designer（若服装是变量）
-> setting_art_generator
-> docs_ui_optimizer
```

### 3. 章节插图与社交传播

```text
illustration_generator
-> jianying_material_prep
```

### 4. Web UI 调整并上线

```text
docs_ui_optimizer
-> site_optimizer
```

## 总控层输出要求

每次经由总控层处理时，最终响应至少应说明：

1. 当前被识别成哪类任务
2. 使用了哪些 skill
3. 产物落到哪里
4. 是否已经同步、审计、提交、推送
