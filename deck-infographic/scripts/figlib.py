"""図のスクリプトで共通に使う部品（色・字・アイコン・矢印・凡例・本文だけの書き出し）。

使い方: このファイルを作業フォルダの source/<版>/ に写し、図のスクリプトで `from figlib import *` する。
座標は pptx のページと同じ 1920x1080。図のスクリプトは `python3 figNN_*.py <出力.html> [<出力.svg>]` で
呼ばれ（render.sh から）、最後に write() で本文の範囲だけを書き出す。
"""
import math
import sys
from xml.sax.saxutils import escape

BLUE = "#0035B4"
LIGHT = "#EEF3FC"
TRACK = "#D3DDF3"
INK = "#2F3437"
SUB = "#5F666D"
RULE = "#E1E6EF"
GRAY = "#6B737B"
WHITE = "#FFFFFF"

MINCHO = "'Hiragino Mincho ProN', serif"
GOTHIC = "'Hiragino Sans', 'Hiragino Kaku Gothic ProN', sans-serif"

W, H = 1920, 1080

# lucide 風の線画アイコン（24x24 の座標系）
ICONS = {
    "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/>'
             '<path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21v-1a6 6 0 0 1 6-6h4a6 6 0 0 1 6 6v1"/>',
    "record": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/>'
              '<path d="M8 13h8"/><path d="M8 17h5"/>',
    "review": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h4"/><path d="M14 2v6h6"/>'
              '<path d="M8 13h3"/><circle cx="16" cy="16" r="3.6"/><path d="m18.6 18.6 2.9 2.9"/>',
    "judge": '<path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>',
    "folder": '<path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 '
              '7.93 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z"/><path d="M7 11h10"/><path d="M7 15h6"/>',
    "layers": '<path d="m12 2 10 5-10 5L2 7z"/><path d="m2 17 10 5 10-5"/><path d="m2 12 10 5 10-5"/>',
    "checks": '<path d="m3 17 2 2 4-4"/><path d="m3 7 2 2 4-4"/><path d="M13 6h8"/><path d="M13 12h8"/>'
              '<path d="M13 18h8"/>',
    "kanban": '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M8 7v7"/><path d="M12 7v4"/>'
              '<path d="M16 7v9"/>',
    "filecheck": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/>'
                 '<path d="m9 15 2 2 4-4"/>',
    "history": '<path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/>'
               '<path d="M12 7v5l4 2"/>',
    "spread": '<circle cx="12" cy="5" r="3"/><circle cx="5" cy="19" r="3"/><circle cx="19" cy="19" r="3"/>'
              '<path d="M12 8v3"/><path d="M5 16v-2c0-.6.4-1 1-1h12c.6 0 1 .4 1 1v2"/>',
    "usercheck": '<circle cx="9" cy="7" r="4"/><path d="M3 21v-2a4 4 0 0 1 4-4h4"/><path d="m15 19 2 2 5-5"/>',
    "message": '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
    "branch": '<path d="M6 3v12"/><circle cx="18" cy="6" r="3"/><circle cx="6" cy="18" r="3"/>'
              '<path d="M18 9a9 9 0 0 1-9 9"/>',
    "list": '<path d="M9 6h12"/><path d="M9 12h12"/><path d="M9 18h12"/><path d="M4 6h.01"/>'
            '<path d="M4 12h.01"/><path d="M4 18h.01"/>',
    "eye": '<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/>',
    "upload": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="m17 8-5-5-5 5"/><path d="M12 3v12"/>',
    "pr": '<circle cx="18" cy="18" r="3"/><circle cx="6" cy="6" r="3"/><path d="M13 6h3a2 2 0 0 1 2 2v7"/>'
          '<path d="M6 9v12"/>',
    "merge": '<circle cx="18" cy="18" r="3"/><circle cx="6" cy="6" r="3"/><path d="M6 21V9a9 9 0 0 0 9 9"/>',
    "play": '<path d="M5 3l14 9-14 9V3z"/>',
    "info": '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/>',
    "code": '<path d="m16 18 6-6-6-6"/><path d="m8 6-6 6 6 6"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/>',
    "target": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
    "laptop": '<rect x="4" y="4" width="16" height="11" rx="1.5"/><path d="M2 19h20"/>',
    "cloud": '<path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z"/>',
    "database": '<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v14c0 1.66 3.58 3 8 3s8-1.34 8-3V5"/>'
                '<path d="M4 12c0 1.66 3.58 3 8 3s8-1.34 8-3"/>',
    "slides": '<rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8"/><path d="M12 17v4"/>'
              '<path d="M7 12l3-3 3 2 4-4"/>',
    "lock": '<rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
    "flag": '<path d="M4 22V4"/><path d="M4 4h12l-2 4 2 4H4"/>',
    "alert": '<path d="M12 3 2 21h20L12 3z"/><path d="M12 10v5"/><path d="M12 18h.01"/>',
    "settings": '<circle cx="12" cy="12" r="3"/><path d="M12 2v3"/><path d="M12 19v3"/><path d="m4.9 4.9 2.1 2.1"/>'
                '<path d="m17 17 2.1 2.1"/><path d="M2 12h3"/><path d="M19 12h3"/><path d="m4.9 19.1 2.1-2.1"/>'
                '<path d="m17 7 2.1-2.1"/>',
    "calendar": '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4"/><path d="M8 2v4"/><path d="M3 10h18"/>',
    "book": '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20V3H6.5A2.5 2.5 0 0 0 4 5.5z"/><path d="M4 19.5A2.5 2.5 0 0 0 6.5 22H20v-5"/>',
    "heart": '<path d="M19 14c1.5-1.5 3-3.2 3-5.5A5.5 5.5 0 0 0 12 5a5.5 5.5 0 0 0-10 3.5c0 2.3 1.5 4 3 5.5l7 7z"/>',
    "gitgraph": '<circle cx="6" cy="6" r="2.5"/><circle cx="6" cy="18" r="2.5"/><circle cx="18" cy="12" r="2.5"/>'
                '<path d="M6 8.5v7"/><path d="M8.5 6h3a4 4 0 0 1 4 4v-.5"/>',
}


