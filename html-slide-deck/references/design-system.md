# continova slide design system v1

`Quiet Intelligence` を維持しつつ、Klein Blue を差し色にして、ミニマルだが情報設計の豊かさがあるスライドを作るためのデザイン指針。

## Design Principles

1. **One slide, one decision**
   - 1枚のスライドは1つの認識変化、判断、合意事項だけを担う
   - 補足説明や背景は本文ではなく speaker notes 相当に逃がす

2. **Consulting calm, infographic richness**
   - 基本は白地、細い罫線、余白、強い見出しで構成
   - 複雑な概念は文章ではなく、循環図・フロー・マトリクス・比較表・KPI・図解で表現
   - リッチさは装飾ではなく、構造化された情報表現で出す

3. **Klein Blue as signal**
   - Klein Blue は「注目点」「推奨案」「決定してほしい要素」にだけ使う
   - 画面全体を青くしない。通常は5-12%程度の視覚面積に抑える

4. **Template consistency, not template sameness**
   - タイトル、トップメッセージ、フッター、余白、罫線のリズムは共通化
   - 各スライドの主役はテンプレに合わせて変える

5. **Information design over decoration**
   - 装飾ではなく、情報の主従と構造で見せる
   - アイコンは意味を補うときだけ使う

---

## Color Palette

| Token | Hex | 用途 |
|---|---|---|
| `--brand-klein` | `#002FA7` | 主アクセント、推奨案、重要ノード |
| `--brand-blue` | `#1D6CFF` | 明るい補助アクセント、リンク的強調 |
| `--brand-blue-soft` | `#EAF1FF` | 薄い背景、青の面を使うとき |
| `--ink` | `#111111` | 本文、タイトル、主要線 |
| `--stone` | `#2F3135` | 本文サブカラー |
| `--pebble` | `#6F7175` | 注釈、ラベル、フッター |
| `--fog` | `#A9AAAD` | 非アクティブ要素 |
| `--border` | `#B7B7B7` | 罫線 |
| `--border-soft` | `#DDDDDD` | 補助罫線 |
| `--snow` | `#F6F5F2` | 通常の淡色背景 |
| `--white` | `#FFFFFF` | スライド背景 |
| `--success` | `#10B981` | 良化、達成、完了 |
| `--warning` | `#F59E0B` | 注意、リスク、未確定 |

### Klein Blueの使用例

```css
/* 推奨案カードの強調 */
.recommended-card {
  border: 1.5px solid var(--brand-klein);
  background: var(--brand-blue-soft);
}

/* タイトル下のアクセント線 */
.title-rule {
  width: 60px;
  height: 3px;
  background: var(--brand-klein);
}

/* 左ボーダーアクセント */
.mitigation {
  border-left: 2px solid var(--brand-klein);
  padding-left: 16px;
  color: var(--brand-klein);
}
```

### 副次的な色の使い方

- `--success` (緑): バイアス小・良好評価
- `--warning` (オレンジ): 注意・部分的・要議論
- `#B0413E` (赤系): バイアス大・否定的評価 (※トークン化していない場合)

ネガティブな評価は赤一色ではなくニュアンスをつける(色面ではなくテキスト色で軽く)。

---

## Typography

```css
/* 日本語本文 */
font-family: "Hiragino Sans", "Noto Sans JP", "Yu Gothic", system-ui, sans-serif;

/* 日本語タイトル(セリフ) */
font-family: "Hiragino Mincho ProN", "Yu Mincho", "Noto Serif JP", serif;

/* 英数字・KPI */
font-family: "Helvetica Neue", "Inter", Arial, sans-serif;
```

### サイズ階層

| 要素 | サイズ | weight | 色 |
|---|---|---|---|
| Slide title | 46px | 600 | `--ink` (セリフ) |
| Top message | 26px | 500 | `--stone` |
| Section label | 13-14px | 600-700 | `--pebble` (uppercase, letter-spacing 0.14em) |
| Body text | 15-17px（既定16px） | 400 | `--stone` |
| Card heading | 16-17px | 700 | `--ink`(または白地・青ヘッダ上で白) |
| KPI数値 | 24-30px | 700 | `--brand-klein` (Helvetica Neue) |
| Caption | 13-14px | 400 | `--pebble` |
| Eyebrow | 13-14px | 500 | `--pebble` (uppercase, letter-spacing 0.18em) |

> **可読性の基準（2026-06 更新・底上げ版）**: 1672×941 の投影前提では、本文 14px 以下は潰れやすく「パッと見て伝わらない」。**Body text は 16px を既定**とし、15-17px の帯で運用する。チェックリスト・カード本文・注釈帯・コマンド帯もこの帯に合わせる（読み手が一番触れる本文を最優先で大きく）。Top message は **26px**。ツリー・プロンプト掲載ボックス等のモノスペース密度の高い要素は 15px まで、注釈・凡例・補助ラベル（SVG 図中ラベルを含む）は **12px を下限**とする。**11px 以下は投影で読めないため使わない**。**スライドからのはみ出し・`overflow:hidden` でのクリップは絶対に出さない（フォントサイズより優先）。** 情報量が多くて収まらないスライドは、まず 2 枚に分割／4 カラムを 2×2 に組み替える → それでも収まらない（分割したくない）場合は、本文を一段下げて収める（**14px 目安、投影下限 12px まで**）。「全情報を載せたい」ときも、はみ出すくらいなら font を縮めて収めるのが正しい。

