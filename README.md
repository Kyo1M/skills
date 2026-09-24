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
| [brainstorming](./brainstorming/SKILL.md) | 対話で要件と設計を固め、`docs/superpowers/specs/` に設計書を書いて writing-plans へ渡す。superpowers 6.4.1（MIT、Jesse Vincent）から取り込み、他の superpowers skill への参照を外した |
| [writing-plans](./writing-plans/SKILL.md) | 設計書から実装計画を作り、実行方法（サブエージェント／このセッション）を選んでもらう。superpowers 6.4.1（MIT）から取り込み |
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
