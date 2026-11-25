# /// script
# requires-python = ">=3.10"
# dependencies = ["lxml", "Pillow"]
# ///
"""元の pptx の全ページを残し、図の案のページを元のページの直後に足した新しい版を作る。

図の中の文字は、既定で pptx のテキストボックスにする（figlib.text が控えた位置・大きさ・色・そろえで置き、
文字を抜いた PNG と 1 つのグループにまとめる）。--text image で、今までどおり文字入りの PNG だけを貼る。
回転した文字など、figlib が控えなかった文字は PNG に残る。

案のページは元のページを複製し、タイトル・リード・罫線・フッターを pptx の文字のまま残す。
本文（上端が --body-top〜--body-bottom にある図形）を外し、本文の範囲に図の PNG を貼る。
フッターのページ番号の枠（--footer-name）は「元p.N 差し替え候補」にする（N は元の pptx でのページの並び順。
1 始まり。案を足し済みの pptx にもう一度かけるときは、その pptx での並び順で数える）。
複製にはコメント・ノート・アニメーションを持ち込まない。元のページのパーツは書き換えない
（最後に、変えたのが一覧のパーツだけであることを確かめる）。

図は、--figures の `NN-<内容>.png` と --meta の `figNN_<内容>.json`（figlib.write が書く）を番号 NN で組にする。
JSON の page（元のページ番号）・x・top・width（貼る位置）・title・lead（差し替えるときだけ）を使う。

使い方:
  python3 build_deck.py <元.pptx> <出力.pptx> --figures inputs/v7 --meta source/v7 [--tag v7]
  python3 build_deck.py <元.pptx> --dry-run --pages 5 6   # 図形ごとの位置と分け方を出すだけ

既定の座標（本文の範囲・タイトルとリードの高さ・フッターの枠）は 1920x1080 換算の px。
テンプレートが異なるときは、元のページの図形の位置を確かめてから引数で合わせる。
"""
import argparse
import copy
import glob
import hashlib
import json
import os
import posixpath
import re
import sys
import zipfile

from lxml import etree as E
from PIL import Image

P = "http://schemas.openxmlformats.org/presentationml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PK = "http://schemas.openxmlformats.org/package/2006/relationships"
CT = "http://schemas.openxmlformats.org/package/2006/content-types"
EP = "http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
ns = {"p": P, "a": A, "r": R}
MC = "http://schemas.openxmlformats.org/markup-compatibility/2006"
P14 = "http://schemas.microsoft.com/office/powerpoint/2010/main"
SHAPES = {f"{{{P}}}{t}" for t in ("sp", "pic", "grpSp", "cxnSp", "graphicFrame", "contentPart")} | {
    f"{{{MC}}}AlternateContent"}
# 複製に残すと元のページとパーツを共有してしまう関係（本文を外したあとも参照が残っていれば止める）
SHARED_TYPES = ("chart", "diagramData", "diagramLayout", "diagramQuickStyle", "diagramColors", "diagramDrawing",
                "oleObject", "package", "vmlDrawing", "tags")
CANVAS_W = 1920  # figlib の座標の幅
ALLOWED_CHANGES = {"ppt/presentation.xml", "ppt/_rels/presentation.xml.rels", "[Content_Types].xml",
                   "docProps/app.xml"}


def xml(b):
    return E.fromstring(b)


def ser(x):
    return E.tostring(x, xml_declaration=True, encoding="UTF-8", standalone=True)


def own_off(el):
    """図形自身が持つ位置（a:off）。AlternateContent などは中の最初の位置を使う。"""
    for path in ("p:spPr/a:xfrm/a:off", "p:grpSpPr/a:xfrm/a:off", "p:xfrm/a:off"):
        off = el.find(path, ns)
        if off is not None:
            return off
    if el.tag in (f"{{{MC}}}AlternateContent", f"{{{P}}}contentPart"):
        return el.find(f".//{{{A}}}off")
    return None


def ph_key(el):
    ph = el.find("./*/p:nvPr/p:ph", ns)
    if ph is None:
        return None
    return ph.get("type", "obj"), ph.get("idx")


