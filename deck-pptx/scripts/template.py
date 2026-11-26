# /// script
# requires-python = ">=3.10"
# dependencies = ["python-pptx>=1.0", "lxml", "Pillow", "budoux>=0.6"]
# ///
"""土台（テンプレート・前回の資料）の操作と、土台の設定。

    uv run template.py --inspect <pptx|potx> [--page N]   # レイアウト・ページの一覧。--page でそのページの図形の一覧と設定の候補だけ

資料ごとの build.py から読み込んで使う:

    prs = template.open_deck("unbranded")                       # 同梱のテンプレート（ロゴなし）。"continova" でロゴあり
    prs = template.open_deck("前回.pptx", base=template.Base.from_deck(...))   # 前回の資料を土台にする
    s = template.new_slide(prs, "03", "題", ["リード文"])       # レイアウト名の先頭でページを足す
    s = template.duplicate(prs, template.find_sample(prs, "目次"))  # サンプル・前回のページを複製する
    template.finalize(prs, "out.pptx", title="資料の題")          # 後始末をして保存し、パッケージを確かめる
"""
from __future__ import annotations

import copy
import io
import re
import sys
import unicodedata
import zipfile
from dataclasses import dataclass, field, replace
from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.oxml.ns import qn
from pptx.util import Emu

sys.path.insert(0, str(Path(__file__).resolve().parent))
import parts  # noqa: E402

HERE = Path(__file__).resolve().parent
TEMPLATES = HERE.parent / "assets" / "templates"
TEMPLATE_FILES = {
    "continova": TEMPLATES / "continova-business-template.pptx",
    "unbranded": TEMPLATES / "unbranded-business-template.pptx",
}
POTX_CT = b"application/vnd.openxmlformats-officedocument.presentationml.template.main+xml"
PPTX_CT = b"application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
COMMENT_RTS = (
    "http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments",
    "http://schemas.microsoft.com/office/2018/10/relationships/comments",
)

COLORS = {
    "ink": "111111", "body": "2F3135", "sub": "6F7175", "accent": "002FA7", "surface": "F4F2EE",
    "line": "D8D6D0", "pale": "EAF1FF", "mid": "C9D8F5", "bad": "C0392B", "good": "1E8449",
    "pale_bad": "FBEDEB", "white": "FFFFFF",
}


# ---------------------------------------------------------------- 土台の設定


