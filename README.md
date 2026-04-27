# 长生不死 · 项目说明

《长生不死的我，在南宋点歪了科技树》是一个“硬核科幻 × 南宋历史”小说工程仓库。这里同时承载正文创作、设定管理、公开站点发布、角色图鉴、插图资产和社交传播素材。

## 当前状态

- 正文中文已发布到第七章《旗下》；英文当前发布到第一章。
- 当前剧情时间点是“绍兴十一年春末”，地点在折冲大营，陆辰已进入岳家军前军斥候序列。
- 角色图鉴与道具图鉴的公开发布源在 `docs/`，当前角色发布图已统一从 `资源/源图/图鉴/` 同步。
- `资源/设定图/` 当前不再作为角色发布链路来源，仅保留说明用途。

当前创作驾驶舱入口：

- `创作/00_驾驶舱/当前状态.md`
- `创作/00_驾驶舱/铁律速查.md`
- `创作/00_驾驶舱/章节简报_模板.md`

## 仓库结构

- `创作/`
  内部创作中台。包含驾驶舱、大纲、设定、团队档案、会议纪要。
- `资料/`
  只读资料库。包含原典、研究、范文与索引。
- `docs/`
  对外静态站点与唯一公开发布面。正文、图鉴、词典、前端页面都在这里。
- `资源/`
  内部视觉资产仓。包含源图、品牌资产、插图、社交分享、服装设定等。
- `.agents/skills/`
  本项目自带的本地工作流 skills、脚本与参考模板。

## 公开内容与发布源

### 正文

- 中文正文源：`docs/content/chapters/zh/`
- 英文正文源：`docs/content/chapters/en/`
- 章节索引：`docs/data/chapters_zh.json`、`docs/data/chapters_en.json`

### 图鉴

- 中文图鉴源：`docs/content/profiles/zh/`
- 英文图鉴源：`docs/content/profiles/en/`
- 图鉴索引：`docs/data/characters_zh.json`、`docs/data/characters_en.json`
- 发布图片：`docs/images/characters/`

### 词典

- 中文词典源：`docs/content/glossary/zh/`
- 英文词典源：`docs/content/glossary/en/`
- 词典索引：`docs/data/glossary_zh.json`、`docs/data/glossary_en.json`

## 视觉资产约定

- 角色、种族、道具的当前发布源图统一放在 `资源/源图/图鉴/`
- 当前目录分层：
  - `资源/源图/图鉴/人物/`
  - `资源/源图/图鉴/种族/`
  - `资源/源图/图鉴/道具/`
- `docs/images/characters/` 是站点实际使用的发布图目录
- `资源/设定图/` 当前不作为发布同步源，只保留说明和未来可能恢复的过程资产入口
- 章节插图与海报资产在 `资源/插图/` 与 `docs/images/chapters/`
- 社交传播素材在 `资源/社交分享/`

## 常用命令

- `make publish`
  规范化公开章节 Markdown，并重建章节索引。
- `make sync-chars`
  基于公开图鉴 Markdown 重建角色轻索引。
- `make sync-glossary`
  基于公开词典 Markdown 重建词典索引。
- `make optimize-assets`
  压缩 `docs/images` 下的发布图，并将发布引用切到 WebP。
- `make sync-head`
  同步所有静态页的公共 head 元信息。
- `make audit`
  站点发布前审计，检查 JSON、JS、图片与引用完整性。
- `make compose-poster SRC=... OUT=...`
  给插图叠加统一海报模板。
- `make sync-posters`
  从 `资源/插图/` 批量生成章节发布海报。
- `make export-social-covers`
  从竖版封面导出抖音与小红书分享尺寸。

常见收口顺序：

1. 正文改完：`make publish`
2. 图鉴改完：`make sync-chars`
3. 词典改完：`make sync-glossary`
4. 需要时：`make optimize-assets`
5. 发布前：`make sync-head && make audit`

## 本项目 Skills 清单

以下是仓库内自带的本地 skills。它们是本项目工作流的一部分，不等于你运行环境里的所有全局插件技能。

| Skill | 作用 |
|---|---|
| `novel_creator` | 控制小说创作主流程。进入驾驶舱、拆大纲、写正文、同步状态与发布。 |
| `copy_editor` | 审校正文、图鉴、词典等 Markdown 文稿。先给问题清单，确认后再精确替换。 |
| `docs_ui_optimizer` | 维护 `docs/` 站点前端、双语索引、详情页渲染与内容同步脚本。 |
| `site_optimizer` | 负责发布前质量控制：JSON/JS 校验、图片优化、引用审计、head 同步。 |
| `setting_art_generator` | 生成角色、种族、道具、建筑等 1:1 设定图，或基于旧图反推重绘。 |
| `illustration_generator` | 生成 16:9 写实电影风格章节插图与宣传图，并审核人物一致性。 |
| `costume_designer` | 为角色建立结构化服装设定，输出可复用的服装约束与提示词片段。 |
| `prose_collector` | 联网搜集高质量小说范文，按写法与用途沉淀到参考资料库。 |

本地 skills 路径：

- `.agents/skills/novel_creator/`
- `.agents/skills/copy_editor/`
- `.agents/skills/docs_ui_optimizer/`
- `.agents/skills/site_optimizer/`
- `.agents/skills/setting_art_generator/`
- `.agents/skills/illustration_generator/`
- `.agents/skills/costume_designer/`
- `.agents/skills/prose_collector/`

## 相关补充说明

- 社交传播目录说明见 `资源/社交分享/README.md`
- 品牌与封面说明见 `资源/品牌/README.md`
- 插图目录说明见 `资源/插图/README.md`
- 设定图说明见 `资源/设定图/README.md`

## Git 约定

- `docs/` 是唯一公开发布面，公开内容改动最终都要落到这里。
- 角色发布图当前以 `资源/源图/图鉴/` 为基线，再同步到 `docs/images/characters/`。
- 提交前优先确认是否混入用户个人素材试验稿或无关生成中间件。

## 许可与 IP

本项目当前采用“代码可商用复用，内容 IP 非商用共享”的双层结构。

- 代码、脚本、前端结构与通用流程默认按 `MIT License` 提供
- 小说正文、设定、图像、角色形象、世界观资料等创作内容默认按 `CC BY-NC-SA 4.0` 提供
- 内容资产允许非商用转载与二创，但不得用于商业落地项目
- 项目名、Logo、官方视觉识别不授予默认品牌或商标使用权
- 法律上保留对未授权商用、品牌冒充和 IP 滥用的追诉权利

详细说明见：

- [LICENSE](/Users/lipeng/Documents/Repository/immortal-song-novel/LICENSE)
- [LICENSE-CODE-MIT.md](/Users/lipeng/Documents/Repository/immortal-song-novel/LICENSE-CODE-MIT.md)
- [IP_POLICY.md](/Users/lipeng/Documents/Repository/immortal-song-novel/IP_POLICY.md)
- [TRADEMARK_POLICY.md](/Users/lipeng/Documents/Repository/immortal-song-novel/TRADEMARK_POLICY.md)
- [COMMERCIAL_LICENSE.md](/Users/lipeng/Documents/Repository/immortal-song-novel/COMMERCIAL_LICENSE.md)
