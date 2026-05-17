---
name: meeting-minutes
description: project-context-template リポジトリ専用の議事録作成スキル。docs/minutes/_drafts/ の議事メモから対話を通じて内容を補完し、docs/minutes/ の正式議事録 + docs/decisions/ / tasks/ への派生抽出までを一気通貫で行う。「議事録を作成」「議事録化して」「議事メモを整えて」「ミーティングメモをまとめて」等のリクエスト時に起動。
---

# meeting-minutes — project-context 議事録作成スキル

`project-context-template`（および同テンプレから生成されたコンテキストリポジトリ）専用の議事録作成スキル。`_drafts/` の議事メモを整形して `docs/minutes/` 配下に正式議事録を生成し、決定事項とアクションアイテムを派生抽出する。

## 前提

このスキルは **次の規約を持つリポジトリでのみ動作** する想定:

- `AGENTS.md` がリポジトリルートに存在
- `docs/minutes/_drafts/` と `docs/minutes/` ディレクトリ構造
- ファイル命名規約 `yyyymmdd_<kebab-slug>.md`
- frontmatter スキーマ（`type: minutes` / `title` / `date` / `status` / `topics` / `attendees` / `meeting_type` / `derived_from` 等）
- 「Git 運用ルール」（main 直接編集禁止、ブランチ運用、コミットメッセージ確認）

判定方法: cwd の `AGENTS.md` を読み、ヘッダや本文に "project-context" や上記ディレクトリ構造に関する記述があるかで判定する。当てはまらない場合は「このスキルは project-context-template 規約のリポジトリ専用です」と明示して中断する。

## ワークフロー全体

```
Step 1: ブランチ確認・切替
   ↓
Step 2: 入力収集（_drafts のメモ + 任意で transcript）
   ↓
Step 3: 内容分析 + 対話質問（2〜3 ラウンド）
   ↓
Step 4: 正式議事録の生成（docs/minutes/yyyymmdd_<slug>.md）
   ↓
Step 5: 決定事項の派生抽出ドラフト（docs/decisions/）
   ↓
Step 6: アクションアイテムの派生抽出ドラフト（tasks/ or GitHub Issues 提案）
   ↓
Step 7: lint + コミットメッセージ案 → ユーザー確認 → commit
   ↓
Step 8: push 提案
```

---

## Step 1: ブランチ確認・切替

```bash
git rev-parse --abbrev-ref HEAD
```

- `main` 上にいる場合: `git pull --ff-only` を実行し、`minutes/<yyyymmdd>-<slug>` 形式のブランチ名を提案。`<slug>` は対象議事メモのスラグを流用。
  - 例: 入力が `docs/minutes/_drafts/20260517_onboarding-kickoff-memo.md` → ブランチ `minutes/20260517-onboarding-kickoff`
  - `git checkout -b minutes/<yyyymmdd>-<slug>`
- `main` 以外のブランチにいる場合: そのまま続行。

## Step 2: 入力収集

1. `docs/minutes/_drafts/*.md` をリストアップ
2. ユーザーが対象を明示していなければ、選んでもらう（複数候補あり時）
3. 対象メモを Read
4. 同じスラグ + `-transcript.txt` または `-transcript.md` が `_drafts/` にあれば併読
5. `recording:` パスがあれば本文に注記（再生は行わない）

## Step 3: 内容分析と対話質問

メモ内容を以下の観点で分析し、**対話質問でユーザーから補完情報を引き出す**。一度に 3〜4 項目、合計 2〜3 ラウンドが目安。

### 質問の観点

**議論の深堀り**
- 「〇〇という結論になった理由・背景は？」
- 「他に出た意見や反論はありましたか？」
- 「〇〇さんの反応はどうでしたか？」
- 「この議題で特に議論が盛り上がった点は？」

**決定事項の明確化**
- 「これは決定事項ですか？それとも検討中ですか？」
- 「誰が最終的に決めましたか？」
- 「いくつか案があったと思いますが、なぜこの案に決まりましたか？」

**文脈・前提**
- 「『〇〇の件』など曖昧な記述の具体化」
- 「この話の発端・きっかけは？」
- 「前回からの続きの話ですか？新規の話題ですか？」

**アクションの確認**
- 「担当者と期限は決まっていますか？」
- 「このタスクの完了条件は何ですか？」
- 「他に宿題として残ったことはありますか？」

**抜け漏れの確認**
- 「他に話した議題はありましたか？」
- 「メモに残っていないが印象に残っている発言はありますか？」

### 進め方

- 重要な議題から順に深堀り
- 「覚えていない」「特にない」も有効な回答として受け入れる
- 尋問にならないよう配慮、各ラウンドで「ありがとうございます。続けて〜」のように受ける

### 質問例

```
いくつか確認させてください:

1. トライブ分析で「原体験を入れてほしい」という話がありましたが、富岡さんはどのように回答されましたか？対応する方向ですか？
2. 「10 個という数に意味はない」という指摘に対して、具体的にどう見直す方向になりましたか？
3. POS レジの不具合について、いつ頃から発生していた問題ですか？影響範囲などの話はありましたか？
4. 他に話した議題や、印象に残っているやりとりはありますか？
```

## Step 4: 正式議事録の生成

パス: `docs/minutes/yyyymmdd_<slug>.md`

### frontmatter

