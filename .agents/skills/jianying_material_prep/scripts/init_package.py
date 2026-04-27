#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


MEDIA_EXTS = {
    ".mp4": "video",
    ".mov": "video",
    ".mkv": "video",
    ".webm": "video",
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
    ".webp": "image",
    ".mp3": "audio",
    ".wav": "audio",
    ".m4a": "audio",
}


def infer_role(path: Path) -> str:
    parts = {p.lower() for p in path.parts}
    if "分享" in parts:
        return "share"
    if path.suffix.lower() in {".mp3", ".wav", ".m4a"}:
        return "bgm"
    if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
        return "poster"
    return "main"


def shot_from_name(path: Path) -> str:
    stem = path.stem
    digits = "".join(ch for ch in stem if ch.isdigit())
    return digits.zfill(2) if digits else stem


def build_manifest(repo_root: Path, source_dir: Path, title: str, aspect_ratio: str) -> dict:
    assets = []
    for path in sorted(source_dir.rglob("*")):
        if not path.is_file():
            continue
        media_type = MEDIA_EXTS.get(path.suffix.lower())
        if not media_type:
            continue
        rel = path.relative_to(repo_root).as_posix()
        shot = shot_from_name(path)
        role = infer_role(path)
        assets.append(
            {
                "id": f"shot-{shot}-{media_type}-{role}",
                "shot": shot,
                "type": media_type,
                "path": rel,
                "role": role,
            }
        )
    return {
        "title": title,
        "aspect_ratio": aspect_ratio,
        "source_dir": source_dir.relative_to(repo_root).as_posix(),
        "assets": assets,
    }


def build_storyboard(manifest: dict) -> list[dict]:
    preferred = {}
    for asset in manifest["assets"]:
        shot = asset["shot"]
        current = preferred.get(shot)
        if current is None:
            preferred[shot] = asset
            continue
        if current["type"] != "video" and asset["type"] == "video":
            preferred[shot] = asset

    rows = []
    for shot in sorted(preferred):
        asset = preferred[shot]
        rows.append(
            {
                "shot": shot,
                "asset_ref": asset["id"],
                "subtitle": "",
                "voiceover": "",
                "suggested_duration_sec": None,
                "notes": "",
            }
        )
    return rows


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize a jianying input package from existing trailer assets.")
    parser.add_argument("--source", required=True, help="Source media directory")
    parser.add_argument("--out", required=True, help="Output package directory")
    parser.add_argument("--title", required=True, help="Package title")
    parser.add_argument("--aspect", default="9:16", help="Aspect ratio, e.g. 9:16 or 16:9")
    args = parser.parse_args()

    repo_root = Path.cwd().resolve()
    source_dir = (repo_root / args.source).resolve() if not Path(args.source).is_absolute() else Path(args.source).resolve()
    out_dir = (repo_root / args.out).resolve() if not Path(args.out).is_absolute() else Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest = build_manifest(repo_root, source_dir, args.title, args.aspect)
    storyboard = build_storyboard(manifest)

    write_json(out_dir / "asset-manifest.json", manifest)
    write_json(out_dir / "storyboard.json", storyboard)

    (out_dir / "subtitles.srt").write_text("", encoding="utf-8")
    (out_dir / "voiceover.txt").write_text("", encoding="utf-8")
    (out_dir / "bgm-notes.md").write_text("# BGM Notes\n\n", encoding="utf-8")
    (out_dir / "edit-brief.md").write_text(
        f"# {args.title}\n\n- Aspect ratio: `{args.aspect}`\n- Source dir: `{manifest['source_dir']}`\n",
        encoding="utf-8",
    )

    print(f"Initialized jianying package: {out_dir}")
    print(f"Assets indexed: {len(manifest['assets'])}")
    print(f"Storyboard rows: {len(storyboard)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
