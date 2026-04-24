# 品牌资产

当前目录用于存放《长生不死》的官方品牌资产源文件。

## 现有文件
- `LOGO/`：当前可用的 4 套正式 logo 导出版本。
- `插图模板.png`：透明插图模板，后续章节海报统一通过脚本叠加，避免手工摆版漂移。
- `share-cover-realistic.png`：当前写实风格横版社交分享图源文件。
- `book-cover-portrait-realistic.png`：当前写实风格竖版封面源文件。

## 使用约束
- 章节插图默认优先使用 `LOGO/` 目录中的正式导出版：
  - 浅底：`LOGO/白底.png` / `LOGO/白底-剪影.png`
  - 深底：`LOGO/黑底.png` / `LOGO/黑底-剪影.png`
- 章节插图定稿后，优先通过 `make compose-poster SRC=... OUT=...` 或 `apply_poster_template.py` 叠加 `插图模板.png`，而不是手工再排一遍。
- 新的 VI 延展稿应继续落在本目录，不混入 `docs/images/` 的发布目录。
- 发布用裁切、压缩或导出版本，放到 `docs/images/branding/`。
