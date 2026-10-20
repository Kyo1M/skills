#!/usr/bin/env bash
# table-definition・metric-definition の既定の型（references/*-schema.md）が、
# 正本の project-context-template の docs/guide/data-definition-guide.md と一致しているかを確かめる。
# 使い方: scripts/check-schema-copies.sh [テンプレートのパス]（既定 ~/Developer/project-context-template）
# 比べる相手は、そのパスで今チェックアウトしているブランチのガイド（main とは限らない）。
set -euo pipefail

skills_root="$(cd "$(dirname "$0")/.." && pwd)"
template="${1:-$HOME/Developer/project-context-template}"
guide="$template/docs/guide/data-definition-guide.md"

if [[ ! -f "$guide" ]]; then
  echo "ガイドが見つかりません: $guide" >&2
  exit 2
fi

status=0

# $1: 写しのファイル  $2: 抜き出し始めの見出し  $3: 抜き出し終わりの見出し（含まない）
check() {
  local copy="$skills_root/$1" from="$2" to="$3"
  if diff -u \
      <(awk -v from="$from" -v to="$to" 'index($0, to) == 1 {f = 0} index($0, from) == 1 {f = 1} f' "$guide") \
      <(awk '/^<!-- BEGIN:/ {f = 1; next} /^<!-- END -->/ {f = 0} f' "$copy") >/dev/null; then
    echo "OK   $1"
  else
    echo "DIFF $1（ガイドの「${from}」から「${to}」の手前までと食い違っています）"
    status=1
  fi
}

check table-definition/references/table-schema.md "### 2-1." "### 2-5."
check metric-definition/references/metric-schema.md "### 3-1." "### 3-6."

exit "$status"