class Inherit:
    """プレースホルダーが自分で位置を持たないとき、レイアウト → マスターの同じプレースホルダーから引く。"""

    def __init__(self, data):
        self.data = data

    def rel_target(self, part, typ):
        relp = posixpath.join(posixpath.dirname(part), "_rels", posixpath.basename(part) + ".rels")
        if relp not in self.data:
            return None
        for r in xml(self.data[relp]):
            if r.get("Type").endswith("/" + typ):
                return resolve(part, r.get("Target"))
        return None

    def off(self, el, part):
        key = ph_key(el)
        if key is None:
            return None
        lay = self.rel_target(part, "slideLayout")
        chain = [lay, self.rel_target(lay, "slideMaster") if lay else None]
        for src in chain:
            if not src or src not in self.data:
                continue
            for cand in xml(self.data[src]).iter(f"{{{P}}}sp"):
                k = ph_key(cand)
                if k is None:
                    continue
                if (key[1] is not None and k[1] == key[1]) or (key[1] is None and k[0] == key[0]) or \
                        (k[0] == key[0] and key[0] not in ("obj", "body")):
                    off = own_off(cand)
                    if off is not None:
                        return off
        return None


def top_px(el, px, inherit=None, part=None):
    off = own_off(el)
    if off is None and inherit is not None:
        off = inherit.off(el, part)
    return None if off is None else int(off.get("y")) / px


def resolve(base_part, target):
    """rels の Target を zip の中の名前にする（先頭の / はパッケージの絶対参照）。"""
    if target.startswith("/"):
        return target.lstrip("/")
    return posixpath.normpath(posixpath.join(posixpath.dirname(base_part), target))


def settext(sp, t):
    """最初の段落と最初の文字の書式を残して、文字だけ差し替える。

    `**語句**` で囲んだ所だけを太字にする（リードの結論の語句。deck-outline の原則 95）。
    `**` を含むときだけ囲みの外を細字にし、含まないとき（タイトル・フッターなど）は元の書式のまま。"""
    import re
    body = sp.find("p:txBody", ns)
    oldp = body.find("a:p", ns)
    rpr = oldp.find(".//a:rPr", ns)
    for q in list(body):
        if q.tag == f"{{{A}}}p":
            body.remove(q)
    par = E.SubElement(body, f"{{{A}}}p")
    pp = oldp.find("a:pPr", ns)
    if pp is not None:
        par.append(copy.deepcopy(pp))
    for i, piece in enumerate(re.split(r"\*\*(.+?)\*\*", t)):
        if not piece:
            continue
        run = E.SubElement(par, f"{{{A}}}r")
        r2 = copy.deepcopy(rpr) if rpr is not None else E.Element(f"{{{A}}}rPr")
        if "**" in t:
            r2.set("b", "1" if i % 2 else "0")
        run.append(r2)
        E.SubElement(run, f"{{{A}}}t").text = piece


FONTS = {"gothic": "Hiragino Sans", "mincho": "Hiragino Mincho ProN"}


def tw(s, size):
    """文字列の幅の見積もり（figlib.tw と同じ。英数字は全角の約 0.6）"""
    return sum(size * (0.6 if ord(c) < 128 else 1.0) for c in s)


def text_box(t, px, sid, k):
    """figlib が控えた文字 1 つ → 折り返しなし・余白なしのテキストボックス。座標は 1920x1080 の px"""
    size = t["size"]
    bw = tw(t["text"], size) * 1.12 + size * 0.6
    bh = size * 1.45
    left = {"start": t["x"] - size * 0.05, "middle": t["x"] - bw / 2, "end": t["x"] - bw + size * 0.05}[t["anchor"]]
    top = t["y"] + size * 0.26 - bh   # 下ぞろえの枠の下端を、ベースラインの少し下（文字の下の余白）に置く
    algn = {"start": "l", "middle": "ctr", "end": "r"}[t["anchor"]]
    font = FONTS[t.get("font", "gothic")]
    color = t["color"].lstrip("#").upper()
    if len(color) == 3:
        color = "".join(c * 2 for c in color)
    sz = round(size * px / 12700 * 100)
    from xml.sax.saxutils import escape
    return xml(f'''<p:sp xmlns:p="{P}" xmlns:a="{A}"><p:nvSpPr><p:cNvPr id="{sid}" name="図の文字 {k}"/>
<p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="{round(left * px)}" y="{round(top * px)}"/>
<a:ext cx="{round(bw * px)}" cy="{round(bh * px)}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr>
<p:txBody><a:bodyPr wrap="none" lIns="0" tIns="0" rIns="0" bIns="0" anchor="b"><a:noAutofit/></a:bodyPr><a:lstStyle/>
<a:p><a:pPr algn="{algn}"/><a:r><a:rPr lang="ja-JP" altLang="en-US" sz="{sz}" b="{1 if t["weight"] >= 600 else 0}" dirty="0">
<a:solidFill><a:srgbClr val="{color}"/></a:solidFill><a:latin typeface="{font}"/><a:ea typeface="{font}"/></a:rPr>
<a:t>{escape(t["text"])}</a:t></a:r></a:p></p:txBody></p:sp>'''.encode())


