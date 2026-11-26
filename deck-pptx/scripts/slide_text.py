# /// script
# requires-python = ">=3.10"
# dependencies = ["python-pptx>=1.0"]
# ///
"""pptx の全ページの文言を書き出す（グループ・表の中も）。

    uv run slide_text.py <pptx> [--pages 3,5-7] [--json]
"""
import json
import sys

from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE


SLIDENUM = "{http://schemas.openxmlformats.org/drawingml/2006/main}fld"


def _paras(tf):
    """段落の文字。ページ番号のフィールド（a:fld type="slidenum"）だけの段落は外す"""
    out = []
    for p in tf.paragraphs:
        flds = [f for f in p._p.iter(SLIDENUM) if f.get("type") == "slidenum"]
        if flds and not [r for r in p.runs if r.text.strip()]:
            continue
        if p.text.strip():
            out.append(p.text)
    return out


def shape_texts(sh):
    """図形の中の段落の文字を、上から順に返す"""
    out = []
    if sh.shape_type == MSO_SHAPE_TYPE.GROUP:
        for c in sh.shapes:
            out += shape_texts(c)
    elif sh.has_table if hasattr(sh, "has_table") else False:
        for row in sh.table.rows:
            for cell in row.cells:
                if cell.is_spanned:
                    continue
                out += _paras(cell.text_frame)
    elif sh.has_text_frame:
        out += _paras(sh.text_frame)
    return out


def slide_texts(slide):
    shapes = sorted(slide.shapes, key=lambda s: ((s.top or 0), (s.left or 0)))
    out = []
    for sh in shapes:
        out += shape_texts(sh)
    return out


def pages_of(spec, n):
    if not spec:
        return list(range(1, n + 1))
    out = []
    for part in spec.split(","):
        if "-" in part:
            a, b = part.split("-")
            out += list(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return out


def main(argv):
    if not argv:
        sys.exit(__doc__)
    prs = Presentation(argv[0])
    spec = argv[argv.index("--pages") + 1] if "--pages" in argv else None
    pages = pages_of(spec, len(prs.slides))
    data = {i: slide_texts(prs.slides[i - 1]) for i in pages}
    if "--json" in argv:
        print(json.dumps(data, ensure_ascii=False, indent=1))
        return
    for i, ts in data.items():
        print(f"== {i}")
        for t in ts:
            print("  " + t.replace("\v", " / "))


if __name__ == "__main__":
    main(sys.argv[1:])
