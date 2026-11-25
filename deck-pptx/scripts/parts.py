"""pptx の部品（文言・図形・表・図・版上げの道具）。

座標と文字の大きさは 1920×1080 の px で書く。土台のスライドの大きさに合わせて換算する
（テンプレートは 960×540pt なので 1px = 0.5pt、1440×810pt の資料なら 1px = 0.75pt）。
色・文字の大きさ・書体・本文の範囲は土台の設定（template.Base）から読む。template.open_deck() が設定する。

文字列の中の記法:
  **太字**  {強:…}青の太字  {悪:…}赤の太字  {良:…}緑の太字  {灰:…}灰色  {太:…}太字
  {b|…}{g|…}{r|…} 青・緑・赤  {B|…}{G|…}{R|…} 同じ色の太字
  [文字](https://…) リンク付きの文字   （TODO: …）は赤にする   段落の中の改行は \\n
"""
from __future__ import annotations

import copy
import io
import math
import re
from pathlib import Path

from lxml import etree
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from pptx.util import Emu

BASE = None  # template.open_deck() が template.Base を入れる


def use(base):
    global BASE
    BASE = base


def C(key):
    """色の名前 → 16 進。16 進をそのまま渡してもよい"""
    if key is None:
        return None
    return BASE.colors.get(key, key)


def S(key):
    """文字の大きさの名前 → px。数値をそのまま渡してもよい"""
    return BASE.sizes.get(key, key) if isinstance(key, str) else key


# ---------------------------------------------------------------- 単位


def scale_of(slide):
    width = slide.part.package.presentation_part.presentation.slide_width
    return width / 1920


def E(slide, v):
    return Emu(int(round(v * scale_of(slide))))


def pt_of(slide, px_size):
    """文字の大きさ px → pt"""
    return px_size * scale_of(slide) / 12700


# ---------------------------------------------------------------- 文字の幅と行数


def plain(s: str) -> str:
    """記法を外した、表示される文字"""
    s = re.sub(r"\{[強悪良灰太]:(.+?)\}", r"\1", s)
    s = re.sub(r"\{[bgrBGR]\|(.+?)\}", r"\1", s)
    s = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r"\1", s)
    return s.replace("**", "")


def text_width(s: str, size: float) -> float:
    """1 行で書いたときの幅（px）の見積もり。全角 1 字 = 文字の大きさ、半角は 0.58"""
    return sum(size * (1.0 if ord(ch) > 0x2000 else 0.58) for ch in plain(s))


def n_lines(s: str, size: float, width: float) -> int:
    return max(1, sum(max(1, math.ceil(text_width(part, size) / max(width, 1))) for part in plain(s).split("\n")))


def text_height(paras, size, width, line=1.3, gap=None):
    """段落の並びの高さ（px）の見積もり"""
    gap = BASE.gap if gap is None else gap
    h = 0
    for o in _as_dicts(paras):
        sz = S(o.get("size", size))
        w = width - (sz * 0.95 if o.get("bullet") else 0)
        h += n_lines(o["text"], sz, w) * sz * line + o.get("gap", gap)
    return h


def fit_size(paras, width, height, candidates):
    """文字の大きさの候補（大きい順）から、枠に収まる最初のものを返す。収まらなければ最後の候補"""
    for sz in candidates:
        if text_height(paras, sz, width) <= height:
            return sz
    return candidates[-1]


# ---------------------------------------------------------------- 段落


TOKEN = re.compile(
    r"\*\*(?P<bold>.+?)\*\*"
    r"|\{(?P<jk>[強悪良灰太]):(?P<jt>.+?)\}"
    r"|\{(?P<ek>[bgrBGR])\|(?P<et>.+?)\}"
    r"|\[(?P<lt>[^\]]+)\]\((?P<lu>https?://[^)]+)\)"
    r"|(?P<todo>（TODO[:：][^）]*）)"
)
JA = {"強": ("accent", True), "悪": ("bad", True), "良": ("good", True), "灰": ("sub", None), "太": (None, True)}
EN = {"b": "accent", "g": "good", "r": "bad"}


def runs_of(s, color, bold):
    """文字列を (文字, 色, 太字, リンク) の並びにする"""
    out, pos = [], 0
    for m in TOKEN.finditer(s):
        if m.start() > pos:
            out.append((s[pos:m.start()], color, bold, None))
        if m.group("bold") is not None:
            for t, c, b, u in runs_of(m.group("bold"), color, True):
                out.append((t, c, b, u))
        elif m.group("jk"):
            ckey, b = JA[m.group("jk")]
            out.append((m.group("jt"), C(ckey) if ckey else color, bold if b is None else b, None))
        elif m.group("ek"):
            k = m.group("ek")
            out.append((m.group("et"), C(EN[k.lower()]), bold or k.isupper(), None))
        elif m.group("lt"):
            out.append((m.group("lt"), C("accent"), bold, m.group("lu")))
        else:
            out.append((m.group("todo"), C("bad"), bold, None))
        pos = m.end()
    if pos < len(s):
        out.append((s[pos:], color, bold, None))
    return out


def _rpr(slide, tag, size, color, bold, font):
    r = etree.Element(qn(tag), lang="ja-JP", altLang="en-US", sz=str(int(round(pt_of(slide, size) * 100))),
                      b="1" if bold else "0")
    sf = etree.SubElement(r, qn("a:solidFill"))
    etree.SubElement(sf, qn("a:srgbClr"), val=color)
    if font:
        for t in ("a:latin", "a:ea", "a:cs"):
            etree.SubElement(r, qn(t), typeface=font)
    return r


