---
name: continova-business-card
description: Create, update, or redesign continova's printable business card using the HTML+CSS → Chrome "Save as PDF" workflow in `public/card.html`. Use this skill whenever the user mentions 名刺 / business card / card.html in the continova-hp project, or wants to change the card's content (name, title, email, QR), colors, typography, or re-export for print. Handles the exact 97×61mm (91×55mm trim + 3mm bleed) Japanese standard size and the brand tokens (Void / Klein Blue / Bright Blue / Fog / Ink / Stone). Trigger even when the user doesn't explicitly name the file — e.g., "名刺を作り直したい", "名刺のメール変えて", "名刺のQR差し替え".
---

# continova Business Card — HTML/CSS → PDF Workflow

continovaの名刺は **Figmaではなく** `public/card.html` に静的HTMLとして実装されている。Chromeの「PDFに保存」で入稿用PDFを書き出す方式。この仕組みは過去にFigma MCPの回数制限で行き詰まった経緯から採用されたもので、ブラウザだけで物理サイズをピクセルパーフェクトに出力できる点が最大の価値。

## 物理仕様（ここは絶対に変更しない）

| 項目 | 値 | 備考 |
|------|------|------|
| 全体サイズ | **97mm × 61mm** | 塗り足し3mm込み。`@page size` と `.card` の width/height で固定 |
| 仕上がりサイズ | 91mm × 55mm | 日本標準名刺。画面プレビュー時に赤破線で表示 |
| 塗り足し | 天地左右3mm | 印刷所の一般規格 |

**なぜmm単位なのか**: CSSの `mm` は物理寸法（1mm = 3.7795px固定）で、Chromeの印刷エンジンが `@page size` を尊重するため、どんなズーム率でも正確な名刺サイズでPDFが書き出せる。pxで書くと環境依存で寸法が狂う。

## ファイル構成

```
public/
├── card.html    # 表面・裏面の2セクション + 画面プレビュー用トリムガイド
└── qr.png       # 裏面のQRコード画像（continova.jp へのリンク）
```

## ブランドトークン

CSS `:root` で以下を定義（`src/styles/global.css` のデザイントークンと一致させる）：

```css
--void:        #0A0F1C;  /* 表面背景 */
--klein-blue:  #002FA7;  /* 表面グロー（radial gradient） */
--bright-blue: #3B6BF7;  /* 区切り線（表裏共通） */
--white:       #FFFFFF;  /* 表面テキスト / 裏面背景 */
--fog:         #94A3B8;  /* 補足テキスト（英語名、肩書き、URL） */
--ink:         #0F172A;  /* 裏面メインメッセージ */
--stone:       #475569;  /* 裏面サブテキスト（JP、メール） */
```

## フォント

Google Fonts からロード。`Inter` と `Noto Sans JP` の両方を使う：

```html
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+JP:wght@400;500;700&display=swap">
```

## 表面（ダーク）レイアウト

中央揃え1カラム、上から順に：

| 要素 | フォント | サイズ | ウェイト | 色 | 備考 |
|------|---------|--------|---------|-----|------|
| ロゴ `continova` | Inter | 18pt | 700 | White | tracking -0.02em |
| 区切り線 | — | 幅12mm × 高0.4mm | — | Bright Blue | 上下3.8mm マージン |
| 名前 `村上 響一` | Noto Sans JP | 11pt | 500 | White | tracking 0.08em |
| 英語名 `Kyoichi Murakami` | Inter | 7.5pt | 400 | Fog | tracking 0.06em, 名前下1.6mm |
| 肩書き `Data & AI Consultant` | Inter | 7.5pt | 400 | Fog | tracking 0.06em, 英語名下1.8mm |

背景は `Void` + Klein Blue の radial gradient を中央に重ねる（2層）：

```css
background:
  radial-gradient(ellipse 60% 80% at 50% 50%, rgba(59, 107, 247, 0.18) 0%, transparent 60%),
  radial-gradient(ellipse 40% 55% at 50% 50%, rgba(0, 47, 167, 0.35) 0%, transparent 65%);
```

## 裏面（ライト）レイアウト

中央揃え1カラム、上から順に：

| 要素 | フォント | サイズ | ウェイト | 色 | 備考 |
|------|---------|--------|---------|-----|------|
| 英語メッセージ | Inter | 9.5pt | 600 | Ink | tracking 0.03em |
| 日本語メッセージ | Noto Sans JP | 7pt | 400 | Stone | 英語下1.8mm |
| 区切り線 | — | 幅12mm × 高0.4mm | — | Bright Blue | 上下3mm |
| QRコード | `./qr.png` | 18mm × 18mm | — | — | `<img class="qr">` |
| メール | Inter | 7.5pt | 400 | Stone | tracking 0.02em |
| URL `continova.jp` | Inter | 7pt | 400 | Fog | メール下1mm |

## 画面プレビュー用トリムガイド

`@media screen` 内に限定して以下を追加。**印刷時には出ない**：

