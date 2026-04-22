#!/usr/bin/env python3
"""
md_to_json.py — 正文 Markdown → 章节 JSON 转换器

功能：
  - 解析 正文/第N章_*.md 为 reader.js 所需的 JSON 结构
  - 自动修正中文引号方向（"前引号" / "后引号" 配对）
  - 注入 prevChapter / nextChapter 导航链接
  - 生成 docs/chapters/index.json 目录索引
  - ensure_ascii=False 保证汉字直接输出，不产生 \\uXXXX 转义

用法：
  python3 md_to_json.py              # 转换所有章节
  python3 md_to_json.py --check      # 仅校验引号，不写文件
  python3 md_to_json.py 1            # 只转换第 1 章
"""

import os, re, json, sys, glob

# ── 路径配置 ────────────────────────────────────────────────────
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(SCRIPT_DIR))))
SOURCE_DIR   = os.path.join(PROJECT_ROOT, "正文")
OUTPUT_DIR   = os.path.join(PROJECT_ROOT, "docs", "chapters")

# ── 中文数字 → 阿拉伯数字 ───────────────────────────────────────
_CN = {'零':0,'一':1,'二':2,'两':2,'三':3,'四':4,'五':5,
       '六':6,'七':7,'八':8,'九':9,'十':10}

def cn_to_int(s):
    if len(s) == 1:
        return _CN.get(s, 0)
    if s[0] == '十':
        return 10 + _CN.get(s[1], 0) if len(s) > 1 else 10
    if len(s) == 2 and s[1] == '十':
        return _CN[s[0]] * 10
    if len(s) == 3:
        return _CN[s[0]] * 10 + _CN.get(s[2], 0)
    return 0

def chapter_num(filepath):
    m = re.search(r'第([一二三四五六七八九十零]+)章', os.path.basename(filepath))
    return cn_to_int(m.group(1)) if m else 9999

# ── 引号方向修正 ────────────────────────────────────────────────
def normalize_quotes(text):
    """
    将段落内所有中文双引号统一为正确的前/后配对。
    规则：遇到引号时交替分配 U+201C（前）/ U+201D（后）。
    单引号（' '）同理处理。
    """
    result = []
    dq_open = False   # 双引号状态
    sq_open = False   # 单引号状态

    for ch in text:
        if ch in ('\u201c', '\u201d'):          # 双引号
            if not dq_open:
                result.append('\u201c')
                dq_open = True
            else:
                result.append('\u201d')
                dq_open = False
        elif ch in ('\u2018', '\u2019'):         # 单引号
            if not sq_open:
                result.append('\u2018')
                sq_open = True
            else:
                result.append('\u2019')
                sq_open = False
        else:
            result.append(ch)

    return ''.join(result)

# ── Markdown 解析 ───────────────────────────────────────────────
def parse_md(filepath, chapter_id):
    with open(filepath, encoding='utf-8') as f:
        raw = f.read()

    lines = raw.splitlines()

    # 提取一级标题
    title = ''
    for line in lines:
        if line.startswith('# '):
            title = line[2:].strip()
            break
    if not title:
        title = os.path.basename(filepath).replace('.md', '')

    # 字数统计（中文字符 + 字母数字）
    word_count = len(re.findall(r'[\u4e00-\u9fa5a-zA-Z0-9]', raw))

    # 解析小节
    sections = []
    cur = None
    header_done = False

    for line in lines:
        stripped = line.strip()

        # 跳过一级标题行
        if not header_done and stripped.startswith('# '):
            header_done = True
            continue

        # 二级标题 → 新小节
        if stripped.startswith('## '):
            cur = {'heading': stripped[3:].strip(), 'paragraphs': []}
            sections.append(cur)
            continue

        # 分割线 → 无标题小节
        if stripped == '---':
            cur = {'heading': '', 'paragraphs': []}
            sections.append(cur)
            continue

        # 空行跳过
        if not stripped:
            continue

        # 普通段落
        if cur is None:
            cur = {'heading': '', 'paragraphs': []}
            sections.append(cur)

        # 修正引号后加入
        cur['paragraphs'].append(normalize_quotes(stripped))

    return {
        'id':        str(chapter_id),
        'title':     title,
        'wordCount': str(word_count),
        'sections':  sections,
    }

# ── 写 JSON ─────────────────────────────────────────────────────
def write_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ── 主流程 ──────────────────────────────────────────────────────
def main():
    check_only = '--check' in sys.argv
    target_ch  = None
    for arg in sys.argv[1:]:
        if arg.isdigit():
            target_ch = int(arg)

    md_files = sorted(glob.glob(os.path.join(SOURCE_DIR, '*.md')), key=chapter_num)
    if not md_files:
        print('❌ 找不到正文 Markdown 文件。')
        return

    all_data = []
    for i, fp in enumerate(md_files):
        cid = i + 1
        if target_ch and cid != target_ch:
            all_data.append(None)
            continue
        print(f'🔄 解析: {os.path.basename(fp)} → 第 {cid} 章')
        all_data.append(parse_md(fp, cid))

    # 补全缺失的 title/id（用于 prev/next 注入）
    for i, fp in enumerate(md_files):
        if all_data[i] is None:
            all_data[i] = {'id': str(i+1), 'title': _quick_title(fp)}

    # 注入 prev/next 导航
    total = len(all_data)
    for i, data in enumerate(all_data):
        data['prevChapter'] = (
            {'id': all_data[i-1]['id'], 'title': all_data[i-1]['title']}
            if i > 0 else None
        )
        data['nextChapter'] = (
            {'id': all_data[i+1]['id'], 'title': all_data[i+1]['title']}
            if i < total - 1 else None
        )

    # 输出
    written = 0
    for data in all_data:
        if target_ch and data['id'] != str(target_ch):
            continue
        out = os.path.join(OUTPUT_DIR, f"chapter-{data['id']}.json")
        if check_only:
            # 仅做 JSON 序列化校验，不写磁盘
            json.dumps(data, ensure_ascii=False)
            print(f'  ✅ {out} — 格式正常')
        else:
            write_json(data, out)
            print(f'  ✅ 已写入: {out}')
            written += 1

    # 更新目录索引（仅全量转换时）
    if not check_only and not target_ch:
        index = [{'id': d['id'], 'title': d['title'], 'wordCount': d.get('wordCount', '0')}
                 for d in all_data]
        idx_path = os.path.join(OUTPUT_DIR, 'index.json')
        write_json(index, idx_path)
        print(f'📦 目录索引已更新: {idx_path}')

    print(f'\n✅ 完成。共处理 {written} 个章节。' if not check_only else '\n✅ 校验完成。')

def _quick_title(filepath):
    """不做完整解析，只提取标题行。"""
    with open(filepath, encoding='utf-8') as f:
        for line in f:
            if line.startswith('# '):
                return line[2:].strip()
    return os.path.basename(filepath).replace('.md', '')

if __name__ == '__main__':
    main()
