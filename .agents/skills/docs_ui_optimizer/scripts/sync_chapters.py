import os
import json
import re

# Configuration
MD_DIR = '正文'
JSON_DIR = 'docs/chapters'
INDEX_FILE = os.path.join(JSON_DIR, 'index.json')

def clean_paragraph(p):
    """Clean up paragraph text: remove line numbers if present, strip whitespace."""
    # Remove line numbers like "1: " or "123: " at the start of lines
    p = re.sub(r'^\d+:\s*', '', p)
    return p.strip()

def parse_markdown(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    content = "".join(lines)
    
    # Extract Title
    title_match = re.search(r'^#\s+(.*)$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else os.path.basename(file_path)
    
    # Split by sections (##)
    sections_raw = re.split(r'^##\s+', content, flags=re.MULTILINE)
    
    # The first part is usually the title and intro before the first ##
    # We'll skip it or treat it as intro if needed. 
    # For this project, let's skip the title/meta part and focus on sections.
    
    sections = []
    total_words = 0
    
    for s_raw in sections_raw[1:]: # Skip the part before the first ##
        lines = s_raw.split('\n')
        heading = lines[0].strip()
        body = "\n".join(lines[1:])
        
        # Split body into paragraphs
        paragraphs = [clean_paragraph(p) for p in re.split(r'\n\s*\n', body) if clean_paragraph(p)]
        
        sections.append({
            "heading": heading,
            "paragraphs": paragraphs
        })
        
        for p in paragraphs:
            total_words += len(p)

    return {
        "title": title,
        "wordCount": total_words,
        "sections": sections
    }

def sync():
    if not os.path.exists(JSON_DIR):
        os.makedirs(JSON_DIR)

    # Get all markdown files and sort them
    md_files = sorted([f for f in os.listdir(MD_DIR) if f.endswith('.md')])
    
    chapters_data = []

    for i, filename in enumerate(md_files):
        path = os.path.join(MD_DIR, filename)
        print(f"Processing {filename}...")
        
        data = parse_markdown(path)
        chapter_id = str(i + 1)
        data["id"] = chapter_id
        
        # Set prev/next
        data["prevChapter"] = None
        if i > 0:
            prev_data = parse_markdown(os.path.join(MD_DIR, md_files[i-1]))
            data["prevChapter"] = {"id": str(i), "title": prev_data["title"]}
            
        data["nextChapter"] = None
        if i < len(md_files) - 1:
            next_data = parse_markdown(os.path.join(MD_DIR, md_files[i+1]))
            data["nextChapter"] = {"id": str(i + 2), "title": next_data["title"]}
            
        # Save JSON
        output_path = os.path.join(JSON_DIR, f"chapter-{chapter_id}.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        chapters_data.append({
            "id": chapter_id,
            "title": data["title"]
        })

    # Update index.json
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(chapters_data, f, ensure_ascii=False, indent=2)
        
    print(f"Successfully synced {len(md_files)} chapters.")

if __name__ == "__main__":
    sync()
