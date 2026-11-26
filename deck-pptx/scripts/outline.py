# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""構成 md を読む。

    uv run outline.py --check <構成 md>    # 読めなかった行・知らない欄・ID の重複を出し、1 つでもあれば失敗で止める
    uv run outline.py --dump <構成 md>     # ページごとに読んだ中身を出す

build.py からは `pages = outline.read(path)` で読み、`page = outline.by_id(pages, "S3")` でページを取る。

読む文法:
- ページの見出しは `###` か `####` ＋ ID ＋題。ID は英字 1 字＋番号＋枝番（S1・A2・S7b・R1）
- 欄は `- **タイトル**: …` の形（全角コロン、欄名の後ろの括弧書きも読む）。題の欄が無ければ見出しの題を使う
- 太字でない `- 副題：…`・`- 流用元：…` などは、PLAIN_SHOWN・PLAIN_HIDDEN の欄名のときだけ欄として読む（載せる欄は値だけを照合する）
- リード文は 1 行の値・子の箇条書き・`**リード文**` の後の段落のどれでもよい
- ボディは `- **ボディ**:` の子の箇条書きと、欄でない箇条書き。階層を保って読む
- md の表、図のパス（`…png`・`![…](…)`）、図版指示（`- **図版指示**:` か `**図版**：`）の型の名前
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
PAGE = re.compile(r"^#{3,4}\s+(?P<id>[A-Za-z]\d+[a-z]?)\b\s*(?P<title>.*)$")
PAREN = r"(?:[（(](?:[^（）()]|[（(][^（）()]*[）)])*[）)])?"  # 欄名の後ろの括弧書き（1 段の入れ子まで）
FIELD = re.compile(r"^(?P<ind> *)- \*\*(?P<name>[^*]+?)\*\*" + PAREN + r"\s*[:：]\s?(?P<val>.*)$")
FIELD_BARE = re.compile(r"^(?P<ind> *)- \*\*(?P<name>[^*]+?)\*\*" + PAREN + r"\s*$")
# 太字でない欄（`- 副題：…`）。PLAIN の欄名のときだけ欄として読み、ほかは本文の箇条書きにする
FIELD_PLAIN = re.compile(r"^- (?P<name>[^*：:\s][^：:]{0,7}?)[：:]\s?(?P<val>.*)$")
ITEM = re.compile(r"^(?P<ind> *)(?:[-*+]|\d+\.)\s+(?P<text>.*)$")
BOLD_PARA = re.compile(r"^\*\*(?P<name>[^*]+?)\*\*" + PAREN + r"\s*(?:[:：]\s*(?P<val>.*))?$")
FIGURE = re.compile(r"`([^`]+\.(?:png|jpe?g|gif))`|!\[[^\]]*\]\(([^)]+)\)")

# 載せる欄と載せない欄
SHOWN = {"タイトル", "kicker", "リード文", "ボディ"}
HIDDEN = {"役割", "図版指示", "図版", "スクショ", "スクショ（実物）", "補足", "流用元", "実物", "型", "メモ", "制作メモ"}
KNOWN = SHOWN | HIDDEN | {"サブタイトル", "作成日", "ご提出先", "日付", "宛先"}
# 太字でなくても欄として読む名前。載せる欄（値だけをスライドに載せる）と載せない欄
PLAIN_SHOWN = {"副題", "サブタイトル", "日付", "作成日", "章番号", "章名", "章名の下"}
PLAIN_HIDDEN = {"流用元", "役割", "型", "補足", "メモ", "制作メモ", "スクショ", "スクショ（実物）"}


@dataclass
class Node:
    text: str
    line: int
    children: list["Node"] = field(default_factory=list)

    def walk(self):
        yield self
        for c in self.children:
            yield from c.walk()


