# スキル棚卸し 実装計画

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 自作スキルの正本を「Skills リポジトリ」と「各業務・案件リポジトリ」の 2 系統に絞り、Claude Code と Codex には symlink だけで配り、同名の重複・壊れたリンク・廃止品を無くす。

**Architecture:** 実体は git 管理の 2 系統にだけ置く。`~/.claude/skills` と `~/.agents/skills` は `scripts/link-skills.sh` が Skills 直下から張る symlink のみ。業務スキルは repo の `.agents/skills` に実体、`.claude/skills` は相対 symlink。vac-* は vaccinechoice_HH 内で git 管理外。meeting-minutes は Skills の規約駆動版 1 本に統一し軽量化する。

**Tech Stack:** bash（macOS BSD 系コマンド。`readlink -f` は使わず `python3 -c 'import os,sys;print(os.path.realpath(sys.argv[1]))'` か `cd && pwd -P` で実体パスを取る）、git、Markdown。

**Spec:** `~/Developer/Skills/docs/specs/2026-09-18-skills-inventory-design.md`

## Global Constraints

- 削除してよいのは「壊れた symlink」「空ディレクトリ」「Skills の正本が別にある複製」だけ。中身のある唯一の実体は移動か `~/Developer/_archive/` への退避にし、消さない。
- git commit するのは Skills リポジトリだけ。kyo1M-business と vaccinechoice_HH は変更を作業ツリーに残し、コミットしない（各リポジトリの規約）。
- コミットメッセージは日本語 Conventional Commits。末尾に `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>` を付ける。
- 絶対パスは `$HOME` 展開後の実パス。旧パス `~/Documents/Develop/...` は一切使わない。
- Skills 直下でスキルでないディレクトリは `archive/`、`docs/`、`scripts/`、`node_modules/`。スキルは `SKILL.md` を直下に持つディレクトリ。
- claude.ai 側の無効化・削除は村上さんが行う。エージェントは claude.ai を操作しない。
- 各タスクの Step で「Expected」に書いた出力と違ったら止めて報告する。推測で先へ進まない。

---

### Task 1: Skills リポジトリの衛生（未コミット変更の切り離しとブランチ整理）

**Files:**
- Modify（既存の未コミット差分をコミットするだけ）: `deck-outline/SKILL.md`, `deck-outline/references/writing-principles.md`, `html-slide-deck/SKILL.md`, `html-slide-deck/assets/template.dc.html`, `html-slide-deck/references/claude-design-rules.md`, `html-slide-deck/references/design-system.md`, `html-slide-deck/references/self-review-checklist.md`, `html-slide-deck/references/automatic-slide-numbers.md`（新規）, `html-slide-deck/scripts/pptx-slide-numbers.py`（新規）

**Interfaces:**
- Produces: ブランチ `chore/20260918-skills-inventory`（main から派生）。以降の Task 2〜5・Task 10 はこのブランチで作業する。

- [x] **Step 1: 現状確認**

Run:
```bash
cd ~/Developer/Skills && git status --short && git branch --show-current
```
Expected: 変更ファイル 7 件と未追跡 2 件（上記）。ブランチは `chore/20260703-env-overhaul`。`docs/specs/2026-09-18-skills-inventory-design.md` は既にコミット済みで一覧に出ない。

- [x] **Step 2: deck 系の未コミット変更を 1 コミットにする**

Run:
```bash
cd ~/Developer/Skills && git add deck-outline html-slide-deck && git commit -q -m "deck-outline/html-slide-deck: 初稿の文章ルール参照・フッターの作成日非表示・PPTX 自動ページ番号（references/automatic-slide-numbers.md、scripts/pptx-slide-numbers.py）・スクショ枠を機能説明ページに限定

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" && git status --short
```
Expected: 出力なし（作業ツリーがきれい）。

- [x] **Step 3: 作業ブランチを push し main へ ff マージ**

Run:
```bash
cd ~/Developer/Skills && git push -q origin chore/20260703-env-overhaul && git checkout -q main && git pull -q --ff-only origin main && git merge -q --ff-only chore/20260703-env-overhaul && git push -q origin main && git log --oneline -3
```
Expected: 先頭 3 件が「deck-outline/html-slide-deck: 初稿の…」「docs: スキル棚卸しの設計書…」「書き方原則 50 を追加…」。`--ff-only` が失敗したら止めて報告する（main に別のコミットがある）。

- [x] **Step 4: 棚卸し用ブランチを作る**

Run:
```bash
cd ~/Developer/Skills && git checkout -q -b chore/20260918-skills-inventory && git branch --show-current
```
Expected: `chore/20260918-skills-inventory`

---

### Task 2: Codex 専用の自作 2 件を Skills へ移設し、参照パスを直す

**Files:**
- Move: `~/.codex/skills/business-slide-writing/` → `~/Developer/Skills/business-slide-writing/`
- Move: `~/.codex/skills/gemini-ja-proofread/` → `~/Developer/Skills/gemini-ja-proofread/`
- Modify: `~/Developer/Skills/business-slide-writing/SKILL.md`（最終段落の絶対パス）
- Modify: `~/Developer/Skills/deck-outline/SKILL.md`, `~/Developer/Skills/html-slide-deck/SKILL.md`（`~/.codex/skills/business-slide-writing/references/principles.md` の参照）

**Interfaces:**
- Produces: Skills 直下のスキルディレクトリ 12 件（一般 10 + この 2 件）。Task 3 のスクリプトがこれを symlink の対象にする。

- [x] **Step 1: 移動**

Run:
```bash
cd ~/Developer/Skills && test ! -e business-slide-writing && test ! -e gemini-ja-proofread && mv ~/.codex/skills/business-slide-writing . && mv ~/.codex/skills/gemini-ja-proofread . && ls -d business-slide-writing gemini-ja-proofread && find business-slide-writing gemini-ja-proofread -type f | sort
```
Expected: 7 ファイル（`business-slide-writing/SKILL.md`, `business-slide-writing/agents/openai.yaml`, `business-slide-writing/references/principles.md`, `gemini-ja-proofread/SKILL.md`, `gemini-ja-proofread/agents/openai.yaml`, `gemini-ja-proofread/references/preferences.md`, `gemini-ja-proofread/scripts/review.py`）。

- [x] **Step 2: 絶対パス参照を相対パスに書き換える**

`business-slide-writing/SKILL.md` の
```
PPTX 出力の手順は `~/.claude/skills/html-slide-deck/references/automatic-slide-numbers.md` を参照する。
```
を
```
PPTX 出力の手順は `../html-slide-deck/references/automatic-slide-numbers.md`（このスキルと同じ置き場にある html-slide-deck）を参照する。
```
に。`deck-outline/SKILL.md` と `html-slide-deck/SKILL.md` にある
```
`~/.codex/skills/business-slide-writing/references/principles.md`
```
を
```
`../business-slide-writing/references/principles.md`（同じ置き場の business-slide-writing）
```
に置換する（両ファイルとも 1 か所ずつ）。

