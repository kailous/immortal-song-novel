import os
import glob
import subprocess
import json

try:
    from ebooklib import epub
    import markdown
except ImportError:
    print("错误: 缺少依赖库。请先运行 'pip3 install ebooklib markdown'")
    exit(1)

def main():
    deliver_dir = "交付"
    # 获取脚本所在的当前目录，通过向上跳转 4 级到达项目根目录
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_script_dir))))
    deliver_path = os.path.join(base_dir, deliver_dir)
    
    if not os.path.exists(deliver_path):
        print(f"错误: 找不到目录 '{deliver_path}'")
        return

    # 读取 book_info.json
    info_path = os.path.join(base_dir, "book_info.json")
    if not os.path.exists(info_path):
        print(f"错误: 找不到书籍配置文件 '{info_path}'")
        return
        
    with open(info_path, "r", encoding="utf-8") as f:
        book_info = json.load(f)

    # 获取所有的 .md 文件，并根据文件名排序（01_第一章, 02_第二章...）
    md_files = sorted(glob.glob(os.path.join(deliver_path, "*.md")))
    if not md_files:
        print(f"错误: '{deliver_path}' 目录下没有找到任何 .md 文件")
        return

    print(f"🚀 发现 {len(md_files)} 个章节，正在打包组装 epub 杂志...")

    # 初始化电子书对象
    book = epub.EpubBook()
    
    # 设置元数据
    # 1. 强制统一识别码 (Identifier)，防止生成多个副本
    book.set_identifier(book_info.get("identifier", "urn:uuid:novel-xyz-default"))
    
    # 2. 注入 Schema Version 版本控制，满足 Apple Books 的版本覆盖硬性要求
    book_version = str(book_info.get("version", "1.0"))
    book.add_metadata(None, 'meta', book_version, {'property': 'schema:version'})
    
    book.set_title(book_info.get("title", "默认书名"))
    book.set_language(book_info.get("language", "zh-CN"))
    book.add_author(book_info.get("author", "未知作者"))

    # ===== 自动加载封面 =====
    title_cover_name = book_info.get("cover_image_base64", "title.cover")
    title_cover = os.path.join(base_dir, title_cover_name)
    cover_png = os.path.join(base_dir, "cover.png")
    cover_jpg = os.path.join(base_dir, "cover.jpg")
    
    if os.path.exists(title_cover):
        print(f"🤫 发现隐藏封面文本 {title_cover_name}，正在内嵌为电子书封面...")
        import base64
        img_bytes = None
        with open(title_cover, "rb") as c:
            data = c.read()
            try:
                # 尝试将它整体按 Base64 文本解码
                text_data = data.decode('utf-8').strip()
                if "\n" in text_data and ("cover" in text_data[:100] or "封面" in text_data[:100]):
                    text_data = text_data.split("\n", 1)[1].strip()
                img_bytes = base64.b64decode(text_data)
                print("   -> 成功通过 Base64 解码提取纯文本伪装封面")
            except Exception:
                # 如果解码失败，说明它是被伪装头破坏的原始二进制图片
                idx_jpg = data.find(b'\xff\xd8')
                idx_png = data.find(b'\x89PNG')
                
                real_start = -1
                if idx_jpg != -1 and idx_png != -1:
                    real_start = min(idx_jpg, idx_png)
                elif idx_jpg != -1:
                    real_start = idx_jpg
                elif idx_png != -1:
                    real_start = idx_png
                    
                if real_start > 0:
                    img_bytes = data[real_start:]
                    print("   -> 成功剥离干扰字符，解析二进制隐藏封面")
                elif real_start == -1 and b'\n' in data[:100]:
                    img_bytes = data.split(b'\n', 1)[1]
                else:
                    img_bytes = data
                    
        if img_bytes:
            # 先还原为临时图片文件
            temp_cover_path = os.path.join(base_dir, "temp_restore_cover.jpg")
            with open(temp_cover_path, "wb") as f_temp:
                f_temp.write(img_bytes)
                
            # 设置封面
            with open(temp_cover_path, "rb") as f_temp:
                book.set_cover("cover.jpg", f_temp.read())
                
            # 删除临时文件
            if os.path.exists(temp_cover_path):
                os.remove(temp_cover_path)
            print("   -> 临时图片已就地销毁，不留痕迹")
            
    elif os.path.exists(cover_png):
        print("🖼️ 发现封面 cover.png，正在自动内嵌为杂志首图...")
        with open(cover_png, "rb") as c:
            book.set_cover("image/cover.png", c.read())
    elif os.path.exists(cover_jpg):
        print("🖼️ 发现封面 cover.jpg，正在自动内嵌为杂志首图...")
        with open(cover_jpg, "rb") as c:
            book.set_cover("image/cover.jpg", c.read())

    # 定义 CSS 样式表以美化阅读体验
    style = """
        @namespace epub "http://www.idpf.org/2007/ops";
        body { font-family: "Helvetica Neue", Helvetica, Arial, "PingFang SC", "Microsoft YaHei", sans-serif; padding: 10px; line-height: 1.8; color: #333; }
        h1, h2, h3 { color: #800000; text-align: center; border-bottom: 1px dotted #ccc; padding-bottom: 10px; margin-bottom: 20px;}
        p { text-indent: 2em; text-align: justify; font-size: 1.1em; margin-bottom: 15px;}
        hr { border: 0; height: 1px; background: #ddd; margin: 30px 0; }
        strong { color: #d32f2f; } /* 强调心理与生理描写 */
    """
    
    # 添加一个默认 CSS
    default_css = epub.EpubItem(uid="style_default", file_name="style/default.css", media_type="text/css", content=style)
    book.add_item(default_css)

    chapters = []
    
    for i, file_path in enumerate(md_files):
        filename = os.path.basename(file_path)
        # 去掉文件后缀 .md 作为章节标题，例如 "01_第一章_发现新大陆"
        chapter_title = filename.replace(".md", "")
        
        with open(file_path, "r", encoding="utf-8") as f:
            md_content = f.read()
            
        # 将 Markdown 原生语法转换为 HTML
        html_content = markdown.markdown(md_content, extensions=['extra', 'nl2br'])
        
        # 创建单个电子章节对象
        chapter = epub.EpubHtml(title=chapter_title, file_name=f"chapter_{i:03d}.xhtml", lang=book_info.get("language", "zh-CN"))
        chapter.add_item(default_css)
        
        # 将 HTML 内容包装成标准的 xhtml 结构
        chapter.content = f"""
        <html>
        <head>
            <title>{chapter_title}</title>
            <link rel="stylesheet" href="style/default.css" type="text/css" />
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        book.add_item(chapter)
        chapters.append(chapter)
        print(f"✅ 已添加 -> {chapter_title}")

    # ===== 定义目录与阅读导航 =====
    book.toc = tuple(chapters)

    # 必须添加 Ncx 和 Nav 否则很多阅读器无法拉出目录面板
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # 书脊配置：定义电子书的翻页顺序
    book.spine = ["nav"] + chapters

    # ===== 输出最终文件 =====
    output_filename = book_info.get("output_filename", "全集_纯白深渊_杂志版.epub")
    output_path = os.path.join(base_dir, output_filename)
    epub.write_epub(output_path, book, {})
    
    print(f"\n🎉 打包大功告成！文件已生成在: {output_path}")
    print(f"📦 共计 {len(chapters)} 章。")
    print("💡 由于使用了恒定的 identifier，导入阅读器时将自动进行版本「覆盖更新」，不会产生新副本。如果您希望产生新书，请修改 book_info.json 中的 identifier。")

if __name__ == "__main__":
    main()
