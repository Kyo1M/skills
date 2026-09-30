#!/usr/bin/env python3
"""Markdown を docx にする（画像を埋め込む）。元の md は変えない。

使い方:
    python3 md_to_docx.py <md> --list
        画像の参照の一覧（番号・キャプション・パス・存在）を出す
    python3 md_to_docx.py <md> --out <docx> [--exclude 2 3] [--root <リポジトリの root>] [--reference-doc <docx>] [--no-borders]
        docx を作り、見出し・表・画像の数を md と照合する

- frontmatter は消す（Doc の表題が二重になるため）
- 画像は `![cap](path)`（md のフォルダ基準）と `[FIG] path`（--root 基準、既定は git の root、git でなければ md のフォルダ）の 2 形式を読む
- 表には罫線を直接付ける（--no-borders で付けない）
- 照合で数が合わなければ終了コード 1
- pandoc が要る（brew install pandoc）
"""

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

FRONTMATTER = re.compile(r"\A---\n.*?\n---\n", re.S)
MD_IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
FIG_LINE = re.compile(r"^\[FIG\][ \t]+(\S+\.(?:png|jpe?g|gif|svg))[ \t]*$", re.M | re.I)
HEADING = re.compile(r"^#{1,6} ", re.M)
TABLE_SEPARATOR = re.compile(r"^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$", re.M)


def strip_code_blocks(text: str) -> str:
    return re.sub(r"^```.*?^```", "", text, flags=re.S | re.M)


def git_root(directory: Path) -> Path:
    """[FIG] の基準。git のリポジトリなら root、そうでなければ md のフォルダ"""
    result = subprocess.run(
        ["git", "-C", str(directory), "rev-parse", "--show-toplevel"], capture_output=True, text=True
    )
    return Path(result.stdout.strip()) if result.returncode == 0 else directory


def find_images(text: str, md_dir: Path, root: Path):
    images = []
    for match in re.finditer(f"{MD_IMAGE.pattern}|{FIG_LINE.pattern}", text, re.M | re.I):
        if match.group(0).startswith("!"):
            caption, raw = match.group(1), match.group(2)
            path = (md_dir / raw).resolve()
        else:
            raw = match.group(3)
            caption = ""
            path = (root / raw).resolve()
        images.append({"span": match.span(), "caption": caption, "raw": raw, "path": path})
    for number, image in enumerate(images, start=1):
        image["number"] = number
    return images


def build_copy(text: str, images, exclude: set[int]) -> str:
    pieces, cursor = [], 0
    for image in images:
        start, end = image["span"]
        pieces.append(text[cursor:start])
        if image["number"] not in exclude:
            pieces.append(f"![{image['caption']}]({image['path']})")
        cursor = end
    pieces.append(text[cursor:])
    return "".join(pieces)


BORDERS = "<w:tblBorders>" + "".join(
    f'<w:{side} w:val="single" w:sz="4" w:space="0" w:color="999999"/>'
    for side in ("top", "left", "bottom", "right", "insideH", "insideV")
) + "</w:tblBorders>"


def add_table_borders(docx: Path) -> None:
    """表に罫線を直接付ける（pandoc の既定の表には罫線が無く、Google Docs でも罫線なしになるため）"""
    with zipfile.ZipFile(docx) as source:
        items = [(info, source.read(info.filename)) for info in source.infolist()]
    with zipfile.ZipFile(docx, "w", zipfile.ZIP_DEFLATED) as target:
        for info, data in items:
            if info.filename == "word/document.xml":
                xml = data.decode()
                # tblBorders は tblW の後、tblLook の前に置く（OOXML の要素の順番）
                xml = re.sub(r"(<w:tblPr>(?:(?!</w:tblPr>).)*?<w:tblW [^>]*/>)", r"\1" + BORDERS, xml)
                data = xml.encode()
            target.writestr(info, data)


def count_structure(markdown: str) -> dict:
    body = strip_code_blocks(markdown)
    return {
        "見出し": len(HEADING.findall(body)),
        "表": len(TABLE_SEPARATOR.findall(body)),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("md")
    parser.add_argument("--out")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--exclude", type=int, nargs="*", default=[])
    parser.add_argument("--root")
    parser.add_argument("--reference-doc")
    parser.add_argument("--no-borders", action="store_true", help="表に罫線を付けない（--reference-doc の書式に任せるとき）")
    args = parser.parse_args()

    md_path = Path(args.md).resolve()
    if not md_path.exists():
        print(f"md がありません: {md_path}", file=sys.stderr)
        return 2
    text = FRONTMATTER.sub("", md_path.read_text(), count=1)
    root = Path(args.root).resolve() if args.root else git_root(md_path.parent)
    images = find_images(text, md_path.parent, root)

    if args.list or not args.out:
        print("| # | キャプション | パス | 存在 |")
        print("|---|---|---|---|")
        for image in images:
            exists = "OK" if image["path"].exists() else "無い"
            print(f"| {image['number']} | {image['caption'] or '(無し)'} | {image['raw']} | {exists} |")
        return 0

    if not shutil.which("pandoc"):
        print("pandoc がありません（brew install pandoc）", file=sys.stderr)
        return 2
    exclude = set(args.exclude)
    missing = [i for i in images if i["number"] not in exclude and not i["path"].exists()]
    if missing:
        for image in missing:
            print(f"画像がありません: #{image['number']} {image['raw']}", file=sys.stderr)
        return 2

    copy = build_copy(text, images, exclude)
    out = Path(args.out).expanduser().resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as work:
        copy_path = Path(work) / "copy.md"
        copy_path.write_text(copy)
        command = ["pandoc", str(copy_path), "-f", "gfm+implicit_figures", "-o", str(out)]
        if args.reference_doc:
            command += ["--reference-doc", str(Path(args.reference_doc).expanduser())]
        subprocess.run(command, check=True)
        if not args.no_borders:
            add_table_borders(out)
        roundtrip = subprocess.run(
            ["pandoc", str(out), "-t", "gfm"], check=True, capture_output=True, text=True
        ).stdout

    expected = count_structure(copy)
    expected["画像"] = len(images) - len(exclude & {i["number"] for i in images})
    actual = count_structure(roundtrip)
    actual["画像"] = len(re.findall(r"<img |!\[", roundtrip))

    print(f"docx: {out}")
    print("| 項目 | md | docx |")
    print("|---|---|---|")
    ok = True
    for key in ("見出し", "表", "画像"):
        mark = "" if expected[key] == actual[key] else " ← 不一致"
        ok = ok and not mark
        print(f"| {key} | {expected[key]} | {actual[key]}{mark} |")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
