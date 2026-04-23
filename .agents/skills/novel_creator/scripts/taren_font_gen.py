#!/usr/bin/env python3
"""
塔伦人文字字体生成器 — Style A（角线风格）
生成 docs/fonts/taren.otf 和 docs/fonts/taren.woff2

设计原则：
- 纯直线构成，无曲线
- 笔画原件（stroke primitives）20个，分属9个语义族
- 字形由1~4个组件按 S/H/V/Q 布局组合
- Phase 1: 生成 ~300 个字形，Unicode PUA U+E000 起
"""

import math
import random
import os
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont
from fontTools.ttLib.woff2 import compress

# ── 坐标空间 ────────────────────────────────────────────────
# 每个组件在 100×100 单位的归一化格子内定义
# 字形 EM = 1000，笔画宽 W = 8
GRID   = 100
EM     = 1000
W      = 8        # 笔画宽度（归一化空间）
ASCENDER  = 800
DESCENDER = -200

# ── 笔画原件定义 ────────────────────────────────────────────
# 每条笔画：[(x1,y1,x2,y2), ...]  坐标在 0-100 归一化空间
# 族：生命/战争/记忆/时间/技术/熄灭/共享/穿越/家园

STROKES: dict[str, list[tuple]] = {
    # ── 生命族（Life）──
    "L1": [(50,10,50,90)],                          # 垂直长线
    "L2": [(10,50,90,50)],                          # 水平长线
    "L3": [(10,10,90,90)],                          # 斜线 ↘
    "L4": [(10,90,90,10)],                          # 斜线 ↗

    # ── 战争族（War）──
    "W1": [(10,10,90,10),(90,10,50,90),(50,90,10,10)],  # 三角
    "W2": [(10,10,90,10),(90,10,90,90),(90,90,10,90),(10,90,10,10)],  # 矩形框
    "W3": [(50,10,90,50),(90,50,50,90),(50,90,10,50),(10,50,50,10)],  # 菱形框

    # ── 记忆族（Memory）──
    "M1": [(20,80,50,20),(50,20,80,80)],            # V 形
    "M2": [(20,20,50,80),(50,80,80,20)],            # 倒 V
    "M3": [(20,50,80,50),(50,20,50,80)],            # 十字

    # ── 时间族（Time）──
    "T1": [(10,90,50,10),(50,10,90,90)],            # Z 形骨架（简化）
    "T2": [(10,10,90,10),(50,10,50,90)],            # T 形
    "T3": [(10,90,90,90),(50,90,50,10)],            # 倒 T

    # ── 技术族（Tech）──
    "C1": [(10,30,10,70),(10,70,90,70),(90,70,90,30)],   # C 形（开口朝右）
    "C2": [(90,30,90,70),(90,70,10,70),(10,70,10,30)],   # 反 C
    "C3": [(10,10,90,10),(90,10,90,90),(10,90,90,90)],   # U 形

    # ── 熄灭族（Extinction）──
    "E1": [(10,10,90,90),(10,90,90,10)],            # X 形
    "E2": [(50,10,50,90),(10,50,90,50),(20,20,80,80)],  # 带对角的十字

    # ── 穿越族（Traverse）──
    "X1": [(10,50,90,50),(30,20,70,80)],            # 平行双斜
    "X2": [(50,10,50,90),(20,30,80,70)],            # 竖线＋斜线
}

STROKE_KEYS = list(STROKES.keys())

# ── 笔画 → 矩形多边形 ─────────────────────────────────────
def seg_to_quad(x1, y1, x2, y2, w):
    """将线段转换为带宽度的四边形，返回4个顶点（逆时针）"""
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy)
    if length < 1e-9:
        return None
    nx, ny = -dy / length * w / 2, dx / length * w / 2
    return [
        (x1 + nx, y1 + ny),
        (x2 + nx, y2 + ny),
        (x2 - nx, y2 - ny),
        (x1 - nx, y1 - ny),
    ]

def draw_stroke_seg(pen, x1, y1, x2, y2, ox, oy, sx, sy, w):
    """在偏移 (ox,oy)、缩放 (sx,sy) 下画一条线段"""
    def tr(px, py):
        return int(ox + px * sx), int(oy + py * sy)

    quad = seg_to_quad(x1, y1, x2, y2, w)
    if quad is None:
        return
    pts = [tr(p[0], p[1]) for p in quad]
    pen.moveTo(pts[0])
    for pt in pts[1:]:
        pen.lineTo(pt)
    pen.closePath()

