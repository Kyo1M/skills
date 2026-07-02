---
name: daily-log
description: 今日の Claude Code / Codex セッションと Linear アクティビティを Markdown の振り返りとして ~/Daily/ に保存するスキル
---

# Daily Log Generator

今日（または指定日）の作業を Markdown 1 ファイルにまとめて `~/Daily/YYYY/MM/YYYY-MM-DD.md` に保存するスキル。`daily-flipbook` の簡素化・自分用再設計版。

## トリガー

- `/daily-log` で起動（今日分）
- `/daily-log 2026-04-10` で過去日分
- 「今日の振り返り作って」「デイリーログ生成」等の自然言語

## 入力ソース

| ソース | 取得方法 | 取得対象 |
|---|---|---|
| Claude Code セッション | `collect-claude.sh` (jq で `~/.claude/projects/**/*.jsonl` 解析) | ユーザメッセージ・ツール使用サマリ |
| Codex セッション | `collect-codex.sh` (jq で `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl` 解析) | ユーザメッセージ・ツール使用サマリ・cwd ベースのプロジェクト名 |
| Linear | `collect-linear.sh` (GraphQL + Keychain トークン) | 当日更新イシュー・自分のコメント |

将来: Notion / Obsidian を追加予定。

## 処理フロー

### Step 1: 日付確定

引数が `YYYY-MM-DD` 形式なら採用、なければ `date +%Y-%m-%d`。

### Step 2: 出力パス決定

```
OUTPUT_DIR="$HOME/Daily/$(echo $DATE | cut -d- -f1)/$(echo $DATE | cut -d- -f2)"
OUTPUT_FILE="$OUTPUT_DIR/$DATE.md"
RAW_DIR="$OUTPUT_DIR/.raw"
RAW_FILE="$RAW_DIR/$DATE.json"
```

既存ファイルがある場合: 手動実行ならユーザーに上書き確認、cron 実行なら黙って上書き。

### Step 3: データ収集

Skill ディレクトリ配下の 3 つの collector を呼び出す:

```bash
SKILL_DIR="$HOME/.claude/skills/daily-log"
"$SKILL_DIR/collect-claude.sh" "$DATE" > "$RAW_DIR/claude.json"
"$SKILL_DIR/collect-codex.sh"  "$DATE" > "$RAW_DIR/codex.json"  || echo '{"error":"codex unavailable"}'  > "$RAW_DIR/codex.json"
"$SKILL_DIR/collect-linear.sh" "$DATE" > "$RAW_DIR/linear.json" || echo '{"error":"linear unavailable"}' > "$RAW_DIR/linear.json"
```

- Codex collector は `~/.codex/sessions` が無い場合 `session_count: 0` で正常終了する
- Linear 側は失敗しても継続する（トークン未設定・ネットワーク不通等）

各 collector は同じ「ローカル日付の 0:00 〜 翌 0:00」の窓で動き、内部タイムスタンプ (UTC) で範囲フィルタするため、深夜 0 時を跨いだセッションも適切な日付に分類される。

### Step 4: Markdown 生成

`template.md` をベースに以下を埋める:

- `{{DATE}}` `{{WEEKDAY}}` `{{GENERATED_AT}}`
- `{{SESSION_COUNT}}` `{{LINEAR_COUNT}}`
- `{{SUMMARY}}` — 当日の主要トピック 3-5 行（Claude synthesis）
- `{{CLAUDE_SESSIONS}}` — プロジェクトごとに H3 + 箇条書き
- `{{CODEX_SESSIONS}}` — プロジェクトごとに H3 + 箇条書き。`event_count` / `first_ts` / `last_ts` から所要時間を算出し、`tool_counts` から `exec_command`（Bash 相当） / `apply_patch`（Edit 相当）等を要約
- `{{LINEAR_ISSUES}}` — 箇条書き（identifier + title + state）
- `{{LINEAR_NOTES}}` — イシューごとにメモ内容と、そこから読み取れる気づき・判断・次アクション。振り返りに有効な粒度で言語化されていれば原文抜粋を含めてよい
- `{{INSIGHTS}}` — 気づき・学び（Claude synthesis）
- `{{TODO}}` — 明日に持ち越すタスク（Claude synthesis）

