# 品牌资产

当前目录用于存放《长生不死》的官方品牌资产源文件。

## 现有文件
- `logo-vi-board-v2.png`：当前官方 VI 版式总板，后续海报模板、logo 版本选择和一致性检查都以此为准。
- `logo-title-legacy.png`：早期单张标题 logo 源文件，暂时保留作兼容参考，不再视为最新官方版。
- `LOGO/`：当前可用的 4 套正式 logo 导出版本。
- `插图模板.png`：透明插图模板，后续章节海报统一通过脚本叠加，避免手工摆版漂移。

## 使用约束
- 章节插图默认优先使用 `logo-vi-board-v2.png` 中定义的单色 / 反白 / 极简版本。
- 章节插图定稿后，优先通过 `make compose-poster SRC=... OUT=...` 或 `apply_poster_template.py` 叠加 `插图模板.png`，而不是手工再排一遍。
- 新的 VI 延展稿应继续落在本目录，不混入 `docs/images/` 的发布目录。
- 发布用裁切、压缩或导出版本，放到 `docs/images/branding/`。
