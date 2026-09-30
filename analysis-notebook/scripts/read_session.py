#!/usr/bin/env python3
"""marimo の session の出力（__marimo__/session/<file>.py.json）を、セルごとの文字で出す。

使い方:
    python3 read_session.py <notebook のパス か session の JSON のパス> [--max-chars N] [--max-rows N]

- 各セルの出力からタグを除いた文字を出す。表は先頭の行（既定 20 行）と全体の行数、
  Plotly の図はタイトル・軸・系列の数を出す
- 失敗したセル（type: error）と stderr を ERROR として出し、1 つでもあれば終了コード 1
- 標準ライブラリだけで動く
"""

import argparse
import html
import json
import re
import sys
from pathlib import Path


def session_path(target: Path) -> Path:
    if target.suffix == ".json":
        return target
    return target.parent / "__marimo__" / "session" / f"{target.name}.json"


def to_text(value: str) -> str:
    value = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", value, flags=re.S)
    value = re.sub(r"<[^>]+>", " ", value)
    value = html.unescape(value)
    return re.sub(r"\s+", " ", value).strip()


def attribute(value: str, name: str):
    found = re.search(rf"{name}='([^']*)'", value)
    return html.unescape(found.group(1)) if found else None


def plotly_summary(value: str) -> str:
    raw = attribute(value, "data-figure")
    try:
        figure = json.loads(raw)
        title = (figure.get("layout", {}).get("title") or {}).get("text", "")
        axes = [
            (figure["layout"].get(axis, {}).get("title") or {}).get("text", "")
            for axis in ("xaxis", "yaxis")
        ]
        return f"[plotly の図] {title}（横軸: {axes[0]}、縦軸: {axes[1]}、系列 {len(figure.get('data', []))}）"
    except (TypeError, ValueError, KeyError):
        return "[plotly の図]"


def table_summary(value: str, max_rows: int) -> str:
    raw = attribute(value, "data-data")
    total = attribute(value, "data-total-rows")
    try:
        rows = json.loads(raw)
        if isinstance(rows, str):
            rows = json.loads(rows)
    except (TypeError, ValueError):
        return f"[表] {total} 行（中身を読めませんでした）"
    if not rows:
        return f"[表] {total} 行"
    columns = list(rows[0].keys())
    body = [" | ".join(columns)]
    body += [" | ".join(str(row.get(c)) for c in columns) for row in rows[:max_rows]]
    more = f"（全 {total} 行のうち先頭 {min(len(rows), max_rows)} 行）"
    return "[表] " + more + "\n" + "\n".join(body)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("target")
    parser.add_argument("--max-chars", type=int, default=600)
    parser.add_argument("--max-rows", type=int, default=20)
    args = parser.parse_args()

    path = session_path(Path(args.target))
    if not path.exists():
        print(f"session の出力がありません: {path}", file=sys.stderr)
        return 2

    data = json.loads(path.read_text())
    errors = 0
    for index, cell in enumerate(data.get("cells", [])):
        lines = []
        for output in cell.get("outputs", []):
            if output.get("type") == "error":
                errors += 1
                lines.append(f"ERROR {output.get('ename')}: {output.get('evalue')}")
                continue
            for mime, value in (output.get("data") or {}).items():
                value = str(value)
                if "<marimo-plotly" in value:
                    lines.append(plotly_summary(value))
                elif "<marimo-table" in value:
                    lines.append(table_summary(value, args.max_rows))
                else:
                    text = to_text(value)
                    if text:
                        lines.append(text[: args.max_chars])
        for stream in cell.get("console", []) or []:
            if stream.get("name") == "stderr":
                text = to_text(str(stream.get("text", "")))
                if text:
                    lines.append(f"STDERR {text[: args.max_chars]}")
        print(f"--- セル {index} ({cell.get('id')})")
        print("\n".join(lines) if lines else "(出力なし)")

    if errors:
        print(f"\n失敗したセル: {errors}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
