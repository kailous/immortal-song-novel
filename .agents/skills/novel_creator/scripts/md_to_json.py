#!/usr/bin/env python3
"""
Chapter publish pipeline.

Source of truth:
  - Chinese source chapters live in 正文/*.md
  - Public chapter markdown lives in docs/content/chapters/zh|en/*.md
  - Reader/catalog use lightweight indexes in docs/data/chapters_zh.json and chapters_en.json

Compatibility:
  - `make publish` still calls this script
  - `--check` still validates source content without writing files
"""

import glob
import json
import os
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[3]
SOURCE_ZH_DIR = PROJECT_ROOT / "正文"
DOCS_DIR = PROJECT_ROOT / "docs"
PUBLIC_CONTENT_DIR = DOCS_DIR / "content" / "chapters"
PUBLIC_ZH_DIR = PUBLIC_CONTENT_DIR / "zh"
PUBLIC_EN_DIR = PUBLIC_CONTENT_DIR / "en"
DATA_DIR = DOCS_DIR / "data"
ZH_INDEX_FILE = DATA_DIR / "chapters_zh.json"
EN_INDEX_FILE = DATA_DIR / "chapters_en.json"
LEGACY_JSON_DIR = DOCS_DIR / "chapters"
LEGACY_EN_JSON_GLOB = "chapter-*-en.json"

_CN = {
    "零": 0,
    "一": 1,
    "二": 2,
    "两": 2,
    "三": 3,
    "四": 4,
    "五": 5,
    "六": 6,
    "七": 7,
    "八": 8,
    "九": 9,
    "十": 10,
}


def cn_to_int(text):
    if len(text) == 1:
        return _CN.get(text, 0)
    if text[0] == "十":
        return 10 + _CN.get(text[1], 0) if len(text) > 1 else 10
    if len(text) == 2 and text[1] == "十":
        return _CN[text[0]] * 10
    if len(text) == 3:
        return _CN[text[0]] * 10 + _CN.get(text[2], 0)
    return 0


def chapter_num(filepath):
    match = re.search(r"第([一二三四五六七八九十零两]+)章", os.path.basename(filepath))
    return cn_to_int(match.group(1)) if match else 9999


def normalize_quotes(text):
    result = []
    dq_open = False
    sq_open = False

    for char in text:
        if char in ("\u201c", "\u201d"):
            result.append("\u201c" if not dq_open else "\u201d")
            dq_open = not dq_open
        elif char in ("\u2018", "\u2019"):
            result.append("\u2018" if not sq_open else "\u2019")
            sq_open = not sq_open
        else:
            result.append(char)
    return "".join(result)


def normalize_markdown(text):
    lines = []
    for line in text.replace("\r\n", "\n").split("\n"):
        stripped = line.strip()
        if stripped.startswith("#") or stripped.startswith("!["):
            lines.append(line.rstrip())
            continue
        lines.append(normalize_quotes(line.rstrip()))
    normalized = "\n".join(lines).strip()
    return normalized + "\n"


def quick_title(path):
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem


def count_words(text):
    return len(re.findall(r"[\u4e00-\u9fa5a-zA-Z0-9]", text))


def write_text_if_changed(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return
    path.write_text(content, encoding="utf-8")


def write_json_if_changed(path, data):
    content = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    write_text_if_changed(path, content)


def build_index_entry(chapter_id, title, word_count, source):
    return {
        "id": str(chapter_id),
        "title": title,
        "wordCount": str(word_count),
        "source": source,
    }


def collect_zh_entries(target_chapter=None, write_files=True):
    entries = []
    md_files = sorted(glob.glob(str(SOURCE_ZH_DIR / "*.md")), key=chapter_num)
    if not md_files:
        print("❌ 找不到正文 Markdown 文件。")
        sys.exit(1)

    for index, filepath in enumerate(md_files, start=1):
        path = Path(filepath)
        raw = path.read_text(encoding="utf-8")
        normalized = normalize_markdown(raw)
        title = quick_title(path)
        entry = build_index_entry(
            chapter_id=index,
            title=title,
            word_count=count_words(normalized),
            source=f"content/chapters/zh/chapter-{index}.md",
        )
        entries.append(entry)
        if write_files and (target_chapter is None or target_chapter == index):
            write_text_if_changed(PUBLIC_ZH_DIR / f"chapter-{index}.md", normalized)
            print(f"  ✅ 已同步: docs/content/chapters/zh/chapter-{index}.md")
    return entries


def markdown_from_legacy_json(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    lines = [f"# {data['title']}", ""]
    for section in data.get("sections", []):
        heading = (section.get("heading") or "").strip()
        if heading:
            lines.extend([f"## {heading}", ""])
        for paragraph in section.get("paragraphs", []):
            text = str(paragraph).strip()
            if not text:
                continue
            if text == "---":
                lines.extend(["---", ""])
            else:
                lines.extend([text, ""])
    return "\n".join(lines).strip() + "\n"


def bootstrap_legacy_english():
    PUBLIC_EN_DIR.mkdir(parents=True, exist_ok=True)
    for path in sorted(LEGACY_JSON_DIR.glob(LEGACY_EN_JSON_GLOB)):
        chapter_id = re.search(r"chapter-(\d+)-en\.json$", path.name)
        if not chapter_id:
            continue
        target = PUBLIC_EN_DIR / f"chapter-{chapter_id.group(1)}.md"
        if target.exists():
            continue
        content = markdown_from_legacy_json(path)
        write_text_if_changed(target, content)
        print(f"  ✅ 已迁移英文正文: {target.relative_to(PROJECT_ROOT)}")


def collect_en_entries():
    entries = []
    for path in sorted(PUBLIC_EN_DIR.glob("chapter-*.md"), key=lambda item: int(re.search(r"chapter-(\d+)", item.name).group(1))):
        match = re.search(r"chapter-(\d+)\.md$", path.name)
        if not match:
            continue
        chapter_id = int(match.group(1))
        raw = path.read_text(encoding="utf-8")
        entries.append(
            build_index_entry(
                chapter_id=chapter_id,
                title=quick_title(path),
                word_count=count_words(raw),
                source=f"content/chapters/en/chapter-{chapter_id}.md",
            )
        )
    return entries


def validate_only(target_chapter=None):
    zh_entries = collect_zh_entries(target_chapter=target_chapter, write_files=False)
    json.dumps(zh_entries, ensure_ascii=False)
    bootstrap_legacy_english()
    en_entries = collect_en_entries()
    json.dumps(en_entries, ensure_ascii=False)
    print("\n✅ 校验完成。")


def publish(target_chapter=None):
    bootstrap_legacy_english()
    zh_entries = collect_zh_entries(target_chapter=target_chapter, write_files=True)
    en_entries = collect_en_entries()

    if target_chapter is None:
        write_json_if_changed(ZH_INDEX_FILE, zh_entries)
        write_json_if_changed(EN_INDEX_FILE, en_entries)
        print(f"📦 目录索引已更新: {ZH_INDEX_FILE.relative_to(PROJECT_ROOT)}")
        print(f"📦 目录索引已更新: {EN_INDEX_FILE.relative_to(PROJECT_ROOT)}")

    print(f"\n✅ 完成。共处理 {len(zh_entries)} 个中文章节，{len(en_entries)} 个英文章节。")


def main():
    check_only = "--check" in sys.argv
    target_chapter = None
    for arg in sys.argv[1:]:
        if arg.isdigit():
            target_chapter = int(arg)

    if check_only:
        validate_only(target_chapter=target_chapter)
        return
    publish(target_chapter=target_chapter)


if __name__ == "__main__":
    main()
