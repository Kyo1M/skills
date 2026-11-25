# /// script
# requires-python = ">=3.10"
# dependencies = ["python-pptx>=1.0", "lxml", "Pillow"]
# ///
"""例の構成 md（example-outline.md）から、同梱のテンプレートで pptx を組む。新しい資料はこれを写して始める。

    uv run example-build.py <構成 md> <出力の pptx> [unbranded|continova]

受け方の 2 通り（サンプルの複製・レイアウト＋部品）を使う。文言は構成 md から読み、このスクリプトに書き写さない。
ページの組み方（どのページをどの部品で描くか）だけをここに書く。
"""
import os
import sys
from pathlib import Path

SKILL = Path(os.environ.get("DECK_PPTX", Path.home() / ".claude/skills/deck-pptx"))
sys.path.insert(0, str(SKILL / "scripts"))
import outline  # noqa: E402
import parts as P  # noqa: E402
import template as T  # noqa: E402

src, out = Path(sys.argv[1]), Path(sys.argv[2])
brand = sys.argv[3] if len(sys.argv) > 3 else "unbranded"
pages = {p.sid: p for p in outline.read(src)}
prs = T.open_deck(brand)
samples = list(prs.slides)  # 最後に外すサンプルのページ


def split_head(text):
    """「**見出し**：本文」→ (見出し, 本文)"""
    import re

    m = re.match(r"^\*\*(.+?)\*\*[：:]?(.*)$", text)
    return (m.group(1), m.group(2).strip()) if m else (text, "")


# S1 表紙（レイアウト）
p = pages["S1"]
s = T.new_slide(prs, "01", p.title)
T.set_text(s, 1, p.lead)

# S2 目次（サンプルの複製）。項目の数だけ残し、残りの組を外す
p = pages["S2"]
s = T.duplicate(prs, T.find_sample(prs, "目次"))
groups = [(2, 3, 4, 5), (6, 7, 8, 9), (10, 11, 12, 13), (14, 15, 16, 17), (18, 19, 20, 21), (22, 23, 24, 25)]
items = [split_head(n.text) for n in p.body]
for i, (rule, num, head, desc) in enumerate(groups):
    if i < len(items):
        P.replace_paras(P.shape(s, num), [f"{i + 1:02d}"])
        P.replace_paras(P.shape(s, head), [items[i][0]])
        P.replace_paras(P.shape(s, desc), [items[i][1]])
    else:
        for sid in (rule, num, head, desc):
            P.delete(P.shape(s, sid))

# S3 章扉（レイアウト）
p = pages["S3"]
s = T.new_slide(prs, "02", p.title)
T.set_text(s, 1, p.lead)
T.set_text(s, 10, [p.fields["kicker"]])

# S4 図＋説明（レイアウト＋部品）
p = pages["S4"]
s = T.new_slide(prs, "03", p.title, p.lead)
x, y, w, h = T.body_area(s)
head, _ = split_head(p.body[0].text)
fig = src.parent / p.figures[0]
note_text = p.body[1].text.split("：", 1)[1]
note_y = P.note(s, [note_text])
P.figure_page(s, fig, head, [c.text for c in p.body[0].children], area=(x, y, w, note_y - y - 16))

# S5 4 ステップ（主体付きのステップノード列）
p = pages["S5"]
s = T.new_slide(prs, "03", p.title, p.lead)
nodes = []
for n in p.body:
    owner, hd = split_head(n.text)
    nodes.append(dict(owner=owner, head=hd, items=[c.text for c in n.children], emph=(owner == "AI")))
P.steps(s, nodes, area=T.body_area(s))

# S6 マトリクス（行＝目指す姿・今の状態、列＝工程、最後の列は成果）
p = pages["S6"]
s = T.new_slide(prs, "03", p.title, p.lead)
rows = [split_head(n.text)[0] for n in p.body]
cols = [c.text for c in p.body[0].children]
cells = [[[g.text for g in c.children] for c in n.children] for n in p.body]
P.matrix(s, cols, rows, cells, area=T.body_area(s), outcome=True)

# S7 比較表（推奨の列を青の太字）
p = pages["S7"]
s = T.new_slide(prs, "12", p.title, p.lead)
rows = p.tables[0]
x, y, w, h = T.body_area(s)
P.table(s, rows, x=x, y=y, w=w, marks=[(r, 1) for r in range(len(rows))])

# S8 循環（サンプルの複製）
p = pages["S8"]
s = T.duplicate(prs, T.find_sample(prs, "実行と改善を循環させる"))
T.set_title(s, p.title)
T.set_lead(s, p.lead)
labels = [n.text for n in p.body]
for i, name in enumerate(["node-151", "node-152", "node-153", "node-154"]):
    P.replace_paras(P.shape(s, name), [f"{i + 1:02d}  {labels[i]}"])
P.replace_paras(P.shape(s, "text-155"), [labels[4]])

# S9 議論（見出し帯カード 2 列＋お伺いしたいこと）
p = pages["S9"]
s = T.new_slide(prs, "03", p.title, p.lead)
x, y, w, h = T.body_area(s)
ask_h = P.text_height(["x", "x"], P.S("body"), w) + 60
cards_, ask = p.body[:2], p.body[2]
P.cards(s, [split_head(n.text)[0] for n in cards_], [[c.text for c in n.children] for n in cards_],
        area=(x, y, w, h - ask_h - 40))
P.ask_box(s, [c.text for c in ask.children], head=split_head(ask.text)[0])

# S10 まとめ（サンプルの表を作り直す）
p = pages["S10"]
s = T.duplicate(prs, T.find_sample(prs, "決定事項と次のアクション"))
T.set_title(s, p.title)
T.set_lead(s, p.lead)
gf = [sh for sh in s.shapes if sh.has_table][0]
P.rebuild_table(s, gf, p.tables[0], merge_first=True)

for sm in samples:
    T.delete_slide(prs, sm)
T.finalize(prs, out, title=pages["S1"].title)
print("wrote", out)