Run:
```bash
cd ~/Developer/Skills && grep -rn 'codex/skills\|\.claude/skills/html-slide-deck' business-slide-writing deck-outline/SKILL.md html-slide-deck/SKILL.md; echo "exit=$?"
```
Expected: 一致なし、`exit=1`。

- [x] **Step 3: gemini-ja-proofread に絶対パス参照が無いか確認**

Run:
```bash
cd ~/Developer/Skills && grep -rn '/Users/\|~/\.codex\|~/\.claude' gemini-ja-proofread; echo "exit=$?"
```
Expected: `exit=1`。一致があればその行を報告し、`~/.codex/skills/<name>` 形式なら `../<name>` に直す。それ以外（API キーの置き場など）は触らない。

- [x] **Step 4: コミット**

Run:
```bash
cd ~/Developer/Skills && git add business-slide-writing gemini-ja-proofread deck-outline/SKILL.md html-slide-deck/SKILL.md && git commit -q -m "feat: Codex 専用だった business-slide-writing と gemini-ja-proofread を Skills に移設し、参照を相対パスにする

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" && git status --short
```
Expected: 出力なし。

---

### Task 3: `scripts/link-skills.sh`（symlink 張り直しと点検）

**Files:**
- Create: `~/Developer/Skills/scripts/link-skills.sh`
- Create: `~/Developer/Skills/scripts/test-link-skills.sh`

**Interfaces:**
- Produces: `scripts/link-skills.sh`（引数なし = 張り直し、`--check` = 点検、結果があれば exit 1）。環境変数 `SKILLS_DIR`（既定 `~/Developer/Skills`）、`CLAUDE_SKILLS_DIR`（既定 `~/.claude/skills`）、`AGENTS_SKILLS_DIR`（既定 `~/.agents/skills`）、`CODEX_SKILLS_DIR`（既定 `~/.codex/skills`）、`REPO_DIR`（既定 `$PWD`）で置き場を差し替えられる。Task 7・10 と README・グローバル CLAUDE.md が呼ぶ。

- [x] **Step 1: テストスクリプトを書く（失敗する状態）**

`~/Developer/Skills/scripts/test-link-skills.sh`:
```bash
#!/usr/bin/env bash
# link-skills.sh の動作確認。一時ディレクトリに置き場を作って link と --check を検証する。
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd -P)"
T="$(mktemp -d)"
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
```

Run:
```bash
chmod +x ~/Developer/Skills/scripts/test-link-skills.sh && ~/Developer/Skills/scripts/test-link-skills.sh
```
Expected: `link-skills.sh: No such file or directory` で失敗。

- [x] **Step 2: スクリプトを書く**

`~/Developer/Skills/scripts/link-skills.sh`:
```bash
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
        echo "missing  $dst（$name を $target に配置していない）"; findings=$((findings+1))
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
```

Run:
```bash
chmod +x ~/Developer/Skills/scripts/link-skills.sh && ~/Developer/Skills/scripts/test-link-skills.sh
```
Expected: `OK`。失敗したら NG 行を読み、スクリプト側を直す（テストの期待は変えない）。

- [x] **Step 3: コミット**

Run:
```bash
cd ~/Developer/Skills && git add scripts/link-skills.sh scripts/test-link-skills.sh && git commit -q -m "feat: scripts/link-skills.sh（~/.claude/skills と ~/.agents/skills への symlink 張り直しと --check 点検）とそのテスト

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" && git status --short
```
Expected: 出力なし。

---

### Task 4: Skills の `.gitignore` と README を新しい配置に合わせる

**Files:**
- Modify: `~/Developer/Skills/.gitignore`（`vac-*/` の除外を消す）
- Modify: `~/Developer/Skills/README.md`（全面書き換え）

**Interfaces:**
- Consumes: Task 3 の `scripts/link-skills.sh`。
- Produces: README の管理表（`| [name](./name/SKILL.md) | 説明 |` 形式）。`--check` がこの形式を読む。

- [x] **Step 1: .gitignore から vac-* の除外を消す**

`.gitignore` の次の 2 行を削除する。
```
# Project-private skills (vaccinechoice_HH 等の限定公開スキル)
vac-*/
```
vac-* の実体はまだ Skills 直下にある（Task 6 で移す）ので、この時点では `git status` に `?? vac-*/` が出る。それで正しい。

- [x] **Step 2: README を書き換える**

