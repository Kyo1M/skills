# /// script
# requires-python = ">=3.10"
# dependencies = ["python-pptx>=1.0", "lxml", "Pillow"]
# ///
"""版上げの例。前回の資料を土台に、ページを並べ替え・複製・写し、文言と表と図を差し替える。

    uv run example-revise.py <前回の pptx> <写す元の pptx> <出力の pptx> <差し替えの一覧の出力.json>

前回の資料は example-build.py の出力（テンプレートの系統）を使う。テンプレートの系統でない資料を土台にするときは、
`template.py --inspect <pptx> --page <本文のあるページ>` で枠の図形の名前を確かめ、
`T.open_deck(path, base=T.Base.from_deck(path, page, title=…, lead=…, number=…, keep=(…)))` で開く。
依頼者が PowerPoint で手直しした版を土台にし、構成 md から作り直さない（手直しを消さない）。
差し替える文言は、版上げでは一覧としてこのスクリプトに書いてよい。照合は check_text.py --against で行う。
"""
import json
import os
import sys
from pathlib import Path

SKILL = Path(os.environ.get("DECK_PPTX", Path.home() / ".claude/skills/deck-pptx"))
sys.path.insert(0, str(SKILL / "scripts"))
import parts as P  # noqa: E402
import template as T  # noqa: E402

prev, other, out, changes_out = (Path(a) for a in sys.argv[1:5])
prs = T.open_deck(prev)
S = list(prs.slides)
report = []

# 骨格: 章扉（3 枚目）を外し、議論（9 枚目）を比較表（7 枚目）の前へ。4 枚目を複製して「前回からの変化」のページにする
extra = T.duplicate(prs, S[3], report=report)
T.keep_slides(prs, [S[0], S[1], S[3], extra, S[4], S[5], S[8], S[6], S[7], S[9]])
S = list(prs.slides)

# 3 枚目（元の 4 枚目）: リード文の 1 行目を差し替え、図を差し替える
lead = T.frame_shape(S[2], 1)
P.replace_paras(lead, ["一次回答までの時間の{強:6割}が、資料を探す時間に使われています。",
                       "資料が置き場ごとに分かれ、同じ質問に担当者ごとに異なる資料で答えています。"])
pic = [sh for sh in S[2].shapes if sh.shape_type == 13][0]
P.replace_picture(S[2], pic, SKILL / "references" / "example-bars.png")

# 4 枚目（複製）: 本文を外し、別の資料の 8 枚目（循環の図）を写す。題とリード文を差し替える
T.strip_body(S[3])
T.set_title(S[3], "前回からの変化")
T.set_lead(S[3], ["回し方の図は前回の資料から写しています。"])
T.import_slide(S[3], other, 8, drop=lambda sh: sh.is_placeholder, report=report)

# 8 枚目（元の 7 枚目）: 比較表の値を書式のまま差し替える
gf = [sh for sh in S[7].shapes if sh.has_table][0]
P.set_cell(gf, 3, 2, "中")

T.finalize(prs, out, title="社内ナレッジ検索ツール導入のご提案（改訂）")
changes = {"pages": {
    "1": {"from": 1}, "2": {"from": 2},
    "3": {"from": 4, "replace": [["半分以上が、資料を探す時間", "6割が、資料を探す時間"]]},
    "4": {"new": True, "texts": ["前回からの変化", "回し方の図は前回の資料から写しています。", "計画する", "使われ方と回答の質"]},
    "5": {"from": 5}, "6": {"from": 6}, "7": {"from": 9},
    "8": {"from": 7, "replace": [["低", "中"]]},
    "9": {"from": 8}, "10": {"from": 10},
}}
changes_out.write_text(json.dumps(changes, ensure_ascii=False, indent=1), encoding="utf-8")
for r in report:
    print("note:", r)
print("wrote", out)
