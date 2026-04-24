---
name: docs_ui_optimizer
description: 用于优化 docs 目录 Web UI 的专业 Skill。包括设计系统维护、章节同步、页面优化等。
---

# Docs UI Optimizer Skill

此 Skill 专门维护 `docs/` 目录下的官方站点前端，不负责内部创作资料整理，也不负责发布审计。

## 工作边界
- 负责页面结构、前端渲染逻辑、内容同步脚本、语言切换和详情页组件。
- 公开内容源当前统一在：
  - `docs/content/chapters/{zh,en}/`
  - `docs/content/profiles/{zh,en}/`
  - `docs/content/glossary/{zh,en}/`
- 发布索引层当前统一在：
  - `docs/data/chapters_zh.json` / `docs/data/chapters_en.json`
  - `docs/data/characters_zh.json` / `docs/data/characters_en.json`
  - `docs/data/glossary_zh.json` / `docs/data/glossary_en.json`
- 站点当前架构是“Markdown 公开源 + 轻索引 JSON + 前端直读 Markdown”，不要再回退到“整章/整条目 JSON 正文”模式。

## 核心设计原则
- **主题**：重工大宋 × 星海赛博。
- **视觉基调**：深色背景、古金强调、克制的玻璃拟态与微动效。
- **交互原则**：优先可读性和信息密度控制，不为了“炫”牺牲加载速度和叙事效率。
- **内容原则**：样式组件化，数据源轻量化，正文/图鉴/词典统一走 Markdown 结构。

## 常用流程

### 章节同步
1. 运行 `make publish`。
2. 确认 `docs/content/chapters/{zh,en}/` 已整理完毕。
3. 确认 `docs/data/chapters_zh.json` 和 `docs/data/chapters_en.json` 已更新。
4. 若阅读页结构有改动，同时检查 `docs/js/reader.js` 与 `docs/js/catalog.js`。

### 图鉴同步
1. 运行 `make sync-chars`。
2. 确认 `docs/content/profiles/{zh,en}/` 是唯一公开源。
3. 确认 `docs/data/characters_zh.json` 和 `docs/data/characters_en.json` 已更新。
4. 若详情页结构变化，检查 `docs/js/character-detail.js` 的 section 渲染、时间线渲染和本地链接渲染。

### 词典同步
1. 运行 `make sync-glossary`。
2. 确认 `docs/content/glossary/{zh,en}/` 是唯一公开源。
3. 确认 `docs/data/glossary_zh.json` 和 `docs/data/glossary_en.json` 已更新。
4. 若浮窗结构变化，检查 `docs/js/character-detail.js` 中词典索引读取、Markdown 解析和危险链接过滤逻辑。

### 页面维护
- 公共元信息、图标、分享图由 `make sync-head` 统一维护。
- 图片资源优化和删除原图由 `make optimize-assets` 统一处理。
- 发布审计由 `site_optimizer` 负责；Web UI 变更完成后通常要补跑 `make audit`。

## 重点文件
- `docs/js/reader.js`：正文阅读页与 Markdown 解析。
- `docs/js/catalog.js`：目录页与章节索引读取。
- `docs/js/character-detail.js`：图鉴详情、词典浮窗、本地 Markdown 链接转译。
- `docs/css/style.css`：站点核心样式。
- `scripts/sync_characters.py`：图鉴轻索引生成。
- `scripts/sync_glossary.py`：词典轻索引生成。

## 维护清单
- 检查所有章节、图鉴、词典索引引用是否仍然有效。
- 检查中英双语切换时是否读到正确的 Markdown 源。
- 检查移动端导航、目录、详情页浮窗是否可用。
- 检查时间线、生平志、表格等特殊组件样式是否被新解析逻辑破坏。