`~/Developer/Skills/README.md` を次の内容にする。
```markdown
# skills

自作 skill の正本を管理するリポジトリ。Claude Code と Codex の両方から symlink で使う。

## 置き場のルール

自作 skill の正本は 2 系統だけ。

| 系統 | 正本 | 入るもの |
|---|---|---|
| Skills リポジトリ（このリポジトリ） | `~/Developer/Skills/<name>/` | どのリポジトリでも使う skill |
| 各業務・案件リポジトリ | そのリポジトリの `.agents/skills/<name>/` に実体、`.claude/skills/<name>` は `../../.agents/skills/<name>` への symlink | そのリポジトリの規約に依存する skill |

- Claude Code は `~/.claude/skills/`、Codex は `~/.agents/skills/` を読む。どちらにも実体を置かず、`scripts/link-skills.sh` が張る symlink だけを置く。`~/.codex/skills/` は Codex 側で非推奨なので使わない。
- 同じ名前の skill は 1 つの実装だけ。リポジトリごとの違いは、そのリポジトリの CLAUDE.md / AGENTS.md に書き、skill が規約として読む。
- claude.ai には自作 skill を置かない。スマホや Chrome から使いたい skill が出たら、このリポジトリの正本を上げ直し、下の「claude.ai 専用」に記す。
- skill が見えないときは symlink 切れを疑う: `scripts/link-skills.sh --check`

## 新規スキル追加手順

```bash
NAME=<skill-name>
mkdir -p ~/Developer/Skills/$NAME
$EDITOR ~/Developer/Skills/$NAME/SKILL.md
~/Developer/Skills/scripts/link-skills.sh      # ~/.claude/skills と ~/.agents/skills に symlink
```

Claude Code と Codex を再起動して認識を確認したら、`git add` & commit し、下の管理表に追記する。`scripts/link-skills.sh --check` が管理表との食い違いを報告する。

## 定期点検

月初の weekly-review の前に `scripts/link-skills.sh --check` を 1 回走らせ、壊れたリンク・未配置・同名の別実体・管理表との食い違いをゼロにする。

## 管理対象スキル（Skills リポジトリ管理）

| skill | 説明 |
|-------|------|
| [grill-me](./grill-me/SKILL.md) | 批判的壁打ち。前提を疑い・論点ツリーを整理し・ヌケモレと反証を指摘する。アイデア壁打ちモードとプラン精査モードの 2 モード。終了時に論点整理 md を残す |
| [deck-outline](./deck-outline/SKILL.md) | 資料・スライドの「構成」を実装前に実文言の Markdown で設計する。入力メモのインベントリ化とトレーサビリティで、依頼者のメモの黙った省略を防ぐ。書き方原則の正本は `deck-outline/references/writing-principles.md` |
| [html-slide-deck](./html-slide-deck/SKILL.md) | 事業用スライド DS（白地・明朝タイトル・Klein Blue、1920×1080）で `.dc.html`（deck-stage・Claude Design 互換）を生成。20 型・アイコン対応表・機械チェック・セルフレビュー。deck-outline の構成 md を入力に Phase 3 から。ルール正本は `html-slide-deck/references/design-system.md`。旧 continova v1 は `references/legacy/` |
| [deck-critique](./deck-critique/SKILL.md) | 資料（構成 md / 完成 `.dc.html`）を作成とは別の目で批評・推敲する。指摘リスト+修正案を返す（勝手に直さない） |
| [business-slide-writing](./business-slide-writing/SKILL.md) | 日本語の業務スライドの構成・初稿・リライトで、共有する対象と相談事項を明確にし、作業・利用状況を適切な粒度で書く。文章ルールは `references/principles.md`。deck-outline / html-slide-deck が初稿前に参照する |
| [gemini-ja-proofread](./gemini-ja-proofread/SKILL.md) | Gemini API で日本語の校正案を作り、ユーザーの文章ルール（`references/preferences.md`）を適用して差分を確認する。`scripts/review.py` |
| [meeting-minutes](./meeting-minutes/SKILL.md) | 規約駆動の議事録作成。対象 repo の CLAUDE.md / AGENTS.md から出力先・命名・スキーマ・git 運用を読み取って適応する。質問は日付と人物が分からないときだけ。派生ファイルと git 操作は規約と依頼の範囲内でだけ行う |
| [spec-to-readable-html](./spec-to-readable-html/SKILL.md) | 仕様書 Markdown を要約・図解つきの可読 HTML に変換する |
| [article-pipeline](./article-pipeline/SKILL.md) | note・Zenn 記事を企画→公開準備の 7 フェーズで伴走する。`writing-articles` リポジトリ専用 |
| [empirical-prompt-tuning](./empirical-prompt-tuning/SKILL.md) | skill やプロンプトを実行者に実際に動かして両面評価（成功・失敗）で反復改善する。新規 skill を数回実戦投入したらこれで改善する |
| [daily-log](./daily-log/SKILL.md) | 当日の Claude Code / Codex / Linear 活動を `~/Daily/` に保存する。launchd の plist はマシン固有の絶対パスを含むため移植時は要書き換え |
| [continova-business-card](./continova-business-card/SKILL.md) | continova 名刺を HTML → Chrome PDF で出力する。continova-hp プロジェクト専用 |

## リポジトリ管理の業務・案件スキル（場所だけ記す）

| リポジトリ | 場所 | skill |
|---|---|---|
| kyo1M-business | `.agents/skills/`（実体、git 管理）。`.claude/skills/` は symlink | brutal-advisor, business-planning, contact-profile-drafter, document-drafter, git-commit, hypothesis-map, interview-prep-drafter, project-update-from-meetings, weekly-review |
| vaccinechoice_HH | `.agents/skills/`（実体、git 管理外）。`.claude/skills/` は symlink | vac-gdocs-report, vac-linear-plan, vac-linear-update, vac-minutes, vac-nb, vac-report, vac-report-html, vac-understand |

## 第三者製（管理外。場所と出所だけ記す）

| skill | 場所 | 出所 |
|---|---|---|
| gog | `~/.claude/skills/gog`（実体） | steipete/gogcli |
| agmsg | `~/.agents/skills/agmsg` | 導入物（`VERSION`・`uninstall.sh` を持つ） |
| find-skills | `~/.agents/skills/find-skills` | vercel-labs/skills（`npx skills add`、`~/.agents/.skill-lock.json`） |
| orca-cli, orchestration | `~/.agents/skills/` | stablyai/orca（同上） |
| linear | `~/.agents/skills/linear` | Linear 公式の Codex 向け skill（Apache-2.0） |

## claude.ai 専用

なし（2026-09-18 に自作 7 件を無効化。ローカルに無かった 3 件は `archive/claude-ai-skills/` に退避）。

## スキル間の使い分け（2 レーン）

**資料作成レーン**:

```
(論点が固まっていなければ) grill-me → deck-outline（構成 md） → html-slide-deck（`.dc.html` 実装） → deck-critique（批評） → pptx が要れば `.dc.html` を Claude Design に持ち込む
```

初稿の文章ルールは business-slide-writing の `references/principles.md`、Gemini で校正するときは gemini-ja-proofread。

**設計・実装レーン**:

```
軽い壁打ちなら最初から superpowers:brainstorming → docs/superpowers/specs/ に設計書 → writing-plans → 実装
深掘りが要るときは grill-me（論点整理 md）→ brainstorming に接続
```

書き方原則の正本は `deck-outline/references/writing-principles.md`。要約はグローバル `~/.claude/CLAUDE.md` に常設。新しい書き方フィードバックは両方に反映する。

## 注意

- 機密情報（API キー・トークン）は SKILL 内にハードコードしない。Keychain 等から参照する。
- `~/.claude/skills/` や `~/.agents/skills/` に実体ディレクトリを作らない。`scripts/link-skills.sh` は実体があると上書きせず skip として報告する。
```

- [x] **Step 3: コミット**

Run:
```bash
cd ~/Developer/Skills && git add .gitignore README.md && git commit -q -m "docs: README を置き場のルール・4 区分の管理表・link-skills.sh の手順に書き換え、vac-* の gitignore を撤去

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" && git status --short
```
Expected: `?? vac-gdocs-report/` など vac-* 8 件だけが未追跡として出る（Task 6 で移す）。

---

### Task 5: meeting-minutes の軽量化

**Files:**
- Modify: `~/Developer/Skills/meeting-minutes/SKILL.md`（全面書き換え）

**Interfaces:**
- Produces: Skills 共通の meeting-minutes 1 本。kyo1M-business（Task 8）と DXB リポジトリはこれを使う。

- [x] **Step 1: SKILL.md を書き換える**

