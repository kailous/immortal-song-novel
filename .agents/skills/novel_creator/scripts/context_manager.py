import os
import argparse
import json

def get_settings(settings_dir):
    settings = {}
    for root, dirs, files in os.walk(settings_dir):
        for file in files:
            if file.endswith('.md'):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    name = os.path.relpath(path, settings_dir)
                    settings[name] = content[:500] + "..." # Snippet
    return settings

def main():
    parser = argparse.ArgumentParser(description="Novel Context Manager")
    parser.add_argument('--summary', action='store_true', help="Show settings summary")
    parser.add_argument('--check', action='store_true', help="Run consistency check (placeholder)")
    parser.add_argument('--dir', default='/Users/lipeng/Documents/Repository/new_book/设定库', help="Settings directory")
    parser.add_argument('--think-tank', default='/Users/lipeng/Documents/Repository/new_book/智囊团', help="Think Tank directory")
    parser.add_argument('--writers', default='/Users/lipeng/Documents/Repository/new_book/写手', help="Writers directory")
    
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
        print("Checking consistency...")
        # Placeholder for more advanced AI-driven or regex-driven checks
        # For now, just verifying files are readable and non-empty
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
