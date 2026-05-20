---
name: article-pipeline
description: note・Zenn 記事を企画から公開準備まで伴走するスキル。memos/ のネタ整理、構成作り、執筆、クリティカルなレビュー、codex CLI での画像生成、公開準備までをフェーズ単位で進める。ユーザーが「記事を書きたい」「ネタを整理して」「記事の構成を考えて」「下書きをレビューして」「推敲して」「記事の画像を作って」と言ったときに使用。writing-articles リポジトリでの作業を想定。
---

# 記事作成パイプラインスキル

note・Zenn 向け記事を、**企画 → 構成 → 執筆 → 推敲 → 画像 → 公開準備**の 6 フェーズで伴走する。

## 対象ディレクトリ

`writing-articles` リポジトリで作業する前提。

- `memos/` — ネタ（テーマごと 1 ファイル）
- `drafts/` — 執筆中の記事
- `published/` — 公開済み記事
- `assets/<slug>/` — 記事ごとの画像
- `templates/` — `memo.md` / `article.md` のひな型

## 進め方の原則

- **フェーズは独立して呼べる**。「構成だけ」「推敲だけ」「画像だけ」も可。ユーザーの要望から今どのフェーズかを判断する。
- **忖度しない**。良くない部分は明確に指摘し、改善案まで出す。
- **対話的に進める**。確認質問は一度に 5 項目以内。既に明らかなものは省略。
- 体裁ルールはプラットフォーム（note / zenn）で切り替える。詳細は `references/platform-conventions.md`。

---

## Phase 1: 企画

ネタを記事テーマに育てる。

1. `memos/` を見渡し、書けそうなテーマを提示する。ネタが特定済みならそれを使う。
2. 新規ネタなら `templates/memo.md` を元に `memos/<theme-slug>.md` を作る。
3. テーマが決まったら **プラットフォーム（note / zenn）** を決める。
   - note: ビジネス・読み物・考え方の言語化向け
   - zenn: 技術記事・実装知見・コード中心向け
4. メモに `platform_candidate` を記入。

## Phase 2: 構成

メモから記事の骨子を作る。

1. 確認質問（5 項目以内、既知のものは省略）:
   - ターゲット読者
   - 記事の目的（読者に何をしてほしいか）
   - 想定ボリューム
   - 単発かシリーズか
2. 見出し構成（H2 / H3）と各セクションの想定文字数をテーブルで提示する。
3. 構成案をユーザーと詰めてから執筆へ進む。

構成テンプレート:

```
| 章 | 内容 | 想定文字数 |
|----|------|-----------|
| 導入 | （概要） | 250字 |
| 1章 | （概要） | 600字 |
| まとめ | （概要） | 200字 |
```

文字数の目安はプラットフォームで異なる（`platform-conventions.md` 参照）。

## Phase 3: 執筆

`templates/article.md` を元に `drafts/<article-slug>.md` を作る。

- frontmatter を埋める（`title` / `slug` / `platform` / `created` / `source_memo` など）。
- 本文をプラットフォーム別の体裁で書く（`platform-conventions.md`）。
- 「さっぱりしすぎ」を避ける: 主張には理由を、抽象論には具体例を添える。1 段落 3〜5 文。
- 箇条書きと長文を使い分ける（並列の列挙は箇条書き、概念説明・具体例・主張は長文）。

## Phase 4: 推敲

下書きをクリティカルにレビューする。観点の詳細は `references/review-checklist.md`。

提示順:

1. **致命的な問題** — 読者が離脱する / 誤解を招く
2. **構造的な問題** — 導入が長い、論理の飛躍、ターゲットのズレ
3. **言葉の問題** — 刺さらない表現、専門用語の乱用、トーンの不一致
4. **改善後の構成案** — 章立てと想定文字数

タイトル案（複数）と冒頭の引きも点検する。ユーザーが方向性を承認したら改善版を作成する。

## Phase 5: 画像

記事に挿入する画像を生成する。手順の詳細は `references/image-generation.md`。

1. 挿入位置を決め、図解パターンを選ぶ（`references/image-prompts.md` の 10 種）。
2. 各画像の生成プロンプトを作成する。
3. codex CLI で実画像を生成し、`assets/<slug>/NN-<desc>.png` へ配置する。
4. 本文の挿入位置に `![alt](../assets/<slug>/NN-<desc>.png)` を入れる。
5. codex が使えない場合はフォールバックとして本文に画像プロンプトをインライン記載する。

画像枚数の目安: 1,500 字以下 2〜3 枚 / 2,000〜3,000 字 3〜5 枚 / 3,500 字以上 5〜6 枚（上限 6 枚）。

## Phase 6: 公開準備

1. 記事を `drafts/` から `published/` へ移動する。
2. frontmatter の `status` を `published`、`published_at` と `url` を記入する。
3. `platform: zenn` の場合は Zenn 形式 frontmatter を生成する（`platform-conventions.md`）。
4. 区切りとして git コミットする。

---

## 参照ファイル

- `references/platform-conventions.md` — note と Zenn の体裁・frontmatter 差分
- `references/review-checklist.md` — 推敲のレビュー観点
- `references/image-prompts.md` — 画像生成プロンプトの図解パターン集
- `references/image-generation.md` — codex CLI で実画像を生成し配置する手順