def icon(name, cx, cy, size, color, sw=2.0):
    s = size / 24
    return (f'<g transform="translate({cx - size / 2:.1f} {cy - size / 2:.1f}) scale({s:.4f})" '
            f'fill="none" stroke="{color}" stroke-width="{sw / s:.2f}" stroke-linecap="round" '
            f'stroke-linejoin="round">{ICONS[name]}</g>')


def text(x, y, s, size, color=INK, weight=300, anchor="start", family=GOTHIC, extra=""):
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{weight}" '
            f'fill="{color}" text-anchor="{anchor}" {extra}>{escape(str(s))}</text>')


def tw(s, size):
    """文字列の幅の見積もり（英数字は全角の約0.6）。"""
    return sum(size * (0.6 if ord(c) < 128 else 1.0) for c in s)


def lines(x, y, rows, size, color=INK, weight=300, anchor="start", lh=None):
    lh = lh or round(size * 1.42)
    return [text(x, y + i * lh, r, size, color, weight, anchor) for i, r in enumerate(rows)]


DEFS = """<defs>
<marker id="ah" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
  <path d="M0 0 L10 5 L0 10 z" fill="#0035B4"/></marker>
<marker id="ahs" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
  <path d="M0 0 L10 5 L0 10 z" fill="#0035B4"/></marker>
<marker id="ahg" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
  <path d="M0 0 L10 5 L0 10 z" fill="#6B737B"/></marker>
</defs>"""

# 矢印の線種（作業の順序・情報の参照と更新・改善の戻し先）
SOLID = f'stroke="{BLUE}" stroke-width="4" stroke-linecap="round" marker-end="url(#ah)" fill="none"'
DOTTED = (f'stroke="{BLUE}" stroke-width="2.5" stroke-dasharray="2 6" stroke-linecap="round" '
          f'marker-end="url(#ahs)" fill="none"')
DASHED = f'stroke="{GRAY}" stroke-width="2.5" stroke-dasharray="8 6" marker-end="url(#ahg)" fill="none"'


def arrow(x0, y0, x1, y1, style=SOLID):
    return f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" {style}/>'


def shorten(x0, y0, x1, y1, a, b):
    """線分の両端を a・b だけ縮める（円の縁から矢印を出すため）。"""
    L = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    return x0 + ux * a, y0 + uy * a, x1 - ux * b, y1 - uy * b


def ai_node(x, y, r, size=None):
    """AI を白抜きの円に「AI」の字で示す。"""
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{WHITE}" stroke="{BLUE}" stroke-width="3"/>'
            + text(x, y + (size or r * 0.62) * 0.36, "AI", size or round(r * 0.62), BLUE, 600, "middle"))


def soft(x, y, r, ic, isize=None, color=BLUE, fill=LIGHT):
    """役割を持たない要素のアイコン（薄い青の円）。"""
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}"/>' + icon(ic, x, y, isize or r * 1.0, color, 2)


def node(x, y, r, ic, human, isize=None):
    """人の作業は塗り、AI の作業は白抜き。"""
    fill, ic_color = (BLUE, WHITE) if human else (WHITE, BLUE)
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="{BLUE}" stroke-width="3"/>'
            + icon(ic, x, y, isize or r * 0.85, ic_color, 2.2))


def check_badge(x, y, r=17):
    """人が確かめる印（AI の記録・更新に付ける）。"""
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{BLUE}" stroke="{WHITE}" stroke-width="3"/>'
            + icon("usercheck", x, y, r * 1.18, WHITE, 2))