def group_with_texts(pic, texts, px, first_id, nn):
    """図とその上の文字を 1 つのグループにする。グループの中の文字はそのまま直せる"""
    boxes = [text_box(t, px, first_id + k, k + 1) for k, t in enumerate(texts)]
    xs, ys, xe, ye = [], [], [], []
    for el in [pic] + boxes:
        off = el.find(".//a:xfrm/a:off", ns)
        ext = el.find(".//a:xfrm/a:ext", ns)
        x, y, cx, cy = (int(off.get("x")), int(off.get("y")), int(ext.get("cx")), int(ext.get("cy")))
        xs.append(x), ys.append(y), xe.append(x + cx), ye.append(y + cy)
    x0, y0, x1, y1 = min(xs), min(ys), max(xe), max(ye)
    g = xml(f'''<p:grpSp xmlns:p="{P}" xmlns:a="{A}"><p:nvGrpSpPr><p:cNvPr id="{first_id + len(boxes)}" name="図の案 {nn}（図と文字）"/>
<p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="{x0}" y="{y0}"/><a:ext cx="{x1 - x0}" cy="{y1 - y0}"/>
<a:chOff x="{x0}" y="{y0}"/><a:chExt cx="{x1 - x0}" cy="{y1 - y0}"/></a:xfrm></p:grpSpPr></p:grpSp>'''.encode())
    g.append(pic)
    for b in boxes:
        g.append(b)
    return g


def figures(fig_dir, meta_dir, text_mode="pptx"):
    out = []
    for png in sorted(glob.glob(os.path.join(fig_dir, "[0-9][0-9]-*.png"))):
        if text_mode == "image":   # 文字入りの PNG（render.sh が with-text/ に書く）を使う
            alt = os.path.join(fig_dir, "with-text", os.path.basename(png))
            if not os.path.exists(alt):
                raise SystemExit(f"{alt} が無い（--text image には文字入りの PNG が要る）")
            png = alt
        nn = os.path.basename(png)[:2]
        metas = glob.glob(os.path.join(meta_dir, f"fig{nn}_*.json"))
        if len(metas) != 1:
            raise SystemExit(f"{png}: figNN_*.json が 1 つに決まらない: {metas}")
        out.append((nn, png, json.load(open(metas[0], encoding="utf-8"))))
    if not out:
        raise SystemExit(f"{fig_dir} に NN-*.png が無い")
    used = {nn for nn, _, _ in out}
    for j in sorted(glob.glob(os.path.join(meta_dir, "fig[0-9][0-9]_*.json"))):
        if os.path.basename(j)[3:5] not in used:
            print(f"注意: {os.path.basename(j)} に対応する PNG が無いので足さない", file=sys.stderr)
    return out


def classify(el, px, a, inherit, part, name):
    if el.tag not in SHAPES:
        return None, None
    y = top_px(el, px, inherit, part)
    if a.footer_name and name == a.footer_name:
        return y, "フッター"
    if y is None:
        return y, "位置不明"
    if a.title_y[0] <= y < a.title_y[1]:
        return y, "タイトル"
    if a.lead_y[0] <= y < a.lead_y[1]:
        return y, "リード"
    if a.body_top <= y < a.body_bottom:
        return y, "本文（外す）"
    return y, "残す"


def shape_name(el):
    c = next((e for e in el.iter(f"{{{P}}}cNvPr")), None)
    return "" if c is None else (c.get("name") or "")


def load(src):
    with zipfile.ZipFile(src) as z:
        names = z.namelist()
        data = {n: z.read(n) for n in names}
    ppt = xml(data["ppt/presentation.xml"])
    sz = ppt.find("p:sldSz", ns)
    px = int(sz.get("cx")) / CANVAS_W
    if abs(int(sz.get("cy")) / px - CANVAS_W * 9 / 16) > 1:
        raise SystemExit(f"16:9 のページではない: {sz.get('cx')}x{sz.get('cy')}")
    prels = xml(data["ppt/_rels/presentation.xml.rels"])
    sld = list(ppt.find("p:sldIdLst", ns))
    rid2part = {r.get("Id"): resolve("ppt/presentation.xml", r.get("Target")) for r in prels}
    page_part = {i: rid2part[s.get(f"{{{R}}}id")] for i, s in enumerate(sld, 1)}
    return names, data, ppt, prels, sld, page_part, px


