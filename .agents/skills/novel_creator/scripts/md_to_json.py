#!/usr/bin/env python3
"""
Chapter publish pipeline.

Source of truth:
  - Public chapter markdown lives in docs/content/chapters/zh|en/*.md
  - Reader/catalog use lightweight indexes in docs/data/chapters_zh.json and chapters_en.json

Compatibility:
  - `make publish` still calls this script
  - `--check` still validates source content without writing files
"""

import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[3]
DOCS_DIR = PROJECT_ROOT / "docs"
PUBLIC_CONTENT_DIR = DOCS_DIR / "content" / "chapters"
PUBLIC_ZH_DIR = PUBLIC_CONTENT_DIR / "zh"
PUBLIC_EN_DIR = PUBLIC_CONTENT_DIR / "en"
DATA_DIR = DOCS_DIR / "data"
ZH_INDEX_FILE = DATA_DIR / "chapters_zh.json"
EN_INDEX_FILE = DATA_DIR / "chapters_en.json"


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


def chapter_sort_key(path):
    match = re.search(r"chapter-(\d+)\.md$", path.name)
    return int(match.group(1)) if match else 9999


def collect_entries(locale_dir, locale, target_chapter=None, normalize=False):
    entries = []
    md_files = sorted(locale_dir.glob("chapter-*.md"), key=chapter_sort_key)
    if not md_files:
        print(f"❌ 找不到章节 Markdown 文件：{locale_dir.relative_to(PROJECT_ROOT)}")
        sys.exit(1)

    for path in md_files:
        index = chapter_sort_key(path)
        raw = path.read_text(encoding="utf-8")
        normalized = normalize_markdown(raw)
        title = quick_title(path)
        entry = build_index_entry(
            chapter_id=index,
            title=title,
            word_count=count_words(normalized),
            source=f"content/chapters/{locale}/chapter-{index}.md",
        )
        entries.append(entry)
        if normalize and (target_chapter is None or target_chapter == index):
            write_text_if_changed(path, normalized)
            print(f"  ✅ 已规范化: {path.relative_to(PROJECT_ROOT)}")
    return entries


def validate_only(target_chapter=None):
    zh_entries = collect_entries(PUBLIC_ZH_DIR, "zh", target_chapter=target_chapter, normalize=False)
    json.dumps(zh_entries, ensure_ascii=False)
    en_entries = collect_entries(PUBLIC_EN_DIR, "en", target_chapter=target_chapter, normalize=False)
    json.dumps(en_entries, ensure_ascii=False)
    print("\n✅ 校验完成。")


def publish(target_chapter=None):
    zh_entries = collect_entries(PUBLIC_ZH_DIR, "zh", target_chapter=target_chapter, normalize=True)
    en_entries = collect_entries(PUBLIC_EN_DIR, "en", target_chapter=target_chapter, normalize=True)

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
