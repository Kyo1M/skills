#!/bin/bash
# daily-cron.sh - launchd / 手動実行両対応のオーケストレータ
#
# Usage:
#   ./daily-cron.sh              # 今日分
#   ./daily-cron.sh 2026-04-12   # 指定日
#
# Flow:
#   1. collect-claude.sh と collect-linear.sh で生データ収集
#   2. ~/Daily/YYYY/MM/.raw/YYYY-MM-DD.json に保存
#   3. claude -p でテンプレート + 生データから Markdown を synthesis
#   4. ~/Daily/YYYY/MM/YYYY-MM-DD.md に書き出し
#   5. index.md を更新
#   6. macOS 通知

set -euo pipefail

# Ensure claude CLI is findable (cmux bundled path + homebrew)
export PATH="$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin:/Applications/cmux.app/Contents/Resources/bin:$PATH"

DATE="${1:-$(date +%Y-%m-%d)}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DAILY_ROOT="$HOME/Daily"

YEAR=$(echo "$DATE" | cut -d- -f1)
MONTH=$(echo "$DATE" | cut -d- -f2)
OUT_DIR="$DAILY_ROOT/$YEAR/$MONTH"
RAW_DIR="$OUT_DIR/.raw"
OUT_FILE="$OUT_DIR/$DATE.md"
RAW_FILE="$RAW_DIR/$DATE.json"
CACHE_DIR="$DAILY_ROOT/.cache"
LOG_FILE="$CACHE_DIR/cron.log"

mkdir -p "$OUT_DIR" "$RAW_DIR" "$CACHE_DIR"

# Weekday (Japanese)
WEEKDAY_EN=$(date -j -f "%Y-%m-%d" "$DATE" "+%a" 2>/dev/null || echo "")
case "$WEEKDAY_EN" in
  Mon) WEEKDAY="月" ;;
  Tue) WEEKDAY="火" ;;
  Wed) WEEKDAY="水" ;;
  Thu) WEEKDAY="木" ;;
  Fri) WEEKDAY="金" ;;
  Sat) WEEKDAY="土" ;;
  Sun) WEEKDAY="日" ;;
  *) WEEKDAY="?" ;;
esac
GENERATED_AT=$(date "+%Y-%m-%d %H:%M:%S")

echo "=== [$GENERATED_AT] daily-log generating $DATE ==="

# Step 1-2: collect
CLAUDE_JSON=$("$SCRIPT_DIR/collect-claude.sh" "$DATE" 2>/dev/null || echo '{"error":"collect-claude failed","sessions":[]}')
CODEX_JSON=$("$SCRIPT_DIR/collect-codex.sh"  "$DATE" 2>/dev/null || echo '{"error":"collect-codex failed","sessions":[]}')
LINEAR_JSON=$("$SCRIPT_DIR/collect-linear.sh" "$DATE" 2>/dev/null || echo '{"error":"collect-linear failed","issues":[],"comments":[]}')

SESSION_COUNT=$(echo "$CLAUDE_JSON" | jq '.session_count // (.sessions | length // 0)')
CODEX_SESSION_COUNT=$(echo "$CODEX_JSON" | jq '.session_count // (.sessions | length // 0)')
LINEAR_ISSUE_COUNT=$(echo "$LINEAR_JSON" | jq '.issues | length')

COMBINED=$(jq -n \
  --arg date "$DATE" \
  --arg weekday "$WEEKDAY" \
  --arg generated_at "$GENERATED_AT" \
  --argjson claude "$CLAUDE_JSON" \
  --argjson codex "$CODEX_JSON" \
  --argjson linear "$LINEAR_JSON" \
  '{date: $date, weekday: $weekday, generated_at: $generated_at, claude: $claude, codex: $codex, linear: $linear}')

echo "$COMBINED" > "$RAW_FILE"
echo "raw saved: $RAW_FILE (claude_sessions=$SESSION_COUNT, codex_sessions=$CODEX_SESSION_COUNT, linear_issues=$LINEAR_ISSUE_COUNT)"

