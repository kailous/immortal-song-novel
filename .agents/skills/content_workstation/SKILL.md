---
name: content_workstation
description: 《长生不死》内容工作站总控 Skill。用于把自然语言需求路由到写作、审校、设定图、插图、站点、社交视频素材和发布流程。适用于用户不指定具体 skill，只描述目标成果时。
---

# Content Workstation Skill

此 Skill 是项目的总控编排层。

它不替代已有 skills 的专业能力，而是负责：

- 理解用户自然语言目标
- 选择应该调用的 skill 或技能链
- 明确最终应落到哪些文件
- 决定是否需要同步、审计、提交、推送

## 何时使用

- 用户直接说目标，不指定具体 skill
- 用户要“写一章”“更新图鉴”“做预告片”“发布站点”“整理工作流”
- 用户想把创作、宣传、发布串成一条完整链路
- 用户希望把本项目当作一个 AI 内容工作站来驱动

## 核心原则

### 1. 先路由，再执行

不要急着直接写内容。先判断这是哪一类任务：

- 正文创作
- 文案审校
- 设定图
- 章节插图
- 服装设定
- docs 站点
- 发布审计
- 社交视频素材
- 范文资料收集
- 多环节组合任务

### 2. 优先复用现有 skill

默认路由到已有 skill，不要在总控层重复实现子流程：

- `$novel_creator`
- `$copy_editor`
- `$docs_ui_optimizer`
- `$site_optimizer`
- `$setting_art_generator`
- `$illustration_generator`
- `$jianying_material_prep`
- `$costume_designer`
- `$prose_collector`

### 3. 明确交付物

每次任务都要明确：

- 最终落到哪些文件
- 是否需要更新 `docs/data/*.json`
- 是否需要跑 `make publish` / `make sync-chars` / `make sync-glossary`
- 是否需要 `make audit`
- 是否需要提交或推送

## 标准流程

### 第一步：任务分类

把用户请求归到以下类别之一：

1. `chapter`
   - 写正文、改正文、推进剧情、补章节
2. `copyedit`
   - 审校、错别字、病句、轻润色
3. `profile-art`
   - 角色图鉴图、种族图、道具图
4. `scene-art`
   - 章节插图、海报、宣传图
5. `costume`
   - 服装设定、阶段换装、身份服装一致性
6. `docs-ui`
   - 页面布局、样式、交互、前端渲染、同步脚本
7. `publish`
   - 同步索引、优化资源、审计、提交、推送
8. `social-video`
   - 预告片、分镜素材包、字幕、口播、剪映输入物料
9. `research`
   - 范文搜集、风格参考、资料沉淀
10. `composite`
   - 跨多个类别的组合任务

### 第二步：路由到 skill

按下列方式路由：

- `chapter` -> `$novel_creator`
- `copyedit` -> `$copy_editor`
- `profile-art` -> `$setting_art_generator`
- `scene-art` -> `$illustration_generator`
- `costume` -> `$costume_designer`
- `docs-ui` -> `$docs_ui_optimizer`
- `publish` -> `$site_optimizer`
- `social-video` -> `$jianying_material_prep`
- `research` -> `$prose_collector`

若为组合任务，采用链式路由，例如：

- 写章节并发布：
  `$novel_creator -> $site_optimizer`
- 更新角色图并同步图鉴：
  `$costume_designer -> $setting_art_generator -> $docs_ui_optimizer`
- 做预告片视觉与素材包：
  `$illustration_generator -> $jianying_material_prep`
- 写完正文再审校：
  `$novel_creator -> $copy_editor`

### 第三步：确定收口动作

根据任务类型决定是否执行以下动作：

- 正文改动后：`make publish`
- 图鉴内容改动后：`make sync-chars`
- 词典改动后：`make sync-glossary`
- docs 发布前：`make audit`
- 用户要求上线或入库时：提交、推送

## 常见自然语言映射

示例：

- “写第八章”
  -> `chapter`
  -> `$novel_creator`

- “把这段正文顺一下”
  -> `copyedit`
  -> `$copy_editor`

- “更新张宪的图鉴图”
  -> `profile-art`
  -> 若涉及服装一致性，先 `$costume_designer`，否则直接 `$setting_art_generator`

- “角色页 UI 不够好看”
  -> `docs-ui`
  -> `$docs_ui_optimizer`

- “把站点发布一下”
  -> `publish`
  -> `$site_optimizer`

- “把这版预告片整理成剪映可用素材”
  -> `social-video`
  -> `$jianying_material_prep`

- “给赵嬛嬛做一版符合宋制的图，再同步到图鉴”
  -> `composite`
  -> `$costume_designer -> $setting_art_generator -> $docs_ui_optimizer`

## 决策边界

- 若用户明确点名 skill，优先使用指定 skill
- 若任务明显属于单一专业域，不要绕一层多余编排
- 若任务是纯技术实现，不要强行走创作链
- 若任务涉及最终发布，主动补收口检查

## 参考

- 路由表：`references/workstation_routes.md`
