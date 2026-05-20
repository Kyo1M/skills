---
name: html-slide-deck
description: ビジネス・コンサル向けの議論用スライド資料をHTML+SVGで作成するスキル。「スライドを作りたい」「資料化したい」「クライアント説明用に」「議論用の資料を」「PoC設計をスライドに」「提案資料を」などのリクエスト時に使用。continova v1デザインシステム(白地・Klein Blueアクセント・ミニマル+情報リッチ)に従い、議論先行で問いを整理してから16:9スクロール形式のHTMLスライドを生成する。社内議論用、クライアント説明用、提案資料、合意形成資料などに広く適用可能。
---

# HTML Slide Deck Creation

ビジネス・コンサルティング向けの議論用・提案用スライドをHTML+SVGで作成する。**議論先行で問いを整理してから実装する**ことで、見栄えだけでなく構造化された情報設計が伴ったスライドを生成する。

## このスキルが解決する課題

スライド作成では、フォーマットや見栄えに気を取られて中身の構造化が疎かになりがち。本スキルは:

- 議論先行で問いと構造を確定させてからHTMLに着手する
- 統一されたデザインシステム(continova v1)で品質を担保
- 9つの再利用可能なスライドパターンで設計効率化
- スクロール形式で議論中も全体俯瞰できるHTMLとして出力

## ワークフロー

```
Phase 1: 問いの整理      (議論)
  ↓
Phase 2: 全体構成の検討  (アウトライン)
  ↓
Phase 3: スライド設計    (パターン選択)
  ↓
Phase 4: HTML実装        (テンプレート + パターン適用)
```

**重要**: Phase 1-2を飛ばしてHTML実装に直行しない。ここを丁寧にやることが品質の8割を決める。

---

## Phase 1: 問いの整理

スライドを作る前に、以下を明確にする。ユーザーが提示していない場合は対話で引き出す。

### 確認すべき項目

1. **誰のための資料か** — クライアント / 社内 / 経営層 / チーム議論用
2. **意思決定の文脈** — 何を決めるための資料か
3. **答える問い / 答えない問い** — スコープを明示的に切る
4. **前提知識のレベル** — 専門用語をどこまで使えるか
5. **ボリューム感** — 8-10枚(議論用) / 12-15枚(報告用)

### 問いの再フレーミング

ユーザーが提示した問いが曖昧だったり、データ可用性の制約と整合しない場合、**より答えやすく意思決定に直結する問いに再フレーミング**する。

例:「投資全体のROIは?」という問いが、データ制約で答えられない場合
→「全体ROI(継続判断用)」と「限界ROI(運用判断用)」に分解
→ 後者にフォーカスする旨を冒頭スライドで明示

再フレーミングは資料の冒頭スライドで明示的に提示する。クライアントの当初の期待値とズレる可能性があるため、誠実に説明することで信頼を得られる。

---

## Phase 2: 全体構成の検討

各スライドを以下のフォーマットで箇条書きにし、ユーザーと合意する。

```
Slide N: [スライドタイトル]
  - Top message: [1-2文の結論]
  - 主役オブジェクト: [図表 / 表 / SVG / カード]
  - 情報密度: [低 / 中 / 高]
```

### 標準構成テンプレート

議論用資料は概ね以下のセクションで構成できる:

| セクション | 役割 | 推奨スライド数 |
|---|---|---|
| 目的・問いの再設計 | 何のための資料か、何に答えるか | 1 |
| 概念・基礎理解 | 共通言語の構築 | 1-2 |
| アプローチ選択 | 取りうる選択肢と採用理由 | 1-2 |
| 採用設計の詳細 | 選択肢の中身 | 2-3 |
| 限界・前提の明示 | 誠実さによる信頼獲得 | 1 |
| 発展・議論項目 | 次のアクション・論点 | 1 |

**目安**:議論用は8枚、報告用は12-15枚。

### スライド数を絞るコツ

- 似た情報を持つ複数スライドを統合する(各スライドの情報量が多くなっても良い)
- 装飾的なスライド(目次・章扉)を削る
- 複数の主張を持つスライドを「1 slide, 1 decision」原則で分割するのとは逆方向

---

## Phase 3: スライド設計(パターン選択)

各スライドで、以下から主役オブジェクトのパターンを選ぶ。

### 9つのスライドパターン

