#!/usr/bin/env python3
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
DOCS = ROOT / "docs"
IMAGES = DOCS / "images"
DATA_FILES = [DOCS / "data" / "characters.json"]
HTML_FILES = [DOCS / "index.html"]
MIN_SOURCE_KB = 256
QUALITY = "82"


def convert_image(cwebp, path):
    target = path.with_suffix(".webp")
    if target.exists() and target.stat().st_mtime >= path.stat().st_mtime:
        return target, False
    result = subprocess.run(
        [cwebp, "-quiet", "-q", QUALITY, str(path), "-o", str(target)],
        capture_output=True,
        text=True,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or f"failed to convert {path}")
    return target, True


def update_json_refs(mapping):
    changed = []
    for data_file in DATA_FILES:
        if not data_file.exists():
            continue
        data = json.loads(data_file.read_text(encoding="utf-8"))
        touched = False
        for item in data.values():
            image = item.get("image")
            if image in mapping:
                item["image"] = mapping[image]
                touched = True
        if touched:
            data_file.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            changed.append(data_file)
    return changed


def update_html_refs(mapping):
    changed = []
    for html_file in HTML_FILES:
        if not html_file.exists():
            continue
        text = html_file.read_text(encoding="utf-8")
        updated = text
        for old, new in mapping.items():
            updated = updated.replace(f"images/{old}", f"images/{new}")
        if updated != text:
            html_file.write_text(updated, encoding="utf-8")
            changed.append(html_file)
    return changed


def main():
    cwebp = shutil.which("cwebp")
    if not cwebp:
        print("cwebp not found. Install WebP tools before running optimize-assets.")
        return 1

    mapping = {}
    converted = []
    for path in sorted(IMAGES.glob("*")):
        if path.suffix.lower() not in {".png", ".jpg", ".jpeg"}:
            continue
        if path.stat().st_size < MIN_SOURCE_KB * 1024:
            continue
        target, did_convert = convert_image(cwebp, path)
        mapping[path.name] = target.name
        if did_convert:
            converted.append(target)

    json_changed = update_json_refs(mapping)
    html_changed = update_html_refs(mapping)

    for target in converted:
        print(f"converted {target.relative_to(ROOT)}")
    for path in json_changed + html_changed:
        print(f"updated refs {path.relative_to(ROOT)}")
    print(f"optimized {len(mapping)} image reference(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
