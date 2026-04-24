#!/usr/bin/env python3
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
SOURCE_ROOT = ROOT / "资源" / "插图"
TARGET_ROOT = ROOT / "docs" / "images" / "chapters"
TEMPLATE = ROOT / "资源" / "品牌" / "poster-template-overlay.png"


def find_magick() -> str:
    magick = shutil.which("magick")
    if magick:
        return magick
    convert = shutil.which("convert")
    if convert:
        return convert
    raise RuntimeError("ImageMagick not found. Install `magick` or `convert` before syncing posters.")


def image_size(magick: str, path: Path) -> tuple[int, int]:
    result = subprocess.run(
        [magick, "identify", "-format", "%w %h", str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or f"failed to read image size: {path}")
    width, height = result.stdout.strip().split()
    return int(width), int(height)


def composite(magick: str, source: Path, output: Path, template: Path) -> None:
    width, height = image_size(magick, template)
    output.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        magick,
        str(source),
        "-resize",
        f"{width}x{height}^",
        "-gravity",
        "center",
        "-extent",
        f"{width}x{height}",
        str(template),
        "-compose",
        "over",
        "-composite",
        str(output),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or f"failed to composite poster: {output}")


def target_for(source: Path) -> Path:
    relative = source.relative_to(SOURCE_ROOT)
    filename = relative.name.replace("-clean", "")
    return TARGET_ROOT / relative.parent / filename


def main() -> int:
    if not TEMPLATE.exists():
        print(f"template not found: {TEMPLATE}", file=sys.stderr)
        return 1

    source_files = sorted(SOURCE_ROOT.glob("chapter-*/*-clean.png"))
    if not source_files:
        print("no chapter clean sources found", file=sys.stderr)
        return 1

    try:
        magick = find_magick()
        for source in source_files:
            target = target_for(source)
            composite(magick, source, target, TEMPLATE)
            print(f"synced {source.relative_to(ROOT)} -> {target.relative_to(ROOT)}")
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
