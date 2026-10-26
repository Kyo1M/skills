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
- claude.ai には自作 skill を置かない。claude.ai で有効な skill は `~/.claude/skills/synced/` に同期され、Claude Code に `anthropic-skills:<name>` として見える（Anthropic 製の docx・pptx 等もここに入る）。自作を上げると同名の別実体になるので、スマホや Chrome から使いたい skill が出たら、このリポジトリの正本を上げ直したうえで下の「claude.ai 専用」に記す。
- skill が見えないときは symlink 切れを疑う: `scripts/link-skills.sh --check`
- 使わなくなった skill は `archive/` へ `git mv` する（symlink の対象外。退避理由は `archive/README.md`）。

## 新規スキル追加手順

```bash
NAME=<skill-name>
mkdir -p ~/Developer/Skills/$NAME
$EDITOR ~/Developer/Skills/$NAME/SKILL.md
~/Developer/Skills/scripts/link-skills.sh      # ~/.claude/skills と ~/.agents/skills に symlink
```

Claude Code と Codex を再起動して認識を確認したら、`git add` & commit し、下の管理表に追記する。`scripts/link-skills.sh --check` が管理表との食い違いを報告する。`~/Developer/Skills` の作業ツリーが symlink の参照先なので、作業はブランチを切った worktree で行い、`~/Developer/Skills` は main のままにする（別のブランチに切り替えると、そのブランチに無い skill やグローバル CLAUDE.md が読み込む `writing-core.md` が消える）。

## 定期点検

月初に `scripts/link-skills.sh --check` を 1 回走らせ、壊れたリンク・未配置・同名の別実体（claude.ai から同期された同名 skill を含む）・管理表との食い違いをゼロにする。

