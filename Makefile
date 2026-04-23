# 长生不死 · 小说工程 Makefile
# 用法: make <target>

.PHONY: publish sync-chars sync-chapters check report audit optimize-assets help

## 将正文 Markdown 同步发布到网站 JSON（章节定稿后必须执行）
publish:
	python3 .agents/skills/novel_creator/scripts/md_to_json.py

## 仅校验引号，不写文件
validate:
	python3 .agents/skills/novel_creator/scripts/md_to_json.py --check

## 同步角色设定库到网站 characters.json
sync-chars:
	python3 .agents/skills/docs_ui_optimizer/scripts/sync_characters.py

## 同步章节到网站（等效 publish）
sync-chapters:
	python3 .agents/skills/novel_creator/scripts/md_to_json.py

## 检查正文与设定库之间的逻辑冲突
check:
	python3 .agents/skills/novel_creator/scripts/context_manager.py --check

## 生成设定库简要报告
report:
	python3 .agents/skills/novel_creator/scripts/context_manager.py --summary

## 发布前审计：JSON、JS、外部资源、图片体积、引用完整性
audit:
	python3 .agents/skills/site_optimizer/scripts/audit_site.py

## 压缩 docs/images 并将发布数据引用切到 WebP
optimize-assets:
	python3 .agents/skills/site_optimizer/scripts/optimize_assets.py

## 一键完整发布（同步章节 + 同步角色）
all: publish sync-chars

help:
	@echo ""
	@echo "  make publish      将正文同步到网站（定稿后必须执行）"
	@echo "  make sync-chars   同步角色设定到网站"
	@echo "  make check        扫描设定冲突"
	@echo "  make report       生成设定库报告"
	@echo "  make audit        发布前站点审计"
	@echo "  make optimize-assets 压缩图片并更新发布引用"
	@echo "  make all          publish + sync-chars"
	@echo ""
