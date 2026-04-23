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
PUBLIC_ZH_MD_DIR = PUBLIC_MD_DIR / 'zh'
PUBLIC_EN_MD_DIR = PUBLIC_MD_DIR / 'en'
ZH_JSON_FILE = DATA_DIR / 'characters_zh.json'
EN_JSON_FILE = DATA_DIR / 'characters_en.json'

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


def read_text(path):
    return path.read_text(encoding='utf-8')


def write_text_if_changed(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding='utf-8') == content:
        return
    path.write_text(content, encoding='utf-8')


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


def parse_markdown_profile(content):
    source = (content or '').replace('\r\n', '\n')
    parts = re.split(r'^##\s+', source, flags=re.MULTILINE)
    head = parts[0] if parts else source

    title_match = re.search(r'^#\s+(.*?)(?:\s+\(.*\))?$', source, re.MULTILINE)
    title = ''
    if title_match:
        title = title_match.group(1).split('——')[-1].strip()
        title = re.sub(r'^\d+_', '', title)
        title = re.sub(r'^(主角|核心配角|第一女主|第二女主|初始外挂|将领)_', '', title)
        title = re.sub(r'^将领_', '', title)
        title = title.strip('_')

    alias_match = re.search(
        r'^\*\s+\*\*(?:大宋化名|本名|姓名|称号|类型|Alias|Name|Title)\*\*[:：]\s*(.*?)(?:\*\*)?\s*$',
        source,
        re.MULTILINE,
    )
    alias = alias_match.group(1).replace('**', '').strip() if alias_match else ''

    intro = head
    intro = re.sub(r'^#.*?\n', '', intro, flags=re.MULTILINE)
    intro = re.sub(r'!\[.*?\]\(.*?\)\n?', '', intro, flags=re.MULTILINE)
    intro = re.sub(
        r'^\*\s+\*\*(?:大宋化名|本名|姓名|称号|类型|Alias|Name|Title)\*\*[:：].*(?:\n|$)',
        '',
        intro,
        flags=re.MULTILINE,
    )
    intro = clean_text(intro)
    intro = re.sub(r'^---+\s*', '', intro)
    intro = re.sub(r'---+\s*$', '', intro)
    intro = intro.strip()

    sections = []
    for part in parts[1:]:
        lines = part.split('\n')
        heading = (lines[0] if lines else '').strip()
        body = clean_text('\n'.join(lines[1:]))
        body = re.sub(r'---+\s*$', '', body).strip()
        if heading:
            sections.append({'heading': heading, 'content': body})

    return {
        'title': title,
        'alias': alias,
        'intro': intro,
        'sections': sections,
    }
def render_markdown_profile(title, alias, image, intro, sections, lang):
    lines = [f'# {title}', '']
    if image:
        image_path = f'../../../images/{image}'
        lines.append(f'![{title}]({image_path})')
        lines.append('')
    if alias:
        alias_key = '大宋化名' if lang == 'zh' else 'Alias'
        lines.append(f'*   **{alias_key}**：**{alias}**')
        lines.append('')
    if intro:
        lines.append(intro.strip())
        lines.append('')
    for section in sections or []:
        heading = section.get('heading', '').strip()
        content = (section.get('content') or '').strip()
        if heading:
            lines.append(f'## {heading}')
            lines.append('')
        if content:
            lines.append(content)
            lines.append('')
    return '\n'.join(lines).strip() + '\n'


def sync_image(entry_path, content, image_override=''):
    if image_override:
        name = os.path.basename(str(image_override))
        if (DOC_IMAGES_DIR / name).exists():
            return name
        return name

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


def normalize_public_markdown(content, image_name):
    if not image_name:
        return content
    return re.sub(
        r'!\[(.*?)\]\((.*?)\)',
        lambda match: f'![{match.group(1)}](../../../images/{image_name})',
        content,
        count=1,
    )


def parse_profile_entry(entry_path, entry_type, title_override='', alias_override='', image_override=''):
    content = read_text(entry_path)
    parsed = parse_markdown_profile(content)
    image_name = sync_image(entry_path, content, image_override)
    return {
        'title': title_override or parsed['title'],
        'alias': alias_override or parsed['alias'],
        'image': image_name,
        'intro': parsed['intro'],
        'sections': parsed['sections'],
        'type': entry_type,
        'content': content,
    }


def parse_english_profile(entry_id):
    md_path = PUBLIC_EN_MD_DIR / f'{entry_id}.md'
    if md_path.exists():
        content = read_text(md_path)
        parsed = parse_markdown_profile(content)
        return {
            'title': parsed['title'],
            'alias': parsed['alias'],
            'image': '',
            'intro': parsed['intro'],
            'sections': parsed['sections'],
            'source_path': f'content/profiles/en/{entry_id}.md',
            'content': content,
        }
    return None


def build_language_entry(profile, entry_type, source_path, image_name):
    return {
        'title': profile['title'],
        'alias': profile['alias'],
        'image': image_name,
        'intro': profile['intro'],
        'type': entry_type,
        'source': source_path,
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
    PUBLIC_ZH_MD_DIR.mkdir(parents=True, exist_ok=True)
    PUBLIC_EN_MD_DIR.mkdir(parents=True, exist_ok=True)

    zh_data = {}
    en_data = {}

    for entry in list(iter_auto_entries()) + MANUAL_ENTRIES:
        entry_id = entry['id']
        entry_path = Path(entry['path'])
        print(f'Processing profile: {entry_path.relative_to(ROOT)} -> {entry_id}')

        zh_profile = parse_profile_entry(
            entry_path=entry_path,
            entry_type=entry['type'],
            title_override=entry.get('title', ''),
            alias_override=entry.get('alias', ''),
            image_override=entry.get('image', ''),
        )
        write_text_if_changed(
            PUBLIC_ZH_MD_DIR / f'{entry_id}.md',
            normalize_public_markdown(zh_profile['content'], zh_profile['image']),
        )
        zh_data[entry_id] = build_language_entry(
            zh_profile,
            entry['type'],
            f'content/profiles/zh/{entry_id}.md',
            zh_profile['image'],
        )

        en_profile = None
        en_source_path = PUBLIC_EN_MD_DIR / f'{entry_id}.md'
        if en_source_path.exists():
            en_profile = parse_english_profile(entry_id)
            if en_profile is not None:
                en_profile['content'] = read_text(en_source_path)
                en_data[entry_id] = build_language_entry(
                    en_profile,
                    entry['type'],
                    f'content/profiles/en/{entry_id}.md',
                    zh_profile['image'],
                )
        else:
            en_data[entry_id] = build_language_entry(
                zh_profile,
                entry['type'],
                f'content/profiles/en/{entry_id}.md',
                zh_profile['image'],
            )

    with ZH_JSON_FILE.open('w', encoding='utf-8') as file_obj:
        json.dump(zh_data, file_obj, ensure_ascii=False, indent=2)
    with EN_JSON_FILE.open('w', encoding='utf-8') as file_obj:
        json.dump(en_data, file_obj, ensure_ascii=False, indent=2)

    print(f'Successfully synced {len(zh_data)} zh entries to {ZH_JSON_FILE.relative_to(ROOT)}')
    print(f'Successfully synced {len(en_data)} en entries to {EN_JSON_FILE.relative_to(ROOT)}')


if __name__ == '__main__':
    sync()
