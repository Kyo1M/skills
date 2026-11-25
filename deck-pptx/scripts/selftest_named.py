# /// script
# requires-python = ">=3.10"
# dependencies = ["python-pptx>=1.0", "lxml", "Pillow"]
# ///
"""selftest 用: テンプレートの系統でない資料（1440×810pt、題とリード文が名前付きの図形）を作り、
前回の資料から始める経路（Base.from_deck・duplicate・strip_body・set_title・set_lead・部品・import_slide・finalize）を通す。

    uv run selftest_named.py <写す元の pptx（テンプレートの系統）> <出力のフォルダ>
"""
import sys
from pathlib import Path

from pptx import Presentation
from pptx.util import Emu, Pt

sys.path.insert(0, str(Path(__file__).resolve().parent))
import parts as P  # noqa: E402
import template as T  # noqa: E402

other, out = Path(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
k = 18288000 / 1920  # 1440pt の幅の 1px


def box(slide, name, x, y, w, h, text=None, size=None, fill=None):
    sh = slide.shapes.add_textbox(Emu(int(x * k)), Emu(int(y * k)), Emu(int(w * k)), Emu(int(h * k))) if text is not None \
        else slide.shapes.add_shape(1, Emu(int(x * k)), Emu(int(y * k)), Emu(int(w * k)), Emu(int(h * k)))
    sh.name = name
    if text is not None:
        r = sh.text_frame.paragraphs[0].add_run()
        r.text = text
        r.font.size = Pt(size)
    if fill:
        sh.fill.solid()
        from pptx.dml.color import RGBColor
        sh.fill.fore_color.rgb = RGBColor.from_string(fill)
        sh.line.fill.background()
    return sh


# 前回の資料（架空）を作る
prs = Presentation()
prs.slide_width, prs.slide_height = Emu(18288000), Emu(10287000)
blank = prs.slide_layouts[6]
for i in range(2):
    s = prs.slides.add_slide(blank)
    box(s, "slide-title", 96, 68, 1730, 90, f"前回の題 {i + 1}", 40.5)
    box(s, "slide-lead", 96, 211, 1728, 120, "前回のリード文", 19.5)
    box(s, "rule-bottom", 96, 997, 1728, 2, fill="DADADA")
    box(s, "footer", 102, 1017, 700, 32, "架空の定例", 16.5)
    box(s, "body-1", 96, 349, 1728, 400, "前回の本文", 21)
prev = out / "named-prev.pptx"
prs.save(prev)

# 前回の資料から始める
base = T.Base.from_deck(prev, 1, title="slide-title", lead="slide-lead", keep=("rule-bottom", "footer"))
assert base.frame == "named" and base.body[1] == 349, base
prs = T.open_deck(prev, base=base)
S = list(prs.slides)
s = T.duplicate(prs, S[0])
T.strip_body(s)
T.set_title(s, "今回の題")
T.set_lead(s, ["今回のリード文の1行目です。", "今回のリード文の2行目です。"])
x, y, w, h = T.body_area(s)
P.cards(s, ["見出しA", "見出しB"], [["項目1"], ["項目2"]], area=(x, y, w, h / 2))
P.table(s, [["区分", "内容"], ["①", "テスト1"], ["①", "テスト2"]], x=x, y=y + h / 2 + 20, w=w, merge_first=True)
r = T.duplicate(prs, S[1])
T.strip_body(r)
T.set_title(r, "写したページ")
T.import_slide(r, other, 8, drop=lambda sh: sh.is_placeholder)  # 960pt → 1440pt（比 1.5）
T.keep_slides(prs, [S[0], s, r])
T.finalize(prs, out / "named-out.pptx", title="架空の定例")
texts = [sh.text_frame.text for sh in Presentation(out / "named-out.pptx").slides[1].shapes if sh.has_text_frame]
assert "今回の題" in texts and "架空の定例" in texts, texts
print("ok", out / "named-out.pptx")
