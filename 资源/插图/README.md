# 插图源文件

当前目录只存放插图源文件和场景归档，不直接存放站点发布图。

## 目录约定
- `chapter-xxx/`：按章节归档场景源图与场景说明。
- `*-clean.png`：无品牌叠层的清洁底图。
- `*.md`：对应场景的 brief、prompt 与一致性说明。

## 使用约束
- 定稿的发布图放到 `docs/images/chapters/chapter-xxx/`。
- 需要统一海报版式时，先对 `*-clean.png` 执行 `make compose-poster SRC=... OUT=...`。
- 章节内一张场景图对应一份同名 Markdown 说明，避免再出现随机导出文件名。
