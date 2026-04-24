#!/usr/bin/env python3

import argparse
import json
from pathlib import Path


def load_plan(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("plan must be a JSON object")
    files = data.get("files")
    if not isinstance(files, list) or not files:
        raise ValueError("plan.files must be a non-empty list")
    return data


def apply_one(text: str, item: dict):
    replace_id = item.get("id")
    find = item.get("find")
    replace = item.get("replace")
    count = item.get("count", 1)

    if not isinstance(replace_id, int):
        raise ValueError("replacement id must be an integer")
    if not isinstance(find, str) or not find:
        raise ValueError(f"replacement {replace_id}: find must be a non-empty string")
    if not isinstance(replace, str):
        raise ValueError(f"replacement {replace_id}: replace must be a string")
    if not isinstance(count, int) or count <= 0:
        raise ValueError(f"replacement {replace_id}: count must be a positive integer")

    actual = text.count(find)
    if actual < count:
        raise ValueError(
            f"replacement {replace_id}: expected at least {count} match(es), found {actual}"
        )

    new_text = text.replace(find, replace, count)
    changed = new_text != text
    if not changed:
        raise ValueError(f"replacement {replace_id}: replacement produced no change")
    return new_text


def main():
    parser = argparse.ArgumentParser(description="Apply exact text replacements from a JSON plan.")
    parser.add_argument("plan", help="Path to replacement JSON plan")
    parser.add_argument("--check", action="store_true", help="Validate only; do not write files")
    args = parser.parse_args()

    plan_path = Path(args.plan).resolve()
    plan = load_plan(plan_path)
    root = Path(plan.get("root", ".")).resolve()
    files = plan.get("files")

    if not isinstance(files, list) or not files:
        raise ValueError("plan.files must be a non-empty list")

    seen_ids = set()
    touched = []

    for file_entry in files:
        relative_path = file_entry.get("path")
        replacements = file_entry.get("replacements")
        if not isinstance(relative_path, str) or not relative_path:
            raise ValueError("each file entry must include a non-empty path")
        if not isinstance(replacements, list) or not replacements:
            raise ValueError(f"{relative_path}: replacements must be a non-empty list")

        file_path = (root / relative_path).resolve()
        original = file_path.read_text(encoding="utf-8")
        updated = original

        for item in replacements:
            replace_id = item.get("id")
            if replace_id in seen_ids:
                raise ValueError(f"duplicate replacement id: {replace_id}")
            seen_ids.add(replace_id)
            updated = apply_one(updated, item)

        if updated != original:
            touched.append(relative_path)
            if not args.check:
                file_path.write_text(updated, encoding="utf-8")

    action = "validated" if args.check else "applied"
    print(f"{action} replacements for {len(touched)} file(s):")
    for path in touched:
        print(f"- {path}")


if __name__ == "__main__":
    main()
