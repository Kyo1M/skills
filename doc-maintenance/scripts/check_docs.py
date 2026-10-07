#!/usr/bin/env python3
"""ドキュメントの点検：古くなっていそうな文書・リンクの切れ・一覧の食い違いを一覧にする。

正本は Kyo1M/skills の doc-maintenance/scripts/check_docs.py。各リポジトリには写しを置き、
点検の対象はリポジトリごとの設定（既定は scripts/check_docs.toml）に書く。
直すのは人か AI で、このスクリプトは一覧を出すだけ（ファイルは書き換えない）。

    python3 scripts/check_docs.py                 # 設定は scripts/check_docs.toml
    python3 scripts/check_docs.py --config <path>

Python 3.11 以上（設定の読み込みに tomllib を使う）。標準ライブラリだけで動く。
見つかったものがあれば終了コード 1、無ければ 0。

点検すること（設定に書いたものだけ）:

- stale: 文書の frontmatter の derived_from・related にある元のファイルが、文書より後に更新された
  （文書の日付は、文書の最後のコミットと frontmatter の reviewed の遅いほう）
- draft: status: draft のまま、date（と reviewed）から draft_days 日を過ぎた
- superseded: 置き換えられていない文書の frontmatter の related が、status: superseded の文書を指している
  （derived_from と本文の引用は、古い版を由来・根拠として挙げる正しい書き方なので見ない）
- broken: 本文の相対リンクの先が無い。link_targets の文書が対象。.gitignore の対象（手元で作る図など）を
  指すリンク、<slug> や {{...}} を含む仮のリンク、ignore_links に書いた例のリンクと、frontmatter のパス
  （別のリポジトリを指すことがある）は見ない
- dated: YAML などの日付の項目（values_asof・checked など）が days 日より古い
- inventory: 置き場にあるファイルが、一覧の文書（README など）に名前で載っていない
  （strip を書くと、ファイル名からその末尾を外した名前で探す。例：.prompt.md）
"""

from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import re
import subprocess
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 以前
    sys.exit("Python 3.11 以上で実行してください（設定の読み込みに tomllib を使います）。")

CLOSED_STATUSES = {"superseded", "done", "cancelled"}
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
FENCE = re.compile(r"^[ \t]*(```|~~~).*?^[ \t]*\1", re.S | re.M)
HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)
INLINE_CODE = re.compile(r"`[^`\n]*`")
DATE = re.compile(r"\d{4}-\d{2}-\d{2}")


# ---- frontmatter ------------------------------------------------------------


def split_list(value: str) -> list[str]:
    """[a, "b, c", d] を要素に分ける（引用符の中のカンマでは分けない）。"""
    inner = value.strip()[1:-1]
    items, current, quote = [], "", ""
    for ch in inner:
        if quote:
            if ch == quote:
                quote = ""
            else:
                current += ch
        elif ch in "\"'":
            quote = ch
        elif ch == ",":
            items.append(current.strip())
            current = ""
        else:
            current += ch
    if current.strip():
        items.append(current.strip())
    return [i for i in items if i]


def unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def strip_html_comment(text: str) -> str:
    """HTML の文書は、先頭の <!-- --> の中に frontmatter を書く。その中身を取り出す。"""
    stripped = text.lstrip()
    if stripped.startswith("<!--"):
        end = stripped.find("-->")
        if end > 0:
            return stripped[4:end].strip() + "\n"
    return text


def read_frontmatter(text: str) -> dict[str, object]:
    """先頭の --- で囲んだ frontmatter の、トップレベルの key: value と key: [..] と key:\\n  - .. を読む。"""
    text = strip_html_comment(text)
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    data: dict[str, object] = {}
    key = None
    for line in text[3:end].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        item = re.match(r"^\s+-\s+(.*)$", line)
        if item and key and isinstance(data.get(key), list):
            data[key].append(unquote(item.group(1)))  # type: ignore[union-attr]
            continue
        pair = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if not pair:
            continue
        key, value = pair.group(1), pair.group(2).strip()
        if value.startswith("[") and value.endswith("]"):
            data[key] = [unquote(v) for v in split_list(value)]
        elif value == "":
            data[key] = []
        else:
            data[key] = unquote(value)
    return data


