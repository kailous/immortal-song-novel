#!/usr/bin/env python3

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
DATA_DIR = ROOT / "docs" / "data"
PUBLIC_MD_DIR = ROOT / "docs" / "content" / "profiles"
PUBLIC_ZH_MD_DIR = PUBLIC_MD_DIR / "zh"
PUBLIC_EN_MD_DIR = PUBLIC_MD_DIR / "en"
ZH_JSON_FILE = DATA_DIR / "characters_zh.json"
EN_JSON_FILE = DATA_DIR / "characters_en.json"

PROFILE_META = {
    "luchen": {"type": "character"},
    "zhangxian": {"type": "character"},
    "luxiaoxiao": {"type": "character"},
    "zhaohuanhuan": {"type": "character"},
    "lixianzhong": {"type": "character"},
    "bracelet": {"type": "item"},
    "taren": {"type": "faction"},
}


def read_text(path):
    return path.read_text(encoding="utf-8")


def write_json_if_changed(path, data):
    content = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return
    path.write_text(content, encoding="utf-8")


def clean_text(text):
    text = re.sub(r"^\d+:\s*", "", text, flags=re.MULTILINE)
    return text.strip()


def parse_markdown_profile(content):
    source = (content or "").replace("\r\n", "\n")
    parts = re.split(r"^##\s+", source, flags=re.MULTILINE)
    head = parts[0] if parts else source

    title_match = re.search(r"^#\s+(.*?)(?:\s+\(.*\))?$", source, re.MULTILINE)
    title = ""
    if title_match:
        title = title_match.group(1).split("——")[-1].strip()
        title = re.sub(r"^\d+_", "", title)
        title = re.sub(r"^(主角|核心配角|第一女主|第二女主|初始外挂|将领)_", "", title)
        title = re.sub(r"^将领_", "", title)
        title = title.strip("_")

    alias_match = re.search(
        r"^\*\s+\*\*(?:大宋化名|本名|姓名|称号|类型|Alias|Name|Title)\*\*[:：]\s*(.*?)(?:\*\*)?\s*$",
        source,
        re.MULTILINE,
    )
    alias = alias_match.group(1).replace("**", "").strip() if alias_match else ""

    image_match = re.search(r"!\[.*?\]\((.*?)\)", source)
    image = Path(image_match.group(1)).name if image_match else ""

    intro = head
    intro = re.sub(r"^#.*?\n", "", intro, flags=re.MULTILINE)
    intro = re.sub(r"!\[.*?\]\(.*?\)\n?", "", intro, flags=re.MULTILINE)
    intro = re.sub(
        r"^\*\s+\*\*(?:大宋化名|本名|姓名|称号|类型|Alias|Name|Title)\*\*[:：].*(?:\n|$)",
        "",
        intro,
        flags=re.MULTILINE,
    )
    intro = clean_text(intro)
    intro = re.sub(r"^---+\s*", "", intro)
    intro = re.sub(r"---+\s*$", "", intro)
    intro = intro.strip()

    return {"title": title, "alias": alias, "image": image, "intro": intro}


def build_language_data(locale_dir, locale):
    data = {}
    for profile_id, meta in PROFILE_META.items():
        path = locale_dir / f"{profile_id}.md"
        if not path.exists():
            if locale == "en":
                data[profile_id] = {
                    **build_language_data(PUBLIC_ZH_MD_DIR, "zh")[profile_id],
                    "source": f"content/profiles/en/{profile_id}.md",
                }
                continue
            raise FileNotFoundError(f"Missing profile source: {path.relative_to(ROOT)}")
        parsed = parse_markdown_profile(read_text(path))
        data[profile_id] = {
            "title": parsed["title"],
            "alias": parsed["alias"],
            "image": parsed["image"],
            "intro": parsed["intro"],
            "type": meta["type"],
            "source": f"content/profiles/{locale}/{profile_id}.md",
        }
    return data


def sync():
    zh_data = build_language_data(PUBLIC_ZH_MD_DIR, "zh")
    en_data = build_language_data(PUBLIC_EN_MD_DIR, "en")

    write_json_if_changed(ZH_JSON_FILE, zh_data)
    write_json_if_changed(EN_JSON_FILE, en_data)

    print(f"Successfully synced {len(zh_data)} zh entries to {ZH_JSON_FILE.relative_to(ROOT)}")
    print(f"Successfully synced {len(en_data)} en entries to {EN_JSON_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    sync()
