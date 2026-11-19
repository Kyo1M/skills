"""循環＋中心＋土台＋結果の列の例（「AIを活用したプロジェクトの全体像」）。

新しい図はこのファイルを写して build() の中身を書き換える。
使い方: python3 example-cycle.py <出力.html> [<出力.svg>]（scripts/render.sh から呼ぶ）
"""
import math
import sys

BLUE = "#0035B4"
LIGHT = "#EEF3FC"
TRACK = "#D3DDF3"
INK = "#2F3437"
SUB = "#5F666D"
RULE = "#E1E6EF"
GRAY = "#6B737B"

MINCHO = "'Hiragino Mincho ProN', serif"
GOTHIC = "'Hiragino Sans', 'Hiragino Kaku Gothic ProN', sans-serif"

# lucide 風の線画アイコン（24x24 の座標系）
ICONS = {
    "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/>'
             '<path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
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
}


def icon(name, cx, cy, size, color, sw=2.0):
    s = size / 24
    return (f'<g transform="translate({cx - size / 2:.1f} {cy - size / 2:.1f}) scale({s:.4f})" '
            f'fill="none" stroke="{color}" stroke-width="{sw / s:.2f}" stroke-linecap="round" '
            f'stroke-linejoin="round">{ICONS[name]}</g>')


def text(x, y, s, size, color=INK, weight=300, anchor="start", family=GOTHIC, extra=""):
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{weight}" '
            f'fill="{color}" text-anchor="{anchor}" {extra}>{s}</text>')


def pt(c, r, deg):
    a = math.radians(deg)
    return c[0] + r * math.cos(a), c[1] + r * math.sin(a)


def arc(c, r, a0, a1):
    x0, y0 = pt(c, r, a0)
    x1, y1 = pt(c, r, a1)
    large = 1 if (a1 - a0) % 360 > 180 else 0
    return f"M{x0:.1f} {y0:.1f} A{r} {r} 0 {large} 1 {x1:.1f} {y1:.1f}"


