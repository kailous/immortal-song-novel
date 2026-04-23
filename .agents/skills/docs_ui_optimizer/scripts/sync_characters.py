import json
import os
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CHARACTER_DIR = ROOT / '设定库' / '角色'
ITEM_DIR = ROOT / '设定库' / '特殊道具'
WORLD_DIR = ROOT / '设定库' / '世界观设定'
DOC_IMAGES_DIR = ROOT / 'docs' / 'images'
DATA_DIR = ROOT / 'docs' / 'data'
PUBLIC_MD_DIR = ROOT / 'docs' / 'content' / 'profiles'
JSON_FILE = DATA_DIR / 'characters.json'

MANUAL_ENTRIES = [
    {
        'id': 'taren',
        'type': 'faction',
        'path': WORLD_DIR / '外星文明档案.md',
        'title': '塔伦人',
        'alias': '末路殖民者 · 钢铁亡命徒 · 伽南遗民',
        'image': '塔伦人.webp',
    }
]


def clean_text(text):
    text = re.sub(r'^\d+:\s*', '', text, flags=re.MULTILINE)
    return text.strip()


def extract_id(filename):
    name = Path(filename).stem
    name = re.sub(r'^\d+_', '', name)
    name = re.sub(r'^(主角|核心配角|第一女主|第二女主|初始外挂)_', '', name)
    mapping = {
        '陆辰': 'luchen',
        '陆晓晓': 'luxiaoxiao',
        '赵嬛嬛': 'zhaohuanhuan',
        '张宪': 'zhangxian',
        '李显忠': 'lixianzhong',
        '次元手环': 'bracelet',
    }
    return mapping.get(name, name)


def detect_alias(content):
    alias_match = re.search(
        r'^\*\s+\*\*(?:大宋化名|本名|姓名|称号|类型)\*\*：\s*(.*?)(?:\*\*)?\s*$',
        content,
        re.MULTILINE,
    )
    if alias_match:
        return alias_match.group(1).replace('**', '').strip()

    for line in content.splitlines():
        value = line.strip()
        if value and not value.startswith(('#', '!', '---')):
            return value
    return ''


def extract_intro(content):
    raw_sections = re.split(r'^##\s+', content, flags=re.MULTILINE)
    intro = raw_sections[0] if raw_sections else content
    intro = re.sub(r'^#.*?\n', '', intro, flags=re.MULTILINE)
    intro = re.sub(r'!\[.*?\]\(.*?\)\n?', '', intro, flags=re.MULTILINE)
    intro = re.sub(r'^\*\s+\*\*(大宋化名|本名|姓名|称号|类型)\*\*：.*(?:\n|$)', '', intro, flags=re.MULTILINE)
    intro = clean_text(intro)
    intro = re.sub(r'^---+\s*', '', intro)
    intro = re.sub(r'---+\s*$', '', intro)
    return intro.strip()


def detect_title(content, fallback=''):
    title_match = re.search(r'^#\s+(.*?)(?:\s+\(.*\))?$', content, re.MULTILINE)
    if not title_match:
        return fallback
    title = title_match.group(1).split('——')[-1].strip()
    title = re.sub(r'^\d+_', '', title)
    title = re.sub(r'^(主角|核心配角|第一女主|第二女主|初始外挂|将领)_', '', title)
    title = re.sub(r'^将领_', '', title)
    return title.strip('_') or fallback


def sync_image(entry_path, content, image_override=''):
    if image_override:
        return image_override

    img_match = re.search(r'!\[.*?\]\((.*?)\)', content)
    img_path = img_match.group(1) if img_match else ''
    img_name = os.path.basename(img_path) if img_path else ''
    if not img_path or not img_name:
        return ''

    full_img_src = (entry_path.parent / img_path).resolve()
    if not full_img_src.exists():
        print(f'  Warning: Image not found at {full_img_src}')
        return img_name

    DOC_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    webp_name = f'{Path(img_name).stem}.webp'
    if (DOC_IMAGES_DIR / webp_name).exists():
        return webp_name
    target_path = DOC_IMAGES_DIR / img_name
    if not target_path.exists() or full_img_src.stat().st_mtime > target_path.stat().st_mtime:
        print(f'  Copying image: {img_name}')
        shutil.copy2(full_img_src, target_path)
    return img_name


def build_index_entry(entry_id, entry_path, entry_type, overrides=None):
    overrides = overrides or {}
    content = entry_path.read_text(encoding='utf-8')
    image_name = sync_image(entry_path, content, overrides.get('image', ''))
    public_filename = f'{entry_id}.md'
    public_path = PUBLIC_MD_DIR / public_filename
    public_path.parent.mkdir(parents=True, exist_ok=True)
    public_path.write_text(content, encoding='utf-8')

    return {
        'title': overrides.get('title') or detect_title(content, entry_id),
        'alias': overrides.get('alias') or detect_alias(content),
        'image': image_name,
        'intro': extract_intro(content),
        'type': entry_type,
        'source': f'content/profiles/{public_filename}',
    }


def iter_auto_entries():
    if CHARACTER_DIR.exists():
        for path in sorted(CHARACTER_DIR.glob('*.md')):
            yield {
                'id': extract_id(path.name),
                'type': 'character',
                'path': path,
            }

    if ITEM_DIR.exists():
        for path in sorted(ITEM_DIR.glob('*.md')):
            yield {
                'id': extract_id(path.name),
                'type': 'item',
                'path': path,
            }


def sync():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PUBLIC_MD_DIR.mkdir(parents=True, exist_ok=True)

    all_data = {}

    for entry in list(iter_auto_entries()) + MANUAL_ENTRIES:
        entry_id = entry['id']
        entry_path = Path(entry['path'])
        print(f'Processing profile: {entry_path.relative_to(ROOT)} -> {entry_id}')
        all_data[entry_id] = build_index_entry(
            entry_id=entry_id,
            entry_path=entry_path,
            entry_type=entry['type'],
            overrides=entry,
        )

    with JSON_FILE.open('w', encoding='utf-8') as file_obj:
        json.dump(all_data, file_obj, ensure_ascii=False, indent=2)

    print(f'Successfully synced {len(all_data)} entries to {JSON_FILE.relative_to(ROOT)}')


if __name__ == '__main__':
    sync()
