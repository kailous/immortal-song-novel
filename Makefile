# 长生不死 · 小说工程 Makefile
# 用法: make <target>

.PHONY: publish sync-chars sync-glossary sync-chapters check report audit optimize-assets sync-head help

## 规范化公开章节 Markdown 并重建章节索引（章节定稿后必须执行）
publish:
	python3 .agents/skills/novel_creator/scripts/md_to_json.py

## 仅校验引号，不写文件
validate:
	python3 .agents/skills/novel_creator/scripts/md_to_json.py --check

## 基于公开图鉴 Markdown 重建 zh/en 角色轻索引
sync-chars:
	python3 .agents/skills/docs_ui_optimizer/scripts/sync_characters.py

## 基于公开词典 Markdown 重建 zh/en 词典索引
sync-glossary:
	python3 .agents/skills/docs_ui_optimizer/scripts/sync_glossary.py

## 同步章节到网站（等效 publish）
sync-chapters:
	python3 .agents/skills/novel_creator/scripts/md_to_json.py

## 检查设定资料结构完整性
check:
	python3 .agents/skills/novel_creator/scripts/context_manager.py --check

## 生成设定资料简要报告
report:
	python3 .agents/skills/novel_creator/scripts/context_manager.py --summary

## 发布前审计：JSON、JS、外部资源、图片体积、引用完整性
audit:
	python3 .agents/skills/site_optimizer/scripts/audit_site.py

## 压缩 docs/images 并将发布数据引用切到 WebP
optimize-assets:
	python3 .agents/skills/site_optimizer/scripts/optimize_assets.py

## 同步所有静态页的公共 head 元信息
sync-head:
	python3 .agents/skills/site_optimizer/scripts/sync_site_head.py

## 一键完整发布（同步章节 + 同步角色）
all: publish sync-chars sync-glossary

help:
	@echo ""
	@echo "  make publish      规范化公开章节 Markdown 并重建章节索引"
	@echo "  make sync-chars   基于公开图鉴 Markdown 重建角色索引"
	@echo "  make sync-glossary 基于公开词典 Markdown 重建词典索引"
	@echo "  make check        检查设定资料结构完整性"
	@echo "  make report       生成设定资料报告"
	@echo "  make audit        发布前站点审计"
	@echo "  make optimize-assets 压缩图片并更新发布引用"
	@echo "  make sync-head    同步公共 head 元信息"
	@echo "  make all          publish + sync-chars"
	@echo ""
