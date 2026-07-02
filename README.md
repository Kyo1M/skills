# skills

Claude Code 用に自作した Skill を管理するリポジトリ。

## 構成

- 実体: `~/Developer/Skills/<name>/SKILL.md`
- 参照: `~/.claude/skills/<name>` から symlink で参照

Claude Code は `~/.claude/skills/` 配下を読むため、本リポジトリのスキルは symlink 経由で認識させる。
リポジトリを移動すると symlink が切れる(2026-06 に発生)。スキルが見えないときは `test -f ~/.claude/skills/<name>/SKILL.md` で確認する。

## 新規スキル追加手順

```bash
NAME=<skill-name>
mkdir -p ~/Developer/Skills/$NAME
$EDITOR ~/Developer/Skills/$NAME/SKILL.md
ln -s ~/Developer/Skills/$NAME ~/.claude/skills/$NAME
```

Claude Code を再起動して認識を確認したら、リポジトリ側で `git add` & commit し、本 README の管理表に追記する。

## 管理対象スキル

| skill | 説明 |
|-------|------|
| [grill-me](./grill-me/SKILL.md) | 批判的壁打ち。前提を疑い・論点ツリーを整理し・ヌケモレと反証を指摘する。アイデア壁打ちモードとプラン精査モードの 2 モード。終了時に論点整理 md を残す |
| [deck-outline](./deck-outline/SKILL.md) | 資料・スライドの「構成」を実装前に実文言の Markdown で設計する。入力メモのインベントリ化とトレーサビリティで、依頼者のメモの黙った省略を防ぐ。書き方原則の正本は `deck-outline/references/writing-principles.md` |
| [html-slide-deck](./html-slide-deck/SKILL.md) | 議論用 HTML+SVG スライド作成。continova v1 デザインシステム・14 パターン・10 観点セルフレビュー。deck-outline の構成 md を入力に Phase 3 から始める |
| [deck-critique](./deck-critique/SKILL.md) | 資料(構成 md / 完成 HTML)を作成とは別の目で批評・推敲する。ストーリー一貫性・日本語の自然さ・1 ページ 1 決定・元メモからの脱落を検査し、指摘リスト+修正案を返す(勝手に直さない) |
| [meeting-minutes](./meeting-minutes/SKILL.md) | 規約駆動の議事録作成。対象 repo の CLAUDE.md / AGENTS.md から出力先・命名・スキーマを読み取って適応し、決定事項・タスクの派生抽出まで行う |
| [spec-to-readable-html](./spec-to-readable-html/SKILL.md) | 仕様書 Markdown を要約・図解つきの可読 HTML に変換する |
| [article-pipeline](./article-pipeline/SKILL.md) | note・Zenn 記事を企画→公開準備の 7 フェーズで伴走する。`writing-articles` リポジトリ専用 |
| [empirical-prompt-tuning](./empirical-prompt-tuning/SKILL.md) | skill やプロンプトを実行者に実際に動かして両面評価(成功・失敗)で反復改善する。新規 skill を数回実戦投入したらこれで改善する |
| [daily-log](./daily-log/SKILL.md) | 当日の Claude Code / Codex / Linear 活動を `~/Daily/` に保存する。launchd の plist はマシン固有の絶対パスを含むため移植時は要書き換え |
| [continova-business-card](./continova-business-card/SKILL.md) | continova 名刺を HTML → Chrome PDF で出力する。continova-hp プロジェクト専用 |

### project-private スキル(gitignore)

`vac-*/` はワクチン分析プロジェクト(vaccinechoice_HH)専用の限定公開スキル。本リポジトリに実体を置くが gitignore しており、プロジェクト側から symlink / 同期して使う。グローバル(`~/.claude/skills/`)には露出しない。

### 管理外

`~/.claude/skills/gog` は第三者製(steipete/gogcli 由来)のため本リポジトリでは管理しない。

## スキル間の使い分け(資料作成パイプライン)

```
grill-me(壁打ち・論点整理) → deck-outline(構成 md) → html-slide-deck / Claude Design(実装) → deck-critique(批評)
```

書き方原則の正本は `deck-outline/references/writing-principles.md`。要約はグローバル `~/.claude/CLAUDE.md` に常設。新しい書き方フィードバックは両方に反映する。

## 注意

- 機密情報(API キー・トークン)は SKILL 内にハードコードしない。Keychain 等から参照する。
- 既存スキルと同名の symlink は作れない(`File exists`)。`ls ~/.claude/skills/` で事前確認すること。
