#!/usr/bin/env python3
import argparse
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
DEFAULT_TEMPLATE = ROOT / "资源" / "品牌" / "poster-template-overlay.png"


def find_magick() -> str:
    magick = shutil.which("magick")
    if magick:
        return magick
    convert = shutil.which("convert")
    if convert:
        return convert
    raise RuntimeError("ImageMagick not found. Install `magick` or `convert` before compositing posters.")


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


def composite(magick: str, source: Path, template: Path, output: Path) -> None:
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="将插图模板叠加到章节插图上，统一输出品牌版式。",
    )
    parser.add_argument("source", type=Path, help="原始插图路径")
    parser.add_argument("output", type=Path, help="输出路径")
    parser.add_argument(
        "--template",
        type=Path,
        default=DEFAULT_TEMPLATE,
        help=f"透明模板路径，默认 {DEFAULT_TEMPLATE.relative_to(ROOT)}",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = args.source.expanduser().resolve()
    output = args.output.expanduser().resolve()
    template = args.template.expanduser().resolve()

    if not source.exists():
        print(f"source not found: {source}", file=sys.stderr)
        return 1
    if not template.exists():
        print(f"template not found: {template}", file=sys.stderr)
        return 1

    try:
        magick = find_magick()
        composite(magick, source, template, output)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1

    try:
        source_display = source.relative_to(ROOT)
    except ValueError:
        source_display = source
    try:
        output_display = output.relative_to(ROOT)
    except ValueError:
        output_display = output
    print(f"composited {source_display} -> {output_display}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
