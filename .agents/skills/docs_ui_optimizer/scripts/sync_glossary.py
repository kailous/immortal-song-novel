#!/usr/bin/env python3

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
DOCS = ROOT / "docs"
CONTENT_DIR = DOCS / "content" / "glossary"
DATA_DIR = DOCS / "data"
LOCALES = ("zh", "en")


def read_text(path):
    return path.read_text(encoding="utf-8")


def write_json_if_changed(path, data):
    content = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return
    path.write_text(content, encoding="utf-8")


def parse_glossary_markdown(content):
    source = (content or "").replace("\r\n", "\n")
    title_match = re.search(r"^#\s+(.*)$", source, re.MULTILINE)
    subtitle_match = re.search(r"^>\s+(.*)$", source, re.MULTILINE)
    return {
        "title": title_match.group(1).strip() if title_match else "",
        "subtitle": subtitle_match.group(1).strip() if subtitle_match else "",
    }


def build_locale_index(locale):
    locale_dir = CONTENT_DIR / locale
    if not locale_dir.exists():
        raise FileNotFoundError(f"Missing glossary content dir: {locale_dir.relative_to(ROOT)}")

    data = {}
    for path in sorted(locale_dir.glob("*.md")):
        glossary_id = path.stem
        parsed = parse_glossary_markdown(read_text(path))
        data[glossary_id] = {
            "title": parsed["title"],
            "subtitle": parsed["subtitle"],
            "source": f"content/glossary/{locale}/{path.name}",
        }
    return data


def sync():
    for locale in LOCALES:
        index = build_locale_index(locale)
        write_json_if_changed(DATA_DIR / f"glossary_{locale}.json", index)
        print(f"synced glossary index: docs/data/glossary_{locale}.json ({len(index)} entries)")


if __name__ == "__main__":
    sync()