`~/Developer/Skills/meeting-minutes/SKILL.md` を次の内容にする。
```markdown
---
name: meeting-minutes
description: 議事メモ（壁打ち/面談/会議メモ）から、対象リポジトリの規約に従って正式な議事録を作成し、決定・アクション・未確認事項と出所を残す規約駆動スキル。出力先・命名・frontmatter スキーマ・lint・git 運用は、その repo の CLAUDE.md / AGENTS.md から読み取って適応する（特定のディレクトリ構造をハードコードしない）。「議事録を作成」「議事録化して」「議事メモを整えて」「ミーティングメモをまとめて」等のリクエスト時に起動。
---

# meeting-minutes — 規約駆動の議事録作成スキル

任意のリポジトリで、その repo の規約（出力先・命名・frontmatter・派生先・lint・git 運用）に従って議事録を作成する。

**設計原則: 構造をハードコードしない。** 対象リポジトリの契約ファイル（`CLAUDE.md` / `AGENTS.md`）から規約を読み取り、「議事録プロファイル」を組み立ててから動く。`docs/minutes/` 系でも `notes/meetings/` 系でも同じスキルで動作する。

> 旧 `meeting-minutes-drafter`（kyo1M-business 専用）はこのスキルに統合された。kyo1M-business では Step 0 が同リポジトリの CLAUDE.md「議事録の作り方」を読み取って動く。

## ワークフロー全体

```
Step 0: 規約ディスカバリ（議事録プロファイルの構築）  ← 必ず最初
   ↓
Step 1: 入力収集（drafts / メモパス / 貼り付け）
   ↓
Step 2: 記録の組み立て（質問は日付と人物が分からないときだけ）
   ↓
Step 3: 議事録の生成（プロファイルの出力先・命名・スキーマで）
   ↓
Step 4: 派生（規約に派生先があり、依頼の範囲に含まれるときだけ）
   ↓
Step 5: 完了（検証 → 規約にある git 運用 → 短い報告）
```

## Step 0: 規約ディスカバリ（最初に必ず実行）

1. ルートの `CLAUDE.md` と `AGENTS.md`（存在する方／両方）を Read する。`llms.txt` があれば併読。既存の議事録を 1 つ開いて書式を見る。
2. 以下を抽出する。**規約に明示があればそれに従う → 無ければディレクトリを probe → それでも不明ならユーザーに確認**（推測で書かない）。

| プロファイル項目 | 取得元 / 既定の探索 |
|---|---|
| 議事録の出力先 | 規約の「リポジトリ構造」記述。無ければ `notes/meetings/` か `docs/minutes/` の存在を probe |
| 走り書きの入力元 | `docs/minutes/_drafts/` 等が規約/実在すれば使う。無ければユーザーにメモのパス or 貼り付けを依頼 |
| ファイル命名 | 規約の命名ルール。無ければ既存ファイル名から推定して確認 |
| frontmatter スキーマ | 規約の「frontmatter スキーマ」節（議事録の `type` 値、`status` 語彙、必須/任意フィールド） |
| 決定の派生先 | `docs/decisions/` の存在/規約。無ければ派生しない |
| タスクの派生先 | `tasks/` の存在/規約。無ければ派生しない |
| lint | 規約の検証コマンド。無ければスキップ |
| git 運用 | 規約が議事録作成時のブランチ・コミット・push を定めているか。定めが無ければ git 操作をしない |
| contact プロファイル | `notes/contacts/` 等の人物プロファイル置き場があればリンク対象にする |

3. 組み立てたプロファイルを 1〜2 行でユーザーに提示し、ズレがあれば直してもらってから先へ進む。

## Step 1: 入力収集

1. drafts 置き場があれば、その中の対象メモをリストアップしてユーザーに選んでもらう。
2. drafts が無い repo では、ユーザーにメモのパスか本文の貼り付けを依頼する。
3. 対象メモを Read。同じスラグ + transcript ファイルがあれば併読。`recording:` パスは本文に注記のみ（再生しない）。

## Step 2: 記録の組み立て

渡されたメモと会話から、日時、参加者、議題、観察、判断理由、明示的決定、次の約束を取り出す。

- **質問は日付と人物を同定できないときだけ。** それ以外の不足は「要確認」として草案に残し、空欄を埋めるためだけの問答を増やさない。ユーザーが深掘りを求めたときだけ、結論の理由・他に出た意見・決定か検討中か・担当と期限を追加で聞く。
- 会議日と作成日を分ける。
- 発言者と観察者、本人の意思と他者の提案、合意と検討案、予定と実施を区別する。
- 原メモに無い参加者・担当・期限・法的・金銭的結論を作らない。
- 元メモや過去記録を黙って消さず、補足は追記する。訂正は日付と根拠を付ける。

## Step 3: 議事録の生成

プロファイルの **出力先・命名・frontmatter スキーマ** に従って生成する。不明項目は推測で埋めず、`要確認` / 空欄で残し本文末尾に注記する。

本文セクション構成（既存テンプレがあれば優先）:

```markdown
# <日本語タイトル>

## 要約
[3〜5 文。主な議題と結論、重要な決定、全体の方向性]

## 議事内容（詳細）
### <議題1>
- [元のメモを構造化] + [補足]

## 決定事項
- [合意・確定したもの。検討中は含めない]

## ネクストアクション
| 担当者 | アクション | 期限 |
|--------|-----------|------|
| 〇〇 | [内容] | YYYY-MM-DD / 未定 |

## 要確認事項
- [残った質問]
```

- 長さは元の情報量に合わせる。
- contact プロファイル置き場がある repo では、自分以外の参加者のプロファイルにリンクし、無ければ規約に従ってドラフト作成か `contact-profile-drafter` 等へ委譲。

## Step 4: 派生（規約に派生先があり、依頼の範囲に含まれるときだけ）

既定は議事録内の「決定事項」「ネクストアクション」に留める。

- **決定**: 派生先（例 `docs/decisions/`）が規約にあり、規約が「重大な方針変更だけ」等の基準を置いていればそれに従う。派生する場合は雛形に従い、`derived_from: [<この議事録のパス>]` を入れる。候補の一つ一つを ADR にしない。
- **アクション**: 横断タスクや相手別進行の正本（ボード・pipeline 等）が規約にあれば、その該当行の更新に留める。別のタスクファイルや外部 Issue を量産しない。
- いずれも**作成前に一覧を提示してユーザー確認**。派生に確信が持てなければ、議事録末尾に「派生候補（要確認）」節を設けて振り分けを委ねる。

## Step 5: 完了

1. 変更した文書の frontmatter とリンクを検証し、プロファイルに lint コマンドがあれば実行する。失敗したら直してから次へ。
2. git 操作は、規約が議事録作成時のブランチ・コミット・push を定めているときだけ、その規約どおりに行う（例: 「1 作業 = 1 ブランチ、コミットメッセージは案を提示して確認後」）。定めが無い repo では行わず、明示依頼のときだけ行う。
3. 議事録のパスと重要な未確認事項を短く報告する。

## 注意事項

- 規約は repo ごとに違う。**Step 0 を飛ばして特定構造を前提にしない。** 不明点は probe → 確認の順で潰す。
- 元メモは削除せず追記で充実させる。担当者・期限未定のアクションも「未定」で表に含める。
- 派生ファイルは必ず人間レビューを経る。AI が勝手に decisions/ や tasks/ を確定しない。
```

- [x] **Step 2: 旧版の重い手順が残っていないことの確認**

