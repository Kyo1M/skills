# /// script
# requires-python = ">=3.10"
# dependencies = ["python-pptx>=1.0", "lxml"]
# ///
"""pptx のパッケージを確かめる（PowerPoint が修復を求める原因になる壊れ方が無いか）。

    uv run check_package.py <pptx> [--no-notes] [--no-media <md5,…>]

- zip の中の名前の重複
- 関係（.rels）の行き先のパーツが無い
- [Content_Types].xml に種類の書かれていないパーツ
- XML として読めないパーツ
- ページの ID・図形の ID の重複
- python-pptx で開けるか
--no-notes はノートが 1 つでもあれば、--no-media は指定した md5 の画像があれば問題にする（ロゴなし版の確認用）
"""
import hashlib
import posixpath
import re
import sys
import zipfile
from pathlib import Path

from lxml import etree


R_NS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"


def check(path, no_notes=False, no_media=()):
    path = Path(path)
    problems = []
    z = zipfile.ZipFile(path)
    names = [i.filename for i in z.infolist()]
    dup = {n for n in names if names.count(n) > 1}
    if dup:
        problems.append(f"zip の中の名前が重複している: {sorted(dup)}")
    nameset = set(names)
    ct = etree.fromstring(z.read("[Content_Types].xml"))
    ns = "{http://schemas.openxmlformats.org/package/2006/content-types}"
    defaults = {d.get("Extension").lower() for d in ct.iter(ns + "Default")}
    overrides = {o.get("PartName").lstrip("/") for o in ct.iter(ns + "Override")}
    for n in names:
        if n.endswith("/") or n == "[Content_Types].xml":
            continue
        ext = n.rsplit(".", 1)[-1].lower()
        if n not in overrides and ext not in defaults:
            problems.append(f"[Content_Types].xml に種類が無い: {n}")
    for o in overrides:
        if o not in nameset:
            problems.append(f"[Content_Types].xml にあるパーツが無い: {o}")
    for n in names:
        if n.endswith(".xml") or n.endswith(".rels"):
            try:
                etree.fromstring(z.read(n))
            except etree.XMLSyntaxError as e:
                problems.append(f"XML として読めない: {n}（{e}）")
        if n.endswith(".rels"):
            base = posixpath.dirname(posixpath.dirname(n))
            for rel in etree.fromstring(z.read(n)):
                if rel.get("TargetMode") == "External":
                    continue
                tgt = rel.get("Target")
                full = tgt.lstrip("/") if tgt.startswith("/") else posixpath.normpath(posixpath.join(base, tgt))
                if full not in nameset:
                    problems.append(f"関係の行き先が無い: {n} → {tgt}")
    # XML の中の関係 ID（r:id・r:embed など）が、そのパーツの .rels にあるか
    for n in names:
        if not n.endswith(".xml") or n == "[Content_Types].xml" or "/_rels/" in n:
            continue
        relp = posixpath.join(posixpath.dirname(n), "_rels", posixpath.basename(n) + ".rels")
        try:
            root = etree.fromstring(z.read(n))
        except etree.XMLSyntaxError:
            continue
        rids = {v for node in root.iter() if isinstance(node.tag, str)
                for k, v in node.attrib.items() if k.startswith(R_NS)}
        if not rids:
            continue
        have = set()
        if relp in nameset:
            have = {r.get("Id") for r in etree.fromstring(z.read(relp))}
        missing = rids - have
        if missing:
            problems.append(f"{n} が参照する関係が .rels に無い: {sorted(missing)}")
    pres = z.read("ppt/presentation.xml").decode("utf-8")
    sld_ids = re.findall(r'<p:sldId [^>]*id="(\d+)"', pres)
    if len(sld_ids) != len(set(sld_ids)):
        problems.append("ページの ID が重複している")
    for n in names:
        if re.match(r"ppt/slides/[^/]+\.xml$", n):
            ids = re.findall(r'<p:cNvPr [^>]*id="(\d+)"', z.read(n).decode("utf-8"))
            d = {i for i in ids if ids.count(i) > 1}
            if d:
                problems.append(f"{n} の図形の ID が重複している: {sorted(d)}")
    if no_notes and any("notesSlides/notesSlide" in n for n in names):
        problems.append("ノートが残っている")
    for n in names:
        if "/media/" in n and hashlib.md5(z.read(n)).hexdigest() in no_media:
            problems.append(f"指定した画像が残っている: {n}")
    try:
        import io

        from pptx import Presentation

        if path.suffix.lower() == ".potx":  # python-pptx はテンプレートの種類のまま開けないので、種類だけ読み替える
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w") as zout:
                for n in names:
                    blob = z.read(n)
                    if n == "[Content_Types].xml":
                        blob = blob.replace(b"presentationml.template.main+xml", b"presentationml.presentation.main+xml")
                    zout.writestr(n, blob)
            Presentation(io.BytesIO(buf.getvalue()))
        else:
            Presentation(str(path))
    except Exception as e:  # noqa: BLE001
        problems.append(f"python-pptx で開けない: {e}")
    return problems


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    no_notes = "--no-notes" in args
    media = ()
    if "--no-media" in args:
        media = tuple(args[args.index("--no-media") + 1].split(","))
    target = args[0]
    ps = check(target, no_notes, media)
    for p in ps:
        print("NG", p)
    print("OK" if not ps else f"{len(ps)} 件", target)
    sys.exit(1 if ps else 0)
