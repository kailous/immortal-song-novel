#!/usr/bin/env python3
import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
DOCS = ROOT / "docs"
SITE_URL = "https://immortal-song.rainforest.org.cn/"
OG_IMAGE = SITE_URL + "images/og-cover.jpg"

START = "<!-- SITE_META_START -->"
END = "<!-- SITE_META_END -->"

PAGES = {
    "index.html": {
        "description": "公元2056年，人类最后的兵王穿越时空，坠入南宋深山。一枚来自千年后的次元手环，将改写整个文明的命运。硬核科幻×重工大宋，在线阅读。",
        "og_title": "长生不死的我，在南宋点歪了科技树",
        "og_description": "人类最后的兵王穿越时空，坠入南宋。硬核科幻×重工大宋。",
        "og_type": "website",
        "url": SITE_URL,
        "extra": [
            '  <meta name="keywords" content="小说,科幻,穿越,南宋,长生不死,在线阅读,硬核科幻">',
            '  <meta name="author" content="kailous">',
        ],
    },
    "reader.html": {
        "description": "在线阅读《长生不死的我，在南宋点歪了科技树》正文章节。",
        "og_title": "阅读 — 长生不死的我，在南宋点歪了科技树",
        "og_description": "硬核科幻×重工大宋，在线阅读。",
        "og_type": "article",
    },
    "catalog.html": {
        "description": "《长生不死的我，在南宋点歪了科技树》全部章节目录，在线免费阅读。",
        "og_title": "章节目录 — 长生不死的我，在南宋点歪了科技树",
        "og_description": "从坠星深山到星海彼端，一步一步改写文明的轨迹。",
        "og_type": "website",
    },
    "characters.html": {
        "description": "《长生不死的我，在南宋点歪了科技树》主要角色与关键道具图鉴。陆辰、陆晓晓、和亲长公主、次元手环。",
        "og_title": "角色图鉴 — 长生不死的我，在南宋点歪了科技树",
        "og_description": "命运棋局中的关键落子。",
        "og_type": "website",
    },
    "character-detail.html": {
        "description": "《长生不死的我，在南宋点歪了科技树》角色与设定档案详情。",
        "og_title": "档案详情 — 长生不死的我，在南宋点歪了科技树",
        "og_description": "角色、势力与关键道具档案。",
        "og_type": "website",
    },
    "about.html": {
        "description": "《长生不死的我，在南宋点歪了科技树》创作理念、世界观简介与作者信息。硬核科幻×重工大宋。",
        "og_title": "关于本书 — 长生不死的我，在南宋点歪了科技树",
        "og_description": "重工大宋，星海怒火。",
        "og_type": "website",
    },
    "taren-font-preview.html": {
        "description": "《长生不死的我，在南宋点歪了科技树》塔伦文字体预览与译文工具。",
        "og_title": "塔伦文字 · 长生不死",
        "og_description": "塔伦文字体预览与译文工具。",
        "og_type": "website",
    },
}

MANAGED_PATTERNS = [
    r"\s*<meta name=\"description\"[^>]*>\n",
    r"\s*<meta name=\"keywords\"[^>]*>\n",
    r"\s*<meta name=\"author\"[^>]*>\n",
    r"\s*<meta property=\"og:[^\"]+\"[^>]*>\n",
    r"\s*<meta name=\"twitter:[^\"]+\"[^>]*>\n",
    r"\s*<link rel=\"icon\"[^>]*>\n",
    r"\s*<link rel=\"apple-touch-icon\"[^>]*>\n",
    r"\s*<link rel=\"manifest\"[^>]*>\n",
    r"\s*<meta name=\"theme-color\"[^>]*>\n",
    r"\s*<meta name=\"apple-mobile-web-app-[^\"]+\"[^>]*>\n",
]


def attr(value):
    return escape(value, quote=True)


def page_url(filename, page):
    if page.get("url"):
        return page["url"]
    return SITE_URL + filename


def build_block(filename, page):
    lines = [
        "  " + START,
        f'  <meta name="description" content="{attr(page["description"])}">',
        *page.get("extra", []),
        '  <link rel="icon" href="icon.png">',
        '  <link rel="apple-touch-icon" href="icons/apple-touch-icon.png">',
        '  <link rel="manifest" href="site.webmanifest">',
        f'  <link rel="canonical" href="{page_url(filename, page)}">',
        '  <meta name="theme-color" content="#0a0b0f">',
        '  <meta name="apple-mobile-web-app-title" content="长生不死">',
        '  <meta name="apple-mobile-web-app-capable" content="yes">',
        '  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">',
        f'  <meta property="og:title" content="{attr(page["og_title"])}">',
        f'  <meta property="og:description" content="{attr(page["og_description"])}">',
        f'  <meta property="og:type" content="{attr(page["og_type"])}">',
        '  <meta property="og:site_name" content="长生不死">',
        f'  <meta property="og:image" content="{OG_IMAGE}">',
        '  <meta property="og:image:width" content="1200">',
        '  <meta property="og:image:height" content="630">',
        f'  <meta property="og:url" content="{page_url(filename, page)}">',
        '  <meta name="twitter:card" content="summary_large_image">',
        f'  <meta name="twitter:title" content="{attr(page["og_title"])}">',
        f'  <meta name="twitter:description" content="{attr(page["og_description"])}">',
        f'  <meta name="twitter:image" content="{OG_IMAGE}">',
        '  <meta name="twitter:image:alt" content="长生不死的我，在南宋点歪了科技树 分享封面">',
        "  " + END,
    ]
    return "\n".join(lines)


def strip_existing_managed(text):
    text = re.sub(rf"\n?{re.escape(START)}[\s\S]*?{re.escape(END)}\n?", "\n", text)
    for pattern in MANAGED_PATTERNS:
        text = re.sub(pattern, "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def sync_page(filename, page):
    path = DOCS / filename
    text = path.read_text(encoding="utf-8")
    text = strip_existing_managed(text)
    block = build_block(filename, page)
    updated, count = re.subn(r"(  <title>.*?</title>|<title>.*?</title>)", rf"\1\n{block}", text, count=1)
    if count != 1:
        raise RuntimeError(f"Could not find title tag in {filename}")
    path.write_text(updated, encoding="utf-8")
    print(f"synced {path.relative_to(ROOT)}")


def main():
    for filename, page in PAGES.items():
        sync_page(filename, page)


if __name__ == "__main__":
    main()