Run:
```bash
cd ~/Developer/Skills && grep -n '2〜3 ラウンド\|push 提案\|Step 8\|ブランチ確認・切替' meeting-minutes/SKILL.md; echo "exit=$?"
```
Expected: 一致なし、`exit=1`。

- [x] **Step 3: 旧版との対比で落としてはいけない要素を確認**

Run:
```bash
cd ~/Developer/Skills && for k in 'Step 0' 'derived_from' 'contact' 'recording:' 'transcript' '要確認' '規約が議事録作成時' '日付と人物'; do printf '%-22s %s\n' "$k" "$(grep -c "$k" meeting-minutes/SKILL.md)"; done
```
Expected: すべて 1 以上。

- [x] **Step 4: コミット**

Run:
```bash
cd ~/Developer/Skills && git add meeting-minutes/SKILL.md && git commit -q -m "refactor(meeting-minutes): 軽量化（質問は日付と人物だけ、git 操作と派生は規約と依頼の範囲内、記録の作法を明文化）

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" && git status --short
```
Expected: vac-* の未追跡 8 件だけ。

---

### Task 6: vac-* を vaccinechoice_HH 内のローカル管理へ移す

**Files:**
- Move: `~/Developer/Skills/vac-*`（8 件）→ `~/Developer/vaccinechoice_HH/.agents/skills/vac-*`
- Modify: `~/Developer/vaccinechoice_HH/.claude/skills/vac-*`（symlink を相対パスに張り替え）
- Delete: `~/Developer/vaccinechoice_HH/.claude/skills/spec-to-readable-html`（symlink）, `~/Developer/vaccinechoice_HH/.agents/skills/spec-to-readable-html`（実体コピー）, `~/Developer/vaccinechoice_HH/.codex/`（壊れた symlink 4 本のみ）
- Modify: `~/Developer/vaccinechoice_HH/.gitignore`, `~/Developer/vaccinechoice_HH/CLAUDE.md`
- Delete: `~/.claude/skills/vac-minutes`, `vac-nb`, `vac-report`, `vac-report-html`（global symlink）

**Interfaces:**
- Produces: Skills 直下から vac-* が消える（Task 7 の symlink 張り直しの前提）。

- [x] **Step 1: 現状確認**

Run:
```bash
cd ~/Developer/vaccinechoice_HH && git status --short | head -5 && ls -la .agents/skills .claude/skills && ls -la .codex/skills && ls -d ~/Developer/Skills/vac-*
```
Expected: `.agents/skills` に spec-to-readable-html・vac-gdocs-report・vac-minutes・vac-nb・vac-report の実体 5 件、`.claude/skills` に symlink 9 件、`.codex/skills` に壊れた symlink 4 件、Skills 直下に vac-* 8 件。

- [x] **Step 2: 既存の `.agents/skills/vac-*` 4 件の git 追跡を外し、実体を退避してから Skills の最新版で置き換える**

`.agents/skills` のコピーは 07-03 で止まっており、Skills 側が最新。差分があるか先に見る。

Run:
```bash
cd ~/Developer/vaccinechoice_HH && for s in vac-gdocs-report vac-minutes vac-nb vac-report; do echo "== $s"; diff -rq .agents/skills/$s ~/Developer/Skills/$s || true; done
```
Expected: 差分の一覧（vac-report の SKILL.md 等）。差分があっても Skills 側を採用する（Skills 側が利用中の実体）。

Run:
```bash
cd ~/Developer/vaccinechoice_HH && git rm -r -q --cached .agents/skills/vac-gdocs-report .agents/skills/vac-minutes .agents/skills/vac-nb .agents/skills/vac-report .agents/skills/spec-to-readable-html .claude/skills/spec-to-readable-html && mkdir -p ~/Developer/_archive/2026-09-18-vaccinechoice-agents-skills && mv .agents/skills/vac-gdocs-report .agents/skills/vac-minutes .agents/skills/vac-nb .agents/skills/vac-report .agents/skills/spec-to-readable-html ~/Developer/_archive/2026-09-18-vaccinechoice-agents-skills/ && rm .claude/skills/spec-to-readable-html && git status --short | grep -E '^D ' | wc -l
```
Expected: `D ` 行の数が 5 ディレクトリ分のファイル数（`git ls-files` で追跡されていた数。少なくとも 5）。

- [x] **Step 3: Skills から実体を移し、`.claude/skills` の symlink を相対パスに張り替える**

Run:
```bash
cd ~/Developer/vaccinechoice_HH && for s in vac-gdocs-report vac-linear-plan vac-linear-update vac-minutes vac-nb vac-report vac-report-html vac-understand; do mv ~/Developer/Skills/$s .agents/skills/$s && ln -sfn ../../.agents/skills/$s .claude/skills/$s; done && ls -d ~/Developer/Skills/vac-* 2>/dev/null; for s in .claude/skills/vac-*; do test -f "$s/SKILL.md" && echo "ok $s -> $(readlink $s)"; done
```
Expected: Skills 直下に vac-* が無く、`ok .claude/skills/vac-... -> ../../.agents/skills/vac-...` が 8 行。

- [x] **Step 4: `.gitignore` と CLAUDE.md を直す**

`.gitignore` の
```
# vac-* skills は /Users/murakamikyouichi/Documents/Develop/Skills/ に移行（symlink で参照）
.claude/skills/vac-*
```
を
```
# vac-* skills は自分専用のローカル管理（git 管理しない）。実体は .agents/skills/、.claude/skills/ は symlink
.agents/skills/vac-*
.claude/skills/vac-*
```
に。`CLAUDE.md` の 11 行目
```
- 分析ノートブックの作成・編集・実行は `vac-nb` スキル、レポート作成は `vac-report`（Markdown）→ `vac-report-html`（自己完結 HTML）スキルを使う（`.claude/skills/` に登録済み）
```
を
```
- 分析ノートブックの作成・編集・実行は `vac-nb` スキル、レポート作成は `vac-report`（Markdown）→ `vac-report-html`（自己完結 HTML）スキルを使う（実体は `.agents/skills/vac-*`、`.claude/skills/vac-*` は symlink。git 管理外のローカル専用）
```
に。

Run:
```bash
cd ~/Developer/vaccinechoice_HH && git check-ignore -q .agents/skills/vac-nb .claude/skills/vac-nb && echo ignored && git status --short | grep -c 'skills/vac-'
```
Expected: `ignored` と `0`。

- [x] **Step 5: `.codex/` と global symlink を消す**

Run:
```bash
cd ~/Developer/vaccinechoice_HH && for l in .codex/skills/*; do [ -L "$l" ] && [ ! -e "$l" ] || { echo "壊れていないものがある: $l"; exit 1; }; done && rm -r .codex && for s in vac-minutes vac-nb vac-report vac-report-html; do [ -L ~/.claude/skills/$s ] && rm ~/.claude/skills/$s; done; ls ~/.claude/skills | grep -c vac-; ls -d .codex 2>&1 | head -1
```
Expected: `0` と `ls: .codex: No such file or directory`。