def draw_component(pen, stroke_id: str, ox: float, oy: float,
                   sx: float, sy: float, w: float = W):
    """在归一化空间 offset(ox,oy) scale(sx,sy) 下画一个笔画组件"""
    segs = STROKES[stroke_id]
    for (x1, y1, x2, y2) in segs:
        draw_stroke_seg(pen, x1, y1, x2, y2, ox, oy, sx, sy, w)

# ── 布局模式 ─────────────────────────────────────────────
def layout_S(component_ids: list[str], glyph_w: int):
    """单组件铺满"""
    return [(component_ids[0], 0, 0, glyph_w / GRID, ASCENDER / GRID)]

def layout_H(component_ids: list[str], glyph_w: int):
    """左右二分"""
    half = glyph_w / 2
    scale_x = half / GRID
    scale_y = ASCENDER / GRID
    return [
        (component_ids[0], 0,    0, scale_x, scale_y),
        (component_ids[1], half, 0, scale_x, scale_y),
    ]

def layout_V(component_ids: list[str], glyph_w: int):
    """上下二分"""
    half_h = ASCENDER / 2
    scale_x = glyph_w / GRID
    scale_y = half_h / GRID
    return [
        (component_ids[0], 0, half_h, scale_x, scale_y),
        (component_ids[1], 0, 0,      scale_x, scale_y),
    ]

def layout_Q(component_ids: list[str], glyph_w: int):
    """四象限"""
    half_w = glyph_w / 2
    half_h = ASCENDER / 2
    sx, sy = half_w / GRID, half_h / GRID
    return [
        (component_ids[0], 0,      half_h, sx, sy),
        (component_ids[1], half_w, half_h, sx, sy),
        (component_ids[2], 0,      0,      sx, sy),
        (component_ids[3], half_w, 0,      sx, sy),
    ]

# ── 字形生成 ─────────────────────────────────────────────
def make_glyph(fb, glyph_name: str, codepoint: int,
               layout_fn, component_ids: list[str],
               advance_width: int = 600):
    pen = fb.setupGlyph(glyph_name, width=advance_width,
                        unicodes=[codepoint] if codepoint >= 0 else [])
    t2pen = pen  # FontBuilder.setupGlyph 返回 T2Pen 或 TTGlyphPen 包装
    # 实际上我们需要手动用 TTGlyphPen
    return layout_fn, component_ids

def build_glyph(fb_glyphs: dict, glyph_name: str, codepoint: int,
                layout_fn, component_ids: list[str],
                advance_width: int = 600):
    """返回 (glyph_name, advance_width, unicode_list, draw_callback)"""
    def draw(pen):
        for (sid, ox, oy, sx, sy) in layout_fn(component_ids, advance_width):
            draw_component(pen, sid, ox, oy, sx, sy)
    return glyph_name, advance_width, [codepoint] if codepoint >= 0 else [], draw

# ── Phase 1 字形列表生成 ──────────────────────────────────
def gen_phase1_glyphs():
    """生成 Phase 1 约 300 个字形的定义列表"""
    glyphs = []
    codepoint = 0xE000
    rng = random.Random(42)  # 固定随机种子，保证可复现

    keys = STROKE_KEYS

    # 20 个单组件字形 (S layout)
    for i, sk in enumerate(keys[:20]):
        glyphs.append(("S", [sk], codepoint))
        codepoint += 1

    # 100 个左右组合 (H layout)
    pairs = []
    for a in keys:
        for b in keys:
            if a != b:
                pairs.append((a, b))
    rng.shuffle(pairs)
    for (a, b) in pairs[:100]:
        glyphs.append(("H", [a, b], codepoint))
        codepoint += 1

    # 100 个上下组合 (V layout)
    rng.shuffle(pairs)
    for (a, b) in pairs[:100]:
        glyphs.append(("V", [a, b], codepoint))
        codepoint += 1

    # 80 个四象限 (Q layout)
    quads = []
    for a in keys[:10]:
        for b in keys[10:]:
            quads.append((a, b, rng.choice(keys), rng.choice(keys)))
    rng.shuffle(quads)
    for q in quads[:80]:
        glyphs.append(("Q", list(q), codepoint))
        codepoint += 1

    return glyphs  # list of (layout_type, [component_ids], codepoint)

