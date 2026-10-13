#!/usr/bin/env python3
"""Markdown を docx にする（画像を埋め込む）。元の md は変えない。

使い方:
    python3 md_to_docx.py <md> --list
        画像の参照の一覧（番号・キャプション・パス・存在）を出す
    python3 md_to_docx.py <md> --out <docx> [--exclude 2 3] [--root <リポジトリの root>]
                          [--style gdocs | --reference-doc <docx>] [--number-figures] [--no-borders]
        docx を作り、見出し・表・画像の数を md と照合する

- frontmatter は消す（Doc の表題が二重になるため）
- 画像は `![cap](path)`（md のフォルダ基準）と `[FIG] path`（--root 基準、既定は git の root、git でなければ md のフォルダ）の 2 形式を読む
- 表には罫線を直接付ける（--no-borders で付けない）
- --style gdocs は、書体を Arial 11pt・見出しを黒にした雛形を使う（Google ドキュメントの既定の見た目に寄せる）
- --number-figures は、残した図（行に画像だけがあるもの）のキャプションの頭に「図1.」「図2.」…を付ける
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
        line_start = text.rfind("\n", 0, match.start()) + 1
        line_end = text.find("\n", match.end())
        line = text[line_start:len(text) if line_end < 0 else line_end]
        # 行に画像だけがあるとき、pandoc は図（キャプション付き）にする。文中の画像は図にならない
        standalone = line.strip() == match.group(0).strip()
        images.append({"span": match.span(), "caption": caption, "raw": raw, "path": path,
                       "figure": standalone})
    for number, image in enumerate(images, start=1):
        image["number"] = number
    return images


def build_copy(text: str, images, exclude: set[int], number_figures: bool = False) -> str:
    pieces, cursor, figure = [], 0, 0
    for image in images:
        start, end = image["span"]
        pieces.append(text[cursor:start])
        if image["number"] not in exclude:
            caption = image["caption"]
            if number_figures and image["figure"]:
                figure += 1
                caption = f"図{figure}. {caption}".rstrip()
            pieces.append(f"![{caption}]({image['path']})")
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


HEADING_SIZES = {"Title": 52, "Heading1": 40, "Heading2": 32, "Heading3": 28, "Heading4": 24,
                 "Heading5": 22, "Heading6": 22}   # 半ポイント。Google ドキュメントの既定の大きさ
BLACK_STYLES = re.compile(r"^(Title|Subtitle|Heading\d|TOCHeading)(Char)?$")   # 色を外して黒にするスタイル
PLAIN_STYLES = re.compile(r"^(Caption|ImageCaption|TableCaption|Heading\d)(Char)?$")   # 斜体を外すスタイル
STYLE_BLOCK = re.compile(r'<w:style\b[^>]*w:styleId="([^"]+)"[^>]*>.*?</w:style>', re.S)


def _set_size(block: str, size: int) -> str:
    if re.search(r"<w:sz\b", block):
        block = re.sub(r'<w:sz w:val="\d+"(\s*)/>', f'<w:sz w:val="{size}"\\1/>', block)
        return re.sub(r'<w:szCs w:val="\d+"(\s*)/>', f'<w:szCs w:val="{size}"\\1/>', block)
    rpr = f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>'
    if re.search(r"<w:rPr\s*>", block):
        return re.sub(r"(<w:rPr\s*>)", r"\1" + rpr, block, count=1)
    return block.replace("</w:style>", f"<w:rPr>{rpr}</w:rPr></w:style>")


def _patch_style(match: re.Match) -> str:
    style_id, block = match.group(1), match.group(0)
    # テーマの書体だけを外し、既定の Arial を継がせる（コードの Consolas など明示の書体は残す）
    block = re.sub(r"<w:rFonts\b(?=[^>]*Theme=)[^>]*/>", "", block)
    if BLACK_STYLES.match(style_id):
        block = re.sub(r"<w:color\b[^>]*/>", "", block)
    if PLAIN_STYLES.match(style_id):
        block = re.sub(r"<w:iCs\s*/>|<w:i\s*/>", "", block)   # 和文の斜体は読みにくい
    if style_id in HEADING_SIZES:
        block = _set_size(block, HEADING_SIZES[style_id])
    return block


def make_gdocs_reference(path: Path) -> None:
    """pandoc の既定の雛形を、Google ドキュメントの既定の見た目（Arial 11pt・黒の見出し）に寄せて書き出す"""
    data = subprocess.run(["pandoc", "--print-default-data-file", "reference.docx"],
                          check=True, capture_output=True).stdout
    source_path = path.with_suffix(".src.docx")
    source_path.write_bytes(data)
    arial = '<w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:eastAsia="Arial" w:cs="Arial"/>'
    with zipfile.ZipFile(source_path) as source, zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as target:
        for info in source.infolist():
            data = source.read(info.filename)
            if info.filename == "word/styles.xml":
                xml = data.decode()
                defaults = re.search(r"<w:rPrDefault>.*?</w:rPrDefault>", xml, re.S)
                if defaults is None:
                    raise SystemExit("pandoc の雛形に既定の書式（rPrDefault）がありません")
                block = re.sub(r"<w:rFonts\b[^>]*/>", "", defaults.group(0))
                block = re.sub(r"<w:szCs\b[^>]*/>|<w:sz\b[^>]*/>", "", block)
                block = re.sub(r"(<w:rPr\s*>)", r"\1" + arial + '<w:sz w:val="22"/><w:szCs w:val="22"/>', block, count=1)
                block = block.replace('w:eastAsia="zh-CN"', 'w:eastAsia="ja-JP"')
                xml = xml[:defaults.start()] + block + xml[defaults.end():]
                xml = STYLE_BLOCK.sub(_patch_style, xml)
                data = xml.encode()
            target.writestr(info, data)
    source_path.unlink()


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
    parser.add_argument("--style", choices=["pandoc", "gdocs"], default="pandoc",
                        help="gdocs: Arial 11pt・黒の見出しの雛形を使う（--reference-doc と併用しない）")
    parser.add_argument("--number-figures", action="store_true", help="画像のキャプションの頭に 図N. を付ける")
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

    if args.style != "pandoc" and args.reference_doc:
        print("--style と --reference-doc は一緒に使えません", file=sys.stderr)
        return 2
    if not shutil.which("pandoc"):
        print("pandoc がありません（brew install pandoc）", file=sys.stderr)
        return 2
    exclude = set(args.exclude)
    missing = [i for i in images if i["number"] not in exclude and not i["path"].exists()]
    if missing:
        for image in missing:
            print(f"画像がありません: #{image['number']} {image['raw']}", file=sys.stderr)
        return 2

    copy = build_copy(text, images, exclude, args.number_figures)
    out = Path(args.out).expanduser().resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as work:
        copy_path = Path(work) / "copy.md"
        copy_path.write_text(copy)
        command = ["pandoc", str(copy_path), "-f", "gfm+implicit_figures", "-o", str(out)]
        if args.reference_doc:
            command += ["--reference-doc", str(Path(args.reference_doc).expanduser())]
        elif args.style == "gdocs":
            reference = Path(work) / "gdocs-reference.docx"
            make_gdocs_reference(reference)
            command += ["--reference-doc", str(reference)]
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