def _as_dicts(paras):
    if isinstance(paras, (str, dict)):
        paras = [paras]
    return [p if isinstance(p, dict) else {"text": p} for p in paras]


def write_paras(slide, txBody, paras, size="body", color="ink", bold=False, font=None, bullet=False, gap=None,
                align=None, line=None, level=0):
    """txBody の段落を paras で置き換える。

    paras の要素は文字か dict(text=, bullet=, level=, size=, bold=, color=, gap=, align=, line=, font=)。
    bullet=True は「・」のぶら下げの箇条書き（折り返し行を本文の先頭にそろえる）。level=1 で 1 段下げる。
    """
    font = font or BASE.font
    gap = BASE.gap if gap is None else gap
    for p in txBody.findall(qn("a:p")):
        txBody.remove(p)
    for o in _as_dicts(paras):
        sz, bl, cl = S(o.get("size", size)), o.get("bold", bold), C(o.get("color", color))
        bu, lv = o.get("bullet", bullet), o.get("level", level)
        al, gp, ln, fn = o.get("align", align), o.get("gap", gap), o.get("line", line), o.get("font", font)
        p = etree.SubElement(txBody, qn("a:p"))
        ppr = etree.SubElement(p, qn("a:pPr"))
        if al:
            ppr.set("algn", {"left": "l", "center": "ctr", "right": "r"}.get(al, al))
        if bu:
            ind = E(slide, sz * 0.95)
            ppr.set("marL", str(int(ind * (lv + 1))))
            ppr.set("indent", str(-int(ind)))
        elif lv:
            ppr.set("marL", str(int(E(slide, sz * 0.95 * lv))))
        if ln:
            ls = etree.SubElement(ppr, qn("a:lnSpc"))
            etree.SubElement(ls, qn("a:spcPct"), val=str(int(ln * 100000)))
        sa = etree.SubElement(ppr, qn("a:spcAft"))
        etree.SubElement(sa, qn("a:spcPts"), val=str(int(pt_of(slide, gp) * 100)))
        if bu:
            if BASE.bullet_color:
                bc = etree.SubElement(ppr, qn("a:buClr"))
                etree.SubElement(bc, qn("a:srgbClr"), val=C(BASE.bullet_color))
            if fn:
                etree.SubElement(ppr, qn("a:buFont"), typeface=fn)
            etree.SubElement(ppr, qn("a:buChar"), char=BASE.bullet_char if lv == 0 else BASE.bullet_char2)
        else:
            etree.SubElement(ppr, qn("a:buNone"))
        for text, c, b, url in runs_of(o["text"], cl, bl):
            for i, part in enumerate(text.split("\n")):
                if i:
                    br = etree.SubElement(p, qn("a:br"))
                    br.append(_rpr(slide, "a:rPr", sz, c, b, fn))
                if part:
                    r = etree.SubElement(p, qn("a:r"))
                    rpr = _rpr(slide, "a:rPr", sz, c, b, fn)
                    if url:
                        rid = slide.part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink", is_external=True)
                        etree.SubElement(rpr, qn("a:hlinkClick"), {qn("r:id"): rid})  # 書体の後に置く（スキーマの順）
                    r.append(rpr)
                    etree.SubElement(r, qn("a:t")).text = part
        p.append(_rpr(slide, "a:endParaRPr", sz, cl, bl, fn))


def _body_pr(slide, txBody, anchor="t", ins=0, wrap=True, autofit=False):
    bp = txBody.find(qn("a:bodyPr"))
    for k in list(bp.attrib):
        del bp.attrib[k]
    for ch in list(bp):
        bp.remove(ch)
    v = str(int(E(slide, ins)))
    bp.set("wrap", "square" if wrap else "none")
    for side in ("lIns", "tIns", "rIns", "bIns"):
        bp.set(side, v)
    bp.set("anchor", anchor)
    etree.SubElement(bp, qn("a:normAutofit" if autofit else "a:noAutofit"))


def _strip_style(sh):
    st = sh._element.find(qn("p:style"))
    if st is not None:
        sh._element.remove(st)


# ---------------------------------------------------------------- 文字と図形


def text(slide, x, y, w, h, paras, name=None, anchor="t", ins=0, wrap=True, **kw):
    """テキストボックス。kw は write_paras と同じ"""
    sh = slide.shapes.add_textbox(E(slide, x), E(slide, y), E(slide, w), E(slide, h))
    if name:
        sh.name = name
    tb = sh._element.find(qn("p:txBody"))
    _body_pr(slide, tb, anchor, ins, wrap)
    write_paras(slide, tb, paras, **kw)
    return sh


def rect(slide, x, y, w, h, fill=None, line=None, lw=1.5, shape=MSO_SHAPE.RECTANGLE, name=None, dash=None,
         paras=None, anchor="ctr", ins=12, **kw):
    """塗り矩形（帯・カード）。paras を渡すと、矩形の中に文字を書く（帯・カードは 1 つの図形にする）"""
    from pptx.dml.color import RGBColor

    sh = slide.shapes.add_shape(shape, E(slide, x), E(slide, y), E(slide, w), E(slide, h))
    _strip_style(sh)
    if name:
        sh.name = name
    if fill:
        sh.fill.solid()
        sh.fill.fore_color.rgb = RGBColor.from_string(C(fill))
    else:
        sh.fill.background()
    if line:
        sh.line.color.rgb = RGBColor.from_string(C(line))
        sh.line.width = E(slide, lw)
        if dash:
            etree.SubElement(sh._element.spPr.find(qn("a:ln")), qn("a:prstDash"), val=dash)
    else:
        sh.line.fill.background()
    tb = sh._element.find(qn("p:txBody"))
    if tb is not None:
        _body_pr(slide, tb, anchor, ins)
        if paras is not None:
            write_paras(slide, tb, paras, **kw)
    return sh


