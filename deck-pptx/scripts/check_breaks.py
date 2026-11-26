# /// script
# requires-python = ">=3.10"
# dependencies = ["budoux>=0.6"]
# ///
"""語の途中の折り返しと、1〜2 字だけの行を見つける。

    uv run check_breaks.py <pptx か pdf> [--pages 3,5-7]

pptx は LibreOffice（soffice）で PDF にし、pdftotext（poppler）で行ごとの文字を読む。折り返した段落ごとに、
行の切れ目が文節（BudouX で分けた区切り）の境目にあるかを見て、境目でない所（「推進チー／ム」「確／かめ」）と、
最後の行が 2 字以下の段落を出す。直すときは、文節の境目に改行（"\\n"）を入れるか、文言を短くするか、枠を広げる。

行の切れ目は LibreOffice の描画で見ている。PowerPoint は書体と字詰めが少し異なり、行末が 1〜2 字ずれることがある。
1 つでも見つかれば終了コード 1 を返す（見落としを避けるための確認で、すべて直す必要はない）。
"""
import html
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import budoux

PUNCT = set("、。，．・：；！？）」』】〕》〉）)]},.:;!?ー　 ")
OPEN = set("（「『【〔《〈([{")


def to_pdf(src: Path, out_dir: Path) -> Path:
    if src.suffix.lower() == ".pdf":
        return src
    prof = tempfile.mkdtemp()
    subprocess.run(["soffice", f"-env:UserInstallation=file://{prof}", "--headless", "--convert-to", "pdf",
                    "--outdir", str(out_dir), str(src)], check=True, capture_output=True)
    pdf = out_dir / (src.stem + ".pdf")
    if not pdf.exists():
        sys.exit("PDF にできなかった（soffice が別のプロファイルで動いているか確かめる）")
    return pdf


def blocks(pdf: Path):
    """(ページ, [(行の文字, [x0, y0, x1, y1]), …]) の並び。pdftotext -bbox-layout の block ごと"""
    out = subprocess.run(["pdftotext", "-bbox-layout", str(pdf), "-"], check=True, capture_output=True,
                         text=True).stdout
    page = 0
    for part in re.split(r"(<page\b[^>]*>)", out):
        if part.startswith("<page"):
            page += 1
            continue
        for blk in re.findall(r"<block\b.*?</block>", part, flags=re.S):
            lines = []
            for ln in re.findall(r"<line\b.*?</line>", blk, flags=re.S):
                box = [float(v) for v in re.search(r'xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)"',
                                                   ln).groups()]
                words = [html.unescape(w) for w in re.findall(r"<word\b[^>]*>(.*?)</word>", ln, flags=re.S)]
                lines.append((_join(words), box))
            if lines:
                yield page, lines


def _join(words):
    """単語をつなぐ。和文どうしの間は詰め、英数字どうしの間は空白を残す"""
    s = ""
    for w in words:
        if s and re.match(r"[A-Za-z0-9]", s[-1]) and re.match(r"[A-Za-z0-9]", w[0]):
            s += " "
        s += w
    return s


def parse_pages(spec):
    if not spec:
        return None
    pages = set()
    for part in spec.split(","):
        a, _, b = part.partition("-")
        pages |= set(range(int(a), int(b or a) + 1))
    return pages


def find(pdf: Path, pages=None):
    parser = budoux.load_default_japanese_parser()
    problems = []
    for page, rows in blocks(pdf):
        if pages and page not in pages or len(rows) < 2:
            continue
        lines = [t for t, _ in rows]
        right = max(b[2] for _, b in rows)
        # 枠の右端近くまで埋まった行のあとだけが折り返し（短い行のあとは段落の切れ目か手で入れた改行）
        wrapped = [b[2] >= right - (b[3] - b[1]) * 1.5 for _, b in rows]
        text = "".join(lines)
        bounds, pos = set(), 0
        for ph in parser.parse(text):
            pos += len(ph)
            bounds.add(pos)
        pos = 0
        for i, ln in enumerate(lines[:-1]):
            pos += len(ln)
            before, after = text[pos - 1:pos], text[pos:pos + 1]
            if not wrapped[i] or before in "-/_" or pos in bounds or before in PUNCT or after in PUNCT or before in OPEN or after in OPEN:
                continue
            if re.match(r"[A-Za-z0-9]", before) and re.match(r"[A-Za-z0-9]", after):
                problems.append((page, "英数字の途中で折り返している", f"{ln[-8:]}／{lines[i + 1][:8]}"))
                continue
            problems.append((page, "文節の途中で折り返している", f"{ln[-8:]}／{lines[i + 1][:8]}"))
        last = lines[-1].strip()
        if wrapped[-2] and 0 < len(re.sub(r"[、。，．）」]", "", last)) <= 2:
            problems.append((page, "最後の行が 2 字以下", f"{lines[-2][-8:]}／{last}"))
    return problems


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    pages = parse_pages(argv[argv.index("--pages") + 1]) if "--pages" in argv else None
    if pages:
        args = [a for a in args if a != argv[argv.index("--pages") + 1]]
    with tempfile.TemporaryDirectory() as d:
        pdf = to_pdf(Path(args[0]).resolve(), Path(d))
        ps = find(pdf, pages)
    for page, why, where in ps:
        print(f"NG {page} 枚目: {why}: {where}")
    print("OK" if not ps else f"{len(ps)} 件")
    return 1 if ps else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