`table-definition`・`metric-definition` の既定の型（`references/*-schema.md`）は、[project-context-template](https://github.com/Kyo1M/project-context-template) の `docs/guide/data-definition-guide.md` 2・3 章の写し。型はテンプレートのガイドを先に直してから写し、`scripts/check-schema-copies.sh` で一致を確かめる。

## 管理対象スキル（Skills リポジトリ管理）

| skill | 説明 |
|-------|------|
| [grill-me](./grill-me/SKILL.md) | 批判的壁打ち。前提を疑い・論点ツリーを整理し・ヌケモレと反証を指摘する。アイデア壁打ちモード・プラン精査モード（終了時に論点整理 md を残す）と、率直な評価を往復なしで返すモード（一度で評価モード）の 3 モード |
| [brainstorming](./brainstorming/SKILL.md) | 対話で要件と設計を固め、`docs/superpowers/specs/` に設計書を書いて writing-plans へ渡す。superpowers 6.4.1（MIT、Jesse Vincent）から取り込み、他の superpowers skill への参照を外した |
| [writing-plans](./writing-plans/SKILL.md) | 設計書から実装計画を作り、実行方法（サブエージェント／このセッション）を選んでもらう。superpowers 6.4.1（MIT）から取り込み |
| [deck-outline](./deck-outline/SKILL.md) | 資料・スライドの「構成」を実装前に実文言の Markdown で設計する。入力メモのインベントリ化とトレーサビリティで、依頼者のメモの黙った省略を防ぐ。書き方原則の正本（`references/writing-principles.md`）と要約（常時適用の `writing-core.md`、資料・レポート用の `principles-digest.md`）を持ち、手直しされた最終版から原則を学ぶ手順もここにある |
| [html-slide-deck](./html-slide-deck/SKILL.md) | 事業用スライド DS（白地・明朝タイトル・Klein Blue、1920×1080）で `.dc.html`（deck-stage・Claude Design 互換）を生成。20 型・アイコン対応表・機械チェック・セルフレビュー。deck-outline の構成 md を入力に Phase 3 から。ルール正本は `html-slide-deck/references/design-system.md`。旧 continova v1 は `references/legacy/` |
| [deck-critique](./deck-critique/SKILL.md) | 資料（構成 md / 完成 `.dc.html`）を作成とは別の目で批評・推敲する。指摘リスト+修正案を返す（勝手に直さない） |
| [meeting-minutes](./meeting-minutes/SKILL.md) | 規約駆動の議事録作成。対象 repo の CLAUDE.md / AGENTS.md と運用ガイドから出力先・命名・スキーマ・型・承認レベル・git 運用を読み取って適応する。規約にタスク台帳があれば、台帳追記と会議で報告された着手・完了の反映・重い決定だけの決定案・llms.txt・wiki 差分まで 1 回で行う（ID・状態・確認項目はガイドに従う。GitHub Issue 連携を定める repo では前回からの進捗とタスク登録の下書きも。Issue は読むだけ、`references/github-issue-sync.md`）。質問は日付と人物が分からないときと保存前の確認 1 回だけ |
| [table-definition](./table-definition/SKILL.md) | 規約駆動のテーブル定義整理。定義書（Excel・DDL・ヘッダ）や口頭説明から 1 論理テーブル 1 YAML（粒度・キー・列・関係・注意点）と wiki「データ」表を作る。置き場が無い repo では `docs/tables/` の新設を承認後に足す。値・ID・件数は書かない。型の既定は `references/table-schema.md` |
| [metric-definition](./metric-definition/SKILL.md) | 規約駆動の指標の定義整理。既存の SQL・指標定義書・分析設計や口頭説明から 1 指標 1 YAML（式・分子と分母・母集団・束ね方・区分・突き合わせの結果）と wiki「用語」表の行を作る。SQL ごとの取り方の割れを並べて正を決めてもらう。置き場が無い repo では `docs/metrics/` の新設を承認後に足す。値・ID・件数は書かない。型の既定は `references/metric-schema.md` |
| [analysis-plan](./analysis-plan/SKILL.md) | 規約駆動の分析計画。仮説を並べる前に、目的（誰のどの判断に使うか）→ 指標の定義 → 指標ごとの現状把握（概要・具体例・推移・関係。結論は出さない）→ 目的ごとの仮説検証（検証方法の種類と、当たったら・外れたらで変わること）の順で計画 md を組む。計画の行が analysis-notebook の問いになる。1 回の分析ごとの分析設計 md（目的と想定アウトプット・基本情報・要素の見方・レポートの目次・期限）も作り、レビューは直す前の版をステージして差分で見せる。雛形は `references/plan-template.md`・`references/design-template.md`、3 つの analysis skill に共通する考え方は `references/analysis-principles.md` |
| [analysis-notebook](./analysis-notebook/SKILL.md) | 規約駆動の問い駆動の分析 notebook。問い定義 → 最小分析設計 → 実装 → 実行・検証 → 結論要約で、各問いに回答／根拠／確度／限界／次アクションを置く。形式は規約で選び、既定は marimo（`references/marimo.md`・`references/jupytext.md`）。marimo の出力は `scripts/read_session.py` で読む |
| [analysis-report](./analysis-report/SKILL.md) | 規約駆動の分析レポート（md が正本）。notebook のまとめ表と回答を一次ソースにし、答えていないことを補わない。読み手の型はクライアント向け・研究者向け（`references/reader-*.md`）。notebook の外に出してよい範囲を規約で確かめる |
| [understand](./understand/SKILL.md) | 完成した資料・分析を、ユーザーが説明できるところまで対話で理解させる。質問と想定回答の組の teach-back で確かめ、説明台本・用語と数式・FAQ を explainer として残す。共有前の理解の確認にも使う |
| [docx-export](./docx-export/SKILL.md) | md を画像を埋め込んだ docx にする（pandoc、`scripts/md_to_docx.py`）。frontmatter を除き、表に罫線を付け、見出し・表・画像の数を照合する。求められれば Google ドキュメントにして Drive のフォルダに置き、ページ分けなしにする（`scripts/docx_to_gdocs.py`。認証は gog か任意のトークンのコマンド、作り直しは同じ URL に差し替え） |
| [daily-log](./daily-log/SKILL.md) | 当日の Claude Code / Codex / Linear 活動を `~/Daily/` に保存する。launchd の plist はマシン固有の絶対パスを含むため移植時は要書き換え |
| [worklog](./worklog/SKILL.md) | Claude Code / Codex のログからプロジェクト・案件ごとの稼働時間をバーで見せ、作業内容を要約する。数字は `worklog` CLI(`~/Developer/claude-worklog`、GitHub Kyo1M/claude-worklog)が出し、skill は素材を読んで要約・稼働報告の下書きを書く |

## リポジトリ管理の業務・案件スキル（場所だけ記す）

| リポジトリ | 場所 | skill |
|---|---|---|
| kyo1M-business | `.agents/skills/`（実体、git 管理）。`.claude/skills/` は symlink | business-planning, contact-profile-drafter, document-drafter, git-commit, hypothesis-map, project-update-from-meetings, weekly-review |
| writing-articles | 同上 | article-pipeline（note・Zenn 記事の企画→公開準備） |
| continova-hp | 同上 | continova-business-card（名刺を HTML → Chrome PDF で出力） |
| 非公開の案件リポジトリ | `.agents/skills/`（実体、git 管理外）。`.claude/skills/` は symlink | 各リポジトリの AGENTS.md に記す |

## 第三者製（管理外。場所と出所だけ記す）

| skill | 場所 | 出所 |
|---|---|---|
| gog | `~/.claude/skills/gog`（実体） | steipete/gogcli |
| agmsg | `~/.agents/skills/agmsg` | 導入物（`VERSION`・`uninstall.sh` を持つ） |
| orca-cli, orchestration | `~/.agents/skills/` | stablyai/orca（同上） |

## claude.ai 専用

なし。自作 7 件（brutal-advisor、hypothesis-map、html-slide-deck、kpi-structure、meeting-minutes、note-writing-assistant、project-overview）は claude.ai 側で無効化済み（2026-09-29、`synced/` から消えたことを `--check` で確認）。ローカルに無かった 3 件の控えは `archive/claude-ai-skills/`。

## スキル間の使い分け（3 レーン）

**資料作成レーン**:

```
(論点が固まっていなければ) grill-me → deck-outline（構成 md） → deck-critique（構成 md の批評） → pptx（構成 md から Codex・Claude で直接作るか、html-slide-deck で `.dc.html` にして Claude Design で pptx 化。`.dc.html` は deck-critique で再批評できる）
```

初稿の文章ルールは `deck-outline/references/principles-digest.md`（書き方原則の要約）。

**分析レーン**:

```
(問いが固まっていなければ) grill-me → table-definition・metric-definition（使うテーブルと指標の定義を YAML に。分析設計の前でも途中でもよい） → analysis-plan（目的・指標・現状把握・仮説検証の計画と、1 回の分析ごとの分析設計。設計は合意してから分析に入る） → analysis-notebook（問い駆動の notebook。データを見て設計を直しながら） → analysis-report（md のレポート） → docx-export（docx。求められれば Google ドキュメントにして Drive に置く）
共有・説明の前に understand（teach-back と explainer）
```

**設計・実装レーン**:

```
軽い壁打ちなら最初から brainstorming → docs/superpowers/specs/ に設計書 → writing-plans → 実装
深掘りが要るときは grill-me（論点整理 md）→ brainstorming に接続
一度で率直な評価だけ欲しいときは grill-me の一度で評価モード
```

書き方原則の正本は `deck-outline/references/writing-principles.md`（ルールと理由）。原則ごとの実例と経緯は `deck-outline/references/tone-examples.md`。要約は 2 つで、資料以外の文章にも常に効く原則は `writing-core.md`（グローバル `~/.claude/CLAUDE.md` が `@` で読み込み、`~/.codex/AGENTS.md` はこのファイルへの symlink）、資料・レポートの制作で引く原則は `principles-digest.md`。新しい書き方フィードバックは正本・tone-examples・principles-digest に必ず反映し、常時適用の原則が変わるときだけ writing-core も直す。

## 注意

- 機密情報（API キー・トークン）は SKILL 内にハードコードしない。Keychain 等から参照する。
- `~/.claude/skills/` や `~/.agents/skills/` に実体ディレクトリを作らない。`scripts/link-skills.sh` は実体があると上書きせず skip として報告する。