def body_of(text: str) -> str:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end >= 0:
            return text[end + 4 :]
    return text


# ---- git と日付 -------------------------------------------------------------


class Repo:
    def __init__(self, root: Path):
        self.root = root
        self._dates: dict[Path, dt.datetime | None] = {}

    def last_commit(self, path: Path) -> dt.datetime | None:
        """最後にコミットした日時。コミットされていなければ None。"""
        if path not in self._dates:
            out = subprocess.run(
                ["git", "log", "-1", "--format=%cI", "--", str(path.relative_to(self.root))],
                cwd=self.root,
                capture_output=True,
                text=True,
            ).stdout.strip()
            self._dates[path] = dt.datetime.fromisoformat(out) if out else None
        return self._dates[path]

    def ignored(self, path: Path) -> bool:
        """.gitignore の対象か。"""
        return (
            subprocess.run(["git", "check-ignore", "-q", str(path)], cwd=self.root, capture_output=True).returncode == 0
        )

    def glob(self, patterns: list[str]) -> list[Path]:
        found: set[Path] = set()
        for pattern in patterns:
            found.update(p for p in self.root.glob(pattern) if p.is_file())
        return sorted(found)

    def rel(self, path: Path) -> str:
        return str(path.relative_to(self.root))


def parse_date(value: object) -> dt.date | None:
    if isinstance(value, str):
        m = DATE.search(value)
        if m:
            return dt.date.fromisoformat(m.group(0))
    return None


def end_of_day(day: dt.date, tz: dt.tzinfo | None) -> dt.datetime:
    return dt.datetime.combine(day, dt.time(23, 59, 59), tzinfo=tz)


# ---- 点検 -------------------------------------------------------------------


def resolve(repo: Repo, doc: Path, target: str) -> Path | None:
    """リンク・パスを repo の中のファイルにする。repo 相対と文書からの相対の両方を試す。"""
    target = target.split("#", 1)[0].split("?", 1)[0]
    if not target:
        return None
    for base in (doc.parent, repo.root):
        candidate = (base / target).resolve()
        if candidate.is_file() and repo.root in candidate.parents:
            return candidate
    return None


def body_links(text: str) -> list[str]:
    """本文の Markdown の相対リンク。コードブロック・インラインのコード・HTML コメントの中（例として書いたリンク）と、HTML の href は見ない。"""
    body = INLINE_CODE.sub("", FENCE.sub("", HTML_COMMENT.sub("", body_of(text))))
    links = []
    for m in LINK.finditer(body):
        target = m.group(1)
        if re.match(r"^[a-z][a-z0-9+.-]*:", target) or target.startswith("#"):
            continue
        links.append(target)
    return links


