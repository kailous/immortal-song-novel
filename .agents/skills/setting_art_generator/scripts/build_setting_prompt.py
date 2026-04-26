#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="根据设定图 brief JSON 生成主提示词与负面约束。")
    parser.add_argument("brief", type=Path, help="brief JSON 路径")
    return parser.parse_args()


def load_brief(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_prompt(data: dict) -> tuple[str, str]:
    parts = [
        data.get("subject"),
        data.get("image_type"),
        data.get("view"),
        data.get("composition"),
        data.get("structure"),
        data.get("materials"),
        data.get("equipment"),
        data.get("lighting"),
        data.get("background"),
        data.get("style"),
        data.get("retain"),
        data.get("enhance"),
    ]
    prompt = ", ".join(part for part in parts if part)
    negative = ", ".join(item for item in data.get("avoid", []) if item)
    return prompt, negative


def main() -> int:
    args = parse_args()
    data = load_brief(args.brief)
    prompt, negative = build_prompt(data)
    print("### 主提示词")
    print(prompt)
    print()
    print("### 负面约束")
    print(negative)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