def build():
    out = []
    W, H = 1920, 1080
    C = (690, 560)
    R = 250        # 循環の半径
    NR = 48        # 工程の円の半径
    HR = 106       # 中心（案件の情報）の半径

    out.append(f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>')
    out.append("""<defs>
<marker id="ah" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
  <path d="M0 0 L10 5 L0 10 z" fill="#0035B4"/></marker>
<marker id="ahs" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
  <path d="M0 0 L10 5 L0 10 z" fill="#0035B4"/></marker>
<marker id="ahg" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
  <path d="M0 0 L10 5 L0 10 z" fill="#6B737B"/></marker>
</defs>""")

    # タイトルとリード
    out.append(text(96, 122, "AIを活用したプロジェクトの全体像", 54, INK, 300, family=MINCHO))
    out.append(f'<rect x="96" y="152" width="64" height="3" fill="{BLUE}"/>')
    out.append(text(96, 214, "案件の情報をAIと共有し、人が検証と判断を担う", 28, INK, 300))

    # 循環の軌道と作業の順序（実線の矢印）
    out.append(f'<circle cx="{C[0]}" cy="{C[1]}" r="{R}" fill="none" stroke="{TRACK}" stroke-width="2"/>')
    gap = math.degrees(NR / R) + 7
    nodes = {"TL": 225, "TR": 315, "BR": 45, "BL": 135}
    order = ["TL", "TR", "BR", "BL", "TL"]
    for a, b in zip(order, order[1:]):
        a0 = nodes[a] + gap
        a1 = nodes[b] - gap
        if a1 < a0:
            a1 += 360
        out.append(f'<path d="{arc(C, R, a0, a1)}" fill="none" stroke="{BLUE}" stroke-width="4" '
                   f'stroke-linecap="round" marker-end="url(#ah)"/>')

    # 中心：案件の情報
    out.append(f'<circle cx="{C[0]}" cy="{C[1]}" r="{HR}" fill="{LIGHT}" stroke="{BLUE}" stroke-width="2"/>')
    out.append(icon("folder", C[0], C[1] - 52, 34, BLUE, 2))
    out.append(text(C[0], C[1] + 2, "案件の情報", 28, BLUE, 600, "middle"))
    out.append(text(C[0], C[1] + 38, "目的・定義・決定", 20, INK, 300, "middle"))
    out.append(text(C[0], C[1] + 67, "タスク・成果", 20, INK, 300, "middle"))

    # 情報の参照・更新（点線の矢印）
    def radial(deg, r0, r1, rev=False):
        x0, y0 = pt(C, r0, deg)
        x1, y1 = pt(C, r1, deg)
        return (f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="{BLUE}" '
                f'stroke-width="2.5" stroke-dasharray="2 6" stroke-linecap="round" marker-end="url(#ahs)"/>')
    # ② AI の記録 → 人が確かめて更新
    out.append(radial(315, R - NR - 10, HR + 10))
    bx, by = pt(C, (R - NR + HR) / 2, 315)
    out.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="17" fill="{BLUE}" stroke="#FFFFFF" stroke-width="3"/>')
    out.append(icon("usercheck", bx, by, 20, "#FFFFFF", 2))
    lx, ly = pt(C, (R - NR + HR) / 2, 315)
    out.append(text(lx + 26, ly + 36, "更新", 18, BLUE, 600))
    # ③ AI が情報を参照
    out.append(radial(45, HR + 10, R - NR - 10))
    lx, ly = pt(C, (R - NR + HR) / 2, 45)
    out.append(text(lx + 22, ly - 14, "参照", 18, BLUE, 600))

    # 工程の円とラベル
    human = dict(fill=BLUE, stroke=BLUE, ic="#FFFFFF")
    ai = dict(fill="#FFFFFF", stroke=BLUE, ic=BLUE)
    steps = [
        ("TL", "users", human, "① 人：会議・依頼", ["目的と判断基準を合わせる"], "end"),
        ("TR", "record", ai, "② AI：記録と整理", ["人が確かめて情報を更新"], "start"),
        ("BR", "review", ai, "③ AI：案とレビュー", ["情報を読み、", "下書きと一次レビュー"], "start"),
        ("BL", "judge", human, "④ 人：検証と判断", ["実行結果を確かめ、", "採否を決める"], "end"),
    ]
    for key, ic, st, title, subs, anchor in steps:
        x, y = pt(C, R, nodes[key])
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{NR}" fill="{st["fill"]}" stroke="{st["stroke"]}" '
                   f'stroke-width="3"/>')
        out.append(icon(ic, x, y, 40, st["ic"], 2.2))
        tx = x - NR - 26 if anchor == "end" else x + NR + 26
        ty = y - 6 if len(subs) == 1 else y - 20
        out.append(text(f"{tx:.1f}", f"{ty:.1f}", title, 26, BLUE, 600, anchor))
        for i, s in enumerate(subs):
            out.append(text(f"{tx:.1f}", f"{ty + 36 + i * 30:.1f}", s, 21, INK, 300, anchor))

    # 改善の戻し先（破線の矢印）
    out.append(f'<line x1="{C[0]}" y1="{C[1] + R + 12}" x2="{C[0]}" y2="{C[1] + R + 66}" stroke="{GRAY}" '
               f'stroke-width="2.5" stroke-dasharray="8 6" marker-end="url(#ahg)"/>')
    out.append(text(C[0] + 22, C[1] + R + 47, "案件での改善を、組織が用意する共通の型へ戻す", 19, INK, 300))

    # 循環を支えるもの：組織が用意する型と支援（土台）
    by0, bh = 880, 132
    out.append(f'<rect x="96" y="{by0}" width="1194" height="{bh}" fill="{LIGHT}"/>')
    out.append(f'<rect x="96" y="{by0}" width="1194" height="3" fill="{BLUE}"/>')
    out.append(icon("layers", 150, by0 + 68, 46, BLUE, 2))
    out.append(text(196, by0 + 50, "この循環を支えるもの", 18, SUB, 300))
    out.append(text(196, by0 + 92, "組織が用意する型と支援", 30, BLUE, 600))
    out.append(icon("checks", 800, by0 + 44, 28, BLUE, 2))
    out.append(text(830, by0 + 52, "共通の進め方・レビュー観点", 22, INK, 300))
    out.append(icon("kanban", 800, by0 + 94, 28, BLUE, 2))
    out.append(text(830, by0 + 102, "プロジェクト管理・AI利用環境", 22, INK, 300))

    # 目指す品質（右列）
    out.append(f'<line x1="1336" y1="318" x2="1336" y2="770" stroke="{RULE}" stroke-width="2"/>')
    qx = 1392
    out.append(text(qx, 360, "目指す品質", 30, BLUE, 600))
    out.append(f'<rect x="{qx}" y="378" width="48" height="3" fill="{BLUE}"/>')
    quals = [("filecheck", "提出前に不一致やミスを修正"),
             ("history", "担当交代後も経緯を確認"),
             ("spread", "別案件にも改善を反映")]
    for i, (ic, s) in enumerate(quals):
        cy = 466 + i * 112
        out.append(f'<circle cx="{qx + 34}" cy="{cy}" r="34" fill="{LIGHT}"/>')
        out.append(icon(ic, qx + 34, cy, 34, BLUE, 2))
        out.append(text(qx + 88, cy + 8, s, 24, INK, 300))

    # 図の見方（凡例）
    lx0, ly0 = 1392, 850
    out.append(text(lx0, ly0, "図の見方", 16, SUB, 600))
    y = ly0 + 34
    out.append(f'<circle cx="{lx0 + 9}" cy="{y - 6}" r="9" fill="{BLUE}"/>')
    out.append(text(lx0 + 26, y, "人の作業", 17, INK, 300))
    out.append(f'<circle cx="{lx0 + 129}" cy="{y - 6}" r="8" fill="#FFFFFF" stroke="{BLUE}" stroke-width="2.5"/>')
    out.append(text(lx0 + 146, y, "AIの作業", 17, INK, 300))
    out.append(f'<circle cx="{lx0 + 259}" cy="{y - 6}" r="11" fill="{BLUE}"/>')
    out.append(icon("usercheck", lx0 + 259, y - 6, 14, "#FFFFFF", 2))
    out.append(text(lx0 + 278, y, "人が確認", 17, INK, 300))
    rows = [
        (f'stroke="{BLUE}" stroke-width="3.5" marker-end="url(#ah)"', "作業の順序"),
        (f'stroke="{BLUE}" stroke-width="2.5" stroke-dasharray="2 6" stroke-linecap="round" '
         f'marker-end="url(#ahs)"', "案件の情報の参照・更新"),
        (f'stroke="{GRAY}" stroke-width="2.5" stroke-dasharray="8 6" marker-end="url(#ahg)"', "改善の戻し先"),
    ]
    for i, (style, label) in enumerate(rows):
        yy = y + 38 + i * 34
        out.append(f'<line x1="{lx0}" y1="{yy - 6}" x2="{lx0 + 46}" y2="{yy - 6}" {style}/>')
        out.append(text(lx0 + 62, yy, label, 17, INK, 300))

    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
           + "\n".join(out) + "</svg>")
    return svg


if __name__ == "__main__":
    svg = build()
    html = ('<!doctype html><html><head><meta charset="utf-8"><style>html,body{margin:0;padding:0;'
            'background:#fff}svg{display:block}</style></head><body>' + svg + '</body></html>')
    with open(sys.argv[1], "w", encoding="utf-8") as f:
        f.write(html)
    if len(sys.argv) > 2:
        with open(sys.argv[2], "w", encoding="utf-8") as f:
            f.write(svg)