| # | パターン | 用途 |
|---|---|---|
| 01 | comparison-cards | 2-3要素の対比(全体ROI vs 限界ROI など) |
| 02 | dual-panel-diagram | 概念説明(理想 vs 落とし穴) |
| 03 | comparison-table | 選択肢比較(本命行をハイライト) |
| 04 | tradeoff-axis | 1次元軸上の位置づけ |
| 05 | tiered-options | 階層的・複数バリアントの提示 |
| 06 | three-category-cards | 3カテゴリの並列提示(共変量・要素) |
| 07 | estimand-comparison | 大カードでの選択肢提示(本命を強調) |
| 08 | step-flow-with-mockup | 手順フロー + 出力イメージ |
| 09 | limitation-matrix | 限界事項の3列マトリクス(項目/説明/対応) |
| 10 | phased-roadmap | フェーズ別ロードマップ + 議論項目 |

各パターンの詳細(HTML/CSS/SVGコード)は `references/slide-patterns.md` を参照。

### パターン選択の指針

- **3点以上並ぶ情報** → 箇条書きではなく three-category-cards / comparison-table
- **対比・トレードオフ** → comparison-cards / tradeoff-axis
- **時系列・フロー** → step-flow-with-mockup / phased-roadmap
- **限界・前提** → limitation-matrix(必ず「対応」列を入れて誠実さを示す)

---

## Phase 4: HTML実装

### 実装手順

1. `assets/template.html` を `/home/claude/<filename>.html` にコピー
2. デッキ全体のスライド数だけ `<section class="slide">` を増やす
3. 各スライドに `references/slide-patterns.md` のパターンHTMLを貼る
4. SVG主役オブジェクトを実装(パターン内のSVGコードを基に)
5. HTMLバリデーション(タグの開閉確認)
6. `/mnt/user-data/outputs/` にコピーし `present_files` で共有

### 検証コマンド

```bash
python3 -c "
from html.parser import HTMLParser
class V(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.errors = []
        self.void = {'br','hr','img','input','meta','link','rect','line','circle','path','polygon','text','use','marker','stop','polyline','ellipse'}
    def handle_starttag(self, tag, attrs):
        if tag not in self.void: self.stack.append(tag)
    def handle_endtag(self, tag):
        if tag in self.void: return
        if not self.stack: self.errors.append(f'unmatched </{tag}>')
        elif self.stack[-1] != tag: self.errors.append(f'mismatch <{self.stack[-1]}>/</{tag}>')
        else: self.stack.pop()
v = V()
with open('FILENAME.html') as f: v.feed(f.read())
print('errors:', v.errors[:5] if v.errors else 'none')
print('unclosed:', v.stack if v.stack else 'none')
"
```

---

## デザインシステム概要

**ベース**: continova v1 (詳細は `references/design-system.md`)

### 5つのデザイン原則

1. **One slide, one decision** — 1スライドに1つの認識変化・判断・合意事項
2. **Consulting calm, infographic richness** — ミニマルだが情報設計の豊かさ
3. **Klein Blue as signal** — `#002FA7` は推奨案・本命にだけ使用(視覚面積5-12%)
4. **Template consistency** — タイトル・余白・罫線のリズムは共通化
5. **Information design over decoration** — 装飾ではなく構造化された情報表現

### 主要トークン

| 用途 | 値 |
|---|---|
| アクセント | `--brand-klein: #002FA7` |
| 薄背景 | `--brand-blue-soft: #EAF1FF` |
| 本文 | `--ink: #111111` |
| サブカラー | `--stone: #2F3135` |
| 注釈 | `--pebble: #6F7175` |
| 罫線 | `--border-soft: #DDDDDD` |
| 淡色背景 | `--snow: #F6F5F2` |

### サイズ・余白

- スライド: **1672 x 941 px** (16:9固定)
- パディング: 上58px / 左右70px / 下38px
- タイトル: Hiragino Mincho ProN, 46px, 600
- トップメッセージ: 22px, 500, --stone

### Klein Blueの使い方

- 推奨案・本命の枠 (`border-color: var(--brand-klein)`)
- 重要数値・キーフレーズ
- 「本分析のスコープ」などのバッジ
- アクセント線(タイトル下のrule、左ボーダー)

**避けるべき**: 青い面を画面全体に広げない。複数の青ハイライトで意味を希釈しない。

---

## 出力形式

最終的に1ファイルのHTMLとして出力:

- 単一の `.html` ファイル(画像・CSS・JS全て埋め込み)
- スクロール形式(全スライドが縦に並ぶ)
- ブラウザで開けばすぐ見られる