def dry_run(a):
    names, data, ppt, prels, sld, page_part, px = load(a.src)
    inherit = Inherit(data)
    for n in a.pages or sorted(page_part):
        part = page_part[n]
        print(f"--- p.{n}（{part}）")
        for el in xml(data[part]).find("p:cSld/p:spTree", ns):
            name = shape_name(el)
            y, kind = classify(el, px, a, inherit, part, name)
            if kind:
                print(f"  {kind:<8} y={'-' if y is None else round(y)}  {name}")


def build(a):
    if os.path.exists(a.dst) and os.path.samefile(a.src, a.dst):
        raise SystemExit("出力が元の pptx と同じファイル。元の pptx は上書きしない")
    names, data, ppt, prels, sld, page_part, px = load(a.src)
    orig = dict(data)
    inherit = Inherit(data)
    ct = xml(data["[Content_Types].xml"])
    lst = ppt.find("p:sldIdLst", ns)
    mx = max(int(s.get("id")) for s in sld)
    if not any((d.get("Extension") or "").lower() == "png" for d in ct.findall(f"{{{CT}}}Default")):
        E.SubElement(ct, f"{{{CT}}}Default", Extension="png", ContentType="image/png")
    existing_rids = {r.get("Id") for r in prels}
    tag = re.sub(r"[^A-Za-z0-9]", "", a.tag)
    fig_rid = f"rIdInfo{tag}"

    new_after = {}
    report = []
    for k, (nn, png, meta) in enumerate(figures(a.figures, a.meta, a.text), 1):
        n = meta["page"]
        if n not in page_part:
            raise SystemExit(f"図{nn}: 元のページ {n} が無い（全 {len(sld)} ページ）")
        part = page_part[n]
        relp = posixpath.join(posixpath.dirname(part), "_rels", posixpath.basename(part) + ".rels")
        s = xml(data[part])
        rr = xml(data[relp]) if relp in data else E.Element(f"{{{PK}}}Relationships")
        tree = s.find("p:cSld/p:spTree", ns)

        removed, kept, unknown = [], [], []
        found = {"title": False, "lead": False, "footer": False}
        for el in list(tree):
            name = shape_name(el)
            y, kind = classify(el, px, a, inherit, part, name)
            if kind is None:
                continue
            if kind == "位置不明":
                unknown.append(name)
            elif kind == "本文（外す）":
                tree.remove(el)
                removed.append(name)
                continue
            kept.append(f"{name}（{kind}）")
            if el.tag != f"{{{P}}}sp" or el.find("p:txBody", ns) is None:
                continue
            if kind == "タイトル" and meta.get("title"):
                settext(el, meta["title"])
                found["title"] = True
            elif kind == "リード" and meta.get("lead"):
                settext(el, meta["lead"])
                found["lead"] = True
            elif kind == "フッター":
                settext(el, a.label.format(page=n))
                off = el.find("p:spPr/a:xfrm/a:off", ns)
                if off is None:
                    raise SystemExit(f"図{nn}（元p.{n}）: フッターの枠 {name} が自分の位置を持たない"
                                     "（PowerPoint で一度動かすか、--footer-name を空にする）")
                off.set("x", str(round(a.footer_x * px)))
                el.find("p:spPr/a:xfrm/a:ext", ns).set("cx", str(round(a.footer_w * px)))
                found["footer"] = True
        if unknown:
            raise SystemExit(f"図{nn}（元p.{n}）: 位置の分からない図形がある: {unknown}（--dry-run で確かめる）")
        if not removed:
            raise SystemExit(f"図{nn}（元p.{n}）: 本文の範囲 y={a.body_top}〜{a.body_bottom} に図形が無い")
        for key in ("title", "lead"):
            if meta.get(key) and not found[key]:
                raise SystemExit(f"図{nn}（元p.{n}）: 差し替える{key}の枠が見つからない（--{key}-y を確かめる）")
        if a.footer_name and not found["footer"]:
            raise SystemExit(f"図{nn}（元p.{n}）: フッターの枠 {a.footer_name} が無い（--footer-name を確かめる）")

        # 図の PNG を本文の範囲に貼る
        w, h = Image.open(png).size
        cx = round(meta["width"] * px)
        cy = round(cx * h / w)
        media = f"ppt/media/info{tag}-fig{nn}.png"
        newpart = f"ppt/slides/info{tag}fig{nn}.xml"
        for p_ in (media, newpart):
            if p_ in data:
                raise SystemExit(f"{p_} が元の pptx にすでにある（--tag を変える）")
        data[media] = open(png, "rb").read()
        if any(r.get("Id") == fig_rid for r in rr):
            raise SystemExit(f"元p.{n} の rels に {fig_rid} がすでにある（--tag を変える）")
        E.SubElement(rr, f"{{{PK}}}Relationship", Id=fig_rid, Type=R + "/image",
                     Target="../media/" + posixpath.basename(media))
        ids = [int(e.get("id")) for e in s.iter(f"{{{P}}}cNvPr") if (e.get("id") or "").isdigit()]
        pic = xml(f'''<p:pic xmlns:p="{P}" xmlns:a="{A}" xmlns:r="{R}"><p:nvPicPr>
<p:cNvPr id="{max(ids, default=1) + 1}" name="図の案 {nn}"/>
<p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr>
<p:blipFill><a:blip r:embed="{fig_rid}"/><a:stretch><a:fillRect/></a:stretch></p:blipFill>
<p:spPr><a:xfrm><a:off x="{round(meta['x'] * px)}" y="{round(meta['top'] * px)}"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>
<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:pic>'''.encode())
        pic.find("p:nvPicPr/p:cNvPr", ns).set("descr", f"{meta.get('title') or ''}図の案（元p.{n}）")
        texts = meta.get("texts") or []
        if a.text == "pptx" and texts:
            # 図の中の文字を pptx の文字にし、図と 1 つのグループにまとめる（図を動かすと文字も動く）
            pic = group_with_texts(pic, texts, px, max(ids, default=1) + 2, nn)
        ext_lst = tree.find("p:extLst", ns)
        if ext_lst is not None:
            ext_lst.addprevious(pic)   # extLst は図形の並びの最後に置く決まり
        else:
            tree.append(pic)

        # コメントへの参照（extLst の commentRel）とアニメーション（外した図形を指す）は持ち込まない
        for cr in [e for e in s.iter() if isinstance(e.tag, str) and e.tag.endswith("}commentRel")]:
            ext = cr.getparent()
            if ext is not None and ext.getparent() is not None:
                ext.getparent().remove(ext)
        for t in s.findall("p:timing", ns):
            s.remove(t)
        # レイアウト以外で、ページの XML から参照されなくなった関係を外す（コメント・ノートも外す）
        xml_text = ser(s).decode()
        for rel in list(rr):
            typ = rel.get("Type").rsplit("/", 1)[-1]
            if rel.get("Id") == fig_rid:
                continue
            if typ != "slideLayout" and (typ == "notesSlide" or typ.endswith("comments")
                                         or f'"{rel.get("Id")}"' not in xml_text):
                rr.remove(rel)
                continue
            if typ in SHARED_TYPES:
                raise SystemExit(f"図{nn}（元p.{n}）: 本文の外に {typ} が残っていて、複製すると元のページと共有になる")
            if rel.get("TargetMode") != "External":   # 複製は ppt/slides/ に置くので、参照先をそこからの相対にする
                rel.set("Target", posixpath.relpath(resolve(part, rel.get("Target")), "ppt/slides"))
        data[newpart] = ser(s)
        data[posixpath.join("ppt/slides/_rels", posixpath.basename(newpart) + ".rels")] = ser(rr)
        rid = f"rIdInfo{tag}{nn}"
        if rid in existing_rids:
            raise SystemExit(f"presentation.xml.rels に {rid} がすでにある（--tag を変える）")
        E.SubElement(prels, f"{{{PK}}}Relationship", Id=rid, Type=R + "/slide",
                     Target="slides/" + posixpath.basename(newpart))
        E.SubElement(ct, f"{{{CT}}}Override", PartName="/" + newpart,
                     ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml")
        new_id = mx + k
        if new_id >= 2147483648:
            raise SystemExit("ページの id が上限を超える")
        new_after.setdefault(n, []).append(E.Element(f"{{{P}}}sldId", id=str(new_id), attrib={f"{{{R}}}id": rid}))
        report.append({"figure": nn, "sourcePage": n, "png": os.path.basename(png), "removed": removed,
                       "editableTexts": len(texts) if a.text == "pptx" else 0,
                       "textsInImage": meta.get("texts_in_image", []) if a.text == "pptx" else "all",
                       "kept": kept, "replacedTitle": found["title"], "replacedLead": found["lead"],
                       "sourceHidden": s.get("show") == "0"})

    for s in list(lst):
        lst.remove(s)
    for i, s in enumerate(sld, 1):
        lst.append(s)
        for x in new_after.get(i, []):
            lst.append(x)
    # セクションがあれば、案のページを元のページと同じセクションに入れる
    id_of = {i: s.get("id") for i, s in enumerate(sld, 1)}
    for sec_lst in ppt.iter(f"{{{P14}}}sectionLst"):
        for entry in sec_lst.iter(f"{{{P14}}}sldId"):
            page = next((i for i, v in id_of.items() if v == entry.get("id")), None)
            for x in reversed(new_after.get(page, [])):
                entry.addnext(E.Element(f"{{{P14}}}sldId", id=x.get("id")))
    total = len(lst)
    data["ppt/presentation.xml"] = ser(ppt)
    data["ppt/_rels/presentation.xml.rels"] = ser(prels)
    data["[Content_Types].xml"] = ser(ct)
    if "docProps/app.xml" in data:
        app = xml(data["docProps/app.xml"])
        el = app.find(f"{{{EP}}}Slides")
        if el is not None:
            el.text = str(total)
            data["docProps/app.xml"] = ser(app)

    changed = sorted(n for n in names if orig[n] != data[n])
    if not set(changed) <= ALLOWED_CHANGES:
        raise SystemExit(f"元のパーツが変わった: {sorted(set(changed) - ALLOWED_CHANGES)}")
    tmp = a.dst + ".tmp"
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as t:
        for n, b in data.items():
            t.writestr(n, b)
    os.replace(tmp, a.dst)
    out = {"slides": total, "originalSlides": len(sld), "figures": report,
           "originalPartsUnchanged": len(names) - len(changed), "changedParts": changed,
           "sha256": hashlib.sha256(open(a.dst, "rb").read()).hexdigest()}
    report_path = a.report or os.path.join(a.meta, "build-report.json")
    json.dump(out, open(report_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "figures"}, ensure_ascii=False, indent=1))
    for f in report:
        print(f"図{f['figure']} → 元p.{f['sourcePage']}: 外した図形 {len(f['removed'])}、残した図形 {len(f['kept'])}"
              + ("（元のページは非表示）" if f["sourceHidden"] else ""))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src", help="元の pptx（上書きしない）")
    ap.add_argument("dst", nargs="?", help="出力の pptx（--dry-run のときは要らない）")
    ap.add_argument("--dry-run", action="store_true", help="図形ごとの位置と分け方を出すだけ（何も書かない）")
    ap.add_argument("--pages", type=int, nargs="*", help="--dry-run で見るページ（並び順。既定は全ページ）")
    ap.add_argument("--figures", help="NN-<内容>.png のフォルダ（inputs/<版>）")
    ap.add_argument("--meta", help="figNN_<内容>.json のフォルダ（source/<版>）")
    ap.add_argument("--tag", default="fig", help="足すパーツの名前に入れる印（版の名前など。英数字）")
    ap.add_argument("--label", default="元p.{page} 差し替え候補", help="フッターのページ番号の枠に入れる文字")
    ap.add_argument("--report", help="組み立ての記録 JSON（既定は --meta の build-report.json）")
    ap.add_argument("--body-top", type=float, default=240, help="外す本文の図形の上端の下限（px）")
    ap.add_argument("--body-bottom", type=float, default=990, help="外す本文の図形の上端の上限（px。フッターより上）")
    ap.add_argument("--title-y", type=float, nargs=2, default=(60, 90), help="タイトルの枠の上端の範囲（px）")
    ap.add_argument("--lead-y", type=float, nargs=2, default=(200, 230), help="リードの枠の上端の範囲（px）")
    ap.add_argument("--footer-name", default="SlideNumber", help="ページ番号の枠の図形名（空にすると触らない）")
    ap.add_argument("--footer-x", type=float, default=1450, help="ページ番号の枠の左端（px）")
    ap.add_argument("--footer-w", type=float, default=350, help="ページ番号の枠の幅（px）")
    ap.add_argument("--text", choices=("pptx", "image"), default="pptx",
                    help="図の中の文字を pptx の文字にする（既定。図と文字を 1 つのグループにする）か、PNG に残すか")
    a = ap.parse_args()
    if a.dry_run:
        dry_run(a)
        return
    if not (a.dst and a.figures and a.meta):
        ap.error("出力の pptx・--figures・--meta が要る")
    build(a)


if __name__ == "__main__":
    main()
