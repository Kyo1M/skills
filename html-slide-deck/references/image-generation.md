# 画像生成（codex CLI）

スライドに差し込むビジュアル（アイソメトリックなイラスト・図解・アイコン）を codex CLI のネイティブ画像生成で作り、`assets/<slug>/` に配置する。

## いつ使うか

本スキルは SVG とこの生成画像を**併用**する。Phase 3 でスライドごとに選ぶ。

- **SVG を使う** — 正確な数値・比較表・座標が意味を持つ図（比較表、軸図、ファンチャート等）。後から編集できることが重要な図。
- **生成画像を使う** — 構造や概念を直感的に伝えるアイソメトリックなイラスト、タイトル/セクション扉のヒーロー、カード見出し等のアイコン。

迷ったら SVG。生成画像は「絵で伝わると速い」ところに絞る。

## 仕組み

`codex exec` で画像生成を自然言語で依頼すると、codex は次のどちらかで応える。どちらでも指示したパスに PNG が保存される。

- **ネイティブ画像生成**（`imagegen` / `image_gen`）— 絵画的・写実的なイラスト向き。`OPENAI_API_KEY` 不要、ChatGPT サブスクのログインで動く。元画像は `~/.codex/generated_images/<session-id>/` にも残る
- **SVG を自前で作図してラスタライズ** — 幾何学的・アイソメトリックな図解では codex がこちらを選びやすい。クリーンで continova v1 と相性が良く、`.svg` を併せて残せば後から編集できる（実測: 図解プロンプトでこちらになる）

図解・アイコンは SVG 経路になることが多い。経路は codex に委ねてよく、プロンプト側でスタイル（フラット・幾何学的・continova v1 配色）を明確に指定することが品質を決める。

- `codex exec` は git リポジトリ内から、または `--skip-git-repo-check` 付きで実行する。`--sandbox workspace-write` で実行ディレクトリ配下に書き込める。

## 保存先と命名

生成画像は HTML と同じ階層の `assets/<slug>/` に置く。`<slug>` はデッキの ASCII kebab-case スラグ。

```
<出力ディレクトリ>/
  20260520_foo-slides.html
  assets/
    foo/
      hero.png            ← ヒーロー / セクション扉イラスト
      01-system-overview.png   ← 図解（主役オブジェクト）
      02-data-flow.png
      icons/
        target.png        ← アイコン（1 セッションで一括生成）
        cycle.png
        layers.png
```

- 図解・ヒーロー: `assets/<slug>/NN-<desc>.png`（`NN` は連番、`<desc>` は内容を表す kebab-case 英語）
- アイコン: `assets/<slug>/icons/<name>.png`

HTML からの参照は HTML ファイルからの相対パス（`src="assets/<slug>/01-system-overview.png"`）。

## 手順

Phase 3 で「生成画像を使う」と決めたスライドについて、Phase 4 で次を行う。**画像生成は HTML 実装の前**に済ませる（パスが先に確定する）。

### 1. 図解・ヒーロー画像（1 枚ずつ）

`references/image-prompts.md` の continova v1 テンプレートからプロンプトを組み立て、1 枚ずつ `codex exec` を呼ぶ（1 枚ずつの方が品質が安定し、個別に調整できる）。

```bash
codex exec --skip-git-repo-check --sandbox workspace-write \
  "画像を1枚生成してください。
  【プロンプト】
  <image-prompts.md の continova v1 テンプレートに沿ったプロンプト>

  生成できたら assets/<slug>/<NN>-<desc>.png にコピーしてください。
  SVG で作図した場合は同じ場所に .svg も残してください（後から編集できるように）。
  最後の行に、コピー先の相対パスだけを出力してください。" < /dev/null
```

codex は出力先ディレクトリ（HTML を置くプロジェクト直下）から実行する。

### 2. アイコンセット（1 セッションで一括生成）

codex は呼び出しごとに画風がぶれる。**デッキで使うアイコンは 1 回の `codex exec` でまとめて生成**し、共有スタイル仕様を渡して統一感を出す。

```bash
codex exec --skip-git-repo-check --sandbox workspace-write \
  "次のアイコンを、すべて同じスタイル仕様で生成してください。
  【共有スタイル仕様】
  <image-prompts.md のアイコン共通スタイル仕様>

  【生成するアイコン】
  - target: <意味>
  - cycle: <意味>
  - layers: <意味>
  （デッキで実際に使うものだけ）

  各アイコンを assets/<slug>/icons/<name>.png に保存してください。
  最後に、保存した相対パスを1行ずつ出力してください。" < /dev/null
```

### 3. 確認と適用

- 生成された PNG が想定パスに保存されたか確認する。
- HTML の該当箇所に `<img>` で参照を入れる（`template.html` の `.figure` / `.hero-visual` / `img.icon` クラスを使う。詳細は `slide-patterns.md` Pattern 11/12）。
- ラベル・凡例・数値は**画像に焼き込まず HTML テキストで重ねる/隣に置く**（後述）。

## ラベルは焼き込まない

生成画像にスライドの説明文・数値・凡例を焼き込まない。理由は 2 つ:

1. AI 画像生成は日本語テキストの描画品質が低い（崩れ・誤字が出る）。
2. 焼き込んだ文言は後から直せない（`design-system.md` の Avoid 参照）。

生成画像は構造・概念のイラストに徹し、テキストは HTML 側で `.figure-caption` や重ね配置の `<div>` として持つ。プロンプトでも「テキストは最小限、日本語の長文を入れない」を必ず指示する。

## トラブル時・フォールバック

- `codex --version` でエラーになる / 画像生成が使えない場合は、そのスライドを **SVG パターン**（`slide-patterns.md` Pattern 01-10）に切り替える。生成画像は必須ではない。
- codex が指定パスへコピーできなかった場合は、出力された画像（ネイティブ生成なら `~/.codex/generated_images/.../*.png`）の絶対パスを読み取り、こちら側で `assets/<slug>/` へコピーする。
- 生成画像のアスペクト比は約 16:9。図解は `.figure` で幅 100%・高さ自動で収まる。厳密な比率が要る場合はプロンプトでアスペクト比を明示する。