@dataclass
class Page:
    sid: str
    heading: str
    line: int
    fields: dict = field(default_factory=dict)
    lead: list = field(default_factory=list)
    body: list = field(default_factory=list)          # Node の並び
    tables: list = field(default_factory=list)        # 表ごとの行の並び（1 行目は見出し）
    figures: list = field(default_factory=list)
    extras: dict = field(default_factory=dict)        # 載せない欄の子の箇条書き

    @property
    def title(self):
        t = self.fields.get("タイトル") or self.heading
        return re.sub(r"^（再掲）\s*", "", t).strip()

    @property
    def role(self):
        return self.fields.get("役割", "")

    @property
    def pattern(self):
        return self.fields.get("図版指示") or self.fields.get("図版") or ""

    @property
    def is_reuse(self):
        return "再掲" in self.role or self.heading.startswith("（再掲）")

    def items(self, depth=None):
        """ボディの箇条書きを (階層, 文字) の並びで返す"""
        out = []

        def rec(nodes, d):
            for n in nodes:
                out.append((d, n.text))
                if depth is None or d + 1 < depth:
                    rec(n.children, d + 1)

        rec(self.body, 0)
        return out

    def labels(self):
        """1 回あれば足りる文言（子を持つ見出しと、表の左端の列）。マトリクスの列見出しや結合したセルのように、
        構成 md では繰り返し書いてもスライドでは 1 回だけ出る"""
        out = set()
        for n in self.body:
            for x in n.walk():
                if x.children:
                    m = re.match(r"^\*\*(.+?)\*\*[：:]?(.*)$", x.text)
                    out.add(m.group(1) if m else x.text)
        for tb in self.tables:
            out |= {r[0] for r in tb[1:] if r}
        return out

    def shown(self):
        """スライドに載る文言の並び（記法つき）"""
        out = [self.title]
        k = self.fields.get("kicker", "")
        if k and k != "なし":
            out.append(k)
        out += [self.fields[n] for n in sorted(PLAIN_SHOWN) if self.fields.get(n) and n != "タイトル"]
        out += self.lead
        for n in self.body:
            for x in n.walk():
                note_ = re.match(r"^(?:図の下の注|表の下の注|注)[：:](.*)$", x.text)
                m = re.match(r"^\*\*(.+?)\*\*[：:](.*)$", x.text)
                if note_:
                    out.append(note_.group(1).strip())
                elif m:
                    out.append(m.group(1))
                    if m.group(2).strip():
                        out.append(m.group(2).strip())
                else:
                    out.append(x.text)
        for t in self.tables:
            for r in t:
                out += [c for c in r if c]
        return [s for s in out if s and s.strip()]


def plain(s: str) -> str:
    s = re.sub(r"\{[強悪良灰太]:(.+?)\}", r"\1", s)
    s = re.sub(r"\{[bgrBGR]\|(.+?)\}", r"\1", s)
    s = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r"\1", s)
    s = re.sub(r"`([^`]*)`", r"\1", s)
    return s.replace("**", "")


def norm(s: str) -> str:
    """照合用: 記法・空白・行頭の記号を外す（全角と半角・数字・単位はそのまま比べる）"""
    s = re.sub(r"^[・\-－•]\s*", "", plain(s).strip())
    return re.sub(r"\s+", "", s)