### 環境別の出力先

| 環境 | 出力先 | 補足 |
|------|--------|------|
| **Claude.ai** (オリジナル) | `/mnt/user-data/outputs/<filename>.html` | `present_files` で共有 |
| **Claude Code (汎用)** | cwd 配下の任意パス（ユーザーが指定） | `open <path>` でローカル表示 |
| **Claude Code + `project-context-template`** | `docs/deliverables/yyyymmdd_<slug>-slides.html` | 後述「project-context-template での使用」参照 |

スクロール形式のメリット:
- 議論中に前後スライドを参照しやすい
- 全体構造が一覧できる
- スマホ・タブレットでも閲覧可能

---

## project-context-template での使用

[`project-context-template`](https://github.com/Kyo1M/project-context-template) 規約のリポジトリ（cwd の `AGENTS.md` で判定可能）で本 skill を使う場合は、以下の追加ルールに従う。

### 出力先と命名

- パス: `docs/deliverables/yyyymmdd_<slug>-slides.html`
- スラグは ASCII kebab-case
- 例: `docs/deliverables/20260530_onboarding-overview-slides.html`

### frontmatter（HTML コメント先頭埋め込み）

```html
<!--
---
type: deliverable
title: <日本語タイトル>
date: YYYY-MM-DD
status: active
topics: [<関連 topic>]
tags: []
derived_from: [docs/minutes/..., docs/decisions/...]   # 元になった議事録・決定事項
related: []
audience: client | internal | exec | team
format: slide
source_prompt: <生成プロンプトの要約>
---
-->
<!DOCTYPE html>
...
```

### Git ワークフロー

リポジトリの `AGENTS.md` の「Git 運用ルール」に従う:

1. `git rev-parse --abbrev-ref HEAD` で main 上か確認、main なら `deliverable/<yyyymmdd>-<slug>` ブランチへ
2. スライド生成 → HTML バリデーション
3. `npm run lint --prefix scripts` で frontmatter 検証
4. コミットメッセージ案をユーザーに提示 → 確認後 commit
5. `git push -u origin <branch>` → ユーザーへマージ/PR 確認

### コミットメッセージ例

```
[deliverable] Add <title> slides (YYYY-MM-DD)

derived_from:
  - docs/minutes/...
  - docs/decisions/...
```

---

## 自社デザインへのカスタマイズ

このスキルは `continova v1` デザインシステム（白地・Klein Blue アクセント・ミニマル + 情報リッチ）を前提とする。**自社ブランドに合わせて変更する場合**は以下を差し替える:

- `references/design-system.md` — カラートークン、フォント、余白、ロゴ規約
- `assets/template.html` — ベースの HTML テンプレート（CSS 変数・フォント・ヘッダー）
- `references/slide-patterns.md` — 9 パターンの色・アクセントの参照値

カスタマイズ手順例:

1. 自社のブランドガイド（カラー・フォント・ロゴ）を整理
2. `assets/template.html` の `:root` 内 CSS 変数（`--brand-klein`, `--ink`, `--snow` 等）を上書き
3. `references/design-system.md` を社内向けに書き直す
4. fork した `Kyo1M/skills` リポジトリで管理し、`~/.claude/skills/html-slide-deck` の symlink を自社版に向ける

スキル本体（Phase 1〜4 のワークフローやスライドパターン）はそのまま再利用可能。

---

## 留意事項

### やるべきこと

- Phase 1-2に時間を使う(全体時間の半分以上)
- 限界・前提を明示的にスライド化する(誠実さが信頼を生む)
- 議論項目スライドを必ず最後に置く
- ユーザーの分野知識をリスペクトしつつ、構造化に貢献する

### やってはいけないこと

- いきなりHTMLから書き始める
- 1スライドに複数の主張を詰め込む
- カードや箇条書きの反復だけで資料を構成する
- 青い面を広げすぎてKlein Blueの意味を弱める
- ダミーデータを本物のように見せる(必ず`X`, `¥ X,XXX`等のプレースホルダで)

---

## 参照ファイル

- `references/design-system.md` — continova v1の完全仕様(色・タイポ・余白・避けるべきこと)
- `references/slide-patterns.md` — 9つのスライドパターンの詳細HTMLコード
- `assets/template.html` — HTMLスタートテンプレート(ヘッダ・フッタ・基本CSS済み)