- [x] **Step 6: vaccinechoice_HH の変更を一覧にして報告（コミットしない）**

Run:
```bash
cd ~/Developer/vaccinechoice_HH && git status --short
```
Expected: `D .agents/skills/...`、`D .claude/skills/spec-to-readable-html`、`M .gitignore`、`M CLAUDE.md` に加え、棚卸し前からあった `M 03_vaccine_allocation/...ipynb` と `?? data/output/...`、`?? docs/reviews/`。この一覧を最終報告に載せる。

---

### Task 7: `~/.codex/skills` の整理、claude.ai 3 件の退避、symlink の張り直し

**Files:**
- Delete: `~/.codex/skills/vac-minutes`, `vac-nb`, `vac-plan`, `vac-report`（壊れた symlink）, `~/.codex/skills/codex-primary-runtime`（空）
- Move: `~/.codex/skills/{contact-profile-drafter,project-update-from-meetings,meeting-minutes-drafter,git-staged-commit-ja}` → `~/Developer/_archive/2026-09-18-codex-skills/`
- Move: `~/.codex/skills/linear` → `~/.agents/skills/linear`
- Move: `~/.codex/skills/interview-prep-drafter` → `~/Developer/kyo1M-business/.agents/skills/interview-prep-drafter`
- Create: `~/Developer/Skills/archive/claude-ai-skills/{note-writing-assistant,project-overview,kpi-structure}/`（synced からコピー）
- Create: `~/.agents/skills/<12 件>`、`~/.claude/skills/{business-slide-writing,gemini-ja-proofread}` の symlink（スクリプト）

**Interfaces:**
- Consumes: Task 3 の `scripts/link-skills.sh`、Task 6 で Skills 直下から vac-* が消えていること。
- Produces: `~/.codex/skills` は `.system` だけ。`kyo1M-business/.agents/skills/interview-prep-drafter` の実体（Task 8 が symlink を張る）。

- [x] **Step 1: 前提確認**

Run:
```bash
ls -d ~/Developer/Skills/vac-* 2>/dev/null | wc -l; ls ~/.codex/skills; ls ~/.agents/skills
```
Expected: `0`、`~/.codex/skills` に business-slide-writing と gemini-ja-proofread が無い（Task 2 で移動済み）、`~/.agents/skills` は agmsg・find-skills・orca-cli・orchestration の 4 件。

- [x] **Step 2: 壊れた symlink と空ディレクトリを消す**

Run:
```bash
cd ~/.codex/skills && for s in vac-minutes vac-nb vac-plan vac-report; do [ -L $s ] && [ ! -e $s ] && rm $s; done; [ -d codex-primary-runtime ] && [ -z "$(ls -A codex-primary-runtime)" ] && rmdir codex-primary-runtime; ls
```
Expected: `contact-profile-drafter git-staged-commit-ja interview-prep-drafter linear meeting-minutes-drafter project-update-from-meetings`（`.system` は `ls` に出ない）。

- [x] **Step 3: 旧版 4 件を退避、linear を移す**

Run:
```bash
mkdir -p ~/Developer/_archive/2026-09-18-codex-skills && cd ~/.codex/skills && mv contact-profile-drafter project-update-from-meetings meeting-minutes-drafter git-staged-commit-ja ~/Developer/_archive/2026-09-18-codex-skills/ && mv linear ~/.agents/skills/linear && cat > ~/Developer/_archive/2026-09-18-codex-skills/README.md <<'EOF'
# 2026-09-18 ~/.codex/skills から退避した旧版

スキル棚卸し（~/Developer/Skills/docs/specs/2026-09-18-skills-inventory-design.md）で退避。現行の正本は次のとおり。

| 退避したもの | 現行 |
|---|---|
| contact-profile-drafter（2026-01-15 版） | kyo1M-business/.agents/skills/contact-profile-drafter |
| project-update-from-meetings（2026-01-15 版） | kyo1M-business/.agents/skills/project-update-from-meetings |
| meeting-minutes-drafter（2026-06-15 に廃止） | ~/Developer/Skills/meeting-minutes |
| git-staged-commit-ja（2026-01-26 版） | kyo1M-business/.agents/skills/git-commit |

いずれも git 履歴に無かったので削除せず残した。
EOF
ls ~/.codex/skills; ls ~/Developer/_archive/2026-09-18-codex-skills
```
Expected: `~/.codex/skills` は `interview-prep-drafter` だけ。退避先に 4 ディレクトリと README.md。

- [x] **Step 4: interview-prep-drafter を kyo1M-business へ移す**

Run:
```bash
cd ~/Developer/kyo1M-business && test -L .claude/skills/interview-prep-drafter && rm .claude/skills/interview-prep-drafter && mv ~/.codex/skills/interview-prep-drafter .agents/skills/interview-prep-drafter && ln -s ../../.agents/skills/interview-prep-drafter .claude/skills/interview-prep-drafter && test -f .claude/skills/interview-prep-drafter/SKILL.md && echo ok && ls -A ~/.codex/skills
```
Expected: `ok` と `.system`。

- [x] **Step 5: claude.ai の 3 件を退避**

Run:
```bash
B=$(ls -d ~/.claude/skills/synced/*_*/ | head -1) && mkdir -p ~/Developer/Skills/archive/claude-ai-skills && for s in note-writing-assistant project-overview kpi-structure; do cp -R "$B/$s" ~/Developer/Skills/archive/claude-ai-skills/$s; done && cat > ~/Developer/Skills/archive/claude-ai-skills/README.md <<'EOF'
# claude.ai から退避した自作スキル

2026-09-18 のスキル棚卸しで claude.ai の自作 7 件を無効化した。ローカルに無かった 3 件だけ中身を残す（note-writing-assistant 2026-01-13、project-overview 2026-02-02、kpi-structure 2026-02-02）。残り 4 件（brutal-advisor、hypothesis-map、meeting-minutes、html-slide-deck）はローカルに新しい版がある。

`scripts/link-skills.sh` はこの `archive/` を symlink の対象にしない。
EOF
find ~/Developer/Skills/archive/claude-ai-skills -name SKILL.md | wc -l
```
Expected: `3`。

- [x] **Step 6: symlink を張り直す**

Run:
```bash
cd ~/Developer/Skills && scripts/link-skills.sh && ls -l ~/.agents/skills | awk '{print $9, $10, $11}' | sort
```
Expected: `link` 行が `~/.agents/skills` に 12 本、`~/.claude/skills` に 2 本（business-slide-writing、gemini-ja-proofread）、それ以外は `ok`。`skip` は出ない。`~/.agents/skills` の一覧は自作 12 件の symlink + agmsg・find-skills・orca-cli・orchestration・linear の実体。

- [x] **Step 7: 退避をコミット**

