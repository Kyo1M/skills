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
- 主役オブジェクトは SVG ダイアグラムのほか、codex で生成したアイソメトリック画像でもよい（「Image Generation Direction」参照）

### アイコンの使い方

アイコンは codex で生成したラスター画像（PNG）を使う。`references/image-prompts.md` のテンプレ C と `references/image-generation.md` を参照。

- **目的**: ラベル・セクション・カテゴリの識別補助、構造の視認性向上
- **生成方法**: デッキで使うアイコンは 1 回の codex セッションで一括生成し、共通スタイル仕様で画風を揃える
- **位置**: カード見出しの直前、eyebrow 横、テーブルヘッダ横、リスト行頭の機能補助
- **サイズ**: `--icon-size-md` (24px) を標準。インラインは `--icon-size-sm` (16px)、単独セクション標識は `--icon-size-lg` (40px)
- **色**: 主役・推奨アイコンは Klein Blue を効かせ、1 スライド 1-2 個まで。標準はインク、脇役はグレー
- **避けるべき**: 装飾目的の大量配置、絵文字との混在、画風の不揃い

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
- 生成画像にラベル・数値・日本語の文章を焼き込む（テキストは HTML 側で重ねる）
- スライド構成が固まる前に HTML を作り始める
- 装飾目的のアイコン大量配置・画風の不揃いなアイコン
- ストック写真風のフリー素材
- 光沢のある3Dレンダ調・グラデーション過多のアイソメトリック
- 紫グラデーション + 白背景の汎用コーポレート風
- ノイジーな背景・大きな装飾ブロブ

---

## Image Generation Direction

スライドのビジュアルは **SVG と codex 生成画像を併用**する。正確な数値・比較表・座標図は SVG、構造や概念を直感的に伝えるイラスト・ヒーロー・アイコンは生成画像。Phase 3 でスライドごとに選ぶ。生成手順は `references/image-generation.md`、プロンプトは `references/image-prompts.md`。

### 共通の制約（continova v1）

- 純白背景、Klein Blue `#002FA7` を唯一のアクセント、本体はインク／グレー、淡い面は `#EAF1FF` / `#F6F5F2`
- フラットで幾何学的。余白をたっぷり取り、1 画像 1 主題
- **禁止**: 光沢のある3Dレンダ、グラデーション、ドロップシャドウ、ストック写真風、紫系コーポレートクリシェ、ノイジーな背景、装飾ブロブ
- **テキストを焼き込まない**: AI 画像生成は日本語の描画品質が低く、後から直せない。ラベル・凡例・数値は HTML テキストで重ねる／隣に置く

### 3 つのカテゴリ

| カテゴリ | 用途 | スタイル | HTML 受け |
|---|---|---|---|
| ヒーロー / セクション扉 | タイトル・章区切りの象徴イラスト | フラットなアイソメトリックなシーン。左に余白を空けテキストを重ねる | `.hero-visual` |
| アイソメトリック図解 | スライドの主役オブジェクト（構造・流れ） | label-light なアイソメトリック図。ノードは分離し周囲に余白 | `.figure` |
| アイコン | カード見出し・eyebrow 横などの識別補助 | 正面フラットの2トーン、正方形。1 セッション一括生成で統一 | `img.icon` |
