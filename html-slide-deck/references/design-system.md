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
| Top message | 22px | 500 | `--stone` |
| Section label | 12-13px | 600-700 | `--pebble` (uppercase, letter-spacing 0.14em) |
| Body text | 13-14px | 400 | `--stone` |
| Card heading | 16-18px | 700 | `--ink` |
| KPI数値 | 22-28px | 700 | `--brand-klein` (Helvetica Neue) |
| Caption | 11-12px | 400 | `--pebble` |
| Eyebrow | 13px | 500 | `--pebble` (uppercase, letter-spacing 0.18em) |

### ルール

- 文字を詰めて入れない。長い説明はスライド本文から外す
- letter-spacing は uppercase の英数字ラベルだけに使う(日本語には基本使わない)
- セリフ体はタイトルとカード見出しのキー要素のみ。本文には使わない

---

## Layout Rhythm

- スライドサイズ: **1672 x 941 px**、16:9 固定
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

## Avoid

以下は明確にやってはいけないこと:

- 1枚に複数の主張を詰め込む
- 箇条書きを大きなカードに入れて並べるだけの構成
- 青い面を広げすぎて Klein Blue の意味を弱める
- 説明文を画像として固定し後から直せない状態にする
- スライド構成が固まる前に HTML を作り始める
- 装飾目的のアイコン大量配置
- ストック写真風のフリー素材
- 紫グラデーション + 白背景の汎用コーポレート風
- ノイジーな背景・大きな装飾ブロブ

---

## Image Generation Direction

スライド内に画像を配置する場合は、以下のルールに従う(本スキルでは原則SVG優先):

- continova v1: white background, thin rules, ample whitespace, Klein Blue accent `#002FA7`
- minimal premium consulting slide, Japanese business deck, 16:9
- one dominant idea, clean hierarchy, no stock-photo feeling
- if infographic: precise geometric structure, editable reconstruction expected
- avoid: heavy gradients, purple/blue corporate cliche, noisy backgrounds, oversized decorative blobs, dense text