Run:
```bash
cd ~/Developer/Skills && git add archive/claude-ai-skills && git commit -q -m "chore: claude.ai の自作 3 件（note-writing-assistant, project-overview, kpi-structure）を archive/claude-ai-skills に退避

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" && git status --short
```
Expected: 出力なし。

---

### Task 8: kyo1M-business の業務スキルを `.agents` 実体 + `.claude` symlink にし、CLAUDE.md を直す

**Files:**
- Delete: `~/Developer/kyo1M-business/.claude/skills/meeting-minutes/`, `.agents/skills/meeting-minutes/`
- Modify: `~/Developer/kyo1M-business/.claude/skills/<9 件>`（実体を消して相対 symlink に）
- Modify: `~/Developer/kyo1M-business/CLAUDE.md`

**Interfaces:**
- Consumes: Task 7 の `.agents/skills/interview-prep-drafter` と `.claude/skills/interview-prep-drafter` symlink。
- Produces: `.agents/skills` に実体 10 件、`.claude/skills` に symlink 10 件。

- [x] **Step 1: `.claude` と `.agents` の同一性を確認してから meeting-minutes を消す**

Run:
```bash
cd ~/Developer/kyo1M-business && diff -rq .claude/skills .agents/skills; echo "exit=$?"
```
Expected: `Only in .claude/skills: interview-prep-drafter` は出ない（Task 7 で両方に揃った）。差分があれば止めて報告する（symlink 化で片方の内容が失われる）。

Run:
```bash
cd ~/Developer/kyo1M-business && git rm -r -q .claude/skills/meeting-minutes .agents/skills/meeting-minutes && ls .claude/skills .agents/skills | grep -c meeting-minutes
```
Expected: `0`。

- [x] **Step 2: `.claude/skills` の実体 8 件を symlink に置き換える**

Run:
```bash
cd ~/Developer/kyo1M-business && for s in brutal-advisor business-planning contact-profile-drafter document-drafter git-commit hypothesis-map project-update-from-meetings weekly-review; do [ -d .claude/skills/$s ] && [ ! -L .claude/skills/$s ] && git rm -r -q .claude/skills/$s && ln -s ../../.agents/skills/$s .claude/skills/$s && git add .claude/skills/$s; done; git add .agents/skills/interview-prep-drafter .claude/skills/interview-prep-drafter; for s in .claude/skills/*; do printf '%s -> %s : %s\n' "$s" "$(readlink $s)" "$([ -f $s/SKILL.md ] && echo ok || echo NG)"; done
```
Expected: 10 行、すべて `../../.agents/skills/<name> : ok`。

- [x] **Step 3: CLAUDE.md を直す**

`~/Developer/kyo1M-business/CLAUDE.md` に 4 か所の変更。

(a) リポジトリ構造の
```
.claude/skills/                  # Claude Code用スキル
.agents/skills/                  # Agents用スキル
```
を
```
.agents/skills/                  # 業務スキルの実体（Claude Code と Codex の両方が使う）
.claude/skills/                  # .agents/skills への symlink（Claude Code 用）
```
に。

(b) 利用可能なスキル表の
```
| `/meeting-minutes` | 議事メモから議事録を作成し、決定・アクションを派生抽出（規約駆動） |
```
を
```
| `/meeting-minutes` | Skills 共通の規約駆動スキル（`~/Developer/Skills/meeting-minutes`）。このリポジトリでは下の「議事録の作り方」に従う |
```
に。

(c) 「情報の正本と更新境界」の箇条書きの
```
- スキルの戦略・期限・ボトルネックは正本から読む。`.agents/skills/` と `.claude/skills/` の同名スキルは参照資料も含めて同じ内容を維持する。このリポジトリのmeeting-minutesも両方に配置する。個人用・globalスキルは別管理で、このリポジトリの更新に含めない。
```
を
```
- スキルの戦略・期限・ボトルネックは正本から読む。業務スキルは `.agents/skills/` に実体、`.claude/skills/` は同名の symlink（`ln -s ../../.agents/skills/<name> .claude/skills/<name>`）。meeting-minutes は Skills の共通版を使い、このリポジトリの方針は「議事録の作り方」に書く。個人用・globalスキルは別管理で、このリポジトリの更新に含めない。
```
に。

(d) 「## 情報の整理・アーカイブ」の直前に節を足す。
```
## 議事録の作り方

`/meeting-minutes`（Skills 共通の規約駆動スキル）はこの節を読んで動く。

- 保存先は `notes/meetings/`、命名は `YYYY-MM-DD-<slug>.md`、frontmatter は `type: meeting` と上のスキーマ。
- 質問は日付と人物を同定できないときだけ。それ以外の不足は「要確認」として残す。
- 自分以外の参加者は `notes/contacts/` のプロフィールへリンクする。無ければ `/contact-profile-drafter` で作る。
- 決定は議事録内の「決定事項」に留める。重大な方針変更だけ `docs/decisions/` に ADR-lite を起こし、`derived_from` で議事録へ戻れるようにする。候補を全部 ADR にしない。
- アクションは議事録内の表に留める。横断作業は `docs/tasks/2026-q4-task-board.md`、相手別進行は `clients/pipeline.md` の該当行を更新し、別のタスクファイルや外部 Issue を作らない。
- 完了時に `npm run lint --prefix scripts` を実行する。ブランチ切替・コミット・push は明示依頼のときだけ。
```

Run:
```bash
cd ~/Developer/kyo1M-business && grep -c '議事録の作り方' CLAUDE.md && grep -c '同じ内容を維持' CLAUDE.md
```
Expected: `3`（見出し、スキル表、正本の箇条書き）と `0`。

- [x] **Step 4: lint と状態の報告（コミットしない）**

Run:
```bash
cd ~/Developer/kyo1M-business && npm run lint --prefix scripts 2>&1 | tail -3 && git status --short | grep -E 'skills|CLAUDE.md'
```
Expected: lint が通る。`D .agents/skills/meeting-minutes/...`、`D .claude/skills/<8 件>/...`、`A .claude/skills/<8 件>`、`A .agents/skills/interview-prep-drafter/...`、`M .claude/skills/interview-prep-drafter`（symlink 先の変更）、`M CLAUDE.md`。棚卸し前からあった他の変更（`M docs/now.md` 等）には触れない。

---

### Task 9: グローバル CLAUDE.md と記憶メモの更新

**Files:**
- Modify: `~/.claude/CLAUDE.md`（「開発環境」節の 2 行を書き換え、2 行を追加）
- Modify: `~/.claude/projects/-Users-murakamikyouichi-Developer-kyo1M-business/memory/skills-topology.md`

- [x] **Step 1: グローバル CLAUDE.md**