```css
.card::after {
  content: '';
  position: absolute;
  top: 3mm; left: 3mm;
  width: 91mm; height: 55mm;
  border: 0.2mm dashed rgba(244, 63, 94, 0.55);
  pointer-events: none;
}
```

`@media screen` で body に背景色とpaddingを与えて、カードが浮いて見えるようにする。`@media print` では `.note` など説明文は `display: none` で隠す。

## 更新時の標準ワークフロー

1. `public/card.html` を編集
2. `npm run dev` → `http://localhost:4321/card.html` を開く
3. （オプション）Playwright MCPでスクリーンショットを撮って目視検証：
   ```
   browser_navigate → browser_resize(720, 1000) → browser_take_screenshot(fullPage: true)
   ```
4. Chromeで **印刷 → PDFに保存** を選択
5. 印刷ダイアログで：
   - **送信先**: PDFに保存
   - **用紙サイズ**: カスタム 97×61mm
   - **余白**: なし
   - **倍率**: 100%
   - **背景のグラフィック**: ON
6. PDF を確認

## よくある変更パターン

### テキストだけ変える

`<section class="card front">` または `<section class="card back">` の中のテキストを書き換える。`.divider` は `<hr class="divider">` として配置されているので触らない。

### QRコードを差し替える

`public/qr.png` を新しい画像で上書き保存するだけ。サイズは18mm角で自動リサイズされる。高解像度（300dpi以上）のPNGを使うこと。

### 色を微調整する

`:root` の CSS変数を変える。ブランドトークンは `src/styles/global.css` と整合性を保つこと（名刺だけ独自の色にしない）。

### フォントサイズ・間隔を調整する

全てpt単位・mm単位で記述している。印刷物ではptとmmが物理寸法として正しく反映されるので、px換算は不要。ただし `7pt` を下回ると読みにくくなるので、**最小でも7pt** を目安にする。

### レイアウト構造を大きく変える

中央揃えの1カラム構造は維持したほうが良い（「静かな知性」のブランドトーン）。どうしても左右分割にしたい場合は仕上がり領域（91×55mm）の内側に3mmのセーフエリアを残す。

## やってはいけないこと

- **全体サイズを97×61mm以外にしない** — 印刷所の入稿規格とズレる
- **塗り足しを3mm以外にしない** — 日本の印刷所の一般規格
- **mm単位の代わりにpxを使わない** — 物理寸法がズレる
- **トリムガイド（赤破線）を `@media screen` の外に出さない** — 印刷物に出てしまう
- **`-webkit-print-color-adjust: exact` を外さない** — 背景色・グラデーションがPDFで白飛びする
- **Google Fonts のリンクを外さない** — フォントが落ちると可読性が崩れる
- **QRコードを `<div>` のプレースホルダに戻さない** — `public/qr.png` の `<img>` を維持する

## 印刷入稿時の注意

- Chromeから書き出したPDFはRGB。**多くの日本の印刷所（ラクスル、プリントパック等）はRGB入稿OK** で自動的にCMYK変換してくれるため、そのまま入稿できるケースが多い
- CMYK必須の印刷所に入稿する場合：
  - **Adobe Acrobat Pro**: 「印刷工程 → 色を変換」でCMYK化
  - **Ghostscript（無料）**: `gs -sDEVICE=pdfwrite -sColorConversionStrategy=CMYK -dProcessColorModel=/DeviceCMYK -o out.pdf in.pdf`
- 入稿前に必ず**実寸で試し刷り**をして、文字の可読性・塗り足し・QR読み取りを確認する

## トラブルシューティング

| 症状 | 原因 | 対処 |
|------|------|------|
| 印刷PDFの背景が白い | `print-color-adjust: exact` が効いていない | Chrome印刷ダイアログで「背景のグラフィック」をON |
| 文字が切れる | `line-height` が未指定で行高がmm単位と合わない | 各テキストに `line-height: 1` を明示 |
| 用紙サイズが変 | Chromeで印刷時に「カスタム用紙サイズ」が選択されていない | 必ず「カスタム → 97×61mm」を入力 |
| QRが読めない | 画像解像度不足 / サイズ不足 | 300dpi以上、最低15mm角。テスト読み取りを実機スマホで |
| トリムガイドが印刷に出る | `@media print` にも `::after` が漏れている | `@media screen { .card::after { ... } }` に閉じ込める |

## 関連ファイル

- `public/card.html` — 実装本体
- `public/qr.png` — QRコード
- `src/styles/global.css` — ブランドトークンの出典
- `docs/superpowers/specs/2026-04-08-business-card-design.md` — 初期設計仕様書（Figma前提の旧版、参考用）
- `CLAUDE.md` — プロジェクト全体のルール

## 履歴の文脈（なぜこの方式か）

2026年4月初旬、当初はFigmaで名刺デザインを作成していたが、Figma MCP（Starterプラン: 月6回のツール呼び出し上限）の制限に頻繁にぶつかり、サイズ調整が進まなかった。継続的に編集するにはブラウザ完結の方式が合理的という判断から、`public/card.html` に移行した。この経緯を理解しておくと、「Figmaで作り直しましょう」という提案をせずに済む。