# Step 3: synthesis via claude -p
if ! command -v claude &>/dev/null; then
  echo "WARNING: claude CLI not found. Raw data saved but Markdown not generated."
  echo "Run the /daily-log skill interactively to complete."
  exit 0
fi

TEMPLATE_CONTENT=$(cat "$SCRIPT_DIR/template.md")

PROMPT=$(cat <<EOF
以下は $DATE ($WEEKDAY 曜日) の作業データです。このデータを読んで、template.md の骨組みを埋めた完成版の Markdown を生成し、$OUT_FILE に書き出してください。

## 生データ (JSON)

$(echo "$COMBINED" | head -c 60000)

## テンプレート (template.md)

\`\`\`markdown
$TEMPLATE_CONTENT
\`\`\`

## 指示

- プレースホルダ ({{DATE}} 等) を適切な値で置換して完成版 Markdown を作る
- {{DATE}} = $DATE
- {{WEEKDAY}} = $WEEKDAY
- {{GENERATED_AT}} = $GENERATED_AT
- {{SESSION_COUNT}} = $SESSION_COUNT
- {{CODEX_SESSION_COUNT}} = $CODEX_SESSION_COUNT
- {{LINEAR_COUNT}} = $LINEAR_ISSUE_COUNT
- {{SUMMARY}} は claude / codex / linear の 3 ソースから主要トピックを 3-5 行で要約
- {{CLAUDE_SESSIONS}} はプロジェクトごとに H3 見出し + 箇条書き。最大 6 プロジェクトまで
- {{CODEX_SESSIONS}} は Codex セッションを cwd ベースのプロジェクト名で H3 + 箇条書き。`event_count` / `first_ts` / `last_ts` から所要時間を出し、`tool_counts` の `exec_command` (Bash 相当) / `apply_patch` (Edit 相当) などを要約に使う。0 件なら「(なし)」
- {{LINEAR_ISSUES}} は identifier + title + state を箇条書き。0件なら「(なし)」
- {{LINEAR_NOTES}} は自分のコメントをイシュー単位でまとめる。原文抜粋はしてよいが、それに加えて読み取れる気づき・判断・次のアクションを 1〜3 行添える（振り返りに有効な粒度で言語化されていれば OK）。書籍メモなら要点 + 「自分の仕事にどう効くか」、決定・完了系なら背景・判断理由・今後の留意点を推論で補う。0件なら「(なし)」
- {{INSIGHTS}} は学びや気づきを 2-4 点。Claude セッションと Linear メモの両方から抽出する
- {{TODO}} は翌日に持ち越すタスク（未完了イシュー等から）
- 図が有益な箇所は mermaid コードブロックを使ってよい
- 検証されていない成果を数字で表示しない
- 最終出力先: $OUT_FILE （Write ツールで書き出す）
- $OUT_FILE に書き出したら、$DAILY_ROOT/index.md に当日分のエントリを追加または更新する:
  - フォーマット: \`- [$DATE ($WEEKDAY)]($YEAR/$MONTH/$DATE.md) — 一行サマリー\`
  - 日付降順で並べる
  - index.md が存在しない場合は新規作成（見出し "# Daily Log Index" を付ける）
EOF
)

echo "Invoking claude -p..."
if claude -p "$PROMPT" --permission-mode acceptEdits 2>&1 | tee -a "$LOG_FILE"; then
  if [ -f "$OUT_FILE" ]; then
    echo "Generated: $OUT_FILE"
    osascript -e "display notification \"📓 $DATE の daily-log を生成しました\" with title \"Daily Log\" sound name \"Tink\"" 2>/dev/null || true
  else
    echo "WARNING: claude -p returned but $OUT_FILE was not written"
    exit 1
  fi
else
  echo "ERROR: claude -p failed"
  exit 1
fi
