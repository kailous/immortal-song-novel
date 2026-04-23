---
name: docs_ui_optimizer
description: 用于优化 docs 目录 Web UI 的专业 Skill。包括设计系统维护、章节同步、页面优化等。
---

# Docs UI Optimizer Skill

此 Skill 专门用于维护和优化“长生不死”官方小说网站（`/docs` 目录）。

## 1. 核心设计原则 (Aesthetics)
- **主题**: “重工大宋 × 星海赛博” (Heavy Industry Song × Cosmic Cyber)。
- **色调**: 深色背景 (`#0a0b0f`)，配合古金色氛围调器 (`#c8a86e`)。
- **字体**: 正文使用 `Noto Serif SC` (宋体风格)，界面使用 `Inter` (无衬线)。
- **动效**: 使用 Glassmorphism (毛玻璃) 和轻微的悬浮缩放，增强高级感。

## 2. 常用操作流程

### 2.1 同步最新章节
1.  **执行同步脚本**: 在根目录下运行 `python3 .agents/skills/docs_ui_optimizer/scripts/sync_chapters.py`。
2.  **验证结果**: 检查 `/docs/content/chapters/zh` 与 `/docs/content/chapters/en` 是否已同步 Markdown，并确认 `/docs/data/chapters_zh.json`、`/docs/data/chapters_en.json` 已更新。
3.  **上传静态资源**: 如有新增插图，放入 `/docs/images` 并在 Markdown 中引用。

### 2.2 更新图鉴详情
1.  **执行同步脚本**: 在根目录下运行 `python3 .agents/skills/docs_ui_optimizer/scripts/sync_characters.py`。
2.  **验证结果**: 检查 `/docs/data/characters_zh.json` 和 `/docs/data/characters_en.json` 是否已更新。
3.  **内容源**: 中文图鉴唯一源为 `/docs/content/profiles/zh`，英文唯一源为 `/docs/content/profiles/en`；头像直接引用 `/docs/images` 中的已发布资源。

### 2.3 UI 性能优化
- 确保所有的 `.png` 图片在发布前都进行了压缩（或使用 `.webp`）。
- 检查 `/docs/js/main.js` 中的 `IntersectionObserver` 是否工作正常。
- 验证 `/docs/reader.html` 的阅读进度条是否平滑。

## 3. SEO 最佳实践
- 确保每个页面都有唯一的 `<title>` 和 `<meta name="description">`。
- 章节页应包含正确的 `og:title` 标签。

## 4. 维护清单
- [ ] 检查所有章节链接是否有效。
- [ ] 确认移动端导航菜单是否能正常呼出。
- [ ] 检查字号和行间距在 Kindle/iPad 模拟器下的舒适度。
