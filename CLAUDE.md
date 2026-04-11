# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

本仓库是小说《长生不死的我，在南宋点歪了科技树》的完整创作工程，包含正文、设定库、大纲、写手/智囊团角色设定、官方网站（`docs/`），以及自动化脚本。

## 常用脚本命令

```bash
# 将正文 Markdown 转换并同步到网站 JSON（章节定稿后必须执行）
python3 .agents/skills/novel_creator/scripts/publish_to_docs.py

# 同步角色设定库到网站 characters.json
python3 .agents/skills/docs_ui_optimizer/scripts/sync_characters.py

# 同步章节到网站（等效 publish_to_docs）
python3 .agents/skills/docs_ui_optimizer/scripts/sync_chapters.py

# 检查正文与设定库之间的逻辑冲突
python3 .agents/skills/novel_creator/scripts/context_manager.py --check

# 生成当前项目设定的简要报告
python3 .agents/skills/novel_creator/scripts/context_manager.py --summary
```

## 目录结构

| 目录 | 用途 |
|------|------|
| `正文/` | 小说章节草稿（Markdown） |
| `大纲/` | 卷级和章级大纲、未来规划（只有规划，不记录已发生的事实） |
| `设定库/` | 已发生事实的日志——世界观、角色档案、时间线、道具 |
| `会议记录/` | 智囊团联席会议纪要 |
| `写手/` | 写手角色人设文档（刘慈欣、曹雪芹、司马迁等） |
| `智囊团/` | 领域专家角色文档（历史学家、物理学家、化学家等） |
| `参考资料/` | 历史文献、科学论文、宏观背景资料 |
| `docs/` | GitHub Pages 静态网站（HTML/CSS/JS + JSON 数据） |
| `交付/` | 最终发布文件 |
| `.agents/skills/` | Skill 定义及自动化脚本 |

## 正文 → 网站 发布流程

1. 在 `正文/` 中完成并定稿章节 Markdown。
2. 更新 `设定库/00_全局时间线.md` 与相关角色的 `生平志`（`附、 生平志` 节）。
3. 运行 `publish_to_docs.py`，生成 `docs/chapters/chapter-N.json` 并更新 `docs/chapters/index.json`。
4. 如有角色变动，运行 `sync_characters.py` 更新 `docs/data/characters.json`。

## 网站架构（`docs/`）

- 纯静态站点，无构建步骤，直接部署到 GitHub Pages。
- 章节内容以 JSON 存储于 `docs/chapters/`，由 `docs/js/reader.js` 通过 `fetch()` 动态加载。
- 角色数据存储于 `docs/data/characters.json`，由 `docs/js/character-detail.js` 读取。
- 设计主题：深色背景 `#0a0b0f`，古金色 `#c8a86e`；正文字体 `Noto Serif SC`，界面字体 `Inter`。

## 设定库核心规范

- **日志化铁律**：`设定库/` 只记录正文中**已发生**的事实。未来路线图和战役规划一律放入 `大纲/`，严禁混入设定库。
- **角色档案结构**：必须包含"〇姓名渊源 → 一形象 → 二背景 → 三性格 → 四作用 → 五装备 → 附生平志"七个模块。
- **世界观分类**：设定库下分三大类——`01_底层逻辑与物理机制`、`02_社会演进与制度体系`、`03_群系生态与情感锚点`，严禁平铺存放。
- 每章定稿后须同步 `00_全局时间线.md` 和相关角色生平志，再执行网站发布。

## 创作铁律（核心红线）

- 严禁出现魔法或超自然元素；所有技术优势来自 2056 年知识、外星手环（有限资源）或大宋工业潜力。
- 严禁"系统加点"或"现成图纸"；技术突破必须经历"概念→工匠研发→失败→定型"的过程。
- 主角是会犯错、会疲惫的凡人兵王，禁止神化。
- 子嗣异能必须在碳基生物极限内，严禁超自然超能力。

## 创作会议制度

涉及重大设定变更时，触发词 **"开始会议"** 进入论证期（只讨论，锁定文件修改）；触发词 **"会议结束 执行"** 进入执行期（批量回溯修改设定库/正文/大纲），会议纪要存入 `会议记录/`。

## Skills

- `/novel_creator`：全流程创作控制（设定同步→大纲拆解→草稿撰写→一致性校验→网站发布）。
- `/docs_ui_optimizer`：网站 UI 维护与章节/角色数据同步。
