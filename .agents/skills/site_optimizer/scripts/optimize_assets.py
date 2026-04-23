#!/usr/bin/env python3
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
DOCS = ROOT / "docs"
IMAGES = DOCS / "images"
MIN_SOURCE_KB = 256
QUALITY = "82"
KEEP_ORIGINALS = {"og-cover.jpg"}
TEXT_FILE_EXTENSIONS = {".html", ".json", ".md", ".css", ".js", ".txt", ".xml", ".webmanifest"}


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


def replace_image_refs(text, mapping):
    updated = text
    for old, new in mapping.items():
        updated = updated.replace(f"images/{old}", f"images/{new}")
        updated = updated.replace(f"/images/{old}", f"/images/{new}")
        updated = updated.replace(f'"{old}"', f'"{new}"')
        updated = updated.replace(f"'{old}'", f"'{new}'")
    return updated


def update_text_refs(mapping):
    changed = []
    for path in sorted(DOCS.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in TEXT_FILE_EXTENSIONS:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        updated = replace_image_refs(text, mapping)
        if updated != text:
            if path.suffix.lower() == ".json":
                payload = json.loads(updated)
                path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            else:
                path.write_text(updated, encoding="utf-8")
            changed.append(path)
    return changed


def main():
    cwebp = shutil.which("cwebp")
    if not cwebp:
        print("cwebp not found. Install WebP tools before running optimize-assets.")
        return 1

    mapping = {}
    converted = []
    deleted = []
    for path in sorted(IMAGES.glob("*")):
        if path.suffix.lower() not in {".png", ".jpg", ".jpeg"}:
            continue
        if path.name in KEEP_ORIGINALS:
            continue
        if path.stat().st_size < MIN_SOURCE_KB * 1024:
            continue
        target, did_convert = convert_image(cwebp, path)
        mapping[path.name] = target.name
        if did_convert:
            converted.append(target)

    changed_files = update_text_refs(mapping)

    for old_name, new_name in mapping.items():
        if old_name == new_name:
            continue
        source = IMAGES / old_name
        if source.exists():
            source.unlink()
            deleted.append(source)

    for target in converted:
        print(f"converted {target.relative_to(ROOT)}")
    for path in changed_files:
        print(f"updated refs {path.relative_to(ROOT)}")
    for path in deleted:
        print(f"deleted {path.relative_to(ROOT)}")
    print(f"optimized {len(mapping)} image reference(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
