#!/usr/bin/env python3

import argparse
import json
from pathlib import Path


def load_brief(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("brief must be a JSON object")
    required = [
        "title",
        "purpose",
        "aspect_ratio",
        "location",
        "moment",
        "composition",
        "lighting",
        "mood",
    ]
    missing = [key for key in required if not data.get(key)]
    if missing:
        raise ValueError(f"brief missing required fields: {', '.join(missing)}")
    return data


def join_subjects(subjects):
    parts = []
    for subject in subjects or []:
        name = subject.get("name", "").strip()
        role = subject.get("role", "").strip()
        traits = ", ".join(subject.get("traits", []))
        reference = subject.get("reference", "").strip()
        reference_part = f"reference: {reference}" if reference else ""
        item = ", ".join(part for part in [name, role, traits, reference_part] if part)
        if item:
            parts.append(item)
    return "; ".join(parts)


def build_prompt(brief):
    subjects = join_subjects(brief.get("subjects", []))
    must_include = ", ".join(brief.get("must_include", []))
    avoid = ", ".join(brief.get("avoid", []))
    style = brief.get("style", "写实电影风格")
    review_notes = "; ".join(brief.get("review_notes", []))

    prompt = (
        f"{brief['title']}，{brief['purpose']}，{brief['aspect_ratio']} realistic cinematic illustration, "
        f"set in {brief.get('era', '')} {brief['location']}, "
        f"moment: {brief['moment']}, "
        f"subjects: {subjects}, "
        f"composition: {brief['composition']}, "
        f"lighting: {brief['lighting']}, "
        f"mood: {brief['mood']}, "
        f"style: {style}, "
        f"must include: {must_include}, "
        f"realistic materials, strong sense of weight, film still, high narrative clarity, "
        f"characters should remain consistent with the referenced profile images and descriptions, "
        f"review focus: {review_notes}."
    )

    negative = (
        f"avoid: {avoid}, anime face, idol drama makeup, fantasy spell effects, "
        f"cheap neon sci-fi glow, plastic skin, overdesigned costume, poster collage composition, "
        f"incorrect dynasty clothing, incorrect props, extra limbs, wrong hand anatomy, "
        f"character face drift from reference."
    )
    return prompt, negative


def main():
    parser = argparse.ArgumentParser(description="Build a standard illustration prompt from a JSON brief.")
    parser.add_argument("brief", help="Path to illustration brief JSON")
    args = parser.parse_args()

    brief = load_brief(Path(args.brief).resolve())
    prompt, negative = build_prompt(brief)

    print("## 主提示词")
    print(prompt)
    print()
    print("## 负面约束")
    print(negative)


if __name__ == "__main__":
    main()