# ── 主构建函数 ────────────────────────────────────────────
def build_font(output_dir: str):
    fb = FontBuilder(EM, isTTF=True)

    # 基本 name table
    fb.setupGlyphOrder([".notdef"])
    fb.setupCharacterMap({})
    fb.setupGlyf({})
    fb.setupHorizontalMetrics({".notdef": (600, 0)})
    fb.setupHorizontalHeader(ascent=ASCENDER, descent=DESCENDER)
    fb.setupNameTable({
        "familyName": "Taren",
        "styleName":  "Regular",
    })
    fb.setupOS2(sTypoAscender=ASCENDER, sTypoDescender=DESCENDER,
                usWinAscent=ASCENDER, usWinDescent=abs(DESCENDER),
                fsType=0, panose=None)
    fb.setupPost()
    fb.setupHead(unitsPerEm=EM)

    # 重新构建，这次带上所有字形
    phase1 = gen_phase1_glyphs()

    glyph_order = [".notdef"]
    cmap = {}
    metrics = {".notdef": (600, 0)}
    glyphs_data = {}

    layout_map = {"S": layout_S, "H": layout_H, "V": layout_V, "Q": layout_Q}
    AW = 600  # advance width

    for (lt, cids, cp) in phase1:
        name = f"uni{cp:04X}"
        glyph_order.append(name)
        cmap[cp] = name
        metrics[name] = (AW, 0)

        # 画字形
        pen = TTGlyphPen(None)
        fn = layout_map[lt]
        for (sid, ox, oy, sx, sy) in fn(cids, AW):
            draw_component(pen, sid, ox, oy, sx, sy)
        glyphs_data[name] = pen.glyph()

    # .notdef 空字形
    pen0 = TTGlyphPen(None)
    pen0.moveTo((50, 0))
    pen0.lineTo((550, 0))
    pen0.lineTo((550, ASCENDER))
    pen0.lineTo((50, ASCENDER))
    pen0.closePath()
    glyphs_data[".notdef"] = pen0.glyph()

    # 重建 FontBuilder
    fb2 = FontBuilder(EM, isTTF=True)
    fb2.setupGlyphOrder(glyph_order)
    fb2.setupCharacterMap(cmap)
    fb2.setupGlyf(glyphs_data)
    fb2.setupHorizontalMetrics(metrics)
    fb2.setupHorizontalHeader(ascent=ASCENDER, descent=DESCENDER)

    # 完整 name 表（满足 sfnt 安装要求）
    fb2.setupNameTable({
        "familyName":           "Taren",
        "styleName":            "Regular",
        "uniqueFontIdentifier": "Taren-Regular;1.0;2026",
        "fullName":             "Taren Regular",
        "version":              "Version 1.0",
        "psName":               "Taren-Regular",
        "copyright":            "Copyright 2026 kailous. Velkor Script Phase 1.",
        "trademark":            "",
    })

    # 完整 OS/2 表
    fb2.setupOS2(
        sTypoAscender=ASCENDER,
        sTypoDescender=DESCENDER,
        sTypoLineGap=0,
        usWinAscent=ASCENDER,
        usWinDescent=abs(DESCENDER),
        sxHeight=500,
        sCapHeight=700,
        usWeightClass=400,       # Regular
        usWidthClass=5,          # Medium / Normal
        fsType=0,                # 可自由嵌入
        fsSelection=0x40,        # bit 6 = REGULAR
        ulUnicodeRange1=0,
        ulUnicodeRange2=0,
        ulUnicodeRange3=0,
        ulUnicodeRange4=0,
        achVendID="KAIL",
    )

    # post 表：version 2.0 兼容性最好
    fb2.setupPost(keepGlyphNames=True)

    # head 表
    fb2.setupHead(unitsPerEm=EM, macStyle=0)

    os.makedirs(output_dir, exist_ok=True)
    # TTF 格式用 .ttf 扩展名，避免 macOS 混淆 OTF/CFF
    ttf_path   = os.path.join(output_dir, "taren.ttf")
    woff2_path = os.path.join(output_dir, "taren.woff2")

    fb2.font.save(ttf_path)
    print(f"[OK] 已生成 {ttf_path}  ({len(glyph_order)-1} 字形)")

    compress(ttf_path, woff2_path)
    print(f"[OK] 已生成 {woff2_path}")

    return ttf_path, woff2_path

if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "docs/fonts"
    # 切换到项目根目录
    root = os.path.dirname(os.path.abspath(__file__))
    for _ in range(4):  # 向上最多4层找到项目根
        if os.path.exists(os.path.join(root, "docs")):
            break
        root = os.path.dirname(root)
    os.chdir(root)
    build_font(out)
