#!/usr/bin/env python3
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "资源" / "品牌" / "book-cover-portrait-realistic.png"
OUTPUT_DIR = ROOT / "资源" / "品牌" / "社交分享"

TARGETS = [
    ("douyin-share-1080x1920.png", 1080, 1920, 28, "-12x-5"),
    ("xiaohongshu-share-1242x1660.png", 1242, 1660, 24, "-10x-3"),
]


def find_magick() -> str:
    magick = shutil.which("magick")
    if magick:
        return magick
    convert = shutil.which("convert")
    if convert:
        return convert
    raise RuntimeError("ImageMagick not found. Install `magick` or `convert` before exporting social covers.")


def export_variant(
    magick: str,
    source: Path,
    output: Path,
    width: int,
    height: int,
    blur_radius: int,
    contrast: str,
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        magick,
        str(source),
        "(",
        "+clone",
        "-resize",
        f"{width}x{height}^",
        "-gravity",
        "center",
        "-extent",
        f"{width}x{height}",
        "-blur",
        f"0x{blur_radius}",
        "-brightness-contrast",
        contrast,
        ")",
        "(",
        "+clone",
        "-resize",
        f"{width}x{height}>",
        ")",
        "-gravity",
        "center",
        "-compose",
        "over",
        "-composite",
        str(output),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or f"failed to export social cover: {output}")


def main() -> int:
    if not SOURCE.exists():
        print(f"source not found: {SOURCE}", file=sys.stderr)
        return 1

    try:
        magick = find_magick()
        for filename, width, height, blur_radius, contrast in TARGETS:
            output = OUTPUT_DIR / filename
            export_variant(magick, SOURCE, output, width, height, blur_radius, contrast)
            print(f"exported {output.relative_to(ROOT)}")
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
