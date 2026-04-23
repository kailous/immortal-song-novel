# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 每次创作会话的第一件事

**按顺序读这四个文件，然后再做任何事：**

1. `创作/00_驾驶舱/当前状态.md` — 剧情进度、角色状态、上次断点
2. `创作/00_驾驶舱/铁律速查.md` — 创作红线速查（禁用词、世界观铁律、对白语调）
3. `创作/00_驾驶舱/角色速查.md` — 三位写手核心指令 + 智囊团 + 范文库索引（替代逐一读取独立档案）
4. `创作/00_驾驶舱/章节简报_模板.md` — 动笔前填写，锁定本章任务

> 这四步是创作会话的"冷启动协议"，跳过它们会导致设定冲突。
> 团队独立档案只在需要深挖细节时读取：`创作/03_团队/写手/*.md`、`创作/03_团队/智囊团/*.md`。

---

## 常用命令

```bash
make publish       # 规范化公开章节 Markdown 并重建章节索引
make sync-chars    # 基于公开图鉴 Markdown 重建角色轻索引
make check         # 检查设定资料结构完整性
make report        # 生成设定资料简要报告
make all           # publish + sync-chars
```

---

## 目录职责

| 目录 | 职责 |
|------|------|
| `创作/00_驾驶舱/` | **创作驾驶舱**（当前状态、铁律速查、章节简报模板）——每次会话入口 |
| `docs/content/chapters/zh/` | 中文正文章节 Markdown（唯一中文源） |
| `docs/content/chapters/en/` | 英文章节 Markdown（唯一英文源） |
| `创作/01_大纲/` | 未来规划、卷/章大纲、战役路线图（**只存未来，不存已发生事实**） |
| `创作/02_设定/` | 已发生事实的 Log（时间线、内部世界观补充）——**只存 Log** |
| `创作/04_会议/纪要/` | 智囊团联席会议纪要 |
| `创作/03_团队/写手/` | 写手角色人设（司马迁/刘慈欣/曹雪芹） |
| `创作/03_团队/智囊团/` | 领域专家角色（历史学家/物理学家/化学家/地缘战略专家） |
| `资料/00_索引/` | 资料导航入口（记忆宫殿） |
| `资料/01_原典/` | 原始文献与论文 |
| `资料/02_范文/` | 写法参考与范文库 |
| `资料/03_研究/` | 整理后的研究材料（只读引用，不修改） |
| `资源/` | 内部源图与参考图 |
| `docs/` | GitHub Pages / Vercel 静态网站（HTML/CSS/JS + 公开内容文件） |
| `.agents/skills/` | Skill 定义及自动化脚本 |

---

## 设定核心规范

**`创作/02_设定/` 与 `创作/01_大纲/` 的分界线**：
- 设定 = 已在正文中发生的事实（Log）
- 大纲 = 尚未发生的规划、未来路线图

**角色档案必须包含七模块**：`〇姓名渊源 → 一形象 → 二背景 → 三性格 → 四作用 → 五装备 → 附生平志`

**设定分类（严禁平铺存放）**：
- `01_底层逻辑与物理机制`：量子重置、手环机制、物理常数
- `02_社会演进与制度体系`：政治架构、法律铁律、监察体系
- `03_群系生态与情感锚点`：后宫生态、阶层关系、基础导览

---

## 正文 → 网站发布流程

```
docs/content/chapters/zh/chapter-N.md 定稿
  → 更新 创作/00_驾驶舱/当前状态.md
  → 更新 创作/02_设定/00_全局时间线.md
  → 更新相关公开图鉴条目的生平志（附节末尾）
  → make publish   → 同步 docs/content/chapters/zh|en/*.md + docs/data/chapters_zh.json / chapters_en.json
  → make sync-chars（如有角色变动）
```

---

## 网站架构（`docs/`）

纯静态站点，无构建步骤，直接部署 GitHub Pages。

- 章节内容：`docs/content/chapters/zh/*.md` / `docs/content/chapters/en/*.md`，由 `reader.js` 先读取 `docs/data/chapters_zh.json` / `docs/data/chapters_en.json` 再 `fetch()` Markdown
- 角色索引：`docs/data/characters_zh.json` / `docs/data/characters_en.json`，列表页按语言读取；中文详情页直读 `docs/content/profiles/zh/*.md`，英文详情页直读 `docs/content/profiles/en/*.md`
- 设计主题：深色 `#0a0b0f` + 古金色 `#c8a86e`；正文 `Noto Serif SC`，界面 `Inter`

---

## Skills

- `/novel_creator`：全流程创作控制（四阶段：设定同步→大纲拆解→正文撰写→定稿同步）
- `/docs_ui_optimizer`：网站 UI 维护与章节/角色数据同步