「開発環境」節の
```
- 自作 skill の実体は `~/Developer/Skills/`(GitHub Kyo1M/skills)。`~/.claude/skills/` に symlink 配置。skill が見えないときは symlink 切れを疑う: `test -f ~/.claude/skills/<name>/SKILL.md`
- 新規 skill は `~/Developer/Skills/` に作成 → `~/.claude/skills/` へ symlink → Skills リポジトリ README の管理表に追記する。
```
を
```
- 自作 skill の正本は 2 系統。どのリポジトリでも使うものは `~/Developer/Skills/`(GitHub Kyo1M/skills)、リポジトリの規約に依存する業務・案件 skill はそのリポジトリの `.agents/skills/` に実体(`.claude/skills/` は `../../.agents/skills/<name>` への symlink)。
- Skills の skill は `~/.claude/skills/`(Claude Code)と `~/.agents/skills/`(Codex)に symlink で配る。実体は置かない。`~/.codex/skills/` は非推奨なので使わない。skill が見えないときは `~/Developer/Skills/scripts/link-skills.sh --check`。
- 新規 skill は `~/Developer/Skills/<name>/SKILL.md` を作成 → `scripts/link-skills.sh` → README の管理表に追記する。同じ名前の skill は 1 実装だけ。リポジトリごとの違いはそのリポジトリの CLAUDE.md / AGENTS.md に書く。claude.ai には自作 skill を置かない。
- 月初の weekly-review の前に `scripts/link-skills.sh --check` を走らせ、壊れたリンク・同名の別実体をゼロにする。
```
に。

Run:
```bash
grep -c 'link-skills.sh' ~/.claude/CLAUDE.md
```
Expected: `3`。

- [x] **Step 2: 記憶メモを書き換える**

`~/.claude/projects/-Users-murakamikyouichi-Developer-kyo1M-business/memory/skills-topology.md` を次の内容にする（frontmatter の `originSessionId` は既存値のまま、`modified` は書き換え時刻）。
```markdown
---
name: skills-topology
description: 自作 skill の正本 2 系統と、Claude Code / Codex への配り方（2026-09-18 棚卸しで確定）
metadata:
  type: reference
---

自作 skill の正本は 2 系統（設計書: `~/Developer/Skills/docs/specs/2026-09-18-skills-inventory-design.md`）。

- **Skills リポジトリ** `~/Developer/Skills`（git: Kyo1M/skills）: どのリポジトリでも使うもの 12 件（grill-me, deck-outline, html-slide-deck, deck-critique, business-slide-writing, gemini-ja-proofread, meeting-minutes, spec-to-readable-html, article-pipeline, empirical-prompt-tuning, daily-log, continova-business-card）。`scripts/link-skills.sh` が `~/.claude/skills`（Claude Code）と `~/.agents/skills`（Codex）に symlink を張る。`--check` で点検。
- **業務・案件リポジトリ**: kyo1M-business は `.agents/skills` に実体 10 件（git 管理）、`.claude/skills` は相対 symlink。vaccinechoice_HH は vac-* 8 件を `.agents/skills` に実体（git 管理外）、`.claude/skills` は相対 symlink。

**Why:** Codex は `~/.agents/skills` とリポジトリの `.agents/skills` を読み、symlink 追従を公式に保証する。`~/.codex/skills` はソース内で deprecated。Claude Code は `~/.claude/skills` とリポジトリの `.claude/skills` を読み、同名は Personal > Project で隠れる。

**How to apply:** 同じ名前の skill は 1 実装だけ。リポジトリごとの違いはそのリポジトリの CLAUDE.md / AGENTS.md に書く（例: kyo1M-business の「議事録の作り方」）。`~/.claude/skills`・`~/.agents/skills`・`~/.codex/skills` に実体を作らない。claude.ai には自作 skill を置かない（2026-09-18 に 7 件を無効化）。第三者製は `~/.agents/skills`（agmsg, find-skills, orca-cli, orchestration, linear）と `~/.claude/skills/gog`。
```

MEMORY.md の該当行を
```
- [skills-topology](skills-topology.md) — 自作 skill の正本 2 系統（Skills リポジトリ／業務・案件リポジトリ）と link-skills.sh による配り方。同名は 1 実装
```
に。

Run:
```bash
grep -n 'skills-topology' ~/.claude/projects/-Users-murakamikyouichi-Developer-kyo1M-business/memory/MEMORY.md
```
Expected: 1 行、上の文言。

---

### Task 10: 検証と計画のコミット

**Files:**
- Modify: `~/Developer/Skills/docs/plans/2026-09-18-skills-inventory.md`（チェックボックスを進める）

- [x] **Step 1: 点検スクリプトを kyo1M-business と vaccinechoice_HH を cwd にして走らせる**

Run:
```bash
cd ~/Developer/kyo1M-business && ~/Developer/Skills/scripts/link-skills.sh --check; echo "exit=$?"; cd ~/Developer/vaccinechoice_HH && ~/Developer/Skills/scripts/link-skills.sh --check; echo "exit=$?"
```
Expected: 両方 `check: 問題なし` と `exit=0`。`duplicate` が出たら、その名前の実体が 2 か所にある。設計書 2.2 に従い片方を消すのではなく止めて報告する。

- [x] **Step 2: 配置の最終確認**

Run:
```bash
echo "--- ~/.codex/skills"; ls -A ~/.codex/skills; echo "--- ~/.claude/skills (vac)"; ls ~/.claude/skills | grep -c vac-; echo "--- Skills 直下"; ls ~/Developer/Skills; echo "--- broken anywhere"; for d in ~/.claude/skills ~/.agents/skills ~/.codex/skills ~/Developer/kyo1M-business/.claude/skills ~/Developer/vaccinechoice_HH/.claude/skills; do for l in $d/*; do [ -L "$l" ] && [ ! -e "$l" ] && echo "BROKEN $l"; done; done; echo "(end)"
```
Expected: `.system` のみ、`0`、Skills 直下に vac-* 無し、`BROKEN` なし。

- [x] **Step 3: テストを再実行し、Skills をコミット・push**

Run:
```bash
cd ~/Developer/Skills && scripts/test-link-skills.sh && git add docs/plans && git commit -q -m "docs: スキル棚卸しの実装計画

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" && git push -q -u origin chore/20260918-skills-inventory && git log --oneline main..HEAD
```
Expected: `OK` の後、main..HEAD に 6 コミット（移設、スクリプト、README、meeting-minutes、退避、計画）。

- [x] **Step 4: 最終報告に載せる事項を集める**

次を報告する。(1) Skills のブランチ名と main へのマージ待ち、(2) kyo1M-business と vaccinechoice_HH の未コミット変更一覧（`git status --short`）、(3) 村上さんが claude.ai で無効化・削除する 7 件の名前、(4) Claude Code と Codex の再起動後に `/meeting-minutes` の説明文が共通版になっていることの確認依頼、(5) `~/Developer/_archive/2026-09-18-codex-skills/` と `2026-09-18-vaccinechoice-agents-skills/` に退避したもの。
