# /// script
# requires-python = ">=3.10"
# dependencies = ["python-pptx>=1.0", "lxml"]
# ///
"""テンプレートを公開できる形に掃除して、pptx と potx を書き出す。

    uv run clean_template.py <元の pptx> <出力の pptx>   # 同じ名前の .potx も書く

- ノート（各ページの発表者ノート）をすべて外す
- どこからも参照されていない画像・パーツへの関係を外す（ロゴなし版に残ったロゴの画像など）
- docProps の作成者・最終更新者・会社名・作成したアプリの名前を空にする
- スライドマスター・テーマ・テーマの配色・書体・効果の組の名前を中立の名前（Business）にする
テンプレートを改訂したときも、この掃除を通してから assets/templates/ に置く。
"""
import io
import re
import sys
import zipfile
from pathlib import Path

from pptx import Presentation
from pptx.opc.constants import RELATIONSHIP_TYPE as RT

POTX_CT = "application/vnd.openxmlformats-officedocument.presentationml.template.main+xml"
PPTX_CT = "application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"


R_NS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
MASTER_NAME = "Business"
THEME_NAME = "Business"


def drop_unreferenced_rels(part):
    """XML の中で参照されていない関係を外す（スライド・レイアウト・マスターが対象。属性の接頭辞によらず探す）"""
    used = {v for node in part._element.iter() if isinstance(node.tag, str)
            for k, v in node.attrib.items() if k.startswith(R_NS)}
    for rid, rel in list(part.rels.items()):
        if rel.reltype in (RT.SLIDE_LAYOUT, RT.SLIDE_MASTER, RT.THEME, RT.NOTES_MASTER, RT.NOTES_SLIDE):
            continue
        if rid not in used:
            part.rels.pop(rid)


def clean(src: Path, out: Path) -> None:
    prs = Presentation(str(src))
    for slide in prs.slides:
        for rid, rel in list(slide.part.rels.items()):
            if rel.reltype == RT.NOTES_SLIDE:
                slide.part.rels.pop(rid)
        drop_unreferenced_rels(slide.part)
    for master in prs.slide_masters:
        drop_unreferenced_rels(master.part)
        for layout in master.slide_layouts:
            drop_unreferenced_rels(layout.part)
    cp = prs.core_properties
    cp.author = ""
    cp.last_modified_by = ""
    cp.comments = ""
    cp.keywords = ""
    buf = io.BytesIO()
    prs.save(buf)
    data = strip_company(buf.getvalue())
    out.write_bytes(data)
    out.with_suffix(".potx").write_bytes(to_potx(data))


def strip_company(data: bytes) -> bytes:
    zin = zipfile.ZipFile(io.BytesIO(data))
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            blob = zin.read(item.filename)
            if item.filename == "docProps/app.xml":
                for tag in (rb"Company", rb"Manager", rb"Application"):
                    blob = re.sub(rb"<((?:\w+:)?)" + tag + rb">[^<]*</\1" + tag + rb">", b"", blob)
            if re.match(r"ppt/slideMasters/slideMaster\d+\.xml$", item.filename):
                blob = re.sub(rb'(<p:cSld\b[^>]*\bname=")[^"]*(")', rb"\g<1>" + MASTER_NAME.encode() + rb"\2", blob, count=1)
            if re.search(r"(^|/)theme/theme\d+\.xml$", item.filename):
                blob = re.sub(rb'(<a:theme\b[^>]*\bname=")[^"]*(")', rb"\g<1>" + THEME_NAME.encode() + rb"\2", blob, count=1)
                for tag in (rb"clrScheme", rb"fontScheme", rb"fmtScheme"):  # 配色・書体・効果の組の名前も中立にする
                    blob = re.sub(rb'(<a:' + tag + rb'\b[^>]*\bname=")[^"]*(")', rb"\g<1>" + THEME_NAME.encode() + rb"\2", blob)
            zout.writestr(item, blob)
    return buf.getvalue()


def to_potx(data: bytes) -> bytes:
    zin = zipfile.ZipFile(io.BytesIO(data))
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            blob = zin.read(item.filename)
            if item.filename == "[Content_Types].xml":
                blob = blob.replace(PPTX_CT.encode(), POTX_CT.encode())
            zout.writestr(item, blob)
    return buf.getvalue()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    clean(Path(sys.argv[1]), Path(sys.argv[2]))
    print("wrote", sys.argv[2], "and", Path(sys.argv[2]).with_suffix(".potx"))
