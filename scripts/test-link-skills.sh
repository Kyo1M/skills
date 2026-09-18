#!/usr/bin/env bash
# link-skills.sh の動作確認。一時ディレクトリに置き場を作って link と --check を検証する。
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd -P)"
# macOS の mktemp -d は /var/... を返すが /var は /private/var への symlink なので、
# realpath との比較が食い違う。物理パスに正規化してから使う。
T="$(cd "$(mktemp -d)" && pwd -P)"
trap 'rm -rf "$T"' EXIT
export SKILLS_DIR="$T/Skills" CLAUDE_SKILLS_DIR="$T/claude" AGENTS_SKILLS_DIR="$T/agents" CODEX_SKILLS_DIR="$T/codex" REPO_DIR="$T/repo"
mkdir -p "$SKILLS_DIR"/{alpha,beta,docs,scripts,archive/old} "$CODEX_SKILLS_DIR/.system" "$REPO_DIR/.agents/skills/gamma" "$REPO_DIR/.claude/skills"
echo x > "$SKILLS_DIR/alpha/SKILL.md"; echo x > "$SKILLS_DIR/beta/SKILL.md"; echo x > "$SKILLS_DIR/archive/old/SKILL.md"
echo x > "$REPO_DIR/.agents/skills/gamma/SKILL.md"; ln -s ../../.agents/skills/gamma "$REPO_DIR/.claude/skills/gamma"
cat > "$SKILLS_DIR/README.md" <<'EOF'
| skill | 説明 |
|-------|------|
| [alpha](./alpha/SKILL.md) | a |
| [beta](./beta/SKILL.md) | b |
EOF
fail() { echo "NG: $*"; exit 1; }

# 1. link: 両置き場に symlink ができる
"$HERE/link-skills.sh" >/dev/null
[ "$(python3 -c 'import os,sys;print(os.path.realpath(sys.argv[1]))' "$CLAUDE_SKILLS_DIR/alpha")" = "$SKILLS_DIR/alpha" ] || fail "claude/alpha"
[ "$(python3 -c 'import os,sys;print(os.path.realpath(sys.argv[1]))' "$AGENTS_SKILLS_DIR/beta")" = "$SKILLS_DIR/beta" ] || fail "agents/beta"
[ ! -e "$CLAUDE_SKILLS_DIR/old" ] && [ ! -e "$CLAUDE_SKILLS_DIR/docs" ] || fail "archive/docs が対象になっている"

# 2. check: 正常なら exit 0
"$HERE/link-skills.sh" --check >/dev/null || fail "正常系の --check が非 0"

# 3. check: 壊れた symlink・未配置・同名の別実体・README 漏れを検出して exit 1
ln -s "$T/nowhere" "$CLAUDE_SKILLS_DIR/ghost"
rm "$AGENTS_SKILLS_DIR/beta"
mkdir -p "$CODEX_SKILLS_DIR/alpha"; echo y > "$CODEX_SKILLS_DIR/alpha/SKILL.md"
mkdir -p "$SKILLS_DIR/delta"; echo x > "$SKILLS_DIR/delta/SKILL.md"
out="$("$HERE/link-skills.sh" --check 2>&1)" && fail "異常系の --check が 0"
echo "$out" | grep -q 'broken.*ghost'      || fail "壊れた symlink 未検出: $out"
echo "$out" | grep -q 'missing.*agents.*beta' || fail "未配置 未検出: $out"
echo "$out" | grep -q 'duplicate.*alpha'   || fail "同名の別実体 未検出: $out"
echo "$out" | grep -q 'readme.*delta'      || fail "README 漏れ 未検出: $out"
echo "$out" | grep -q 'gamma' && fail "repo の symlink 対を重複と誤検出: $out"

# 4. link: 既存の実体ディレクトリは上書きしない
mkdir -p "$CLAUDE_SKILLS_DIR/delta"; echo z > "$CLAUDE_SKILLS_DIR/delta/SKILL.md"
out="$("$HERE/link-skills.sh" 2>&1)" || true
[ ! -L "$CLAUDE_SKILLS_DIR/delta" ] || fail "実体を symlink で上書きした"
echo "$out" | grep -q 'skip.*delta' || fail "上書き回避の報告なし: $out"
echo "OK"