def hline(slide, x, y, w, color="line", t=2):
    return rect(slide, x, y, w, t, fill=color)


def vline(slide, x, y, h, color="line", t=2):
    return rect(slide, x, y, t, h, fill=color)


def arrow(slide, x0, y0, x1, y1, color="accent", w=3, dash=None, head=True):
    """直線の矢印（コネクタ）"""
    from pptx.dml.color import RGBColor
    from pptx.enum.shapes import MSO_CONNECTOR

    cn = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, E(slide, x0), E(slide, y0), E(slide, x1), E(slide, y1))
    cn.line.color.rgb = RGBColor.from_string(C(color))
    cn.line.width = E(slide, w)
    ln = cn._element.spPr.find(qn("a:ln"))
    if dash:
        etree.SubElement(ln, qn("a:prstDash"), val=dash)
    if head:
        etree.SubElement(ln, qn("a:tailEnd"), type="triangle", w="med", len="med")
    return cn


def block_arrow(slide, x, y, w, h, fill="accent", direction="right"):
    shape = {"right": MSO_SHAPE.RIGHT_ARROW, "down": MSO_SHAPE.DOWN_ARROW, "left": MSO_SHAPE.LEFT_ARROW}[direction]
    return rect(slide, x, y, w, h, fill=fill, shape=shape)


def heading(slide, x, y, w, label, size="head", color="ink", rule="line"):
    """小見出し（下に細い罫線）。下端の y を返す"""
    sz = S(size)
    h = sz * 1.5
    text(slide, x, y, w, h, [label], size=sz, color=color, bold=True, anchor="b")
    hline(slide, x, y + h + 6, w, rule)
    return y + h + 18


def note(slide, texts, y=None, x=None, w=None, size="note"):
    """ページの下の注・出典。y を省くとフッターの線の上に下ぞろえで置く"""
    bx, by, bw, bh = BASE.body
    x = bx if x is None else x
    w = bw if w is None else w
    paras = [{"text": t} for t in ([texts] if isinstance(texts, str) else texts)]
    h = text_height(paras, S(size), w, gap=2)
    y = by + bh - h if y is None else y
    text(slide, x, y, w, h + 4, paras, size=size, color="sub", gap=2, anchor="b")
    return y


def bullets(items, level=0):
    """[文字 | (文字, [子の文字])] → 箇条書きの段落"""
    out = []
    for it in items:
        if isinstance(it, (tuple, list)):
            out.append({"text": it[0], "bullet": True, "level": level})
            out.extend(bullets(it[1], level + 1))
        else:
            out.append({"text": it, "bullet": True, "level": level})
    return out


def body_text(slide, paras, area=None, size="body", **kw):
    """本文の範囲に箇条書き・段落を置く"""
    x, y, w, h = area or BASE.body
    return text(slide, x, y, w, h, paras, size=size, **kw)


# ---------------------------------------------------------------- 枠・カード・工程


def callout(slide, x, y, w, head, items, h=None, size="body", fill="pale", edge="accent"):
    """見えたことの枠（淡い青の地＋左の青い線）。高さを返す"""
    sz = S(size)
    paras = bullets(items) if items else []
    body_h = text_height(paras, sz, w - 48) if paras else 0
    h = h or (sz * 1.6 + body_h + 36)
    rect(slide, x, y, w, h, fill=fill)
    rect(slide, x, y, 8, h, fill=edge)
    text(slide, x + 28, y + 16, w - 44, sz * 1.5, [head], size=sz, bold=True, color=edge)
    if paras:
        text(slide, x + 28, y + 16 + sz * 1.6, w - 44, h - sz * 1.6 - 24, paras, size=sz)
    return h


def ask_box(slide, items, x=None, y=None, w=None, head="お伺いしたいこと", size="body"):
    """お伺いしたいことの枠（青の線の枠＋番号付き）。y を省くと本文の下端にそろえる。高さを返す"""
    bx, by, bw, bh = BASE.body
    x, w = (bx if x is None else x), (bw if w is None else w)
    sz = S(size)
    paras = [{"text": f"{i}. {t}"} for i, t in enumerate(items, 1)]
    h = sz * 1.6 + text_height(paras, sz, w - 56) + 36
    y = by + bh - h if y is None else y
    rect(slide, x, y, w, h, fill="white", line="accent", lw=2)
    text(slide, x + 28, y + 16, w - 56, sz * 1.5, [head], size=sz, bold=True, color="accent")
    text(slide, x + 28, y + 16 + sz * 1.6, w - 56, h - sz * 1.6 - 24, paras, size=sz)
    return h


def warn_band(slide, x, y, w, text_, size="body"):
    """注意の帯（淡い赤の地）。高さを返す"""
    sz = S(size)
    h = text_height([text_], sz, w - 48) + 28
    rect(slide, x, y, w, h, fill="pale_bad", paras=[text_], size=sz, anchor="ctr", ins=16)
    return h


