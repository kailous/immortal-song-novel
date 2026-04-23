#!/usr/bin/env python3

from pathlib import Path
import runpy


ROOT = Path(__file__).resolve().parents[4]
SCRIPT = ROOT / ".agents" / "skills" / "novel_creator" / "scripts" / "md_to_json.py"


if __name__ == "__main__":
    runpy.run_path(str(SCRIPT), run_name="__main__")