def pt(c, r, deg):
    """中心 c・半径 r・角度 deg（0 度が右、時計回り）の点。"""
    a = math.radians(deg)
    return c[0] + r * math.cos(a), c[1] + r * math.sin(a)


def arc(c, r, a0, a1):
    """a0 から a1 へ時計回りの円弧の path の d。"""
    x0, y0 = pt(c, r, a0)
    x1, y1 = pt(c, r, a1)
    large = 1 if (a1 - a0) % 360 > 180 else 0
    return f"M{x0:.1f} {y0:.1f} A{r} {r} 0 {large} 1 {x1:.1f} {y1:.1f}"


def legend(x, y, kinds=("human", "ai", "check"), arrows=(("solid", "作業の順序"),), horizontal=False, extra=()):
    """図の見方（凡例）。既定では置かず、依頼者が求めたときだけ使う。kinds は塗りの説明、arrows は (線種, ラベル)。
    extra は線以外の意味のある印（フォルダの印・太字など）で、(描く関数 f(cx, cy) -> str, ラベルまでの幅, ラベル) の組。"""
    out = [text(x, y, "図の見方", 16, SUB, 600)]
    items = []
    for k in kinds:
        if k == "human":
            items.append((lambda cx, cy: f'<circle cx="{cx + 9}" cy="{cy - 6}" r="9" fill="{BLUE}"/>', 26, "人の作業"))
        elif k == "ai":
            items.append((lambda cx, cy: f'<circle cx="{cx + 9}" cy="{cy - 6}" r="8" fill="{WHITE}" '
                          f'stroke="{BLUE}" stroke-width="2.5"/>', 26, "AIの作業"))
        elif k == "check":
            items.append((lambda cx, cy: check_badge(cx + 11, cy - 6, 11), 30, "人が確認"))
    styles = {"solid": SOLID.replace('stroke-width="4"', 'stroke-width="3.5"'), "dotted": DOTTED,
              "dashed": DASHED}
    for kind, label in arrows:
        items.append(((lambda st: (lambda cx, cy: f'<line x1="{cx}" y1="{cy - 6}" x2="{cx + 46}" '
                                   f'y2="{cy - 6}" {st}/>'))(styles[kind]), 62, label))
    items += list(extra)
    cx, cy = x, y + 34
    for i, (draw, off, label) in enumerate(items):
        out.append(draw(cx, cy))
        out.append(text(cx + off, cy, label, 17, INK, 300))
        if horizontal:
            cx += off + tw(label, 17) + 34
        else:
            ncols = len(kinds)
            if i < ncols - 1:
                cx += off + tw(label, 17) + 34
            else:
                cx = x
                cy += 38
    return out


# 本文の範囲（テンプレートに合わせて変える。既定は 1920x1080 で左右 96 の余白、フッターの罫線の上まで）
BODY_X0, BODY_X1 = 96, 1824
BODY_BOTTOM = 985


def write(svg_body, page, top, title=None, lead=None, argv=None, x0=None, x1=None, bottom=None):
    """本文だけの SVG・HTML と、大きさの JSON を書く。

    座標は pptx のページと同じ 1920x1080 で、書き出すのは x=x0〜x1・y=top〜bottom の本文の範囲。
    page は元のページ番号（1 始まり）。top は元のページの本文の上端（リードの下。ページごとに異なる）。
    title・lead は pptx の文字を差し替えるときだけ渡す（既定は元のページのまま）。
    JSON は render.sh（書き出す大きさ）と build_deck.py（貼る位置・元のページ）が読む。
    """
    import json
    import os
    argv = argv or sys.argv
    x0 = BODY_X0 if x0 is None else x0
    x1 = BODY_X1 if x1 is None else x1
    bottom = BODY_BOTTOM if bottom is None else bottom
    top = int(top)
    w, h = int(x1 - x0), int(bottom - top)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
           f'viewBox="{x0} {top} {w} {h}">'
           f'<rect x="0" y="0" width="{W}" height="{H}" fill="#FFFFFF"/>{DEFS}' + "\n".join(svg_body) + "</svg>")
    html = ('<!doctype html><html><head><meta charset="utf-8"><style>html,body{margin:0;padding:0;'
            'background:#fff}svg{display:block}</style></head><body>' + svg + '</body></html>')
    import xml.dom.minidom
    xml.dom.minidom.parseString(svg.encode("utf-8"))   # 壊れた SVG を書き出さない（& や < は text() が逃がす）
    with open(argv[1], "w", encoding="utf-8") as f:
        f.write(html)
    if len(argv) > 2:
        with open(argv[2], "w", encoding="utf-8") as f:
            f.write(svg)
    meta = {"page": page, "x": x0, "top": top, "width": w, "height": h, "title": title, "lead": lead}
    with open(os.path.splitext(argv[1])[0] + ".json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