def cards(slide, heads, items, area=None, numbered=False, head_h=None, size="body", head_size="head",
          head_fill="surface", head_color="ink", fill="white", line="line", gap=24, emph=None, fit=True):
    """見出し帯カードの列。heads は見出し、items はカードごとの箇条書き（文字の並び）。

    emph に番号（0 始まり）を渡すと、そのカードの見出しを青にする。カードの下端の y を返す
    """
    x0, y0, w0, h0 = area or BASE.body
    n = len(heads)
    cw = (w0 - gap * (n - 1)) / n
    hs = S(head_size)
    head_h = head_h or max(hs * 2.2, max(text_height([h], hs, cw - 32) for h in heads) + 24)
    if fit:  # カードの高さを中身に合わせる（範囲より高くはしない）
        need = max(text_height(bullets(its), S(size), cw - 40) for its in items) if any(items) else 0
        h0 = min(h0, head_h + need + 56)
    for i, (hd, its) in enumerate(zip(heads, items)):
        x = x0 + i * (cw + gap)
        label = f"{i + 1}. {hd}" if numbered else hd
        on = emph is not None and i in (emph if isinstance(emph, (list, tuple, set)) else [emph])
        rect(slide, x, y0, cw, h0, fill=fill, line=line)
        rect(slide, x, y0, cw, head_h, fill="accent" if on else head_fill,
             paras=[label], size=hs, bold=True, color="white" if on else head_color, anchor="ctr", ins=16)
        if its:
            text(slide, x + 20, y0 + head_h + 20, cw - 40, h0 - head_h - 32, bullets(its), size=size)
    return y0 + h0


def steps(slide, nodes, area=None, size="body", head_size="head", owner_h=None, gap=56, fit=True):
    """主体付きのステップノード列。nodes は dict(owner=主体（ヒト／AI など）, head=見出し, items=[…], emph=bool)。

    上に主体のラベル、その下に番号付きの見出しとカード、カードの間に矢印を置く。下端の y を返す
    """
    x0, y0, w0, h0 = area or BASE.body
    n = len(nodes)
    cw = (w0 - gap * (n - 1)) / n
    hs, sz = S(head_size), S(size)
    owner_h = owner_h if owner_h is not None else (sz * 1.8 if any(nd.get("owner") for nd in nodes) else 0)
    head_h = max(hs * 2.2, max(text_height([nd["head"]], hs, cw - 32) for nd in nodes) + 24)
    if fit:
        need = max(text_height(bullets(nd.get("items") or []), sz, cw - 40) for nd in nodes)
        h0 = min(h0, owner_h + head_h + need + 56)
    for i, nd in enumerate(nodes):
        x = x0 + i * (cw + gap)
        if nd.get("owner"):
            text(slide, x, y0, cw, owner_h, [nd["owner"]], size=sz, color="sub", bold=True, align="center", anchor="ctr")
        y = y0 + owner_h
        on = nd.get("emph")
        rect(slide, x, y, cw, head_h, fill="accent" if on else "surface",
             paras=[f"{i + 1}　{nd['head']}"], size=hs, bold=True, color="white" if on else "ink", ins=16)
        rect(slide, x, y + head_h, cw, h0 - owner_h - head_h, fill="white", line="line")
        if nd.get("items"):
            text(slide, x + 20, y + head_h + 20, cw - 40, h0 - owner_h - head_h - 32, bullets(nd["items"]), size=sz)
        if i < n - 1:
            block_arrow(slide, x + cw + gap * 0.25, y + head_h / 2 - 14, gap * 0.5, 28, fill="accent")
    return y0 + h0


def chevrons(slide, labels, x, y, w, h=56, fills=None, colors=None, size="head", gap=6):
    """シェブロンの工程（1 つ目は五角形）。fills・colors は工程ごとの色の並び"""
    n = len(labels)
    cw = (w - gap * (n - 1)) / n
    for i, lb in enumerate(labels):
        shp = MSO_SHAPE.PENTAGON if i == 0 else MSO_SHAPE.CHEVRON
        fill = (fills or ["accent"] * n)[i]
        color = (colors or ["white"] * n)[i]
        rect(slide, x + i * (cw + gap), y, cw + (h * 0.3 if i < n - 1 else 0), h, fill=fill, shape=shp,
             paras=[lb], size=size, bold=True, color=color, align="center", ins=8)
    return cw


def flow(slide, step_labels, details, area=None, head_h=64, size="body", emph_last=False, gap=6):
    """上に工程のシェブロン、下に工程と列でそろえた説明のボックスを置く。details は工程ごとの箇条書き"""
    x0, y0, w0, h0 = area or BASE.body
    n = len(step_labels)
    fills = ["accent"] * n
    if emph_last:
        fills = ["surface"] * (n - 1) + ["accent"]
    colors = ["white" if f == "accent" else "ink" for f in fills]
    cw = chevrons(slide, step_labels, x0, y0, w0, head_h, fills, colors, gap=gap)
    for i, its in enumerate(details):
        x = x0 + i * (cw + gap)
        rect(slide, x, y0 + head_h + 20, cw, h0 - head_h - 20, fill="white", line="line")
        text(slide, x + 18, y0 + head_h + 38, cw - 36, h0 - head_h - 56, bullets(its), size=size)
    return y0 + h0


