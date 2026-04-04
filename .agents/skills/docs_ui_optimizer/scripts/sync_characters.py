import os
import json
import re
import shutil

# Configuration
CHARACTER_DIR = '设定库/角色'
ITEM_DIR = '设定库/特殊道具'
DOC_IMAGES_DIR = 'docs/images'
DATA_DIR = 'docs/data'
JSON_FILE = os.path.join(DATA_DIR, 'characters.json')

def clean_text(text):
    """Clean up text: remove markdown artifacts, handle line numbers if any."""
    text = re.sub(r'^\d+:\s*', '', text, flags=re.MULTILINE)
    return text.strip()

def extract_id(filename):
    """Extract a clean ID from the filename (e.g., '01_主角_陆辰.md' -> 'luchen')."""
    name = os.path.splitext(filename)[0]
    # Remove numbering like '01_'
    name = re.sub(r'^\d+_', '', name)
    # Remove classification like '主角_' or '核心配角_'
    name = re.sub(r'^(主角|核心配角|第一女主|第二女主|初始外挂)_', '', name)
    
    # Simple mapping for common characters
    mapping = {
        '陆辰': 'luchen',
        '陆晓晓': 'luxiaoxiao',
        '赵嬛嬛': 'zhaohuanhuan',
        '张宪': 'zhangxian',
        '李显忠': 'lixianzhong',
        '次元手环': 'bracelet'
    }
    return mapping.get(name, name)

def parse_profile(file_path, type='character'):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract Title (e.g., # 主角核心档案：【时空守望者】—— 陆辰 (Lu Chen))
    title_match = re.search(r'^#\s+(.*?)(?:\s+\(.*\))?$', content, re.MULTILINE)
    if title_match:
        title = title_match.group(1).split('——')[-1].strip()
        # Remove metadata like '02_核心配角_将领_'
        title = re.sub(r'^\d+_', '', title)
        title = re.sub(r'^(主角|核心配角|第一女主|第二女主|初始外挂|将领)_', '', title, flags=re.MULTILINE)
        title = re.sub(r'^(主角|核心配角|第一女主|第二女主|初始外挂|将领)_', '', title, flags=re.MULTILINE)
        title = title.strip('_')
    else:
        title = ""
    
    # Extract Alias/Subtitle
    alias = ""
    # Look for known metadata keys: 大宋化名, 本名, 姓名, 称号, 类型
    alias_match = re.search(r'\*\s+\*\*(?:大宋化名|本名|姓名|称号|类型)\*\*：\s*(.*?)(?:\*\*)?\s*$', content, re.MULTILINE)
    if alias_match:
        # Clean up possible trailing bold markers and leading/trailing whitespace
        alias = alias_match.group(1).replace('**', '').strip()
    
    if not alias:
        # Fallback for simple items that don't use the metadata list
        # Skip headers, images, and empty lines
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('!') and not line.startswith('---'):
                alias = line
                break

    # Image handling: Copy image to docs/images
    img_match = re.search(r'!\[.*?\]\((.*?)\)', content)
    img_path = img_match.group(1) if img_match else ""
    img_name = os.path.basename(img_path) if img_path else ""
    
    if img_path and img_name:
        # Resolve path relative to the md file
        full_img_src = os.path.normpath(os.path.join(os.path.dirname(file_path), img_path))
        if os.path.exists(full_img_src):
            target_path = os.path.join(DOC_IMAGES_DIR, img_name)
            # Only copy if it doesn't exist or is newer
            if not os.path.exists(target_path) or os.path.getmtime(full_img_src) > os.path.getmtime(target_path):
                print(f"  Copying image: {img_name}")
                shutil.copy2(full_img_src, target_path)
        else:
            print(f"  Warning: Image not found at {full_img_src}")

    # Split into sections
    sections = []
    # Split by ## headers, keeping headers
    raw_sections = re.split(r'^##\s+', content, flags=re.MULTILINE)
    
    # Summary/Intro (before first ##)
    intro = ""
    if len(raw_sections) > 0:
        # Remove the # title and image before intro
        intro = raw_sections[0]
        intro = re.sub(r'^#.*?\n', '', intro, flags=re.MULTILINE)
        intro = re.sub(r'!\[.*?\]\(.*?\)\n', '', intro, flags=re.MULTILINE)
        # Remove alias/本名 lines from intro if they were already extracted
        intro = re.sub(r'^\*\s+\*\*(大宋化名|本名|姓名)\*\*：.*?\n', '', intro, flags=re.MULTILINE)
        intro = clean_text(intro)
        # Strip trailing/leading separators
        intro = re.sub(r'^---+\s*', '', intro)
        intro = re.sub(r'---+\s*$', '', intro)
        intro = intro.strip()

    for s in raw_sections[1:]:
        lines = s.split('\n')
        heading = lines[0].strip()
        body = clean_text("\n".join(lines[1:]))
        
        # Strip trailing "---" if found (separator in some files)
        body = re.sub(r'---+\s*$', '', body)
        
        sections.append({
            "heading": heading,
            "content": body
        })

    return {
        "title": title,
        "alias": alias,
        "image": img_name,
        "intro": intro,
        "sections": sections,
        "type": type
    }

def sync():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if not os.path.exists(DOC_IMAGES_DIR):
        os.makedirs(DOC_IMAGES_DIR)

    all_data = {}

    # Process Characters
    if os.path.exists(CHARACTER_DIR):
        for f in sorted(os.listdir(CHARACTER_DIR)):
            if f.endswith('.md'):
                char_id = extract_id(f)
                print(f"Processing character: {f} -> {char_id}")
                all_data[char_id] = parse_profile(os.path.join(CHARACTER_DIR, f), type='character')

    # Process Items
    if os.path.exists(ITEM_DIR):
        for f in sorted(os.listdir(ITEM_DIR)):
            if f.endswith('.md'):
                item_id = extract_id(f)
                print(f"Processing item: {f} -> {item_id}")
                all_data[item_id] = parse_profile(os.path.join(ITEM_DIR, f), type='item')

    # Save to JSON
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    print(f"Successfully synced {len(all_data)} entries to {JSON_FILE}")

if __name__ == "__main__":
    sync()