synthesis が必要な部分は、対話セッションなら Claude 本体が直接生成、launchd からなら `claude -p` を呼んで生成する。

**Linear メモから気づきを作る方針**

- 原文抜粋はしてよいが、それに加えて読み取れる学び・判断・次のアクションを 1〜3 行添える
- 書籍メモ系（`MYTASK-185` 的なもの）は要点 + 「自分の仕事にどう効くか」の所感
- 決定・完了系（「加入した」等）は背景・判断理由・今後の留意点を推論で補う
- 推論が薄い項目は `{{INSIGHTS}}` には昇格させず、`{{LINEAR_NOTES}}` 内にとどめる

### Step 4.5: 深掘り質問（対話実行時のみ）

**手動 `/daily-log` 実行のときだけ** 実行する。launchd / `claude -p` ヘッドレスでは**絶対にやらない**（ユーザー不在のため）。

目的: ユーザー自身の言葉で気づきを言語化させ、Claude の推論だけでは掴めない当事者視点の学びを `{{INSIGHTS}}` に追記する。

手順:

1. Step 4 で生成した `{{INSIGHTS}}` のドラフトを先に提示する
2. ドラフトに対して、ユーザーの当事者性が必要な項目を **`AskUserQuestion`** で深掘り質問する（件数に上限なし。ただし価値の薄い質問は省く）
3. 質問の選び方:
   - Claude 側の推論が「たぶんこうだろう」止まりで、本人にしか答えられない箇所
   - 感情・判断理由・仮説の強度（「これは確信? それとも試し?」）
   - メモや行動ログだけでは埋まらない「なぜ今それをやったのか」
4. `AskUserQuestion` は 1 回の呼び出しで複数質問をまとめられるので、関連する論点はまとめて聞く
5. ユーザー回答を踏まえて `{{INSIGHTS}}` を書き換え、必要なら `{{TODO}}` も更新
6. ユーザー回答は原文のまま記録せず、気づきとして再構成する（ただし本人の表現は尊重する）

例:

```
Claude: 今日の気づきドラフトは以下です:
  1. macOS TCC の落とし穴 ...
  2. Linear 連携で振り返り密度が上がる ...

1点だけ確認させてください:
Q. MYTASK-122 の保険加入、決め手は "賠償範囲" と "価格" のどちらが支配的でしたか?
   これが分かると「次に契約系を検討するときのチェック順」として気づきに残せます。
```

質問が空振りする場合（当日が単純作業だけ等）はスキップしてよい。

### Step 5: ファイル書き出し

1. `OUTPUT_FILE` に Markdown を書く
2. `~/Daily/index.md` を更新（当日エントリを追加 / 既存なら置換）

### Step 6: 通知

- 手動実行: 出力パスをユーザーに伝える
- launchd 実行: `osascript -e 'display notification ...'` で通知

## 実装ファイル

- `SKILL.md` — この仕様書
- `template.md` — Markdown テンプレート（プレースホルダ付き）
- `collect-claude.sh` — Claude Code ログ収集（`~/.claude/projects/**/*.jsonl`）
- `collect-codex.sh` — Codex ログ収集（`~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl`）
- `collect-linear.sh` — Linear GraphQL 取得
- `daily-cron.sh` — launchd から呼ばれるオーケストレータ（`claude -p` 経由）
- `com.daily-log.plist` — launchd インストール用サンプル

## 注意事項

- 個人情報（API キー、パスワード、トークン）が raw データに含まれていたら除外
- `{{CLAUDE_SESSIONS}}` / `{{CODEX_SESSIONS}}` は多すぎる場合それぞれ 6 プロジェクトまで、重要度で選別
- 検証されていない成果を数字で表示しない
- Linear トークンは Keychain 保管（`security find-generic-password -a $USER -s linear-api-token -w`）
- Codex の `exec_command` は Bash 相当、`apply_patch` は Edit 相当として扱うが、生の名前を保持してプラットフォーム差を曖昧にしないことを優先する