def matrix(slide, cols, rows, cells, area=None, row_head_w=220, head_h=64, size="table", head_size="head",
           col_heads="chevron", outcome=False, row_h=None, gap=6):
    """マトリクス。cols は列の見出し、rows は行の見出し、cells[r][c] は箇条書き（文字の並び）。

    col_heads="chevron" で列の見出しを工程のシェブロンに、"band" で帯にする。
    outcome=True で最後の列を成果の列にし、手前の列から矢印を置く。row_h で行ごとの高さを指定できる
    """
    x0, y0, w0, h0 = area or BASE.body
    nc, nr = len(cols), len(rows)
    xs = x0 + row_head_w + gap
    cw = (w0 - row_head_w - gap - gap * (nc - 1) - (40 if outcome else 0)) / nc
    if col_heads == "chevron":
        n_ch = nc - (1 if outcome else 0)
        chevrons(slide, cols[:n_ch], xs, y0, cw * n_ch + gap * (n_ch - 1), head_h, gap=gap)
        if outcome:
            rect(slide, xs + n_ch * (cw + gap) + 40, y0, cw, head_h, fill="ink", paras=[cols[-1]],
                 size=head_size, bold=True, color="white", align="center")
    else:
        for c, lb in enumerate(cols):
            ox = 40 if (outcome and c == nc - 1) else 0
            rect(slide, xs + c * (cw + gap) + ox, y0, cw, head_h, fill="surface", paras=[lb], size=head_size,
                 bold=True, color="ink", align="center")
    avail = h0 - head_h - gap
    heights = row_h or [(avail - gap * (nr - 1)) / nr] * nr
    y = y0 + head_h + gap
    for r, rl in enumerate(rows):
        rh = heights[r]
        rect(slide, x0, y, row_head_w, rh, fill="surface", paras=[rl], size=head_size, bold=True, color="ink", ins=14)
        for c in range(nc):
            ox = 40 if (outcome and c == nc - 1) else 0
            cx = xs + c * (cw + gap) + ox
            rect(slide, cx, y, cw, rh, fill="white", line="line")
            its = cells[r][c]
            if its:
                text(slide, cx + 14, y + 12, cw - 28, rh - 20, bullets(its), size=size)
        if outcome:
            ax = xs + (nc - 1) * (cw + gap) - gap
            block_arrow(slide, ax + 4, y + rh / 2 - 14, 32, 28, fill="accent")
        y += rh + gap
    return y


