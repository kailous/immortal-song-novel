#!/usr/bin/env python3

import argparse
import json
from pathlib import Path


def load_wardrobe(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("wardrobe must be a JSON object")
    required = ["outfit_id", "character", "purpose", "era"]
    missing = [key for key in required if not data.get(key)]
    if missing:
        raise ValueError(f"wardrobe missing required fields: {', '.join(missing)}")
    return data


def build_prompt(data):
    palette = ", ".join(data.get("palette", []))
    materials = ", ".join(data.get("materials", []))
    layers = data.get("layers", {})
    layer_text = "; ".join(f"{key}: {value}" for key, value in layers.items() if value)
    accessories = ", ".join(data.get("accessories", []))
    must_keep = ", ".join(data.get("must_keep", []))
    avoid = ", ".join(data.get("avoid", []))

    prompt = (
        f"outfit_id: {data['outfit_id']}, character: {data['character']}, "
        f"purpose: {data['purpose']}, era: {data['era']}, "
        f"environment: {data.get('environment', '')}, "
        f"palette: {palette}, materials: {materials}, "
        f"layers: {layer_text}, footwear: {data.get('footwear', '')}, "
        f"accessories: {accessories}, silhouette: {data.get('silhouette', '')}, "
        f"wear and tear: {data.get('wear_and_tear', '')}, "
        f"must keep: {must_keep}."
    )

    negative = (
        f"avoid: {avoid}, incorrect dynasty clothing, overdecorated costume, "
        f"ancient idol-drama styling, fantasy robe design, clean brand-new fabric, "
        f"costume drift across scenes."
    )
    return prompt, negative


def main():
    parser = argparse.ArgumentParser(description="Build a costume prompt fragment from a JSON wardrobe file.")
    parser.add_argument("wardrobe", help="Path to wardrobe JSON")
    args = parser.parse_args()

    data = load_wardrobe(Path(args.wardrobe).resolve())
    prompt, negative = build_prompt(data)
    print("## 服装提示词片段")
    print(prompt)
    print()
    print("## 负面服装约束")
    print(negative)


if __name__ == "__main__":
    main()
