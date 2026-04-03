import os
import json
import re
import glob

def parse_markdown_to_json(md_file_path, chapter_id):
    """
    将正文 Markdown 解析为符合 reader.js 规范的 JSON 结构。
    """
    with open(md_file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 提取标题 (假设首行为 # 标题)
    lines = content.splitlines()
    title = ""
    for line in lines:
        if line.startswith("# "):
            title = line.replace("# ", "").strip()
            break
    
    if not title:
        title = os.path.basename(md_file_path).replace(".md", "")

    # 计算字数 (粗略中文字符统计)
    word_count = len(re.findall(r'[\u4e00-\u9fa5a-zA-Z0-9]', content))

    # 解析小节 (基于 ## 分隔符)
    sections = []
    current_section = None
    
    # 过滤掉开头的标题行
    body_lines = []
    header_passed = False
    for line in lines:
        if line.startswith("# ") and not header_passed:
            header_passed = True
            continue
        body_lines.append(line)

    for line in body_lines:
        line = line.strip()
        if not line:
            continue
        
        # 识别小节标题 (如 ## 一 或 ---)
        if line.startswith("## "):
            heading = line.replace("## ", "").strip()
            current_section = {"heading": heading, "paragraphs": []}
            sections.append(current_section)
        elif line == "---":
            # 分隔符视为无标题的小节开始
            current_section = {"heading": "", "paragraphs": []}
            sections.append(current_section)
        else:
            if current_section is None:
                # 如果正文还没遇到标题，创建一个默认小节
                current_section = {"heading": "", "paragraphs": []}
                sections.append(current_section)
            
            # 将加粗等语法保留，reader.js 会处理 **...**
            current_section["paragraphs"].append(line)

    return {
        "id": str(chapter_id),
        "title": title,
        "wordCount": str(word_count),
        "sections": sections
    }

def main():
    # 路径配置
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_script_dir))))
    source_dir = os.path.join(project_root, "正文")
    output_dir = os.path.join(project_root, "docs", "chapters")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 获取所有章节文件
    md_files = sorted(glob.glob(os.path.join(source_dir, "*.md")))
    if not md_files:
        print("❌ 找不到正文 Markdown 文件。")
        return

    chapter_data_list = []
    for i, md_file in enumerate(md_files):
        chapter_id = i + 1
        print(f"🔄 正在解析: {os.path.basename(md_file)} (ID: {chapter_id})")
        data = parse_markdown_to_json(md_file, chapter_id)
        chapter_data_list.append(data)

    # 注入 prev/next 链接逻辑
    total = len(chapter_data_list)
    for i, data in enumerate(chapter_data_list):
        prev_data = chapter_data_list[i-1] if i > 0 else None
        next_data = chapter_data_list[i+1] if i < total - 1 else None
        
        data["prevChapter"] = {
            "id": prev_data["id"],
            "title": prev_data["title"]
        } if prev_data else None
        
        data["nextChapter"] = {
            "id": next_data["id"],
            "title": next_data["title"]
        } if next_data else None

        # 写入 JSON
        output_file = os.path.join(output_dir, f"chapter-{data['id']}.json")
        with open(output_file, "w", encoding="utf-8") as out:
            json.dump(data, out, ensure_ascii=False, indent=2)
        print(f"✅ 已生成: {output_file}")

    print(f"\n🚀 发布任务完成！共处理 {total} 个章节。")

    # 生成章节全局索引 (用于目录悬浮窗)
    index_file = os.path.join(output_dir, "index.json")
    catalog_index = [
        {"id": d["id"], "title": d["title"], "wordCount": d["wordCount"]}
        for d in chapter_data_list
    ]
    with open(index_file, "w", encoding="utf-8") as idx_out:
        json.dump(catalog_index, idx_out, ensure_ascii=False, indent=2)
    print(f"📦 已更新目录索引: {index_file}")

    print("💡 提示：请确保 docs/catalog.html 已手动更新以匹配最新章节列表。")

if __name__ == "__main__":
    main()