### ルール

- 文字を詰めて入れない。長い説明はスライド本文から外す
- letter-spacing は uppercase の英数字ラベルだけに使う(日本語には基本使わない)
- セリフ体はタイトルとカード見出しのキー要素のみ。本文には使わない

---

## Layout Rhythm

- スライドサイズ: **1672 x 941 px**、16:9 固定。`.slide` は `width`/`height` を px で固定し、狭いビューポートでは `transform: scale()` でデッキ全体を縮小する（`aspect-ratio` で可変幅にすると、窓幅が 1672px 未満のとき本文 px が固定のまま枠だけ縮んで**はみ出し・クリップ**するため不可）。scale 値は末尾の小さなリサイズスクリプトで inline 設定する（CSS calc の `length ÷ length = number` は新しめの Chromium/Safari/Firefox 限定のため、互換性重視で JS にする。JS 無効時は原寸表示で内容はクリップされない）
- 標準余白: 左右 70px、上 58px、下 38px
- タイトル下のルール線(60×3px Klein Blue)とフッター線で資料全体の静かなリズム
- トップメッセージは 1-2 文。スライド上部で読むべき結論を先に置く
- ボディは1つの主役オブジェクトを持つ(チャート・図解・比較表・循環図・KPI・強いテキストのいずれか)

### スライドの基本構造

```
┌────────────────────────────────────────┐
│ Eyebrow (e.g., "01 / OBJECTIVE")       │ ← 13px pebble uppercase
│ Slide Title                            │ ← 46px serif ink
│ ━━━━ (60×3px klein rule)               │
│ Top message: 1-2 sentences with        │ ← 22px stone
│ accent on key terms                    │
│                                        │
│   [Body — main object]                 │ ← 主役オブジェクト
│                                        │
│ ─────────────────────────────────────  │ ← border-soft hairline
│ Footer left              page count    │ ← 12px pebble
└────────────────────────────────────────┘
```

---

## Infographic Rules

- 文章が3点以上並ぶ場合、`bulletList` よりも `threePanel`、`matrix`、`arrowFlow`、`cycleFlow`、`comparisonTable` を検討
- 因果や悪循環は `cycleFlow`、時系列は `roadmap`、手順は `arrowFlow`、意思決定は `matrix` または `comparisonTable` を優先
- KPI は数字だけを大きく置くのではなく、推移・示唆・次アクションと一体で見せる
- アイコンは意味を補うために使う。装飾目的のアイコン大量配置は避ける

### SVGダイアグラムの基本ルール

- viewBox基準でサイズ固定(`viewBox="0 0 760 430"` など)
- 1図1メッセージ
- 主役データはKlein Blue + 薄塗りつぶし、比較対象はグレーで非主役化
- ラベル・凡例は読み手の視線移動を最小化(隣接配置)
- マーカー(矢印)は `<defs>` でmarkerを定義し `marker-end` で参照
- text要素は `font-family="Hiragino Sans, Noto Sans JP, sans-serif"` を継承(SVG内で再指定)

```svg
<defs>
  <marker id="arr" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <polygon points="0 0, 8 4, 0 8" fill="#002FA7"/>
  </marker>
</defs>
<line x1="0" y1="0" x2="100" y2="0" stroke="#002FA7" marker-end="url(#arr)"/>
```

---

## 線アイコンシステム

文字ばかりのスライドはスキャン性が落ちる。**意味を補う線アイコン**を見出しや工程ラベルに添えると、読み手が構造を一目で掴める。装飾ではなく情報設計として使うのが原則。

### 作り方（symbol sprite + use）

外部生成画像（codex 等）は使わず、**手書き SVG の `<symbol>` を 1 箇所に定義**し、各所から `<use>` で参照する（DRY・一貫性確保）。デッキ冒頭の隠し SVG（矢印 marker を置く `<defs>`）にまとめる。

```html
<svg width="0" height="0" style="position:absolute;"><defs>
  <symbol id="ic-database" viewBox="0 0 24 24"><ellipse cx="12" cy="6" rx="7" ry="3"/><path d="M5 6 V18 c0 1.66 3.13 3 7 3 s7 -1.34 7 -3 V6"/><path d="M5 12 c0 1.66 3.13 3 7 3 s7 -1.34 7 -3"/></symbol>
  <!-- 必要なアイコンを意味と 1:1 で定義 -->
</defs></svg>
```

```css
/* stroke は currentColor を継承 → 文脈の color で色を出し分け */
.ic { width:20px; height:20px; flex:none; fill:none; stroke:currentColor;
      stroke-width:1.6; stroke-linecap:round; stroke-linejoin:round; vertical-align:middle; }
.ic-title { width:32px; height:32px; vertical-align:-5px; margin-right:13px; } /* スライドタイトル左 */
```