def _cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def read(path, warnings=None):
    """構成 md を読み、Page の並びを返す。warnings に list を渡すと、読めなかった行を (行番号, 内容, 理由) で足す"""
    warn = warnings if warnings is not None else []
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    pages: list[Page] = []
    cur: Page | None = None
    mode = None            # None・"lead"・"body"・("hidden", 名前)・"lead_para"
    stack: list[tuple[int, Node]] = []
    table = None
    in_code = False

    def close_table():
        nonlocal table
        if cur is not None and table:
            cur.tables.append(table)
        table = None

    def add_item(ind, text, ln):
        node = Node(text.strip(), ln)
        while stack and stack[-1][0] >= ind:
            stack.pop()
        if stack:
            stack[-1][1].children.append(node)
        else:
            cur.body.append(node)
        stack.append((ind, node))
        for m in FIGURE.finditer(text):
            cur.figures.append(m.group(1) or m.group(2))

    for i, raw in enumerate(lines, 1):
        line = raw.rstrip()
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        h = HEADING.match(line)
        if h:
            close_table()
            m = PAGE.match(line)
            if m:
                cur = Page(m.group("id"), m.group("title").strip(), i)
                pages.append(cur)
            else:
                cur = None
            mode, stack = None, []
            continue
        if cur is None:
            continue
        if line.lstrip().startswith("|"):
            cells = _cells(line)
            if all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
                continue
            if isinstance(mode, tuple):  # 載せない欄（補足など）の中の表は載せる文言に入れない
                cur.extras.setdefault(mode[1], []).append(" | ".join(cells))
                continue
            table = (table or []) + [cells]
            continue
        close_table()
        if not line.strip():
            if mode == "lead_para" and cur.lead:
                mode = "lead_para_gap"
            continue
        if line.strip().startswith(">") or line.strip().startswith("<!--"):
            continue
        f = FIELD.match(line) or FIELD_BARE.match(line)
        if f and len(f.group("ind")) == 0 and _field_name(f.group("name")) not in KNOWN and ("タイトル" in cur.fields or "役割" in cur.fields):
            # 欄で書く構成 md（タイトル・役割の欄がある）で、知らない欄名は書き誤りとして止める
            warn.append((i, line.strip()[:60], f"知らない欄「{_field_name(f.group('name'))}」"))
            continue
        if f and len(f.group("ind")) == 0 and _field_name(f.group("name")) in KNOWN:
            name = _field_name(f.group("name"))
            val = (f.groupdict().get("val") or "").strip()
            stack = []
            if name == "リード文":
                mode = "lead"
                if val:
                    cur.lead.append(val)
            elif name == "ボディ":
                mode = "body"
                if val:
                    add_item(-1, val, i)
                    stack = []
            elif name in SHOWN:
                cur.fields[name] = val
                mode = None
            else:
                cur.fields[name] = val
                mode = ("hidden", name)
                for m in FIGURE.finditer(val):
                    cur.figures.append(m.group(1) or m.group(2))
            continue
        fp = FIELD_PLAIN.match(line)
        if fp and mode not in ("body",) and _field_name(fp.group("name")) in PLAIN_SHOWN | PLAIN_HIDDEN:
            name = _field_name(fp.group("name"))
            cur.fields[name] = fp.group("val").strip()
            mode, stack = (("hidden", name) if name in PLAIN_HIDDEN else None), []
            for m in FIGURE.finditer(fp.group("val")):
                cur.figures.append(m.group(1) or m.group(2))
            continue
        b = BOLD_PARA.match(line.strip())
        if b and not line.startswith(" "):
            name = _field_name(b.group("name"))
            if name == "リード文":
                mode = "lead_para"
                if b.group("val"):
                    cur.lead.append(b.group("val").strip())
                continue
            if name in ("図版", "図版指示"):
                cur.fields["図版指示"] = (b.group("val") or "").strip()
                mode = None
                continue
            if name == "表":
                mode = None
                continue
            if name in KNOWN:
                cur.fields[name] = (b.group("val") or "").strip()
                mode = ("hidden", name) if name in HIDDEN else None
                continue
            # 知らない太字の段落は本文の小見出し。続く箇条書きをその子にする
            stack = []
            add_item(-2, line.strip(), i)
            mode = "body_free"
            continue
        it = ITEM.match(line)
        if it:
            ind = len(it.group("ind"))
            if mode == "lead" and ind >= 2:
                cur.lead.append(it.group("text").strip())
                continue
            if isinstance(mode, tuple) and ind >= 2:
                cur.extras.setdefault(mode[1], []).append(it.group("text").strip())
                for m in FIGURE.finditer(it.group("text")):
                    cur.figures.append(m.group(1) or m.group(2))
                continue
            if mode == "body":
                add_item(ind - 2 if ind >= 2 else ind, it.group("text"), i)
                continue
            # 欄の外の箇条書きはボディ（`**リード文**` の段落の書き方）
            mode = "body_free"
            add_item(ind, it.group("text"), i)
            continue
        if mode in ("lead_para", "lead_para_gap"):
            cur.lead.append(line.strip())
            mode = "lead_para"
            continue
        if mode == "lead" and line.startswith("  "):
            cur.lead.append(line.strip())
            continue
        warn.append((i, line.strip()[:60], "どの欄にも入らない行"))
    close_table()
    seen = {}
    for p in pages:
        if p.sid in seen:
            warn.append((p.line, p.sid, f"ID が {seen[p.sid]} 行目と重複している"))
        seen[p.sid] = p.line
        if not p.title:
            warn.append((p.line, p.sid, "題が無い"))
    return pages


def _field_name(n):
    n = n.strip()
    n = re.sub(r"[（(].*[）)]$", "", n).strip()
    return n


def by_id(pages, sid):
    for p in pages:
        if p.sid == sid:
            return p
    raise KeyError(sid)


def main(argv):
    if len(argv) < 2 or argv[0] not in ("--check", "--dump"):
        sys.exit(__doc__)
    warns = []
    pages = read(argv[1], warns)
    if argv[0] == "--dump":
        for p in pages:
            print(f"== {p.sid} {p.title}  （役割: {p.role or '-'}、型: {p.pattern or '-'}）")
            for t in p.lead:
                print(f"  リード: {t}")
            for d, t in p.items():
                print(f"  {'  ' * d}- {t}")
            for t in p.tables:
                print(f"  表: {len(t)} 行 × {len(t[0])} 列（見出し: {' / '.join(t[0])}）")
            for f in p.figures:
                print(f"  図: {f}")
    for ln, s, why in warns:
        print(f"WARN {argv[1]}:{ln}: {why}: {s}")
    print(f"{len(pages)} ページ、警告 {len(warns)} 件")
    return 1 if (warns and argv[0] == "--check") else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
