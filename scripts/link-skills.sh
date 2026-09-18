#!/usr/bin/env bash
# Skills 直下のスキルを ~/.claude/skills と ~/.agents/skills に symlink で配る。
#   link-skills.sh          symlink を張る（既存の実体は上書きせず skip として報告）
#   link-skills.sh --check  壊れた symlink / 未配置 / 同名の別実体 / README 管理表との食い違いを報告し、あれば exit 1
# 置き場は環境変数で差し替え可: SKILLS_DIR CLAUDE_SKILLS_DIR AGENTS_SKILLS_DIR CODEX_SKILLS_DIR REPO_DIR
set -euo pipefail

SKILLS_DIR="${SKILLS_DIR:-$HOME/Developer/Skills}"
CLAUDE_SKILLS_DIR="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
AGENTS_SKILLS_DIR="${AGENTS_SKILLS_DIR:-$HOME/.agents/skills}"
CODEX_SKILLS_DIR="${CODEX_SKILLS_DIR:-$HOME/.codex/skills}"
REPO_DIR="${REPO_DIR:-$PWD}"
NON_SKILL_DIRS="archive docs scripts node_modules"

realpath_py() { python3 -c 'import os,sys;print(os.path.realpath(sys.argv[1]))' "$1"; }

list_skills() {
  local d name
  for d in "$SKILLS_DIR"/*/; do
    [ -d "$d" ] || continue
    name="$(basename "$d")"
    case " $NON_SKILL_DIRS " in *" $name "*) continue ;; esac
    [ -f "$d/SKILL.md" ] && echo "$name"
  done
}

do_link() {
  local target name src dst status=0
  for target in "$CLAUDE_SKILLS_DIR" "$AGENTS_SKILLS_DIR"; do
    mkdir -p "$target"
    for name in $(list_skills); do
      src="$SKILLS_DIR/$name"; dst="$target/$name"
      if [ -L "$dst" ]; then
        if [ "$(realpath_py "$dst")" = "$(realpath_py "$src")" ]; then
          echo "ok    $dst"
        else
          ln -sfn "$src" "$dst"; echo "relink $dst -> $src"
        fi
      elif [ -e "$dst" ]; then
        echo "skip  $dst は実体ディレクトリ（上書きしない。手で確認する）"; status=1
      else
        ln -s "$src" "$dst"; echo "link  $dst -> $src"
      fi
    done
  done
  return $status
}

do_check() {
  local findings=0 target l name src dst readme
  # 1. 壊れた symlink
  for target in "$CLAUDE_SKILLS_DIR" "$AGENTS_SKILLS_DIR" "$CODEX_SKILLS_DIR" "$REPO_DIR/.claude/skills" "$REPO_DIR/.agents/skills" "$REPO_DIR/.codex/skills"; do
    [ -d "$target" ] || continue
    for l in "$target"/*; do
      [ -L "$l" ] && [ ! -e "$l" ] && { echo "broken   $l -> $(readlink "$l")"; findings=$((findings+1)); }
    done
  done
  # 2. Skills のスキルが両置き場に無い
  for target in "$CLAUDE_SKILLS_DIR" "$AGENTS_SKILLS_DIR"; do
    for name in $(list_skills); do
      dst="$target/$name"; src="$SKILLS_DIR/$name"
      if [ ! -L "$dst" ] || [ "$(realpath_py "$dst")" != "$(realpath_py "$src")" ]; then
        echo "missing  ${dst}（$name を $target に配置していない）"; findings=$((findings+1))
      fi
    done
  done
  # 3. 同名が別の実体を指す（symlink 対は同一実体なので対象外）
  local tmp; tmp="$(mktemp)"
  for target in "$CLAUDE_SKILLS_DIR" "$AGENTS_SKILLS_DIR" "$CODEX_SKILLS_DIR" "$REPO_DIR/.claude/skills" "$REPO_DIR/.agents/skills" "$REPO_DIR/.codex/skills"; do
    [ -d "$target" ] || continue
    for l in "$target"/*/; do
      [ -e "$l" ] || continue
      name="$(basename "$l")"; [ "${name#.}" = "$name" ] || continue
      [ -f "$l/SKILL.md" ] || continue
      printf '%s\t%s\t%s\n' "$name" "$(realpath_py "$l")" "$target/$name" >> "$tmp"
    done
  done
  local TAB=$'\t'
  for name in $(cut -f1 "$tmp" | sort -u); do
    if [ "$(grep "^$name$TAB" "$tmp" | cut -f2 | sort -u | wc -l | tr -d ' ')" -gt 1 ]; then
      echo "duplicate $name が別々の実体で複数の置き場にある:"
      grep "^$name$TAB" "$tmp" | awk -F'\t' '{print "           " $3 " -> " $2}'
      findings=$((findings+1))
    fi
  done
  rm -f "$tmp"
  # 4. README 管理表との食い違い
  readme="$SKILLS_DIR/README.md"
  if [ -f "$readme" ]; then
    for name in $(list_skills); do
      grep -q "^| \[$name\](./$name/SKILL.md)" "$readme" || { echo "readme   $name が README の管理表に無い"; findings=$((findings+1)); }
    done
    for name in $(grep -oE '^\| \[[^]]+\]\(\./[^/]+/SKILL\.md\)' "$readme" | sed -E 's/^\| \[([^]]+)\].*/\1/'); do
      [ -f "$SKILLS_DIR/$name/SKILL.md" ] || { echo "readme   管理表の $name に対応するディレクトリが無い"; findings=$((findings+1)); }
    done
  fi
  if [ "$findings" -eq 0 ]; then echo "check: 問題なし"; return 0; fi
  echo "check: $findings 件"; return 1
}

case "${1:-}" in
  --check) do_check ;;
  "") do_link ;;
  *) echo "usage: $0 [--check]" >&2; exit 2 ;;
esac
