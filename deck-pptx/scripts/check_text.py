# /// script
# requires-python = ">=3.10"
# dependencies = ["python-pptx>=1.0"]
# ///
"""構成 md と pptx の文言を照合する。

新しく作ったとき（構成 md が正本）:
    uv run check_text.py <構成 md> <pptx> [--map S1=1,S2=2,…] [--ignore 文言,…]

版を上げたとき（pptx が正本）:
    uv run check_text.py --against <元の pptx> --changes <差し替えの一覧.json> <新しい pptx>
    差し替えの一覧は「旧の文言 → 新しい文言」で書く（形は check_revise() の説明）。元のページに差し替えを当てたものと
    新しいページの文言が一致することを確かめる（一覧に無い変更・差し替えの漏れの両方を見つける）

新しく作ったときに出すもの:
- 欠けた文言（構成 md の載せる欄の文言が、そのページに無い）。表の列・カードの見出しなどに分けて置いた文言は、
  区切り（：／→（）、・）で分けた 2 字以上の断片がすべてそのページにあれば通し、件数を出す
- 別のページに入った文言
- 構成 md に無い文言（複製元の文言の残りなど。ページ番号のフィールドと、--ignore に書いた文言と全体が一致するものは除く）
- 構成 md に対応しないページ（サンプル・複製元のページの残りなど）
- 「（TODO: …）」の残りの数（失敗にはしない）
再掲のページ（役割が再掲・空ページ）は照合から外し、写したページの最初の文言を出す。画像の中の文字は対象外。
「（TODO: …）」で始まる段落（図が無いときの枠など）は数えるだけにする。
ページの対応は、既定では構成 md のページの順と pptx のページの順を 1 対 1 にする（--map で変えられる）。
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import outline  # noqa: E402
from slide_text import slide_texts  # noqa: E402

from pptx import Presentation  # noqa: E402


def parse_map(spec, pages, n_slides):
    if spec:
        m = {}
        for kv in spec.split(","):
            k, v = kv.split("=")
            m[k.strip()] = int(v)
        return m
    return {p.sid: i + 1 for i, p in enumerate(pages) if i < n_slides}


SPLIT = re.compile(r"[：:／→⇒（）()「」、，,・\s]+")   # 半角の / は日付（11/25）に使うので区切りにしない


def fragments(t):
    """区切り（：／→（）、・など）で分けた、2 字以上の断片"""
    out = (re.sub(r"^(?:[①-⑳]|\d{1,2}[.．])", "", outline.norm(x)) for x in SPLIT.split(outline.plain(t)))
    return [f for f in out if len(f) >= 2]   # 番号（①・1.）は部品が付け直すことがあるので外す


def check_new(md, pptx, mapping=None, ignore=()):
    pages = outline.read(md)
    prs = Presentation(pptx)
    m = parse_map(mapping, pages, len(prs.slides))
    texts = {i: slide_texts(prs.slides[i - 1]) for i in range(1, len(prs.slides) + 1)}
    joined = {i: outline.norm("".join(ts)) for i, ts in texts.items()}
    problems, infos, todos, split = [], [], 0, []
    ign = {outline.norm(x) for x in ignore if x}
    for p in pages:
        if p.sid not in m:
            problems.append(f"{p.sid}: 対応する pptx のページが無い")
            continue
        page_no = m[p.sid]
        if p.is_reuse:
            ts = texts.get(page_no) or ["（文言なし）"]
            infos.append(f"{p.sid}（{page_no} 枚目）: 再掲のページは照合から外した（写したページの最初の文言: {ts[0][:30]}）")
            continue
        md_texts = p.shown()
        md_joined = outline.norm("".join(md_texts))
        # 長い文言から順に、見つかった所を消し込む（同じ文言が 2 回あるのに 1 回しか入っていないのも見つける）
        work = joined[page_no]
        labels = {outline.norm(x) for x in p.labels()}
        seen_labels = set()
        for t in sorted(md_texts, key=lambda x: -len(outline.norm(x))):
            todos += len(re.findall(r"（TODO[:：）]", t))
            n = outline.norm(t)
            if not n:
                continue
            if n in labels:  # 見出し・左端の列は 1 回あれば足りる
                if n in seen_labels:
                    continue
                seen_labels.add(n)
            if n in work:
                work = work.replace(n, "\x00", 1)
                continue
            if n in joined[page_no]:
                problems.append(f"{p.sid}（{page_no} 枚目）: 構成 md より入っている回数が少ない: {t[:40]}")
                continue
            frags = fragments(t)
            if frags and frags != [n]:   # 表の列・カードの見出しなどに分けて置いた文言は、区切りで分けた断片がすべてあれば通す
                w2 = work
                for fr in sorted(frags, key=len, reverse=True):
                    if fr not in w2:
                        break
                    w2 = w2.replace(fr, "\x00", 1)
                else:
                    work = w2
                    split.append(f"{p.sid}（{page_no} 枚目）: {t[:40]}")
                    continue
            else_where = [i for i, j in joined.items() if i != page_no and n in j]
            if else_where:
                problems.append(f"{p.sid}（{page_no} 枚目）: 別のページ（{else_where[0]} 枚目）に入っている: {t[:40]}")
            else:
                problems.append(f"{p.sid}（{page_no} 枚目）: 欠けている: {t[:40]}")
        for t in texts[page_no]:
            n = outline.norm(t)
            if not n or n in ign:   # --ignore は文言の全体と一致したものだけを外す
                continue
            if re.match(r"^（TODO[:：）]", n):  # 図が無いときの枠など。数えるだけにする
                todos += 1
                continue
            # 部品が付けた番号（「1　」「01  」「1. 」）は外して比べる。番号だけの文言（目次の「01」）は部品の番号として通す。
            # 3 桁以上の数字・番号のあとに数字が続く文言（「2026」「12月」）は外さない
            if re.fullmatch(r"\d{1,2}[.．、]?", n):
                continue
            if n not in md_joined and re.sub(r"^\d{1,2}[.．、]?(?=\D)", "", n) not in md_joined:
                problems.append(f"{p.sid}（{page_no} 枚目）: 構成 md に無い文言: {t[:40]}")
    mapped = set(m.values())
    for i in range(1, len(prs.slides) + 1):
        if i not in mapped:
            problems.append(f"{i} 枚目: 構成 md に対応するページが無い（複製元・サンプルの残りなど）")
    if split:
        infos.append(f"区切りで分けて置いた文言（断片がすべてあるので通した）: {len(split)} 件。例: {split[0]}")
    return problems, todos, infos


def check_revise(old, changes, new):
    """差し替えの一覧の形:
    {"pages": {"<新しいページ>": {"from": <元のページ>}
                              | {"from": n, "replace": [["旧の文言", "新しい文言"], …]}
                              | {"new": true, "texts": ["入っているべき文言", …]}}}
    from のページは、元のページの文言に replace を当てたものと、新しいページの文言が一致すること。
    new のページは texts が入っていること。一覧に無いページ・出力に無いページは止める
    """
    po, pn = Presentation(old), Presentation(new)
    spec = json.loads(Path(changes).read_text(encoding="utf-8"))["pages"]
    spec = {int(k): v for k, v in spec.items()}
    problems = []

    def joined(slide):
        return "".join(outline.norm(t) for t in slide_texts(slide))

    extra = sorted(k for k in spec if k > len(pn.slides))
    if extra:
        problems.append(f"一覧にあるページが出力に無い: {extra}（全 {len(pn.slides)} ページ）")
    for i in range(1, len(pn.slides) + 1):
        if i not in spec:
            problems.append(f"{i} 枚目: 差し替えの一覧に無い")
            continue
        o = spec[i]
        got = joined(pn.slides[i - 1])
        if o.get("new"):
            for t in o.get("texts", []):
                if outline.norm(t) not in got:
                    problems.append(f"{i} 枚目: 入っているべき文言が無い: {t[:40]}")
            continue
        want = joined(po.slides[o["from"] - 1])
        for old_t, new_t in o.get("replace", []):
            ot, nt = outline.norm(old_t), outline.norm(new_t)
            if ot not in want:
                problems.append(f"{i} 枚目: 差し替える前の文言が元の {o['from']} 枚目に無い: {old_t[:40]}")
            want = want.replace(ot, nt, 1)
        if got != want:
            problems.append(f"{i} 枚目: 元の {o['from']} 枚目に差し替えを当てたものと文言が一致しない（一覧に無い変更か、差し替えの漏れ）")
    return problems


def main(argv):
    if "--against" in argv:
        old = argv[argv.index("--against") + 1]
        changes = argv[argv.index("--changes") + 1]
        new = [a for a in argv if a.endswith(".pptx") and a != old][-1]
        ps = check_revise(old, changes, new)
        for p in ps:
            print("NG", p)
        print("OK" if not ps else f"{len(ps)} 件")
        return 1 if ps else 0
    args = [a for a in argv if not a.startswith("--")]
    if len(args) < 2:
        sys.exit(__doc__)
    mapping = argv[argv.index("--map") + 1] if "--map" in argv else None
    ignore = argv[argv.index("--ignore") + 1].split(",") if "--ignore" in argv else ()
    args = [a for a in args if a not in (mapping, ",".join(ignore))]
    ps, todos, infos = check_new(args[0], args[1], mapping, ignore)
    for x in infos:
        print("--", x)
    for p in ps:
        print("NG", p)
    if todos:
        print(f"TODO が {todos} 件残っている")
    print("OK" if not ps else f"{len(ps)} 件")
    return 1 if ps else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