```yaml
---
type: minutes
title: <日本語タイトル>
date: YYYY-MM-DD
status: active
topics: [<推測 or ユーザー確認>]
tags: []
derived_from: [docs/minutes/_drafts/yyyymmdd_<slug>-memo.md]
related: []
attendees: [<名前1>, <名前2>, ...]
meeting_type: kickoff | review | sync | retrospective | external | adhoc
# recording: <_drafts/...>     # 任意
# transcript: <_drafts/...>    # 任意
---
```

不明な項目:
- `attendees:` が不明 → `["要確認"]` で残し本文末尾に「※ 参加者: 要確認」と注記
- `meeting_type:` が不明 → `adhoc` で仮置き、本文に「※ meeting_type 要確認」
- `topics:` が不明 → 議題から推測してユーザー確認

### 本文セクション構成

```markdown
# <日本語タイトル>

## 要約

[3〜5 文で要点をまとめる。主な議題と結論、重要な決定事項、全体の方向性]

## 議事メモ（詳細）

### <議題1>

- [元のメモを構造化]
- [質問で得た補足情報]

### <議題2>

- ...

## ネクストアクション

| 担当者 | アクション | 期限 |
|--------|-----------|------|
| 〇〇 | [タスク内容] | YYYY-MM-DD |
| 未定 | [タスク内容] | 未定 |

## 次回予定（任意）

- 日時: YYYY-MM-DD HH:MM
- 議題: ...
```

不明な箇所は空欄や「未定」「要確認」のまま残す。

## Step 5: 決定事項の派生抽出

議事録の中から **決定事項を検出** し、`docs/decisions/yyyymmdd_<slug>.md` 形式でドラフトを **提案**（commit 前にユーザーレビュー）。

### 判定基準

「決まった」「採用する」「これでいく」等の合意・確定表現を含む箇所を候補とする。検討中のものは対象外。

### ファイル雛形

パス例: `docs/decisions/20260517_onboarding-tech-stack.md`

```markdown
---
type: decision
title: <決定の日本語タイトル>
date: YYYY-MM-DD
status: active
topics: [<議事録と同じ topics>]
tags: []
derived_from: [docs/minutes/yyyymmdd_<slug>.md]
related: []
drivers: []
alternatives_considered: []
---

# <決定の日本語タイトル>

## Context
（なぜ判断が必要になったか、背景）

## Decision
（何を決めたか）

## Consequences
（この判断によって生じる帰結）

## Alternatives Considered
（検討した別案と却下理由）
```

複数の決定があれば複数ファイルを作る。**作成前にユーザーに「以下を decisions/ ドラフトとして作成して良いですか？」と一覧を提示し確認を取る。**

## Step 6: アクションアイテムの派生抽出

ネクストアクション表の各行を以下の基準で振り分け:

### `tasks/` ファイル化（重い/議論を伴う）

判定基準:
- 1 日以上かかる
- 複数人が関与する
- 設計判断や調査を含む

パス例: `tasks/20260517_setup-nextjs-foundation.md`

```markdown
---
type: task
title: <タスクの日本語タイトル>
date: YYYY-MM-DD
status: todo
topics: [<議事録と同じ topics>]
tags: []
derived_from: [docs/minutes/yyyymmdd_<slug>.md]
related: []
assignee: <名前 or "未定">
due: YYYY-MM-DD
# priority: high | mid | low
# parent_topic: <slug>
---

# <タスクの日本語タイトル>

## 目的
## 完了条件
## メモ
```

### GitHub Issues 登録を提案（細粒度の日常タスク）

- 「メール送る」「ライセンス更新」「設定変える」等の単純タスク
- `gh issue create` のドラフトコマンドを提示して、ユーザーが実行する形にする

両カテゴリも、**作成/提案前に一覧を提示してユーザー確認**。

## Step 7: lint + commit

### lint

```bash
npm run lint --prefix scripts
```

失敗したら frontmatter を修正してから次へ。

### コミットメッセージ案

`git status` / `git diff --cached` を確認し、以下フォーマットで案を提示してユーザー確認を取る。

```
[minutes] Add <title> (YYYY-MM-DD)

derived_from:
  - docs/minutes/_drafts/yyyymmdd_<slug>-memo.md

新規ファイル:
  - docs/minutes/yyyymmdd_<slug>.md
  - docs/decisions/yyyymmdd_<decision-slug>.md (派生)
  - tasks/yyyymmdd_<task-slug>.md (派生)
```

ユーザー承認後に `git commit`。

## Step 8: push 提案

最初の commit:

```bash
git push -u origin minutes/<yyyymmdd>-<slug>
```

ユーザーに「main にマージしますか？ PR を作りますか？」と確認し、明示的依頼があるまでマージしない。

---

## 注意事項

- 質問は「会話を思い出してもらう」ためのもの。尋問にならないよう配慮
- 元のメモの内容は **削除せず**、補足情報を追記する形で充実させる
- 不明な項目は空欄（`______`）または「要確認」と記載
- 担当者・期限が未定のアクションも表に含め「未定」と記載
- 決定事項・タスクの **派生抽出は必ず人間レビュー必須**。AI が勝手に decisions/ や tasks/ を確定 commit しない
- 派生抽出に確信が持てない場合は、議事録ファイルの末尾に「派生候補（要確認）」セクションを設け、ユーザーに振り分けを委ねるオプションもとる