```html
<!-- 青ヘッダのカード見出し: 親の color:#fff を継承して白アイコンになる -->
<div class="card-head"><svg class="ic"><use href="#ic-database"/></svg><span>B. データ・期間</span></div>
<!-- 白地の工程タイトル: Klein Blue で出す -->
<div class="slide-title"><svg class="ic ic-title" style="color:var(--brand-klein)"><use href="#ic-chart"/></svg>工程③ 解析</div>
```

- `<symbol>` の path には stroke/fill を**付けない**（`.ic` から currentColor・stroke-width を継承させる）。
- 色は文脈の `color` で決まる: 青ヘッダ上は白、白地は `--brand-klein`。
- viewBox は全アイコン共通（`0 0 24 24`）、stroke-width も統一（1.6）。サイズは見出し 18-20px / タイトル横 32px。

### 使いどころ（意味と 1:1）

- **工程・ステップのラベル**（フロー図の各段、工程タイトル）
- **観点カードの見出し**（A/B/C/D が「何を見るか」をアイコンで示す: 分岐=ロジック, ファネル=除外, 三角=異常値, 循環=再現性 など）
- **構成・レイヤーの対応**（ディレクトリ役割: 文書=docs, `</>`=code, シリンダ=db, スパーク=AI）

### やりすぎ回避

- **意味と 1:1 のときだけ**付ける。同じ見た目を意味なく量産しない。
- 本文 callout・badge・箇条書きの各行には付けない（ノイズになる）。
- 1 スライド内でストローク太さ・サイズ・色ルールを混在させない。

---

## 記憶に残す（装飾ではなく構造で）

「シンプルで読みやすい」と「記憶に残らない」は紙一重。consulting calm を崩さず（＝グラデ・装飾・色の乱用に逃げず）、**構造と情報設計で印象を立てる**ための指針。箇条書きカードを並べただけのデッキは正しく読めても忘れられる。

- **主役のコンセプト図を 1 枚置く**: デッキ全体の主張を 1 枚の手書き SVG 図（`conceptSchematic` / Pattern 11）に凝縮する。抽象テーマは文章より「図の形」で記憶される。読み手が後で思い出すのはこの 1 枚。
- **章扉・セクション区切りで構造を見せる**: 複数パート（型・フェーズ・トラック）に分かれるデッキは、各パートの頭にマップ／章扉スライドを置き「いま全体のどこか」を常に分かるようにする。マップスライドが章扉を兼ねてよい。
- **反復する視覚モチーフで章を識別**: 章ごとに固定のアイコン＋ラベル（例: `① 分析伴走型`＋コンパス）を各スライド上部に反復表示する。色を増やすのではなく、**同じ Klein Blue の中でアイコンと番号で識別**させる（第2のブランドカラーを増やさない）。
- **結論・キー数値を hero 化する**: そのスライドで一番伝えたい一文／数字を、本文より一段大きく置く（top-message 26px、KPI 24-30px）。1 スライド 1 メッセージを視覚の大小でも表す。
- **共有と差分を図で対比する**: 「共通基盤 ＋ 枝分かれ」「Before / After」のような関係は、文章で書かず分岐フロー・対比図で見せると構造が記憶に残る。

> いずれも「足し算の装飾」ではなく「主従と構造の強調」。迷ったら、装飾を足すのではなく**主役を1つに絞って大きくする**。

---

## Avoid

以下は明確にやってはいけないこと（→ は推奨される代替）:

- 1枚に複数の主張を詰め込む → 主役を1つに絞り、残りは別スライドへ分割する
- 箇条書きを大きなカードに入れて並べるだけの構成 → 関係性があるならフロー・マトリクス・対比図にする
- 青い面を広げすぎて Klein Blue の意味を弱める
- 説明文を画像として固定し後から直せない状態にする
- スライド構成が固まる前に HTML を作り始める
- 装飾目的のアイコン大量配置 → アイコンは意味と 1:1 のときだけ
- 記憶に残すために装飾（グラデ・影・色）を足す → 代わりに主役のコンセプト図（Pattern 11）・章モチーフの反復・hero 化で印象を立てる
- ストック写真風のフリー素材 → 手書き SVG の図解
- 紫グラデーション + 白背景の汎用コーポレート風 → 白地・細罫・余白＋ Klein Blue 差し色
- ノイジーな背景・大きな装飾ブロブ → 余白と構造で「静けさ」を保つ
- 可読性のために本文を 14px 以下へ削る → font は 16px を保ち、密なら 2 枚に分割／2×2 に組み替える

---

## Image Generation Direction

スライド内に画像を配置する場合は、以下のルールに従う(本スキルでは原則SVG優先):

- continova v1: white background, thin rules, ample whitespace, Klein Blue accent `#002FA7`
- minimal premium consulting slide, Japanese business deck, 16:9
- one dominant idea, clean hierarchy, no stock-photo feeling
- if infographic: precise geometric structure, editable reconstruction expected
- avoid: heavy gradients, purple/blue corporate cliche, noisy backgrounds, oversized decorative blobs, dense text
