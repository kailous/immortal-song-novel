import os
import argparse

# 动态解析项目根目录（脚本位于 .agents/skills/novel_creator/scripts/）
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(_SCRIPT_DIR, '..', '..', '..', '..'))

def get_settings(settings_dir):
    settings = {}
    if not os.path.isdir(settings_dir):
        return settings
    for root, dirs, files in os.walk(settings_dir):
        for file in files:
            if file.endswith('.md'):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                name = os.path.relpath(path, settings_dir)
                settings[name] = content[:500] + "..."
    return settings

def main():
    parser = argparse.ArgumentParser(description="Novel Context Manager")
    parser.add_argument('--summary', action='store_true', help="Show settings summary")
    parser.add_argument('--check', action='store_true', help="Run consistency check")
    parser.add_argument('--dir', default=os.path.join(PROJECT_ROOT, '创作', '02_设定'), help="Settings directory")
    parser.add_argument('--think-tank', default=os.path.join(PROJECT_ROOT, '创作', '03_团队', '智囊团'), help="Think Tank directory")
    parser.add_argument('--writers', default=os.path.join(PROJECT_ROOT, '创作', '03_团队', '写手'), help="Writers directory")

    args = parser.parse_args()

    if args.summary:
        settings = get_settings(args.dir)
        think_tank = get_settings(args.think_tank)
        writers = get_settings(args.writers)

        print(f"--- Setting Library Summary ({len(settings)} files) ---")
        for name, snippet in settings.items():
            print(f"\n[ {name} ]")
            print(snippet)

        print(f"\n--- Think Tank Summary ({len(think_tank)} experts) ---")
        for name, snippet in think_tank.items():
            print(f"\n[ {name} ]")
            print(snippet)

        print(f"\n--- Writers Summary ({len(writers)} lead writers) ---")
        for name, snippet in writers.items():
            print(f"\n[ {name} ]")
            print(snippet)

    if args.check:
        print(f"项目根目录: {PROJECT_ROOT}")
        print("Checking consistency...")
        settings = get_settings(args.dir)
        issues = []
        for name, content in settings.items():
            if len(content) < 10:
                issues.append(f"Warning: {name} seems very short or empty.")

        if not issues:
            print("No obvious structural issues found.")
        else:
            for issue in issues:
                print(issue)

if __name__ == "__main__":
    main()
