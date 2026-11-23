"""循環＋中心＋土台＋結果の列の例（「AIを活用したプロジェクトの全体像」の本文）。

新しい図は、このファイルを source/<版>/figNN_<内容>.py に写して中身を書き換える。
同じフォルダに scripts/figlib.py を写しておく。
書き出し: scripts/render.sh figNN_<内容>.py ../../inputs/<版>/NN-<内容>.png

タイトル・リードは pptx の文字のまま残し、ここでは本文（y=TOP〜985）だけを描く。
座標は pptx のページと同じ 1920x1080。
"""
from figlib import *

PAGE = 5      # 元のページ番号
TOP = 270     # 元のページの本文の上端（リードの下。ページごとに確かめる）
out = []

C = (690, 530)
R = 250        # 循環の半径
NR = 48        # 工程の円の半径
HR = 106       # 中心（案件の情報）の半径

# 循環の軌道と作業の順序（実線の矢印）
out.append(f'<circle cx="{C[0]}" cy="{C[1]}" r="{R}" fill="none" stroke="{TRACK}" stroke-width="2"/>')
gap = math.degrees(NR / R) + 7
nodes = {"TL": 225, "TR": 315, "BR": 45, "BL": 135}
order = ["TL", "TR", "BR", "BL", "TL"]
for a, b in zip(order, order[1:]):
    a0, a1 = nodes[a] + gap, nodes[b] - gap
    if a1 < a0:
        a1 += 360
    out.append(f'<path d="{arc(C, R, a0, a1)}" {SOLID}/>')

# 中心：案件の情報（人でも AI でもないものは薄い青）
out.append(f'<circle cx="{C[0]}" cy="{C[1]}" r="{HR}" fill="{LIGHT}" stroke="{BLUE}" stroke-width="2"/>')
out.append(icon("folder", C[0], C[1] - 52, 34, BLUE, 2))
out.append(text(C[0], C[1] + 2, "案件の情報", 28, BLUE, 600, "middle"))
out += lines(C[0], C[1] + 38, ["目的・定義・決定", "タスク・成果"], 20, INK, 300, "middle", 29)


def radial(deg, r0, r1):
    x0, y0 = pt(C, r0, deg)
    x1, y1 = pt(C, r1, deg)
    return arrow(x0, y0, x1, y1, DOTTED)


# 情報の参照・更新（点線）。AI の記録・更新には人が確かめる印を付ける
out.append(radial(315, R - NR - 10, HR + 10))
bx, by = pt(C, (R - NR + HR) / 2, 315)
out.append(check_badge(bx, by))
out.append(text(bx + 26, by + 36, "更新", 18, BLUE, 600))
out.append(radial(45, HR + 10, R - NR - 10))
lx, ly = pt(C, (R - NR + HR) / 2, 45)
out.append(text(lx + 22, ly - 14, "参照", 18, BLUE, 600))

# 工程の円とラベル（人は塗り、AI は白抜き）
steps = [
    ("TL", "users", True, "① 人：会議・依頼", ["目的と判断基準を合わせる"], "end"),
    ("TR", "record", False, "② AI：記録と整理", ["人が確かめて情報を更新"], "start"),
    ("BR", "review", False, "③ AI：案とレビュー", ["情報を読み、", "下書きと一次レビュー"], "start"),
    ("BL", "judge", True, "④ 人：検証と判断", ["実行結果を確かめ、", "採否を決める"], "end"),
]
for key, ic, human, title, subs, anchor in steps:
    x, y = pt(C, R, nodes[key])
    out.append(node(x, y, NR, ic, human, 40))
    tx = x - NR - 26 if anchor == "end" else x + NR + 26
    ty = y - 6 if len(subs) == 1 else y - 20
    out.append(text(f"{tx:.1f}", f"{ty:.1f}", title, 26, BLUE, 600, anchor))
    out += lines(f"{tx:.1f}", ty + 36, subs, 21, INK, 300, anchor, 30)

# 改善の戻し先（灰色の破線）
out.append(arrow(C[0], C[1] + R + 12, C[0], C[1] + R + 66, DASHED))
out.append(text(C[0] + 22, C[1] + R + 47, "案件での改善を、組織が用意する共通の型へ戻す", 19, INK, 300))

# 循環を支えるもの（土台）
by0, bh = 850, 132
out.append(f'<rect x="96" y="{by0}" width="1194" height="{bh}" fill="{LIGHT}"/>')
out.append(f'<rect x="96" y="{by0}" width="1194" height="3" fill="{BLUE}"/>')
out.append(icon("layers", 150, by0 + 68, 46, BLUE, 2))
out.append(text(196, by0 + 50, "この循環を支えるもの", 18, SUB, 300))
out.append(text(196, by0 + 92, "組織が用意する型と支援", 30, BLUE, 600))
out.append(icon("checks", 800, by0 + 44, 28, BLUE, 2))
out.append(text(830, by0 + 52, "共通の進め方・レビュー観点", 22, INK, 300))
out.append(icon("kanban", 800, by0 + 94, 28, BLUE, 2))
out.append(text(830, by0 + 102, "プロジェクト管理・AI利用環境", 22, INK, 300))

# 結果の列（右）
out.append(f'<line x1="1336" y1="288" x2="1336" y2="740" stroke="{RULE}" stroke-width="2"/>')
qx = 1392
out.append(text(qx, 330, "目指す品質", 30, BLUE, 600))
out.append(f'<rect x="{qx}" y="348" width="48" height="3" fill="{BLUE}"/>')
quals = [("filecheck", "提出前に定義との不一致を確認"),
         ("history", "担当交代後も経緯を確認"),
         ("spread", "改善を別の案件でも使う")]
for i, (ic, s) in enumerate(quals):
    cy = 436 + i * 112
    out.append(soft(qx + 34, cy, 34, ic, 34))
    out.append(text(qx + 88, cy + 8, s, 24, INK, 300))

# 凡例（図の見方）は既定で置かない。線の意味は線のそばのラベル（「更新」「参照」など）で示す

# タイトル・リードは元のページのまま。図に合わせて変えるときだけ、依頼者に確かめてから
# write(out, page=PAGE, top=TOP, title="…", lead="…") のように渡す（pptx の文字が差し替わる）
write(out, page=PAGE, top=TOP)
