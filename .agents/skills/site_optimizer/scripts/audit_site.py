#!/usr/bin/env python3
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[4]
DOCS = ROOT / "docs"
MAX_IMAGE_KB = 512
ALLOWED_EXTERNAL = {
    "https://cusdis.com",
    "https://kailous.github.io/immortal-song-novel/",
}


def fail(message):
    print(f"FAIL {message}")
    return 1


def ok(message):
    print(f"OK   {message}")
    return 0


def check_json():
    errors = 0
    for path in sorted(DOCS.rglob("*.json")):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors += fail(f"JSON invalid: {path.relative_to(ROOT)} ({exc})")
    if not errors:
        ok("JSON files are valid")
    return errors


def check_js():
    node = shutil.which("node")
    if not node:
        print("WARN node not found; skipped JS syntax check")
        return 0
    errors = 0
    for path in sorted((DOCS / "js").glob("*.js")):
        result = subprocess.run([node, "--check", str(path)], capture_output=True, text=True)
        if result.returncode:
            errors += fail(f"JS syntax invalid: {path.relative_to(ROOT)}\n{result.stderr.strip()}")
    if not errors:
        ok("JavaScript syntax checks passed")
    return errors


def check_external_assets():
    errors = 0
    pattern = re.compile(r"https?://[^'\"()\s<>]+")
    for path in sorted(DOCS.rglob("*")):
        if path.suffix.lower() not in {".html", ".css", ".js"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for url in pattern.findall(text):
            if any(url.startswith(allowed) for allowed in ALLOWED_EXTERNAL):
                continue
            errors += fail(f"unexpected external runtime asset: {path.relative_to(ROOT)} -> {url}")
    if not errors:
        ok("No unexpected external runtime assets")
    return errors


def check_images():
    referenced = set()
    for data_file in sorted((DOCS / "data").glob("characters*.json")):
        try:
            data = json.loads(data_file.read_text(encoding="utf-8"))
        except Exception:
            continue
        for item in data.values():
            image = item.get("image")
            if image:
                referenced.add(image)
    image_ref_pattern = re.compile(r"images/([^'\"()\s<>]+)")
    for path in sorted(DOCS.rglob("*.html")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        referenced.update(unquote(match) for match in image_ref_pattern.findall(text))

    warnings = 0
    for image in sorted(referenced):
        path = DOCS / "images" / image
        if not path.is_file():
            continue
        size_kb = path.stat().st_size // 1024
        if size_kb > MAX_IMAGE_KB:
            warnings += 1
            print(f"WARN image exceeds {MAX_IMAGE_KB}KB: {path.relative_to(ROOT)} ({size_kb}KB)")
    if not warnings:
        ok("Referenced image sizes are within budget")
    return 0


def check_character_images():
    errors = 0
    for data_file in sorted((DOCS / "data").glob("characters*.json")):
        data = json.loads(data_file.read_text(encoding="utf-8"))
        for item_id, item in data.items():
            image = item.get("image")
            if image and not (DOCS / "images" / image).exists():
                errors += fail(f"missing image for {item_id} in {data_file.relative_to(ROOT)}: {image}")
    if not errors:
        ok("Character image references exist")
    return errors


def check_chapters():
    errors = 0
    index_path = DOCS / "chapters" / "index.json"
    chapters = json.loads(index_path.read_text(encoding="utf-8"))
    for chapter in chapters:
        path = DOCS / "chapters" / f"chapter-{chapter['id']}.json"
        if not path.exists():
            errors += fail(f"chapter index references missing file: {path.relative_to(ROOT)}")
    if not errors:
        ok("Chapter index references exist")
    return errors


def main():
    errors = 0
    errors += check_json()
    errors += check_js()
    errors += check_external_assets()
    errors += check_images()
    errors += check_character_images()
    errors += check_chapters()
    if errors:
        print(f"\nAudit failed with {errors} error(s).")
        return 1
    print("\nAudit passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
