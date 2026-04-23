---
name: site_optimizer
description: 用于长生不死静态站点的发布前安全、性能和供应链优化。覆盖 JSON/JS 校验、危险 Markdown 输出检查、外部资源检查、图片压缩与发布数据引用更新。
---

# Site Optimizer Skill

此 Skill 专门维护 `docs/` 静态站点的发布质量，不负责小说正文创作。

## 工作边界
- 保留 Cusdis 评论能力，但评论内容必须转义渲染，不加载第三方评论脚本。
- Markdown 转 HTML 应保留标题、列表、引用、加粗、斜体、行内代码、站内链接和正常外链。
- 只限制危险协议和未转义 HTML：禁止 `javascript:`, `data:`, 控制字符链接和原始 HTML 注入。
- 生成型数据现在以 `docs/content/chapters/`、`docs/content/profiles/` 为公开源，`docs/data/` 为发布索引层。

## 常用流程
1. 同步内容：`make publish`、必要时 `make sync-chars`。
2. 压缩资源：`make optimize-assets`。
   - 默认把 `docs/images` 中的发布内容图转成 `webp`，更新 `docs/` 内所有发布引用，并删除已替换的原图。
   - `og-cover.jpg` 保留原格式，用于社交分享兼容。
3. 同步页面元信息：`make sync-head`。
4. 发布审计：`make audit`。
5. 若审计失败，先修复硬错误，再重新运行审计。

## 脚本
- `scripts/audit_site.py`：校验 JSON、JS 语法、外部资源、图片体积、角色图片引用和章节索引。
- `scripts/optimize_assets.py`：使用 `cwebp` 将 `docs/images` 中的大图转为 WebP，更新 `docs/` 下全部发布引用，并删除已替换原图；分享封面 `og-cover.jpg` 例外。
- `scripts/sync_site_head.py`：集中维护图标、manifest、OG/Twitter 分享卡片和页面描述，并同步到所有静态 HTML。

## 质量门槛
- 所有 `docs/**/*.json` 必须是合法 JSON。
- 所有 `docs/js/*.js` 必须通过 `node --check`。
- 除 Cusdis API 主机外，发布页不应依赖运行时第三方 JS/CSS。
- 单张发布图片建议不超过 512KB，首屏关键图片建议不超过 300KB。