def quad2(slide, x_label, y_label, quads, area=None, focus=None, size="body", head_size="head"):
    """2 軸の 4 象限。quads は [(見出し, [項目])] を 左上・右上・左下・右下 の順。focus は青にする象限の番号"""
    x0, y0, w0, h0 = area or BASE.body
    lw = 56
    gx, gy = x0 + lw, y0
    gw, gh = w0 - lw, h0 - 48
    qw, qh = (gw - 12) / 2, (gh - 12) / 2
    for i, (hd, its) in enumerate(quads):
        qx = gx + (i % 2) * (qw + 12)
        qy = gy + (i // 2) * (qh + 12)
        on = focus is not None and i == focus
        rect(slide, qx, qy, qw, qh, fill="pale" if on else "white", line="accent" if on else "line", lw=2 if on else 1.5)
        text(slide, qx + 20, qy + 16, qw - 40, S(head_size) * 1.6, [hd], size=head_size, bold=True,
             color="accent" if on else "ink")
        if its:
            text(slide, qx + 20, qy + 16 + S(head_size) * 1.8, qw - 40, qh - 40, bullets(its), size=size)
    text(slide, gx, gy + gh + 8, gw, 40, [f"{x_label} →"], size=size, color="sub", align="center")
    tb = text(slide, x0 - gh / 2 + lw / 2, gy + gh / 2 - 20, gh, 40, [f"{y_label} →"], size=size, color="sub",
              align="center")
    tb.rotation = 270
    return y0 + h0


def month_band(slide, months, bands, area=None, milestones=(), label_w=260, row_h=64, size="body"):
    """月の帯（スケジュール）。months は月の見出し、bands は dict(label=, start=, end=, emph=bool, text=)
    （start・end は月の番号。0 始まりで end を含む）、milestones は (月の番号, 見出し) の並び（◆で示す）
    """
    x0, y0, w0, h0 = area or BASE.body
    n = len(months)
    mw = (w0 - label_w) / n
    for i, m in enumerate(months):
        rect(slide, x0 + label_w + i * mw, y0, mw - 4, 48, fill="surface", paras=[m], size=size, bold=True,
             align="center")
    y = y0 + 60
    for b in bands:
        text(slide, x0, y, label_w - 16, row_h, [b["label"]], size=size, bold=True, anchor="ctr")
        bx = x0 + label_w + b["start"] * mw
        bw = (b["end"] - b["start"] + 1) * mw - 4
        rect(slide, bx, y + 10, bw, row_h - 20, fill="accent" if b.get("emph") else "mid",
             paras=[b.get("text", "")], size=size, color="white" if b.get("emph") else "ink", ins=12)
        hline(slide, x0, y + row_h, w0, "line", 1)
        y += row_h
    for mi, lb in milestones:
        mx = x0 + label_w + (mi + 0.5) * mw
        text(slide, mx - 120, y + 8, 240, 40, [f"◆ {lb}"], size=size, color="accent", bold=True, align="center")
    return y + 56


def gantt(slide, weeks, rows, x=None, y=None, w=None, label_w=420, extra_cols=(), row_h=None, size="table"):
    """ガント（タスク×週）。rows は dict(group=, task=, weeks=[週の番号], done=[週の番号], mark=[週の番号],
    <extra_cols の名前>=文字)。done は ✓、mark は ◆（完了を確かめる週）。左の大項目は同じ値が続けば結合する
    """
    bx, by, bw, _ = BASE.body
    x, y, w = (bx if x is None else x), (by if y is None else y), (bw if w is None else w)
    extra_w = [c[1] for c in extra_cols]
    ww = (w - label_w - sum(extra_w)) / len(weeks)
    header = ["", "タスク"] + [c[0] for c in extra_cols] + list(weeks)
    body = []
    for r in rows:
        line_ = [r.get("group", ""), r["task"]] + [r.get(c[0], "") for c in extra_cols]
        for i in range(len(weeks)):
            if i in r.get("done", []):
                line_.append("✓")
            elif i in r.get("mark", []):
                line_.append("◆")
            elif i in r.get("weeks", []):
                line_.append("■")
            else:
                line_.append("")
        body.append(line_)
    widths = [label_w * 0.38, label_w * 0.62] + extra_w + [ww] * len(weeks)
    gf = table(slide, [header] + body, x=x, y=y, w=w, col_widths=widths, size=size, merge_first=True,
               center_cols=list(range(2 + len(extra_cols), len(header))))
    tbl = gf.table
    for ri, r in enumerate(rows, 1):
        for i in range(len(weeks)):
            if i in r.get("weeks", []) and i not in r.get("done", []) and i not in r.get("mark", []):
                cell = tbl.cell(ri, 2 + len(extra_cols) + i)
                _fill_cell(cell, C("mid"))
                _clear_cell_text(cell)
    return gf


# ---------------------------------------------------------------- 表


def _tcpr(slide, tc, fill, anchor="t", mar=(12, 12, 6, 6), line="line", lw=1):
    old = tc.find(qn("a:tcPr"))
    if old is not None:
        tc.remove(old)
    pr = etree.SubElement(tc, qn("a:tcPr"), marL=str(int(E(slide, mar[0]))), marR=str(int(E(slide, mar[1]))),
                          marT=str(int(E(slide, mar[2]))), marB=str(int(E(slide, mar[3]))), anchor=anchor)
    for side in ("a:lnL", "a:lnR", "a:lnT", "a:lnB"):
        ln = etree.SubElement(pr, qn(side), w=str(int(E(slide, lw))))
        sf = etree.SubElement(ln, qn("a:solidFill"))
        etree.SubElement(sf, qn("a:srgbClr"), val=C(line))
        etree.SubElement(ln, qn("a:prstDash"), val="solid")
    if fill:
        sf = etree.SubElement(pr, qn("a:solidFill"))
        etree.SubElement(sf, qn("a:srgbClr"), val=C(fill))
    else:
        etree.SubElement(pr, qn("a:noFill"))


def _fill_cell(cell, color):
    pr = cell._tc.find(qn("a:tcPr"))
    for tag in ("a:solidFill", "a:noFill"):
        for el in pr.findall(qn(tag)):
            pr.remove(el)
    sf = etree.SubElement(pr, qn("a:solidFill"))
    etree.SubElement(sf, qn("a:srgbClr"), val=color)


def _clear_cell_text(cell):
    for r in cell._tc.iter(qn("a:r")):
        r.find(qn("a:t")).text = ""


NUMERIC = re.compile(r"^[−\-+]?[\d,.]+(%|件|人|円|pt)?$|^[\d.,]+ ?→ ?[\d.,]+$")


def cell_paras(v):
    """セルの値 → 段落。改行（\\n）で分けた 2 項目以上か「・」で始まる項目は箇条書きにする"""
    if isinstance(v, (list, tuple)):
        return bullets(v)
    if isinstance(v, dict):
        return [v]
    lines = [ln for ln in str(v).split("\n")]
    if len(lines) > 1 or str(v).startswith("・"):
        return [{"text": ln.lstrip("・"), "bullet": True} for ln in lines if ln.strip()]
    return [str(v)]


def row_heights(rows, widths, size, pad=(12, 6), line=1.3, min_h=0):
    out = []
    for r in rows:
        hs = []
        for v, cw in zip(r, widths):
            hs.append(text_height(cell_paras(v), size, cw - 2 * pad[0], line=line, gap=2))
        out.append(max(min_h, max(hs) + 2 * pad[1] + 4))
    return out


def col_widths_for(rows, w, size, min_w=120):
    """列ごとの最も長い値から列幅を決める（短いラベルの列は狭く、説明の列は広く）"""
    n = len(rows[0])
    need = []
    for c in range(n):
        longest = max(text_width(plain(str(r[c] if not isinstance(r[c], (list, tuple)) else max(r[c], key=len))), size)
                      for r in rows)
        need.append(max(min_w, min(longest + 32, w)))
    total = sum(need)
    if total <= w:  # 余りは、長い値の列ほど多く配る（短いラベルの列を広げすぎない）
        return [v * w / total for v in need]
    # 収まらないときは、長い列から縮める
    fixed = [v for v in need if v <= w / n]
    flex = [v for v in need if v > w / n]
    room = w - sum(fixed)
    return [v if v <= w / n else room * v / sum(flex) for v in need]


def table(slide, rows, x=None, y=None, w=None, col_widths=None, size="table", header=True, merge_first=False,
          marks=(), total_last=False, center_cols=(), name=None, min_h=0, header_fill="surface",
          header_color="sub"):
    """表。rows の 1 行目は見出し（header=False なら見出しなし）。

    セルの値は文字・文字の並び（箇条書き）・dict(text=, bold=, color=, fill=, align=)。
    merge_first=True で、左端の列の同じ値が続くセルを結合する。marks は青の太字にするセル (行, 列) の並び。
    数値だけのセルは右にそろえる。表の図形を返す（下端は gf.top + gf.height）
    """
    bx, by, bw, _ = BASE.body
    x, y, w = (bx if x is None else x), (by if y is None else y), (bw if w is None else w)
    sz = S(size)
    widths = col_widths or col_widths_for(rows, w, sz)
    k = w / sum(widths)
    widths = [c * k for c in widths]
    heights = row_heights(rows, widths, sz, min_h=min_h)
    gf = slide.shapes.add_table(len(rows), len(widths), E(slide, x), E(slide, y), E(slide, w), E(slide, sum(heights)))
    if name:
        gf.name = name
    tbl = gf.table
    tp = tbl._tbl.tblPr
    for kk in list(tp.attrib):
        del tp.attrib[kk]
    for ch in list(tp):
        tp.remove(ch)
    for i, cw in enumerate(widths):
        tbl.columns[i].width = E(slide, cw)
    for i, rh in enumerate(heights):
        tbl.rows[i].height = E(slide, rh)
    marks = set(marks)
    for ri, r in enumerate(rows):
        is_head = header and ri == 0
        is_total = total_last and ri == len(rows) - 1
        for ci, v in enumerate(r):
            cell = tbl.cell(ri, ci)
            paras = cell_paras(v)
            o = v if isinstance(v, dict) else {}
            al = o.get("align")
            if not al and not is_head and (ci in center_cols):
                al = "center"
            if not al and not is_head and ci > 0 and NUMERIC.match(plain(str(v)).strip() or "x"):
                al = "right"
            color = "accent" if (ri, ci) in marks else (header_color if is_head else o.get("color", "ink"))
            bold = (ri, ci) in marks or is_head or is_total or o.get("bold", False)
            write_paras(slide, cell._tc.find(qn("a:txBody")), paras, size=sz, color=color, bold=bold, gap=2, align=al)
            fill = o.get("fill") or (header_fill if (is_head or is_total) else "white")
            _tcpr(slide, cell._tc, fill, "ctr" if is_head else "t")
    if merge_first:
        start = 1 if header else 0
        i = start
        while i < len(rows):
            j = i
            while j + 1 < len(rows) and rows[j + 1][0] == rows[i][0] and rows[i][0] and not (total_last and j + 1 == len(rows) - 1):
                j += 1
            if j > i:
                for kk in range(i + 1, j + 1):
                    _clear_cell_text(tbl.cell(kk, 0))
                    for p in tbl.cell(kk, 0)._tc.find(qn("a:txBody")).findall(qn("a:p"))[1:]:
                        p.getparent().remove(p)
                keep = copy.deepcopy(tbl.cell(i, 0)._tc.find(qn("a:txBody")))
                tbl.cell(i, 0).merge(tbl.cell(j, 0))
                tb = tbl.cell(i, 0)._tc.find(qn("a:txBody"))
                tb.getparent().replace(tb, keep)
            i = j + 1
    return gf


def mark_cell(gf, r, c):
    """表の見せたいセルを青の太字にする"""
    for rpr in gf.table.cell(r, c)._tc.iter(qn("a:rPr")):
        rpr.set("b", "1")
        sf = rpr.find(qn("a:solidFill"))
        if sf is not None:
            sf[0].set("val", C("accent"))


def bottom(shape_):
    """図形の下端（px）"""
    k =(shape_.part.package.presentation_part.presentation.slide_width / 1920)
    return (shape_.top + shape_.height) / k


# ---------------------------------------------------------------- 図


def image_size(path):
    from PIL import Image

    with Image.open(path) as im:
        return im.size


def picture(slide, path, x, y, w, h, align="center", frame=False, what=None):
    """図を比率を保って枠に収めて置く。図が無ければ撮影前の枠（shot_placeholder）を置く。置いた (x, y, w, h) を返す"""
    path = Path(path) if path else None
    if path is None or not path.exists():
        shot_placeholder(slide, x, y, w, h, what or f"図：{path.name if path else '（図のパスが無い）'}")
        return x, y, w, h
    iw, ih = image_size(path)
    k = min(w / iw, h / ih)
    pw, ph = iw * k, ih * k
    px = x + (w - pw) / 2 if align == "center" else x
    pic = slide.shapes.add_picture(str(path), E(slide, px), E(slide, y), E(slide, pw), E(slide, ph))
    if frame:
        from pptx.dml.color import RGBColor

        pic.line.color.rgb = RGBColor.from_string(C("line"))
        pic.line.width = E(slide, 1.5)
    return px, y, pw, ph


def shot_placeholder(slide, x, y, w, h, what):
    """撮影前の図・スクショの枠（灰色の破線の枠に、何を写すかを書く）"""
    return rect(slide, x, y, w, h, fill="surface", line="sub", dash="dash", paras=[f"（TODO: {what}）"],
                size="body", color="sub", align="center")


def figure_page(slide, fig, head, points, area=None, fig_w=0.6, gap=40):
    """左に図、右に見えたことの枠"""
    x0, y0, w0, h0 = area or BASE.body
    fw = w0 * fig_w
    picture(slide, fig, x0, y0, fw, h0)
    callout(slide, x0 + fw + gap, y0, w0 - fw - gap, head, points, h=h0)


def full_figure(slide, fig, area=None):
    x0, y0, w0, h0 = area or BASE.body
    return picture(slide, fig, x0, y0, w0, h0)


# ---------------------------------------------------------------- 版上げの道具


def shape(slide, key):
    """図形を ID（数）か名前（文字）か、文言の先頭（"text:…"）で取る"""
    for sh in slide.shapes:
        if isinstance(key, int) and sh.shape_id == key:
            return sh
        if isinstance(key, str):
            if key.startswith("text:") and sh.has_text_frame and sh.text_frame.text.startswith(key[5:]):
                return sh
            if sh.name == key:
                return sh
    raise KeyError(key)


def move(sh, x=None, y=None, w=None, h=None):
    k = sh.part.package.presentation_part.presentation.slide_width / 1920
    if x is not None:
        sh.left = Emu(int(x * k))
    if y is not None:
        sh.top = Emu(int(y * k))
    if w is not None:
        sh.width = Emu(int(w * k))
    if h is not None:
        sh.height = Emu(int(h * k))


def delete(sh):
    sh._element.getparent().remove(sh._element)


def clone_shape(slide, sh, dx=0, dy=0):
    """同じページの図形を複製してずらす（画像・グラフを含まない図形）"""
    el = copy.deepcopy(sh._element)
    ids = [int(v) for v in slide.shapes._spTree.xpath(".//p:cNvPr/@id")]
    nid = max(ids) + 1
    for c in el.xpath(".//p:cNvPr"):
        c.set("id", str(nid))
        nid += 1
    for tag in ("a:stCxn", "a:endCxn"):  # 複製した線は元の図形につながったままにしない
        for c in list(el.iter(qn(tag))):
            c.getparent().remove(c)
    ext = slide.shapes._spTree.find(qn("p:extLst"))
    ext.addprevious(el) if ext is not None else slide.shapes._spTree.append(el)
    new = [s for s in slide.shapes if s._element is el][0]
    k = scale_of(slide)
    new.left, new.top = Emu(int(sh.left + dx * k)), Emu(int(sh.top + dy * k))
    return new


def replace_paras(sh, paras, keep_style_from=0):
    """図形の段落を差し替える。書式は既存の段落（keep_style_from 番目）の段落の設定と最初の文字の設定を写す。

    paras の要素は文字（記法つき可）か dict(text=, bold=, color=)。箇条書きの記号・字下げ・行間・色（テーマ色を含む）は
    元の段落のまま。記法や color で色を指定した文字だけ色を替える。リンクは元の文字から引き継がず、[文字](URL) の分だけ付ける
    """
    tb = sh._element.find(qn("p:txBody")) if not hasattr(sh, "_tc") else sh._tc.find(qn("a:txBody"))
    slide_part = sh.part
    ps = tb.findall(qn("a:p"))
    tmpl = ps[min(keep_style_from, len(ps) - 1)]
    ppr = tmpl.find(qn("a:pPr"))
    r0 = tmpl.find(qn("a:r"))
    rpr0 = r0.find(qn("a:rPr")) if r0 is not None else tmpl.find(qn("a:endParaRPr"))
    base_bold = rpr0 is not None and rpr0.get("b") == "1"
    for p in ps:
        tb.remove(p)
    for o in _as_dicts(paras):
        p = etree.SubElement(tb, qn("a:p"))
        if ppr is not None:
            p.append(copy.deepcopy(ppr))
        for t_, c, b, url in runs_of(o["text"], C(o.get("color")), o.get("bold", base_bold)):
            for i, part in enumerate(t_.split("\n")):
                if i:
                    p.append(etree.Element(qn("a:br")))
                if not part:
                    continue
                r = etree.SubElement(p, qn("a:r"))
                rpr = copy.deepcopy(rpr0) if rpr0 is not None else etree.Element(qn("a:rPr"))
                rpr.tag = qn("a:rPr")
                for h in rpr.findall(qn("a:hlinkClick")):
                    rpr.remove(h)
                if b != base_bold:  # 太字は変えるときだけ書く（レイアウトから受け継ぐ太字を消さない）
                    rpr.set("b", "1" if b else "0")
                if c:  # 色を指定した文字だけ、元の色（テーマ色を含む）を置き換える
                    for f in rpr.findall(qn("a:solidFill")):
                        rpr.remove(f)
                    sf = etree.Element(qn("a:solidFill"))
                    etree.SubElement(sf, qn("a:srgbClr"), val=c)
                    rpr.insert(_fill_index(rpr), sf)
                if url:
                    rid = slide_part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink", is_external=True)
                    etree.SubElement(rpr, qn("a:hlinkClick"), {qn("r:id"): rid})
                r.append(rpr)
                etree.SubElement(r, qn("a:t")).text = part
    return sh


def _fill_index(rpr):
    """solidFill は ln の後、latin・ea・cs・hlink の前に置く（スキーマの順）"""
    order = ["a:ln"]
    for i, ch in enumerate(rpr):
        if ch.tag not in [qn(t) for t in order]:
            return i
    return len(rpr)


def set_cell(gf, r, c, value):
    """既存の表のセルの文字を、書式を保って差し替える"""
    cell = gf.table.cell(r, c)
    replace_paras(cell, [p["text"] if isinstance(p, dict) else p for p in cell_paras(value)])


def rebuild_table(slide, gf, rows, **kw):
    """既存の表を作り直す。結合が無く行・列の数が同じで kw を渡さないときは、書式を保ってセルの文字だけを差し替える。
    それ以外（結合がある、数が異なる、merge_first・marks などを渡した）は、同じ位置・幅に土台の書式の表を作り直す
    （kw は table() と同じ）。表の図形を返す"""
    tbl = gf.table
    merged = any(tc.get(a) for tc in tbl._tbl.iter(qn("a:tc")) for a in ("gridSpan", "rowSpan", "hMerge", "vMerge"))
    if not kw and not merged and len(tbl.rows) == len(rows) and len(tbl.columns) == len(rows[0]):
        # 結合の無い表で、行・列の数が同じときだけ書式を保って差し替える（結合のある表は作り直して結合を決め直す）
        for r, line_ in enumerate(rows):
            for c, v in enumerate(line_):
                set_cell(gf, r, c, v)
        return gf
    k = scale_of(slide)
    x, y, w = gf.left / k, gf.top / k, gf.width / k
    delete(gf)
    return table(slide, rows, x=x, y=y, w=w, **kw)


def replace_picture(slide, pic, path, fit=True):
    """図を差し替える。fit=True で元の枠に比率を保って収める"""
    k = scale_of(slide)
    x, y, w, h = pic.left / k, pic.top / k, pic.width / k, pic.height / k
    prev = pic._element.getprevious()
    delete(pic)
    if fit:
        picture(slide, path, x, y, w, h)
    else:
        slide.shapes.add_picture(str(path), E(slide, x), E(slide, y), E(slide, w), E(slide, h))
    new = slide.shapes[-1]
    if prev is not None:
        prev.addnext(new._element)
    return new