def check(repo: Repo, config: dict, today: dt.date) -> dict[str, list[str]]:
    found: dict[str, list[str]] = {k: [] for k in ("stale", "draft", "superseded", "broken", "dated", "inventory")}
    exclude = config.get("exclude", [])

    def collect(key: str) -> list[Path]:
        return [p for p in repo.glob(config.get(key, [])) if not any(fnmatch.fnmatch(repo.rel(p), e) for e in exclude)]

    docs = collect("targets")
    texts = {p: p.read_text(encoding="utf-8") for p in docs}
    status_cache: dict[Path, str] = {}

    def status_of(path: Path) -> str:
        if path not in status_cache:
            fm = read_frontmatter(path.read_text(encoding="utf-8")) if path.suffix in (".md", ".html") else {}
            status_cache[path] = str(fm.get("status", ""))
        return status_cache[path]

    draft_days = int(config.get("draft_days", 30))
    for doc, text in texts.items():
        fm = read_frontmatter(text)
        status = str(fm.get("status", ""))
        if status in CLOSED_STATUSES:
            continue
        reviewed = parse_date(fm.get("reviewed"))
        committed = repo.last_commit(doc)

        # stale
        sources = []
        for key in ("derived_from", "related"):
            value = fm.get(key) or []
            sources += value if isinstance(value, list) else [value]
        if committed is not None:
            doc_time = committed
            if reviewed and end_of_day(reviewed, committed.tzinfo) > doc_time:
                doc_time = end_of_day(reviewed, committed.tzinfo)
            newer = []
            for source in sources:
                path = resolve(repo, doc, str(source))
                when = repo.last_commit(path) if path else None
                if when and when > doc_time:
                    newer.append(f"{repo.rel(path)}（{when.date()}）")
            if newer:
                found["stale"].append(f"{repo.rel(doc)}（{doc_time.date()}）: 元のファイルが後で更新された → {', '.join(newer)}")

        # draft
        if status == "draft":
            since = max(d for d in (parse_date(fm.get("date")), reviewed) if d) if (fm.get("date") or reviewed) else None
            if since and (today - since).days > draft_days:
                found["draft"].append(f"{repo.rel(doc)}: draft のまま {(today - since).days} 日（{since}）")

        # superseded
        related = fm.get("related") or []
        for ref in sorted(set(related if isinstance(related, list) else [related])):
            path = resolve(repo, doc, str(ref))
            if path and status_of(path) == "superseded":
                found["superseded"].append(f"{repo.rel(doc)}: related が置き換え済みの {repo.rel(path)} を指している")

    # broken（<slug> や {{...}} を含む仮のリンクと、ignore_links に書いた例のリンクは見ない）
    ignore_links = config.get("ignore_links", [])
    for doc in collect("link_targets"):
        for link in sorted(set(body_links(doc.read_text(encoding="utf-8")))):
            if "<" in link or "{{" in link or any(fnmatch.fnmatch(link, p) for p in ignore_links):
                continue
            if resolve(repo, doc, link) is None and not repo.ignored(doc.parent / link.split("#", 1)[0]):
                found["broken"].append(f"{repo.rel(doc)}: リンク先が無い → {link}")

    # dated
    for rule in config.get("dated", []):
        days = int(rule.get("days", 60))
        keys = "|".join(re.escape(k) for k in rule.get("keys", []))
        pattern = re.compile(rf"^\s*-?\s*({keys}):\s*[\"']?(\d{{4}}-\d{{2}}-\d{{2}})", re.M)
        for path in repo.glob(rule.get("paths", [])):
            for m in pattern.finditer(path.read_text(encoding="utf-8")):
                day = dt.date.fromisoformat(m.group(2))
                if (today - day).days > days:
                    found["dated"].append(f"{repo.rel(path)}: {m.group(1)} が {day}（{(today - day).days} 日前）")

    # inventory
    for rule in config.get("inventory", []):
        listed = repo.root / rule["listed_in"]
        listed_text = listed.read_text(encoding="utf-8") if listed.is_file() else ""
        for path in repo.glob([rule["files"]]):
            if path.name in rule.get("exclude", []):
                continue
            name = path.name.removesuffix(rule["strip"]) if rule.get("strip") else path.name
            if name not in listed_text:
                found["inventory"].append(f"{repo.rel(path)}: {rule['listed_in']} に載っていない")
    return found


LABELS = {
    "stale": "元のファイルが後で更新された文書（内容が古くなっていないか確かめる）",
    "draft": "draft のまま日数が過ぎた文書",
    "superseded": "置き換え済みの文書への参照",
    "broken": "リンクの切れ",
    "dated": "日付の古い確認の記録（データを取り込み直したら確かめ直す）",
    "inventory": "一覧に載っていないファイル",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", default="scripts/check_docs.toml")
    parser.add_argument("--today", help="今日の日付（YYYY-MM-DD。テスト用）")
    args = parser.parse_args()

    root = Path(
        subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip() or "."
    ).resolve()
    config_path = (root / args.config) if not Path(args.config).is_absolute() else Path(args.config)
    if not config_path.is_file():
        print(f"設定 {config_path} がありません。", file=sys.stderr)
        return 2
    config = tomllib.loads(config_path.read_text(encoding="utf-8"))
    today = dt.date.fromisoformat(args.today) if args.today else dt.date.today()

    found = check(Repo(root), config, today)
    total = sum(len(v) for v in found.values())
    for key, items in found.items():
        if items:
            print(f"## {LABELS[key]}（{len(items)}）")
            for item in items:
                print(f"- {item}")
            print()
    print(f"点検した日: {today}。見つかったもの: {total} 件" if total else f"点検した日: {today}。見つかったものはありません")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