@dataclass
class Base:
    """土台ごとに異なる値。座標と文字の大きさは 1920×1080 の px"""

    name: str
    frame: str = "placeholder"                  # "placeholder"（テンプレート）か "named"（名前付きの図形）
    title: str | int = 0                        # 題の枠（プレースホルダーの番号か図形の名前）
    lead: str | int = 1                         # リード文の枠
    number: str | int = 99                      # ページ番号の枠
    keep: tuple = ()                            # named のとき、本文を外しても残す図形の名前
    body: tuple = (96, 392, 1728, 568)          # 本文の範囲 (x, y, w, h)
    sizes: dict = field(default_factory=lambda: {
        "title": 63, "lead": 28, "body": 27, "head": 28, "table": 24, "note": 20, "small": 23})
    font: str | None = "+mn-lt"                 # 本文の書体（テーマの本文の書体を明示する。書かないと LibreOffice が別の書体で描く）
    head_font: str | None = "+mj-lt"            # 題の書体
    colors: dict = field(default_factory=lambda: dict(COLORS))
    gap: float = 8                              # 段落の後ろの間
    bullet_char: str = "・"
    bullet_char2: str = "－"
    bullet_color: str | None = None
    lead_line: float = 1.15                     # リード文の行間
    head_fill: str = "surface"                  # カード・ステップの見出し帯の地（色の名前か 16 進）
    head_color: str = "ink"                     # 見出し帯の文字の色
    phrase_wrap: bool = True                    # 狭い枠の文字を文節の区切りで改行する（parts.phrase_wrap。BudouX が要る）

    @classmethod
    def from_deck(cls, prs, page, title, lead, number=None, keep=(), **overrides):
        """前回の資料（Presentation かファイルのパス）の page 枚目（1 始まり）から設定の候補を作る。

        title・lead・number は枠の図形の名前。keep は本文を外しても残す図形の名前（罫線・フッターなど）。
        本文の範囲は、そのページの枠以外の図形の範囲から測る。文字の大きさは題・リード文・本文の文字から読む。
        見出し帯（色の地に白い文字）の色は全ページから測り、カード・ステップの見出し帯をその色にする（無ければ淡い地）。
        測った値は --inspect で確かめ、合わなければ overrides（body=…, sizes=… など）で直す。sizes は渡した分だけを替える。
        表だけのページで測ると本文の文字の大きさが表の大きさになるので、本文に箇条書きのあるページで測る。
        """
        if not hasattr(prs, "slides"):
            prs = _load(prs)
        slide = prs.slides[page - 1]
        k = prs.slide_width / 1920
        names = {title, lead} | ({number} if number else set()) | set(keep)
        frame = {sh.name: sh for sh in slide.shapes}
        for n in (title, lead):
            if n not in frame:
                raise KeyError(f"{page} 枚目に図形「{n}」が無い。--inspect で名前を確かめる")
        body_shapes = [sh for sh in slide.shapes if sh.name not in names]
        lead_sh = frame[lead]
        if body_shapes:
            x0 = min(sh.left for sh in body_shapes) / k
            y0 = min(sh.top for sh in body_shapes) / k
            x1 = max(sh.left + sh.width for sh in body_shapes) / k
        else:
            x0, x1, y0 = lead_sh.left / k, (lead_sh.left + lead_sh.width) / k, (lead_sh.top + lead_sh.height) / k + 24
        rules = [frame[n] for n in keep if n in frame and frame[n].top / k > 540]
        y1 = (min(sh.top for sh in rules) / k - 24) if rules else 960
        sizes = dict(cls.__dataclass_fields__["sizes"].default_factory())
        ts, ls = _first_size(frame[title], k), _first_size(lead_sh, k)
        bs = [_first_size(sh, k) for sh in body_shapes if sh.has_text_frame]
        bs = [v for v in bs if v]
        if ts:
            sizes["title"] = ts
        if ls:
            sizes["lead"] = ls
        if bs:
            body = sorted(bs)[len(bs) // 2]
            sizes.update(body=body, head=body, table=round(body * 0.85, 1), note=round(body * 0.75, 1),
                         small=round(body * 0.85, 1))
        font = _first_font(lead_sh) or "+mn-lt"
        head_font = _first_font(frame[title]) or "+mj-lt"
        colors = dict(COLORS)
        ink = _first_color(lead_sh)
        if ink:
            colors["ink"] = ink
        for sh in rules:
            c = _fill_color(sh)
            if c:
                colors["line"] = c
                break
        head = _head_band(prs, names)
        if head:   # 前回の資料の見出し帯（色の地に白い文字の図形）の色に合わせる
            colors["head"] = head
        b = cls(name="deck", frame="named", title=title, lead=lead, number=number,
                keep=tuple(names - {None}), body=(round(x0), round(y0), round(x1 - x0), round(y1 - y0)),
                sizes=sizes, font=font, head_font=head_font, colors=colors,
                **({"head_fill": "head", "head_color": "white"} if head else {}))
        if "sizes" in overrides:   # sizes は渡した分だけを替える（辞書を丸ごと替えない）
            overrides = dict(overrides, sizes={**b.sizes, **overrides["sizes"]})
        return replace(b, **overrides) if overrides else b


def _head_band(prs, frame_names):
    """全ページの本文から、白い文字が乗る色の地（見出し帯）で最も多い色。無ければ None。
    地と文字が 1 つの図形のときも、色の矩形の上に白い文字の枠を重ねたときも数える"""
    from collections import Counter
    cnt = Counter()
    for slide in prs.slides:
        shapes = [sh for sh in slide.shapes if sh.name not in frame_names]
        bands = [(sh, _fill_color(sh).upper()) for sh in shapes if _fill_color(sh) and _saturated(_fill_color(sh))]
        for sh in shapes:
            if not sh.has_text_frame or not sh.text_frame.text.strip():
                continue
            if (_first_color(sh) or "").upper() != "FFFFFF":
                continue
            cx, cy = sh.left + sh.width / 2, sh.top + sh.height / 2
            for b, fill in bands:
                if b is sh or (b.left <= cx <= b.left + b.width and b.top <= cy <= b.top + b.height):
                    cnt[fill] += 1
                    break
    return cnt.most_common(1)[0][0] if cnt else None


def _saturated(hexc):
    """はっきりした色か（淡い地・灰色を除く）"""
    r, g, b = (int(hexc[i:i + 2], 16) for i in (0, 2, 4))
    return max(r, g, b) - min(r, g, b) > 60 and min(r, g, b) < 200


def _first_size(sh, k):
    if not sh.has_text_frame:
        return None
    for p in sh.text_frame.paragraphs:
        for r in p.runs:
            if r.font.size:
                return round(r.font.size / k, 1)
    return None


def _first_color(sh):
    for rpr in sh._element.iter(qn("a:rPr")):
        c = rpr.find(qn("a:solidFill") + "/" + qn("a:srgbClr"))
        if c is not None:
            return c.get("val")
    return None


def _fill_color(sh):
    sp = sh._element.find(qn("p:spPr"))
    c = sp.find(qn("a:solidFill") + "/" + qn("a:srgbClr")) if sp is not None else None
    return c.get("val") if c is not None else None


def _first_font(sh):
    if not sh.has_text_frame:
        return None
    for el in sh._element.iter(qn("a:ea"), qn("a:latin")):
        tf = el.get("typeface")
        if tf:
            return tf
    return None


TEMPLATE = Base(name="template")


# ---------------------------------------------------------------- 開く・保存する


def _load(path) -> Presentation:
    path = Path(path)
    data = path.read_bytes()
    if path.suffix.lower() == ".potx":
        zin = zipfile.ZipFile(io.BytesIO(data))
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                blob = zin.read(item.filename)
                if item.filename == "[Content_Types].xml":
                    blob = blob.replace(POTX_CT, PPTX_CT)
                zout.writestr(item, blob)
        data = buf.getvalue()
    return Presentation(io.BytesIO(data))


def open_deck(path, base: Base | None = None, keep_samples=True):
    """土台を開き、部品が使う設定を入れる。path は "continova"・"unbranded"（同梱のテンプレート）かファイルのパス。

    テンプレートを開くときは base を省く。前回の資料を開くときは Base.from_deck() で作った設定を渡す
    （省くと、テンプレートのレイアウトが無い資料では止める）。
    """
    p = TEMPLATE_FILES.get(path, path)
    prs = _load(p)
    if base is None:
        if any(lo.name.startswith("01｜") for lo in prs.slide_layouts):
            base = TEMPLATE
        else:
            raise SystemExit(f"{p} はテンプレートの系統でない。Base.from_deck() で設定を作って base= に渡す"
                             f"（候補は `template.py --inspect {p} --page <本文のあるページ>`）")
    parts.use(base)
    prs._deck_base = base
    if not keep_samples:
        remove_all_slides(prs)
    return prs


def finalize(prs, out, title=None, check=True):
    """保存の前の後始末をして保存する。

    - 中身の無いプレースホルダーを外す（ページ番号は残す）
    - 外したページへのリンク、外した図形を指すアニメーションを外す
    - どこからも参照されていない画像・パーツへの関係を外す（レイアウトは PowerPoint でページを足すのに使うので残す）
    - 資料の題を入れ、docProps/app.xml のページ数を合わせ、前の資料のページの題の一覧を外す
    - check=True なら check_package で確かめ、問題があれば止める
    """
    live = {s.part for s in prs.slides}
    for i, slide in enumerate(prs.slides, 1):
        drop_empty_placeholders(slide)
        _drop_broken_timing(slide, i)
        for rid, rel in list(slide.part.rels.items()):
            if rel.reltype == RT.SLIDE and rel.target_part not in live:  # 外したページへのリンク
                _remap_rids(slide._element, {rid: None})
                print(f"注意: {i} 枚目の、外したページへのリンクを外した", file=sys.stderr)
        _drop_unreferenced_rels(slide.part)
    if title is not None:
        prs.core_properties.title = title
    buf = io.BytesIO()
    prs.save(buf)
    data = _fix_app_xml(buf.getvalue(), len(prs.slides))
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    if check:
        import check_package

        problems = check_package.check(out)
        if problems:
            raise SystemExit("パッケージに問題がある:\n  " + "\n  ".join(problems))
    return out


def append_shape(tree, el):
    """図形の並びの末尾に足す。extLst があればその前に置く（extLst は並びの最後に置く決まり）"""
    ext = tree.find(qn("p:extLst"))
    if ext is not None:
        ext.addprevious(el)
    else:
        tree.append(el)


def _drop_broken_timing(slide, page):
    """外した図形を指すアニメーションが残ると PowerPoint が修復を求めるので、そのページのアニメーションを外す"""
    timing = slide._element.find(qn("p:timing"))
    if timing is None:
        return
    ids = set(slide._element.xpath(".//p:cNvPr/@id"))
    targets = {t.get("spid") for t in timing.iter(qn("p:spTgt"))}
    if targets - ids:
        slide._element.remove(timing)
        print(f"注意: {page} 枚目のアニメーションは、外した図形を指していたので外した", file=sys.stderr)


def _fix_app_xml(data: bytes, n_slides: int) -> bytes:
    zin = zipfile.ZipFile(io.BytesIO(data))
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            blob = zin.read(item.filename)
            if item.filename == "docProps/app.xml":
                s = blob.decode("utf-8")
                s = re.sub(r"<((?:\w+:)?)HeadingPairs>.*?</\1HeadingPairs>", "", s, flags=re.S)
                s = re.sub(r"<((?:\w+:)?)TitlesOfParts>.*?</\1TitlesOfParts>", "", s, flags=re.S)
                s = re.sub(r"<((?:\w+:)?)Slides>\d+</\1Slides>", lambda m: f"<{m.group(1)}Slides>{n_slides}</{m.group(1)}Slides>", s)
                blob = s.encode("utf-8")
            zout.writestr(item, blob)
    return buf.getvalue()


def rid_refs(el):
    """要素の中で使われている関係 ID（名前空間が relationships の属性の値。接頭辞と属性名によらない）"""
    out = set()
    for node in el.iter():
        if not isinstance(node.tag, str):
            continue
        for k, v in node.attrib.items():
            if k.startswith("{%s}" % R_NS):
                out.add(v)
    return out


KEEP_RTS = (RT.SLIDE_LAYOUT, RT.NOTES_SLIDE, "http://schemas.microsoft.com/office/2007/relationships/diagramDrawing")


def _drop_unreferenced_rels(part):
    used = rid_refs(part._element)
    for rid, rel in list(part.rels.items()):
        if rel.reltype in KEEP_RTS or rel.reltype in COMMENT_RTS:
            continue
        if rid not in used:
            part.rels.pop(rid)


# ---------------------------------------------------------------- ページの枠


def base_of(prs) -> Base:
    return getattr(prs, "_deck_base", parts.BASE)


def placeholder(slide, idx):
    for ph in slide.placeholders:
        if ph.placeholder_format.idx == idx:
            return ph
    return None


def frame_shape(slide, key):
    """題・リード文・ページ番号の枠を返す。key は Base の title・lead・number の値"""
    if isinstance(key, int):
        return placeholder(slide, key)
    for sh in slide.shapes:
        if sh.name == key:
            return sh
    return None


def set_title(slide, text, size=None):
    b = parts.BASE
    sh = frame_shape(slide, b.title)
    if sh is None:
        raise KeyError("題の枠が無い")
    if b.frame == "placeholder" and size is None:
        parts.replace_paras(sh, [text])  # テンプレートの題の書式（レイアウトの大きさ・書体）をそのまま使う
    else:
        parts.write_paras(slide, sh.text_frame._txBody, [text], size=size or "title", color="ink",
                          font=b.head_font, gap=0, line=None)
    return sh


def set_text(slide, key, paras):
    """枠（プレースホルダーの番号か図形の名前）の文字を、枠の書式のまま差し替える"""
    sh = frame_shape(slide, key)
    if sh is None:
        raise KeyError(key)
    return parts.replace_paras(sh, [paras] if isinstance(paras, str) else paras)


LEAD_BOTTOM = {}  # ページのパーツ名 → リード文の下端（px）


def set_lead(slide, paras, size=None, grow=True):
    """リード文を入れる。paras は文字か文字の並び（1 行 1 項目）。文字の下端（px）を返す。

    grow=True で、行数が枠に収まらないときは枠を下へ伸ばす（本文は body_area() で下げる）
    """
    b = parts.BASE
    sh = frame_shape(slide, b.lead)
    if sh is None:
        raise KeyError("リード文の枠が無い")
    sz = parts.S(size or "lead")
    paras = [paras] if isinstance(paras, str) else list(paras)
    parts.write_paras(slide, sh.text_frame._txBody, paras, size=sz, color="ink", gap=2, line=b.lead_line)
    k = parts.scale_of(slide)
    top, w = sh.top / k, sh.width / k
    need = parts.text_height(paras, sz, w - 8, line=b.lead_line + 0.15, gap=2)
    if grow and need > sh.height / k:
        sh.left, sh.top, sh.width = sh.left, sh.top, sh.width  # 位置を明示する（高さだけ書くと位置が 0 になる）
        sh.height = Emu(int(need * k))
    bottom = top + max(need, 0)
    LEAD_BOTTOM[str(slide.part.partname)] = bottom
    return bottom


def body_area(slide, margin=36):
    """リード文の下から本文の範囲 (x, y, w, h) を返す。リード文が長くて本文の上端を越えるときは下げる"""
    x, y, w, h = parts.BASE.body
    lb = LEAD_BOTTOM.get(str(slide.part.partname))
    if lb is not None and lb + margin > y:
        h -= lb + margin - y
        y = lb + margin
    return (x, y, w, h)


def drop_empty_placeholders(slide):
    keep = {parts.BASE.number} if parts.BASE else {99}
    for ph in list(slide.placeholders):
        idx = ph.placeholder_format.idx
        if idx in keep or ph.placeholder_format.type is not None and "SLIDE_NUMBER" in str(ph.placeholder_format.type):
            continue
        if ph.has_text_frame and not ph.text_frame.text.strip():
            ph._element.getparent().remove(ph._element)


# ---------------------------------------------------------------- ページを足す・複製する・並べ替える


def layout(prs, prefix):
    for lo in prs.slide_layouts:
        if lo.name.startswith(prefix) or lo.name == prefix:
            return lo
    names = ", ".join(lo.name for lo in prs.slide_layouts)
    raise KeyError(f"レイアウト「{prefix}」が無い（{names}）")


def _add_slide(prs, lo):
    """add_slide はページの数からパーツ名を決めるので、ページを外した後に足すと名前が重なる。空いている名前に付け直す"""
    from pptx.opc.packuri import PackURI

    slide = prs.slides.add_slide(lo)
    used = {str(p.partname) for p in prs.part.package.iter_parts() if p is not slide.part}
    if str(slide.part.partname) in used:
        n = 1
        while f"/ppt/slides/slide{n}.xml" in used:
            n += 1
        slide.part.partname = PackURI(f"/ppt/slides/slide{n}.xml")
    return slide


def new_slide(prs, layout_prefix, title=None, lead=None):
    """レイアウト名の先頭（"03" など）でページを末尾に足す。ページ番号の枠はレイアウトから写す"""
    lo = layout(prs, layout_prefix)
    slide = _add_slide(prs, lo)
    have = {ph.placeholder_format.idx for ph in slide.placeholders}
    for ph in lo.placeholders:
        if ph.placeholder_format.idx == 99 and 99 not in have:
            append_shape(slide.shapes._spTree, copy.deepcopy(ph._element))
    if title is not None:
        set_title(slide, title)
    if lead is not None:
        set_lead(slide, lead)
    return slide


def _norm(s):
    s = unicodedata.normalize("NFKC", s or "")
    return re.sub(r"\s+", "", s)


def slide_title(slide):
    b = parts.BASE
    sh = frame_shape(slide, b.title) if b else placeholder(slide, 0)
    if sh is not None and sh.has_text_frame:
        return sh.text_frame.text
    return ""


def find_sample(prs, title):
    """題（空白・改行を除いて照合）でページを探す"""
    t = _norm(title)
    hits = [s for s in prs.slides if _norm(slide_title(s)) == t]
    if not hits:
        hits = [s for s in prs.slides if t and t in _norm(slide_title(s))]
    if not hits:
        raise KeyError(f"題が「{title}」のページが無い")
    return hits[0]


def slide_index(prs, slide):
    for i, s in enumerate(prs.slides):
        if s.slide_id == slide.slide_id:
            return i
    raise KeyError(slide)


def move_slide(prs, slide, index):
    """ページを index 番目（0 始まり）へ動かす"""
    lst = prs.slides._sldIdLst
    el = [e for e in lst if int(e.get("id")) == slide.slide_id][0]
    lst.remove(el)
    lst.insert(index, el)


def delete_slide(prs, slide):
    lst = prs.slides._sldIdLst
    for e in list(lst):
        if int(e.get("id")) == slide.slide_id:
            prs.part.drop_rel(e.get(qn("r:id")))
            lst.remove(e)
            return


def remove_all_slides(prs):
    for s in list(prs.slides):
        delete_slide(prs, s)


def keep_slides(prs, slides):
    """並べた順に残し、ほかのページを外す（前回の資料から骨格を作るとき）"""
    ids = [s.slide_id for s in slides]
    for s in list(prs.slides):
        if s.slide_id not in ids:
            delete_slide(prs, s)
    for i, sid in enumerate(ids):
        move_slide(prs, [s for s in prs.slides if s.slide_id == sid][0], i)


def _copy_part(part, package):
    """グラフなどのパーツを、関係ごと写す"""
    name = str(part.partname)
    tmpl = re.sub(r"\d+(\.\w+)$", r"%d\1", name)
    if "%d" not in tmpl:  # 番号の無い名前（image.png など）は、拡張子の前に番号を入れる
        tmpl = re.sub(r"(\.\w+)$", r"%d\1", name)
    pn = package.next_partname(tmpl)
    new = type(part).load(pn, part.content_type, package, part.blob)
    remap = {}
    for rid, rel in part.rels.items():
        if rel.is_external:
            remap[rid] = new.relate_to(rel.target_ref, rel.reltype, is_external=True)
        else:
            remap[rid] = new.relate_to(_copy_part(rel.target_part, package), rel.reltype)
    if remap and hasattr(new, "_element"):
        _remap_rids(new._element, remap)
    return new


def _remap_rids(el, remap):
    for node in el.iter():
        for k, v in list(node.attrib.items()):
            if k.startswith("{%s}" % R_NS) and v in remap:
                if remap[v] is None:
                    del node.attrib[k]
                else:
                    node.set(k, remap[v])


SHARED_RTS = (RT.IMAGE, RT.MEDIA, RT.VIDEO, RT.AUDIO, "http://schemas.microsoft.com/office/2007/relationships/media")
COPIED_RTS = (RT.CHART, RT.OLE_OBJECT, RT.PACKAGE, RT.DIAGRAM_DATA, RT.DIAGRAM_LAYOUT, RT.DIAGRAM_QUICK_STYLE,
              RT.DIAGRAM_COLORS, "http://schemas.microsoft.com/office/2007/relationships/diagramDrawing")


def duplicate(prs, slide, index=None, report=None):
    """同じ資料のページを複製して index 番目（省くと末尾）に置く。

    画像は共有し、グラフ・埋め込みは写す。外部へのリンクは写す。ノート・コメントは持ち込まない。
    report に list を渡すと、持ち込まなかったものを書き足す
    """
    new = _add_slide(prs, slide.slide_layout)
    for sh in list(new.shapes):
        sh._element.getparent().remove(sh._element)
    src_tree = slide.shapes._spTree
    dst_tree = new.shapes._spTree
    for child in src_tree:
        if child.tag in (qn("p:nvGrpSpPr"), qn("p:grpSpPr")):
            continue
        dst_tree.append(copy.deepcopy(child))
    bg = slide._element.cSld.find(qn("p:bg"))
    if bg is not None:
        new._element.cSld.insert(0, copy.deepcopy(bg))
    remap = {}
    for rid, rel in slide.part.rels.items():
        if rel.reltype == RT.SLIDE_LAYOUT:
            continue
        if rel.reltype == RT.NOTES_SLIDE or rel.reltype in COMMENT_RTS:
            if report is not None:
                report.append(f"{slide_index(prs, slide) + 1} 枚目の{'ノート' if rel.reltype == RT.NOTES_SLIDE else 'コメント'}は写さなかった")
            continue
        if rel.is_external:
            remap[rid] = new.part.relate_to(rel.target_ref, rel.reltype, is_external=True)
        elif rel.reltype in COPIED_RTS:
            remap[rid] = new.part.relate_to(_copy_part(rel.target_part, prs.part.package), rel.reltype)
        elif rel.reltype in SHARED_RTS:
            remap[rid] = new.part.relate_to(rel.target_part, rel.reltype)
        elif rel.reltype == RT.SLIDE:
            remap[rid] = None  # 資料の中の別ページへのリンクは外す（外したページの中身が残るのを防ぐ）
            if report is not None:
                report.append(f"{slide_index(prs, slide) + 1} 枚目の別ページへのリンクを外した")
        else:
            raise SystemExit(f"{slide_index(prs, slide) + 1} 枚目は複製できない関係（{rel.reltype.rsplit('/', 1)[-1]}）を持つ")
    _remap_rids(new._element, remap)
    if index is not None:
        move_slide(prs, new, index)
    return new


def strip_body(slide, keep_text=()):
    """枠（題・リード文・ページ番号と、Base.keep の図形）だけを残して本文の図形を外す。

    keep_text に文言の先頭を渡すと、その文言で始まる図形も残す
    """
    b = parts.BASE
    for sh in list(slide.shapes):
        if sh.is_placeholder and sh.placeholder_format.idx in (b.title, b.lead, b.number, 99) and b.frame == "placeholder":
            continue
        if sh.name in b.keep or sh.name in (b.title, b.lead, b.number):
            continue
        if keep_text and sh.has_text_frame and any(sh.text_frame.text.startswith(t) for t in keep_text):
            continue
        sh._element.getparent().remove(sh._element)
    return slide


def import_slide(dst_slide, src, page, drop=None, dy=0, report=None):
    """別の pptx の page 枚目（1 始まり）の図形を dst_slide へ写す（再掲）。

    - drop(shape) が True を返す図形は写さない（元の資料の題・フッター・ページ番号など）
    - スライドの大きさが異なるときは、位置・大きさ・文字の大きさ・線の太さを比で換算する
    - 画像は写す。外部へのリンクは写し、資料の中の別ページへのリンクは外す（report に書く）
    - グラフ・埋め込みなど、ほかの関係を持つ図形は止める（画像にして貼るかを依頼者に聞く）
    """
    src_prs = src if hasattr(src, "slides") else _load(src)
    s = src_prs.slides[page - 1]
    ratio = dst_slide.part.package.presentation_part.presentation.slide_width / src_prs.slide_width
    tree = dst_slide.shapes._spTree
    ids = [int(v) for v in tree.xpath(".//p:cNvPr/@id")] or [1]
    nid = max(ids) + 1
    pending = []
    for sh in s.shapes:
        if drop and drop(sh):
            continue
        el = copy.deepcopy(sh._element)
        if sh.is_placeholder:
            _detach_placeholder(el, sh)
        idmap = {}
        for c in el.xpath(".//p:cNvPr"):
            idmap[c.get("id")] = str(nid)
            c.set("id", str(nid))
            nid += 1
        pending.append((el, idmap))
        for node in el.iter():
            for k, v in list(node.attrib.items()):
                if not k.startswith("{%s}" % R_NS) or not v:
                    continue
                rel = s.part.rels[v]
                if rel.is_external:
                    node.set(k, dst_slide.part.relate_to(rel.target_ref, rel.reltype, is_external=True))
                elif rel.reltype in SHARED_RTS:  # 画像（SVG を含む）・動画はパーツごと写す
                    node.set(k, dst_slide.part.relate_to(_copy_part(rel.target_part, dst_slide.part.package), rel.reltype))
                elif rel.reltype == RT.SLIDE:
                    del node.attrib[k]
                    if report is not None:
                        report.append(f"{page} 枚目の「{sh.name}」の別ページへのリンクを外した")
                else:
                    raise SystemExit(f"{page} 枚目の「{sh.name}」は写せない関係（{rel.reltype.rsplit('/', 1)[-1]}）を持つ。"
                                     "画像にして貼るかを依頼者に聞く")
        if ratio != 1:
            _scale(el, ratio)
        if dy:
            for off in el.xpath("./p:spPr/a:xfrm/a:off | ./p:xfrm/a:off | ./p:grpSpPr/a:xfrm/a:off"):
                off.set("y", str(int(int(off.get("y")) + parts.E(dst_slide, dy))))
        append_shape(tree, el)
    # 線の両端の接続先（図形の ID）を、振り直した ID に合わせる。写さなかった図形への接続は外す
    allmap = {}
    for _, m in pending:
        allmap.update(m)
    for el, _ in pending:
        _remap_connections(el, allmap)
    return dst_slide


def _detach_placeholder(el, sh):
    """写すプレースホルダーを普通の図形にする。レイアウトから受け継いでいた位置を明示する
    （文字の大きさ・書体を受け継いでいた場合は写した先で変わることがあるので、画像で確かめる）"""
    nv = el.find(".//" + qn("p:nvPr"))
    if nv is not None:
        for ph in nv.findall(qn("p:ph")):
            nv.remove(ph)
    sp_pr = el.find(qn("p:spPr"))
    if sp_pr is not None and sp_pr.find(qn("a:xfrm")) is None and sh.left is not None:
        xf = etree.Element(qn("a:xfrm"))
        etree.SubElement(xf, qn("a:off"), x=str(int(sh.left)), y=str(int(sh.top)))
        etree.SubElement(xf, qn("a:ext"), cx=str(int(sh.width)), cy=str(int(sh.height)))
        sp_pr.insert(0, xf)


def _remap_connections(el, idmap):
    for tag in ("a:stCxn", "a:endCxn"):
        for c in el.iter(qn(tag)):
            if c.get("id") in idmap:
                c.set("id", idmap[c.get("id")])
            else:
                c.getparent().remove(c)


def _scale(el, r):
    """位置・大きさ・文字の大きさ・線の太さ・字下げを r 倍する（グループの中は子の座標系のまま）"""
    for xf in el.xpath("./p:spPr/a:xfrm | ./p:xfrm | ./p:grpSpPr/a:xfrm"):
        for tag, attrs in (("a:off", ("x", "y")), ("a:ext", ("cx", "cy"))):
            n = xf.find(qn(tag))
            if n is not None:
                for a in attrs:
                    n.set(a, str(int(int(n.get(a)) * r)))
    for n in el.iter(qn("a:gridCol")):
        n.set("w", str(int(int(n.get("w")) * r)))
    for n in el.iter(qn("a:tr")):
        n.set("h", str(int(int(n.get("h")) * r)))
    for tag in ("a:rPr", "a:defRPr", "a:endParaRPr"):
        for n in el.iter(qn(tag)):
            if n.get("sz"):
                n.set("sz", str(max(100, int(int(n.get("sz")) * r))))
    for n in el.iter(qn("a:ln")):
        if n.get("w"):
            n.set("w", str(int(int(n.get("w")) * r)))
    for n in el.iter(qn("a:pPr")):
        for a in ("marL", "indent"):
            if n.get(a):
                n.set(a, str(int(int(n.get(a)) * r)))
    for n in el.iter(qn("a:spcPts")):
        n.set("val", str(int(int(n.get("val")) * r)))
    for n in el.iter(qn("a:bodyPr")):
        for a in ("lIns", "tIns", "rIns", "bIns"):
            if n.get(a):
                n.set(a, str(int(int(n.get(a)) * r)))
    for n in el.iter(qn("a:tcPr")):
        for a in ("marL", "marR", "marT", "marB"):
            if n.get(a):
                n.set(a, str(int(int(n.get(a)) * r)))


# ---------------------------------------------------------------- コメント


def comments(prs):
    """依頼者のコメントを (ページ, 文字) の並びで返す"""
    out = []
    for i, s in enumerate(prs.slides, 1):
        for rel in s.part.rels.values():
            if rel.reltype in COMMENT_RTS:
                xml = rel.target_part.blob.decode("utf-8", "ignore")
                for t in re.findall(r"<(?:\w+:)?(?:text|t)>([^<]+)</(?:\w+:)?(?:text|t)>", xml):
                    out.append((i, t))
    return out


def remove_comments(prs):
    for s in prs.slides:
        for rid, rel in list(s.part.rels.items()):
            if rel.reltype in COMMENT_RTS:
                s.part.rels.pop(rid)
        for el in [e for e in s._element.iter() if isinstance(e.tag, str) and e.tag.endswith("}commentRel")]:
            ext = el.getparent()
            if ext is not None and ext.getparent() is not None:
                ext.getparent().remove(ext)


# ---------------------------------------------------------------- 一覧（--inspect）


def inspect(path, page=None):
    prs = _load(path)
    k = prs.slide_width / 1920
    print(f"{path}")
    print(f"  大きさ: {prs.slide_width / 12700:.0f}×{prs.slide_height / 12700:.0f}pt（1px = {k / 12700:.3f}pt）")
    if not page:   # --page のときは、そのページの図形の一覧だけを出す
        print("  レイアウト:")
        for lo in prs.slide_layouts:
            phs = ", ".join(f"{ph.placeholder_format.idx}:{ph.name}" for ph in lo.placeholders)
            print(f"    {lo.name}  [{phs}]")
        print("  ページ:")
        for i, s in enumerate(prs.slides, 1):
            texts = [sh.text_frame.text.replace("\n", " ")[:24] for sh in s.shapes
                     if sh.has_text_frame and sh.text_frame.text.strip()]
            print(f"    {i:>3}  {s.slide_layout.name:<16} {' | '.join(texts[:2])}")
    if page:
        s = prs.slides[page - 1]
        print(f"  {page} 枚目の図形（px）:")
        for sh in s.shapes:
            sz = _first_size(sh, k)
            ph = f"ph{sh.placeholder_format.idx}" if sh.is_placeholder else ""
            t = sh.text_frame.text.replace("\n", " ")[:20] if sh.has_text_frame else ""
            print(f"    id={sh.shape_id:<4} {sh.name:<20} {ph:<5} x={sh.left / k:>6.0f} y={sh.top / k:>6.0f} "
                  f"w={sh.width / k:>6.0f} h={sh.height / k:>6.0f} 文字={sz or '':<5} {t}")
        colors = {}
        for el in s._element.iter(qn("a:srgbClr")):
            colors[el.get("val")] = colors.get(el.get("val"), 0) + 1
        print("  使われている色:", ", ".join(f"{c}×{n}" for c, n in sorted(colors.items(), key=lambda x: -x[1])[:12]))
        if not any(lo.name.startswith("01｜") for lo in prs.slide_layouts):
            print("  設定の候補: Base.from_deck(prs, page, title=<題の図形の名前>, lead=<リード文の図形の名前>, "
                  "number=<ページ番号の名前>, keep=(<罫線・フッターの名前>, …))")


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--inspect", required=True)
    ap.add_argument("--page", type=int)
    a = ap.parse_args()
    inspect(TEMPLATE_FILES.get(a.inspect, a.inspect), a.page)
