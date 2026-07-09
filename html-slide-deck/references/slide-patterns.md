# Slide Patterns

continova v1スライドで使える14種類のパターン。各パターンは `assets/template.html` の基本CSSをベースに、追加のスタイルとHTMLを示す。すべて手書きSVG・HTML/CSSで完結し、外部生成画像は使わない。

> **フォントサイズ**: 以下の例の `font-size` 値は最小限の目安。実際のデッキでは投影可読性のため `references/design-system.md`「サイズ階層」の新基準（**本文 16px 既定（最低 15px）／ top-message 26px ／ 注釈・ラベルは 12px 以上、11px 以下は使わない**）に合わせて底上げする。例の 11-14px は本文・チェックリストではそのまま使わない。
>
> **線アイコン**: 見出し・工程ラベル・レイヤー対応には、意味を補う手書き SVG 線アイコンを添えるとスキャン性が上がる。作り方（`<symbol>` sprite + `<use>`・currentColor 継承・やりすぎ回避）は `references/design-system.md`「線アイコンシステム」を参照。card-head・three-category-cards・step-flow・phased-roadmap・concept-schematic と相性が良い。

## 目次

| # | パターン | 用途 | 推奨スライド位置 |
|---|---|---|---|
| 01 | comparison-cards | 2要素の対比、本命の明示 | 冒頭(目的) |
| 02 | dual-panel-diagram | 概念説明(理想 vs 落とし穴) | 概念パート |
| 03 | comparison-table | 選択肢比較、本命行ハイライト | 選択パート |
| 04 | tradeoff-axis | 1次元軸上の位置づけ | 選択パート補助 |
| 05 | tiered-options | 階層的・複数バリアントの提示 | 設計詳細 |
| 06 | three-category-cards | 3カテゴリの並列提示 | 設計詳細 |
| 07 | estimand-comparison | 3つの選択肢を大カードで提示 | 設計詳細 |
| 08 | step-flow-with-mockup | 手順フロー + アウトプット例 | 実装パート |
| 09 | limitation-matrix | 限界事項の3列マトリクス | 限界・前提 |
| 10 | phased-roadmap | フェーズ別ロードマップ + 議論項目 | 締め |
| 11 | concept-schematic | 仕組み・系を1枚の手書きSVG模式図で | 概念・設計パート |
| 12 | visual-band | 変化・遷移を表す補助スリム帯 | 任意(単調さの緩和) |
| 13 | isometric-concept | 節目スライドの主役アイソメ概念図(グレー3トーン＋青1ノード) | 表紙・章マップ・全体像・運用 |
| 14 | question-decision | 議論ページの定型(方針(たたき)と判断材料。聞きたいことは Top message 末尾に改行で添える) | 議論駆動デッキの【議論】ページ |

---

## 共通HTML骨格

すべてのパターンは以下の構造の中に入る:

```html
<section class="slide" id="sN">
  <div class="slide-eyebrow">NN / SECTION_LABEL</div>
  <h1 class="slide-title">スライドタイトル</h1>
  <div class="title-rule"></div>
  <p class="top-message">
    トップメッセージ。<span class="accent">強調語句</span>はaccentで。
  </p>

  <div class="body">
    <!-- ↓ ここにパターンを入れる -->
  </div>

  <div class="footer">
    <span class="left">資料名 | サブタイトル</span>
    <span>NN / TT</span>
  </div>
</section>
```

`assets/template.html` の冒頭CSSにこれらのクラスは定義済み。各パターンは追加のCSS+HTMLとして本ファイルから貼り付ける。

---

## Pattern 01: comparison-cards

**用途**: 2要素の対比で、片方を本命としてKlein Blueで強調する。冒頭スライドで「答える問い / 答えない問い」を提示する用途に最適。

**追加CSS**:
```css
.s1-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 28px; margin-top: 8px; }
.cmp-card {
  border: 1px solid var(--border-soft);
  padding: 28px 30px 24px 30px;
  position: relative;
  background: var(--white);
}
.cmp-card.primary {
  border-color: var(--brand-klein);
  border-width: 1.5px;
}
.cmp-card.primary::before {
  content: "本分析のスコープ";
  position: absolute; top: -11px; left: 24px;
  background: var(--brand-klein); color: var(--white);
  font-size: 11px; letter-spacing: 0.12em; padding: 4px 10px;
  font-weight: 600;
}
.cmp-card h3 { font-size: 22px; margin-bottom: 4px; font-weight: 700; }
.cmp-card .sub { font-size: 13px; color: var(--pebble); margin-bottom: 18px; }
.cmp-card.primary h3 { color: var(--brand-klein); }
.cmp-row {
  display: grid; grid-template-columns: 88px 1fr; gap: 14px;
  padding: 11px 0; border-bottom: 1px solid var(--border-soft);
  font-size: 14px; line-height: 1.55;
}
.cmp-row:last-child { border-bottom: none; }
.cmp-row .k { color: var(--pebble); font-size: 12px; padding-top: 2px; letter-spacing: 0.04em; }
```

**HTML**:
```html
<div class="s1-grid">
  <div class="cmp-card">
    <h3>選択肢A</h3>
    <div class="sub">英語サブタイトル</div>
    <div class="cmp-row"><div class="k">問い</div><div>...</div></div>
    <div class="cmp-row"><div class="k">推定対象</div><div>...</div></div>
    <div class="cmp-row"><div class="k">必要データ</div><div>...</div></div>
    <div class="cmp-row"><div class="k">本件での扱い</div><div style="color:var(--pebble);">スコープ外の理由</div></div>
  </div>

  <div class="cmp-card primary">
    <h3>選択肢B</h3>
    <div class="sub">英語サブタイトル</div>
    <div class="cmp-row"><div class="k">問い</div><div>...</div></div>
    <div class="cmp-row"><div class="k">推定対象</div><div>...</div></div>
    <div class="cmp-row"><div class="k">必要データ</div><div>...</div></div>
    <div class="cmp-row"><div class="k">本件での扱い</div><div><strong>本PoCのスコープ</strong></div></div>
  </div>
</div>
```

**カスタマイズポイント**:
- バッジ文言は `.primary::before` の `content` を変更
- 行は4-6行が読みやすい
- `.k` の幅(88px)は項目名の長さに応じて調整

---

## Pattern 02: dual-panel-diagram

**用途**: 2つの概念を並列で図解する。「理想 vs 現実」「①と②」のような対比に最適。SVGで主役オブジェクトを描く。

**追加CSS**:
```css
.s2-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 32px; height: 100%; }
.panel { border-top: 1px solid var(--ink); padding-top: 18px; }
.panel h3 { font-size: 18px; font-weight: 700; margin-bottom: 4px; }
.panel .panel-sub { font-size: 13px; color: var(--pebble); margin-bottom: 18px; }
.diagram { display: block; width: 100%; height: auto; }
```

**HTML**:
```html
<div class="s2-grid">
  <div class="panel">
    <h3>左パネルのタイトル</h3>
    <div class="panel-sub">サブタイトル(コンセプトの一行説明)</div>
    <svg class="diagram" viewBox="0 0 760 430" xmlns="http://www.w3.org/2000/svg">
      <!-- SVGコンテンツ。例: 反実仮想の図解 -->
      <rect x="20" y="30" width="320" height="160" fill="#EAF1FF" stroke="#002FA7" stroke-width="1.5"/>
      <text x="180" y="84" text-anchor="middle" font-size="15" font-weight="700" fill="#111">概念A</text>
      <!-- ... -->
    </svg>
  </div>

  <div class="panel">
    <h3>右パネルのタイトル</h3>
    <div class="panel-sub">サブタイトル</div>
    <svg class="diagram" viewBox="0 0 760 430" xmlns="http://www.w3.org/2000/svg">
      <!-- 対比となる概念のSVG -->
    </svg>
  </div>
</div>
```

**SVG設計ヒント**:
- viewBoxは縦横比をパネルに合わせる(本パターンは `760 430` 程度)
- 左パネルのSVGには Klein Blue を、右パネルにはコントラスト色(赤系)を配置すると対比が映える
- 図の最下部に結論ボックス(`<rect fill="#002FA7"/>` + 白テキスト)を置くと締まる

---

## Pattern 03: comparison-table

**用途**: 複数の選択肢を行で並べ、評価軸を列で並べる。本命行をKlein Blueでハイライト。

**追加CSS**:
```css
.compare-table { width: 100%; border-collapse: collapse; font-size: 14px; }
.compare-table th, .compare-table td {
  padding: 13px 14px; text-align: left; vertical-align: top;
  border-bottom: 1px solid var(--border-soft); line-height: 1.5;
}
.compare-table th {
  border-top: 1px solid var(--ink); border-bottom: 1px solid var(--ink);
  font-size: 12px; letter-spacing: 0.08em; color: var(--pebble);
  text-transform: uppercase; font-weight: 600;
}
.compare-table tr.recommended td { background: var(--brand-blue-soft); }
.compare-table tr.recommended td:first-child {
  border-left: 3px solid var(--brand-klein); padding-left: 16px;
  font-weight: 700; color: var(--brand-klein);
}
.verdict {
  display: inline-block; font-size: 11px; font-weight: 700;
  padding: 2px 9px; border: 1px solid currentColor; letter-spacing: 0.05em;
}
.verdict.no { color: #B0413E; }
.verdict.partial { color: var(--warning); }
.verdict.yes {
  color: var(--white); background: var(--brand-klein); border-color: var(--brand-klein);
}
```

**HTML**:
```html
<table class="compare-table">
  <thead>
    <tr>
      <th style="width:170px;">選択肢</th>
      <th style="width:230px;">考え方</th>
      <th style="width:120px;">適用可否</th>
      <th>本件での評価</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>選択肢A</strong><br><span style="color:var(--pebble);font-size:11px;">英語サブ</span></td>
      <td>...</td>
      <td><span class="verdict no">適用不可</span></td>
      <td>...</td>
    </tr>
    <tr>
      <td><strong>選択肢B</strong></td>
      <td>...</td>
      <td><span class="verdict partial">条件付き</span></td>
      <td>...</td>
    </tr>
    <tr class="recommended">
      <td><strong>選択肢C(本命)</strong></td>
      <td>...</td>
      <td><span class="verdict yes">採用</span></td>
      <td>採用理由を簡潔に</td>
    </tr>
  </tbody>
</table>
```

---

## Pattern 04: tradeoff-axis

**用途**: 1次元軸上で複数選択肢の位置づけを示す。Pattern 03の補助として下部に配置することが多い。

**HTML**:
```html
<div style="margin-top:36px; border-top: 1px solid var(--border-soft); padding-top: 22px;">
  <div class="label" style="font-size:12px; letter-spacing:0.14em; text-transform:uppercase; color:var(--pebble); font-weight:600;">
    軸ラベル(例: RIGOR vs FEASIBILITY)
  </div>
  <svg class="diagram" viewBox="0 0 1500 130" style="margin-top:14px;">
    <line x1="60" y1="70" x2="1440" y2="70" stroke="#111" stroke-width="1.5"/>
    <polygon points="1440,70 1430,65 1430,75" fill="#111"/>
    <text x="60" y="100" font-size="11" fill="#6F7175" letter-spacing="1">左端ラベル</text>
    <text x="1440" y="100" text-anchor="end" font-size="11" fill="#6F7175" letter-spacing="1">右端ラベル</text>

    <!-- 各マーカー -->
    <g transform="translate(150, 70)">
      <circle r="6" fill="#FFFFFF" stroke="#6F7175" stroke-width="1.5"/>
      <text y="-18" text-anchor="middle" font-size="13" fill="#2F3135" font-weight="600">選択肢A</text>
      <text y="38" text-anchor="middle" font-size="10" fill="#6F7175">短い説明</text>
    </g>

    <!-- 本命マーカー(大きめ + Klein Blue) -->
    <g transform="translate(720, 70)">
      <circle r="11" fill="#002FA7" stroke="#002FA7" stroke-width="2"/>
      <text y="-22" text-anchor="middle" font-size="14" fill="#002FA7" font-weight="700">本命</text>
      <text y="40" text-anchor="middle" font-size="10" fill="#002FA7">採用理由</text>
    </g>

    <g transform="translate(1100, 70)">
      <circle r="6" fill="#FFFFFF" stroke="#6F7175" stroke-width="1.5"/>
      <text y="-18" text-anchor="middle" font-size="13" fill="#2F3135" font-weight="600">選択肢C</text>
    </g>
  </svg>
</div>
```

**カスタマイズポイント**:
- マーカーの x座標(`translate`)は viewBox 幅で位置を決める
- 本命マーカーは半径11、塗りKlein Blue。他は半径6、白塗り

---

## Pattern 05: tiered-options

**用途**: 階層的な選択肢や複数バリアントの提示。例えば「メイン処置 / サブ処置 / 比較対象」のような3階層、または「広い対比 / 中の対比 / 狭い対比」のような並列バリアント。

**追加CSS**:
```css
.tier-card {
  border: 1px solid var(--border-soft); padding: 14px 18px; margin-bottom: 10px;
  display: grid; grid-template-columns: 200px 1fr 130px; gap: 16px; align-items: center;
}
.tier-card.main {
  border: 1.5px solid var(--brand-klein); background: var(--brand-blue-soft);
  position: relative;
}
.tier-card.main::before {
  content: "本命"; position: absolute; top: -10px; left: 18px;
  background: var(--brand-klein); color: white;
  font-size: 10px; padding: 3px 9px; letter-spacing: 0.12em; font-weight: 700;
}
.tier-card .role {
  font-size: 11px; letter-spacing: 0.12em; color: var(--pebble); font-weight: 700;
}
.tier-card.main .role { color: var(--brand-klein); }
.tier-card .var-name { font-size: 18px; font-weight: 700; margin-top: 2px; }
.tier-card.main .var-name { color: var(--brand-klein); }
.tier-card .desc { font-size: 12px; color: var(--stone); line-height: 1.55; }
.tier-card .tag { text-align: right; }
.tier-card .tag-row { font-size: 10px; color: var(--pebble); }
```

**HTML**:
```html
<div class="label" style="margin-bottom:14px;">階層タイトル</div>

<div class="tier-card">
  <div>
    <div class="role">役割A</div>
    <div class="var-name">バリアント1</div>
  </div>
  <div class="desc">説明文。2行程度。</div>
  <div class="tag">
    <div class="tag-row">特性A: <strong>値</strong></div>
    <div class="tag-row">特性B: <strong>値</strong></div>
  </div>
</div>

<div class="tier-card main">
  <div>
    <div class="role">役割B / 本命</div>
    <div class="var-name">バリアント2</div>
  </div>
  <div class="desc">本命の説明。</div>
  <div class="tag">
    <div class="tag-row">特性A: <strong style="color:var(--success);">良好</strong></div>
    <div class="tag-row">特性B: <strong style="color:var(--success);">良好</strong></div>
  </div>
</div>

<div class="tier-card">
  <div>
    <div class="role">役割C</div>
    <div class="var-name">バリアント3</div>
  </div>
  <div class="desc">参考の説明。</div>
  <div class="tag">
    <div class="tag-row">特性A: <strong style="color:var(--warning);">中</strong></div>
  </div>
</div>
```

**意図メモ用の補助ボックス**:
```html
<div style="background: var(--snow); padding: 14px 18px; border-left: 3px solid var(--ink); margin-top: 14px;">
  <div style="font-size:11px; font-weight:700; letter-spacing:0.1em; color:var(--ink); margin-bottom:6px;">
    なぜこの階層化か
  </div>
  <div style="font-size:12px; color:var(--stone); line-height:1.6;">
    意図の説明。
  </div>
</div>
```

---

## Pattern 06: three-category-cards

**用途**: 3つのカテゴリを並列で提示する。「共変量の3カテゴリ(属性/行動/嗜好性)」「リスクの3区分」など。

**追加CSS**:
```css
.cat-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; }
.cat-card { border-top: 2px solid var(--ink); padding-top: 14px; }
.cat-card h4 { font-size: 14px; margin-bottom: 4px; font-weight: 700; }
.cat-card .cat-en {
  font-size: 11px; color: var(--pebble); letter-spacing: 0.1em;
  margin-bottom: 12px;
  font-family: "Helvetica Neue", sans-serif;
}
.cat-card ul { list-style: none; font-size: 13px; line-height: 1.85; color: var(--stone); padding: 0; }
.cat-card li { padding-left: 14px; position: relative; }
.cat-card li::before {
  content: ""; width: 4px; height: 1px; background: var(--fog);
  position: absolute; left: 0; top: 12px;
}
```

**HTML**:
```html
<div class="cat-grid">
  <div class="cat-card">
    <h4>① カテゴリA</h4>
    <div class="cat-en">CATEGORY_A_EN</div>
    <ul>
      <li>項目1</li>
      <li>項目2</li>
      <li>項目3</li>
    </ul>
  </div>
  <div class="cat-card">
    <h4>② カテゴリB</h4>
    <div class="cat-en">CATEGORY_B_EN</div>
    <ul>
      <li>項目1</li>
      <li>項目2 <strong style="color:var(--brand-klein);">(重要)</strong></li>
    </ul>
  </div>
  <div class="cat-card">
    <h4>③ カテゴリC</h4>
    <div class="cat-en">CATEGORY_C_EN</div>
    <ul>
      <li>項目1</li>
    </ul>
  </div>
</div>

<!-- 設計上のポイントを下部に挿入 -->
<div style="margin-top:18px; padding: 12px 18px; background: var(--snow); border-left: 3px solid var(--ink);">
  <span style="font-size:11px;font-weight:700;letter-spacing:0.1em;color:var(--ink);margin-right:12px;">設計上のポイント</span>
  <span style="font-size:13px;color:var(--stone);">補足説明。重要な箇所は<strong>太字</strong>。</span>
</div>
```

---

## Pattern 07: estimand-comparison

**用途**: 3つの選択肢を大きなカードで提示し、選択した本命を強調。「ATT vs ATE vs CATE」「Phase A vs B vs C」などのestimand選択や戦略選択に使う。

**HTML(SVG埋め込み版)**:
```html
<div class="label" style="margin-bottom:14px;">選択肢の比較タイトル</div>

<svg class="diagram" viewBox="0 0 1500 200" xmlns="http://www.w3.org/2000/svg">
  <!-- 本命 (左 / Klein Blue) -->
  <rect x="0" y="0" width="490" height="200" fill="#EAF1FF" stroke="#002FA7" stroke-width="1.5"/>
  <text x="20" y="30" font-size="12" font-weight="700" fill="#002FA7" letter-spacing="2">選択肢A — 採用</text>
  <text x="20" y="62" font-size="18" font-weight="700" fill="#111">本命の名称</text>
  <text x="20" y="92" font-size="13" fill="#2F3135">直感的な意味の説明1行目</text>
  <text x="20" y="112" font-size="13" fill="#2F3135">2行目</text>
  <text x="20" y="148" font-size="11" fill="#002FA7" font-weight="700" letter-spacing="1">なぜ採用</text>
  <text x="20" y="168" font-size="12" fill="#2F3135">理由1</text>
  <text x="20" y="186" font-size="12" fill="#2F3135">/ 理由2</text>

  <!-- 対比1 (中央) -->
  <rect x="510" y="0" width="490" height="200" fill="#FFFFFF" stroke="#DDDDDD" stroke-width="1"/>
  <text x="530" y="30" font-size="12" font-weight="700" fill="#6F7175" letter-spacing="2">選択肢B</text>
  <text x="530" y="62" font-size="18" font-weight="700" fill="#111">名称</text>
  <text x="530" y="92" font-size="13" fill="#2F3135">説明1行目</text>
  <text x="530" y="112" font-size="13" fill="#2F3135">2行目</text>
  <text x="530" y="148" font-size="11" fill="#6F7175" font-weight="700" letter-spacing="1">扱い</text>
  <text x="530" y="168" font-size="12" fill="#6F7175">不採用の理由</text>

  <!-- 対比2 (右) -->
  <rect x="1020" y="0" width="480" height="200" fill="#FFFFFF" stroke="#DDDDDD" stroke-width="1"/>
  <text x="1040" y="30" font-size="12" font-weight="700" fill="#6F7175" letter-spacing="2">選択肢C — 副次</text>
  <text x="1040" y="62" font-size="18" font-weight="700" fill="#111">名称</text>
  <text x="1040" y="92" font-size="13" fill="#2F3135">説明</text>
  <text x="1040" y="148" font-size="11" fill="#6F7175" font-weight="700" letter-spacing="1">扱い</text>
  <text x="1040" y="168" font-size="12" fill="#6F7175">副次扱いの理由</text>
</svg>
```

---

## Pattern 08: step-flow-with-mockup

**用途**: 分析・実装ステップを5段階で示し、下部にアウトプットイメージ(チャート + 文章フォーマット)を配置。

**追加CSS**:
```css
.step-flow { display: grid; grid-template-columns: repeat(5, 1fr); gap: 0; margin-bottom: 28px; }
.step { padding: 16px 18px 14px 18px; border-top: 2px solid var(--ink); position: relative; }
.step .step-num {
  font-family: "Helvetica Neue", sans-serif;
  font-size: 12px; color: var(--brand-klein); font-weight: 700;
  letter-spacing: 0.1em; margin-bottom: 4px;
}
.step h4 { font-size: 15px; font-weight: 700; margin-bottom: 6px; }
.step p { font-size: 12px; color: var(--pebble); line-height: 1.55; }
.step:not(:last-child)::after {
  content: ""; position: absolute; right: -6px; top: 28px;
  width: 0; height: 0;
  border-top: 5px solid transparent; border-bottom: 5px solid transparent;
  border-left: 7px solid var(--fog);
}
```

**HTML**:
```html
<div class="step-flow">
  <div class="step">
    <div class="step-num">STEP 01</div>
    <h4>ステップ1名</h4>
    <p>2-3行の説明</p>
  </div>
  <div class="step">
    <div class="step-num">STEP 02</div>
    <h4>ステップ2名</h4>
    <p>説明</p>
  </div>
  <!-- ... step 03, 04, 05 -->
</div>

<!-- アウトプットイメージ -->
<div style="display: grid; grid-template-columns: 1.3fr 1fr; gap: 36px; margin-top: 12px;">
  <div>
    <div class="label" style="margin-bottom:12px;">アウトプット① 数値の可視化</div>
    <svg class="diagram" viewBox="0 0 800 320">
      <!-- バーチャート、ファンチャート等 -->
      <line x1="120" y1="40" x2="120" y2="260" stroke="#111" stroke-width="1"/>
      <line x1="120" y1="260" x2="780" y2="260" stroke="#111" stroke-width="1"/>
      <!-- 本命バー(Klein Blue) + 比較バー(グレー) -->
    </svg>
  </div>

  <div>
    <div class="label" style="margin-bottom:12px;">アウトプット② 文章化フォーマット</div>
    <div style="border: 1.5px solid var(--brand-klein); padding: 18px 22px; background: var(--brand-blue-soft); margin-bottom: 12px;">
      <div style="font-size: 11px; color: var(--brand-klein); letter-spacing: 0.1em; font-weight: 700; margin-bottom: 8px;">
        本命メトリクス
      </div>
      <div style="font-size: 13px; line-height: 1.65;">
        指標名:<br>
        <strong style="font-size: 22px; color: var(--brand-klein); font-family: 'Helvetica Neue', sans-serif;">¥ X,XXX</strong>
        <span style="font-size: 11px; color: var(--pebble);"> (95%CI: A − B)</span>
      </div>
    </div>
    <div style="border: 1px solid var(--border-soft); padding: 14px 18px;">
      <div style="font-size: 11px; color: var(--pebble); letter-spacing: 0.1em; font-weight: 700; margin-bottom: 6px;">
        参考メトリクス
      </div>
      <div style="font-size: 13px;">
        <strong style="font-size: 18px;">¥ Y</strong>
        <span style="font-size: 11px; color: var(--pebble);"> ※注釈</span>
      </div>
    </div>
  </div>
</div>
```

**プレースホルダ規約**:
- 数値は `¥ X` `¥ X,XXX` 等のプレースホルダを使う
- 信頼区間は `(95%CI: A − B)` のようにアルファベット
- 実数値を入れる場合は必ずユーザー確認を取る

---

## Pattern 09: limitation-matrix

**用途**: 限界事項を「項目 / 説明 / 対応」の3列マトリクスで提示。「対応」列にKlein Blueの左ボーダーを付け、誠実な姿勢を示す。

**追加CSS**:
```css
.limit-row {
  display: grid; grid-template-columns: 240px 1fr 1fr; gap: 24px;
  padding: 18px 0; border-bottom: 1px solid var(--border-soft);
}
.limit-row:first-of-type { border-top: 1px solid var(--ink); }
.limit-row h4 { font-size: 16px; font-weight: 700; }
.limit-row .lim-en {
  font-size: 11px; color: var(--pebble); margin-top: 4px;
  letter-spacing: 0.08em; font-family: "Helvetica Neue", sans-serif;
}
.limit-row .body-text { font-size: 13px; color: var(--stone); line-height: 1.65; }
.limit-row .mitigation {
  font-size: 13px; color: var(--brand-klein); line-height: 1.65;
  padding-left: 16px; border-left: 2px solid var(--brand-klein);
}
.limit-row .mitigation .mit-label {
  font-size: 10px; letter-spacing: 0.14em; text-transform: uppercase;
  font-weight: 700; display: block; margin-bottom: 3px;
}
```

**HTML**:
```html
<div class="limit-row">
  <div>
    <h4>限界項目1</h4>
    <div class="lim-en">LIMITATION_KEY_1</div>
  </div>
  <div class="body-text">
    限界の説明。何ができないか、なぜできないかを2-3行で。
  </div>
  <div class="mitigation">
    <span class="mit-label">対応</span>
    どう緩和するか。具体的な手法名を含めると説得力が出る。
  </div>
</div>

<div class="limit-row">
  <div>
    <h4>限界項目2</h4>
    <div class="lim-en">LIMITATION_KEY_2</div>
  </div>
  <div class="body-text">説明</div>
  <div class="mitigation"><span class="mit-label">対応</span>対応策</div>
</div>

<!-- ... 4-5項目が読みやすい上限 -->
```

**設計の意図**:
- 「対応」列は**必ず埋める**。「対応なし」のままだと誠実さが伝わらない
- 限界項目は3-5個が読みやすい。10個以上書くと逆に薄く見える

---

## Pattern 10: phased-roadmap

**用途**: フェーズ別のロードマップを左側に、議論項目を右側に並べる締めスライド。

**追加CSS**:
```css
.s8-layout { display: grid; grid-template-columns: 1.4fr 1fr; gap: 50px; height: 100%; }
.phase {
  display: grid; grid-template-columns: 90px 1fr; gap: 20px;
  padding: 16px 0; border-bottom: 1px solid var(--border-soft);
}
.phase:first-child { border-top: 1px solid var(--ink); }
.phase .ph-label {
  font-family: "Helvetica Neue", sans-serif;
  font-size: 11px; letter-spacing: 0.14em; color: var(--pebble);
  font-weight: 700; padding-top: 3px;
}
.phase.current .ph-label { color: var(--brand-klein); }
.phase h4 { font-size: 16px; font-weight: 700; margin-bottom: 4px; }
.phase.current h4 { color: var(--brand-klein); }
.phase p { font-size: 13px; color: var(--pebble); line-height: 1.55; }

.discussion-item {
  padding: 14px 0; border-bottom: 1px solid var(--border-soft);
  display: grid; grid-template-columns: 28px 1fr; gap: 12px;
}
.discussion-item:first-of-type { border-top: 1px solid var(--ink); }
.discussion-item .qnum {
  font-family: "Helvetica Neue", sans-serif;
  font-size: 14px; color: var(--brand-klein); font-weight: 700;
}
.discussion-item h4 { font-size: 14px; font-weight: 700; margin-bottom: 3px; }
.discussion-item p { font-size: 12px; color: var(--pebble); line-height: 1.5; }
```

**HTML**:
```html
<div class="s8-layout">
  <!-- 左: ロードマップ -->
  <div>
    <div class="label" style="margin-bottom:14px;">ロードマップタイトル</div>

    <div class="phase current">
      <div class="ph-label">PHASE 01<br>本PoC</div>
      <div>
        <h4>現フェーズ名</h4>
        <p>説明。何をやるか、何を残すか。</p>
      </div>
    </div>

    <div class="phase">
      <div class="ph-label">PHASE 02</div>
      <div>
        <h4>次フェーズ名</h4>
        <p>説明</p>
      </div>
    </div>

    <div class="phase">
      <div class="ph-label">PHASE 03</div>
      <div>
        <h4>...</h4>
        <p>...</p>
      </div>
    </div>

    <div class="phase">
      <div class="ph-label">PHASE 04</div>
      <div>
        <h4>...</h4>
        <p>...</p>
      </div>
    </div>
  </div>

  <!-- 右: 議論項目 -->
  <div>
    <div class="label" style="margin-bottom:14px;">本日議論したい論点</div>

    <div class="discussion-item">
      <div class="qnum">Q1</div>
      <div>
        <h4>論点1の問い</h4>
        <p>具体的に何を聞きたいか。</p>
      </div>
    </div>

    <div class="discussion-item">
      <div class="qnum">Q2</div>
      <div>
        <h4>論点2</h4>
        <p>...</p>
      </div>
    </div>

    <!-- Q3, Q4 -->
  </div>
</div>
```

**設計のポイント**:
- 現フェーズには `.current` クラスを付けてKlein Blueでマーク
- 議論項目は3-5個が適切。「フィードバックが欲しい具体的な論点」に絞る
- 「ご質問ありますか?」のような汎用的な締めは避ける

---

## Pattern 11: concept-schematic

**用途**: 1 つの系(システム / 仕組み / データフロー)を手書き SVG の平面模式図で示す。Pattern 02(dual-panel)が左右 2 概念の対比なのに対し、本パターンは「要素 + 関係」を 1 枚の図にまとめる。表やカードの上に補助図(スリム版)として置くと、密度の高いスライドに概念の見取り図を与えられる。主役オブジェクトとしても使える。

**設計方針**:
- 要素 = 矩形ブロック。関係 = 矢印・破線・内包枠で表す
- 内包(グループが要素を含む)は枠で囲い、枠外の要素との連携は破線で示す
- 主役・本命ノードだけ Klein Blue、残りはインク / グレーの線画
- ラベルは SVG text。長文は焼き込まず、詳細は隣接する表・カードに逃がす
- viewBox で固定。補助バンドなら横長スリム(~1500x130)、主役オブジェクトなら縦を広げる(~1500x430)

**追加CSS**(補助バンドとして表・カードの上に置く場合):
```css
.viz-strip {
  margin-bottom: 18px; padding-bottom: 16px;
  border-bottom: 1px solid var(--border-soft);
}
.viz-strip svg { display: block; width: 100%; height: auto; }
```

**HTML**(「内包 + 外部連携 + エンジン」型の模式図 — 表の上に補助バンドとして配置):
```html
<div class="viz-strip">
  <svg class="diagram" viewBox="0 0 1500 124" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
    <defs>
      <marker id="schemaArr" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto">
        <polygon points="0 0, 9 4.5, 0 9" fill="#002FA7"/>
      </marker>
    </defs>
    <!-- 内包枠: グループが要素 A・B を含む -->
    <rect x="150" y="8" width="586" height="72" rx="8" fill="none" stroke="#002FA7" stroke-width="1.6"/>
    <rect x="166" y="1" width="214" height="14" fill="#FFFFFF"/>
    <text x="172" y="12" font-size="11" fill="#002FA7" font-weight="700" letter-spacing="0.04em">グループ名（器）</text>
    <!-- 要素 A・B: 枠の内側 -->
    <rect x="170" y="20" width="546" height="26" fill="#EAF1FF" stroke="#002FA7" stroke-width="1.2"/>
    <text x="188" y="37" font-size="13" fill="#002FA7" font-weight="700">要素 A</text>
    <rect x="170" y="50" width="546" height="26" fill="#EAF1FF" stroke="#002FA7" stroke-width="1.2"/>
    <text x="188" y="67" font-size="13" fill="#002FA7" font-weight="700">要素 B</text>
    <!-- 要素 C: 枠外。破線コネクタで連携 -->
    <rect x="170" y="92" width="546" height="26" fill="#F6F5F2" stroke="#A9AAAD" stroke-width="1.2" stroke-dasharray="5 3"/>
    <text x="188" y="109" font-size="13" fill="#6F7175" font-weight="700">要素 C（枠外）</text>
    <line x1="116" y1="105" x2="170" y2="105" stroke="#002FA7" stroke-width="1.4" stroke-dasharray="4 3"/>
    <text x="46" y="102" font-size="10.5" fill="#002FA7" font-weight="700">連携</text>
    <text x="38" y="115" font-size="10.5" fill="#6F7175">外部参照</text>
    <!-- エンジン / 処理ノードが全要素を横断参照 -->
    <path d="M716 33 C 812 33, 814 66, 896 66" fill="none" stroke="#002FA7" stroke-width="1.5" marker-end="url(#schemaArr)"/>
    <path d="M716 63 C 802 63, 808 66, 896 66" fill="none" stroke="#002FA7" stroke-width="1.5" marker-end="url(#schemaArr)"/>
    <path d="M716 105 C 814 105, 810 66, 896 66" fill="none" stroke="#002FA7" stroke-width="1.5" marker-end="url(#schemaArr)"/>
    <rect x="902" y="38" width="468" height="56" rx="10" fill="#FFFFFF" stroke="#002FA7" stroke-width="1.6"/>
    <text x="938" y="64" font-size="14.5" fill="#002FA7" font-weight="700">エンジン / 処理ノード</text>
    <text x="938" y="83" font-size="12" fill="#2F3135">＝ 横断参照と生成の役割</text>
  </svg>
</div>
```

**カスタマイズポイント**:
- 内包枠で「内 / 外」「対象 / 対象外」を視覚化できる(○/△ バッジの代わり)
- 補助バンドとして使う場合、下に詳細表(Pattern 03)やカードを置き、図は見取り図に徹する
- 主役オブジェクトにする場合は viewBox を縦に広げ、各ブロックを大きくして注釈を増やす
- これは旧 codex 生成版「isometric-diagram」の手書き SVG 後継。生成画像は品質が不安定なため使わない
- 平面の模式図はこの Pattern 11、**立体（アイソメ）で「記憶に残る主役図」にしたいときは Pattern 13: isometric-concept** を使う

---

## Pattern 12: visual-band(transition strip)

**用途**: トップメッセージと主役オブジェクトの間に挟む、変化・遷移・段階を表す横長スリムな SVG 帯。AS-IS→TO-BE、Before→After、個人→組織 などの「動き」を補助的に可視化し、カード・表が続くデッキの視覚的単調さを和らげる。**主役オブジェクトではなく補助要素**。

**設計方針**:
- 高さは控えめ(viewBox ~1500x80)。`.viz-strip`(Pattern 11 と共通)で margin と下罫線
- 左に変化前(グレー・不揃い)、中央に矢印、右に変化後(整列・Klein Blue アクセント数個)
- 「動き」が一目で伝われば十分。要素を詰め込まない
- 1 スライドにつき 1 本まで。これを主役オブジェクトに昇格させない

**HTML**(AS-IS→TO-BE の変化を表す帯 — トップメッセージ直下に配置):
```html
<div class="viz-strip">
  <svg class="diagram" viewBox="0 0 1500 80" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
    <!-- 変化前: 不揃いに散らばった要素(グレー) -->
    <g fill="#FFFFFF" stroke="#A9AAAD" stroke-width="1.3">
      <rect x="72" y="16" width="18" height="18" transform="rotate(-9 81 25)"/>
      <rect x="170" y="40" width="18" height="18" transform="rotate(8 179 49)"/>
      <rect x="122" y="6" width="18" height="18" transform="rotate(13 131 15)"/>
      <rect x="248" y="30" width="18" height="18" transform="rotate(-6 257 39)"/>
      <rect x="332" y="9" width="18" height="18" transform="rotate(9 341 18)"/>
      <rect x="300" y="44" width="18" height="18" transform="rotate(-12 309 53)"/>
      <rect x="412" y="34" width="18" height="18" transform="rotate(6 421 43)"/>
      <rect x="458" y="12" width="18" height="18" transform="rotate(-8 467 21)"/>
    </g>
    <text x="74" y="74" font-size="11.5" fill="#6F7175" letter-spacing="0.5">変化前の状態(AS-IS)</text>
    <!-- 遷移の矢印 -->
    <line x1="620" y1="36" x2="952" y2="36" stroke="#002FA7" stroke-width="1.8"/>
    <polygon points="952,36 936,28 936,44" fill="#002FA7"/>
    <text x="620" y="22" font-size="10.5" fill="#6F7175" letter-spacing="0.18em">TRANSITION</text>
    <!-- 変化後: 整列した要素 + Klein Blue アクセント -->
    <g>
      <rect x="1020" y="6"  width="20" height="20" fill="#F6F5F2" stroke="#B7B7B7" stroke-width="1.2"/>
      <rect x="1092" y="6"  width="20" height="20" fill="#EAF1FF" stroke="#002FA7" stroke-width="1.4"/>
      <rect x="1164" y="6"  width="20" height="20" fill="#F6F5F2" stroke="#B7B7B7" stroke-width="1.2"/>
      <rect x="1236" y="6"  width="20" height="20" fill="#F6F5F2" stroke="#B7B7B7" stroke-width="1.2"/>
      <rect x="1308" y="6"  width="20" height="20" fill="#EAF1FF" stroke="#002FA7" stroke-width="1.4"/>
      <rect x="1380" y="6"  width="20" height="20" fill="#F6F5F2" stroke="#B7B7B7" stroke-width="1.2"/>
      <rect x="1020" y="34" width="20" height="20" fill="#F6F5F2" stroke="#B7B7B7" stroke-width="1.2"/>
      <rect x="1092" y="34" width="20" height="20" fill="#F6F5F2" stroke="#B7B7B7" stroke-width="1.2"/>
      <rect x="1164" y="34" width="20" height="20" fill="#EAF1FF" stroke="#002FA7" stroke-width="1.4"/>
      <rect x="1236" y="34" width="20" height="20" fill="#F6F5F2" stroke="#B7B7B7" stroke-width="1.2"/>
      <rect x="1308" y="34" width="20" height="20" fill="#F6F5F2" stroke="#B7B7B7" stroke-width="1.2"/>
      <rect x="1380" y="34" width="20" height="20" fill="#F6F5F2" stroke="#B7B7B7" stroke-width="1.2"/>
    </g>
    <text x="1020" y="74" font-size="11.5" fill="#002FA7" letter-spacing="0.5" font-weight="700">変化後の状態(TO-BE)</text>
  </svg>
</div>
```

**カスタマイズポイント**:
- 散らばり / 整列のほか、段階バー(個人→チーム→組織)や Before/After のミニ図でもよい
- Klein Blue は変化後の数個(視覚面積 5-12%)に絞る
- ラベルは短く。詳細は下のカード・表で語る

---

## Pattern 13: isometric-concept(アイソメトリック概念図)

**用途**: **節目スライド**（表紙・章マップ・全体像・運用イメージなど structural / concept スライド）の主役に、手書きのアイソメトリック概念図を置く。文字主体のデッキに「図の形」で記憶のアンカーを与える。Pattern 11（平面模式図）の立体版で、グラフィカルな質感（接地影・面の陰影・小ディテール）で印象を立てつつ consulting calm を崩さない。

**置く場所（節目限定）**:
- ✓ 表紙のヒーロー、章マップ／章扉、全体像（共通基盤＋枝分かれ）、運用ループ
- ✗ 観点カードが密なスライド（チェックリスト 3カラム・2×2・table・掲載ボックス）には置かない ── 文字を優先し、はみ出させない

**設計キット（必ず守る）**:
- **グレー 3 トーンの面＝立体の形**: 天面 `--iso-top #FBFBFA` / 左面 `--iso-left #E7E7E4` / 右面 `--iso-right #D5D5D1`、輪郭 `--iso-line #6F7175`・`stroke-width:1.4`・`stroke-linejoin:round`（本文の `.ic` と同じ線質）。これは装飾ではなく「形」の情報設計（design-system.md「グレー面陰影は『形』であり装飾ではない」参照）。
- **主役ノードだけ Klein Blue（1 図 1 ノード）**: その図の核を 1 ブロックだけ青で示す。面は `#EAF1FF / #C9D8F5 / #AFC4EF`、輪郭・ラベルは `#002FA7`。第 2 ブランドカラーは増やさない。
- **ソフト接地影**: デッキ冒頭の `<defs>` に `<filter id="iso-shadow"><feGaussianBlur stdDeviation="7"/></filter>` を 1 つ定義し、各立体の下に淡いだ円（`fill="#2F3135" opacity="0.12" filter="url(#iso-shadow)"`）を敷く。これも「接地＝立体がそこに在る」の表現で、派手なドロップシャドウとは別物。
- **小ディテールで意味を補う**（任意）: 立体の上に小さな線画アイコン（虫眼鏡＝解析・分析、モニタ＋バー＝可視化/ダッシュボード、菱形＝示唆、データ層の薄い線＝マート 等）。意味と 1:1 のときだけ。
- **ラベルは SVG に焼き込まず横書き**: text 要素は水平（傾けない）、投影下限 12px。長文は隣接カードへ逃がす。
- **`viewBox` 固定＋フィット**: 主役カードに入れるときは `preserveAspectRatio="xMidYMid meet"` ＋ `flex:1; min-height:0` で残り空間にフィットさせる（`height:auto` の固定だと枠を超えてクリップするので、はみ出し回避にはフィット方式が安全）。帯として使うときは `width:100%; height:auto`。

**形のボキャブラリ ── 立方体だけにしない（重要）**: 立方体/スラブの反復は「箱ばっかり」で単調・安っぽく見える。**意味に合った多様なアイソメ形**を使い分ける（すべてグレー3トーン線画＋主役のみ青）:

| 形 | 作り方の要点 | 何を表すか |
|---|---|---|
| プラットフォーム/スラブ | 薄い大きな箱＋天面に淡いグリッド線 | 土台・共通基盤 |
| 円柱（DB ドラム） | 天面だ円＋側面＋前面の半だ円リッジ2本 | データ・データストア・マート |
| モニタ（スタンド付き画面） | 傾いた平行四辺形の画面＋薄い奥行き面＋棒グラフ＋スタンド | 可視化・ダッシュボード |
| 折れ線グラフ | 平らなタイル（ダイヤ）＋上昇するポリライン＋点 | 解析・モデリング |
| 虫眼鏡 | 円＋柄。中に小さな上昇マーク | 考察・裏取り・レビュー |
| 書類/重ね書類 | 立った平行四辺形＋本文線。重ねてナレッジ、★で正本 | 設計書・観点ファイル・ナレッジ |
| ゲージ（半円メーター） | 半円アーク＋針＋中心点 | 検証・運用監視 |
| チェック付き書類 | 書類＋✓ | 要件・指標・チェックリスト |

1 つの図、および 1 つの帯（4 工程など）の中で **同じ形を反復させない**。工程フローの帯は各ステップを別々の形（書類→円柱→グラフ→虫眼鏡 等）にすると、下の詳細フローと対応しつつ記憶に残る。下記キューブのレシピは「土台」や数合わせの汎用ブロックに留め、主役・各ノードは上表の形から選ぶ。

**アイソメ立体（箱）の作り方（再利用できる座標レシピ）**: 箱は「天面ダイヤ＋左面＋右面」の 3 パスで描く。天面中心 `(cx,cy)`・半幅 `W`・ダイヤ半高 `Hd=W/2`・高さ `H` とすると:
```
天面: M cx,(cy-Hd) L (cx+W),cy L cx,(cy+Hd) L (cx-W),cy Z      ← fill #FBFBFA
左面: M (cx-W),cy L cx,(cy+Hd) L cx,(cy+Hd+H) L (cx-W),(cy+H) Z ← fill #E7E7E4
右面: M (cx+W),cy L cx,(cy+Hd) L cx,(cy+Hd+H) L (cx+W),(cy+H) Z ← fill #D5D5D1
```
主役は同じ式で fill を `#EAF1FF / #C9D8F5 / #AFC4EF`・stroke を `#002FA7` に。

**HTML（主役カードに入れる「共通基盤＋主役キーストーン＋2タワー」型 — 最小例）**:
```html
<!-- デッキ冒頭の隠し <defs> に 1 度だけ -->
<filter id="iso-shadow" x="-40%" y="-40%" width="180%" height="190%"><feGaussianBlur stdDeviation="7"/></filter>

<div class="card" style="flex:1.3; display:flex; flex-direction:column;">
  <div class="cap">共有の構造 ── 土台の上に主役が立つ</div>
  <svg viewBox="0 0 820 470" preserveAspectRatio="xMidYMid meet" style="width:100%; flex:1; min-height:0;" aria-hidden="true">
    <ellipse cx="410" cy="452" rx="296" ry="17" fill="#2F3135" opacity="0.13" filter="url(#iso-shadow)"/>
    <!-- 土台スラブ（薄い大ブロック・グレー3面） -->
    <path d="M410,148 L698,280 L410,412 L122,280 Z" fill="#FBFBFA" stroke="#6F7175" stroke-width="1.4" stroke-linejoin="round"/>
    <path d="M122,280 L410,412 L410,442 L122,310 Z" fill="#E7E7E4" stroke="#6F7175" stroke-width="1.4" stroke-linejoin="round"/>
    <path d="M698,280 L410,412 L410,442 L698,310 Z" fill="#D5D5D1" stroke="#6F7175" stroke-width="1.4" stroke-linejoin="round"/>
    <!-- 主役キーストーン（青・1図1ノード） -->
    <path d="M410,171 L494,210 L410,249 L326,210 Z" fill="#EAF1FF" stroke="#002FA7" stroke-width="1.7" stroke-linejoin="round"/>
    <path d="M326,210 L410,249 L410,305 L326,266 Z" fill="#C9D8F5" stroke="#002FA7" stroke-width="1.7" stroke-linejoin="round"/>
    <path d="M494,210 L410,249 L410,305 L494,266 Z" fill="#AFC4EF" stroke="#002FA7" stroke-width="1.7" stroke-linejoin="round"/>
    <!-- 左右のタワー・小ディテール・横書きラベルは用途に応じて追加（虫眼鏡=分析, モニタ=可視化 等） -->
    <text x="410" y="392" text-anchor="middle" font-size="15" font-weight="700" fill="#111111">共通基盤</text>
  </svg>
</div>
```

**バリエーション（同じキットで展開）**:
- **章マップの帯**: 4 工程を「昇る 4 ステップ」の小さなアイソメ立方体で表し、境界に ✓ のソフトゲート・破線コネクタを置く。重心側（例: ②データ）を青に。`width:100%` の横長帯（viewBox ~1500×195）で top-message と詳細フローの間に挟む（抽象の絵＋下に具体フロー）。
- **循環ループ**: 破線のアイソメだ円を軌道に、3 ノードのアイソメ立方体を環状配置＋時計回りの青矢印で「育てる/回す」を表す。直線矢印＋「↺」より「ループ」が伝わる。中心の正本ノードを青に。
- **表紙ヒーロー**: 上記スラブ＋主役＋2タワーを縮約し、タイトル脇の右カラムに大きく配置（ラベルは省きトーンセッターに徹する）。

**カスタマイズポイント**:
- 「土台＝共通基盤、その上に主役・枝分かれ」を一目で見せたいとき最適（チップ列や ▲ 矢印の置き換え）。
- 立体の数を増やしすぎない（3〜5 ブロック）。情報は隣接カード／下の詳細フローへ。
- グレー＋青 1 点を厳守。色や陰影を足したくなったら、立体を 1 つ大きくする方向で解決する。

---

## Pattern 14: question-decision(議論ページ)

**用途**: 定例・部会・レビュー会など「その場で決める」資料の【議論】ページ定型。方針（たたき）と判断材料を 1 枚に収めて議論の発散を防ぎ、聞きたいことは Top message の末尾に改行して添える。SKILL.md「ページ役割設計（議論駆動デッキ）」とセットで使う。

**設計原則**:
- **1 論点 1 ページ**。複数の論点があるならページを分ける
- **選択肢は 2〜3 個**。4 個以上あるなら事前に絞ってから出す（網羅比較は Appendix の【参考】ページ＝Pattern 03 comparison-table へ）
- **判断基準は 3 つまで**。判断に効かない背景情報はこのページに置かない
- 推奨案には Klein Blue 枠＋「推奨」バッジ（本命シグナルの規律と整合）
- 聞きたいことは独立した帯にせず、Top message の末尾に `<br>` で改行して 1〜2 文で添える（2026-07-09 改訂: 毎ページに「この場で決めたいこと」帯が並ぶとしつこいという FB を受け、`.qd-ask` 帯を廃止）。持ち帰りになった論点の決め方（誰が・いつまでに）はまとめページのパーキングロットで扱う

### 役割バッジ（デッキ共通コンポーネント）

議論駆動デッキでは全スライド右上に役割バッジを付ける。`<section class="slide role-discuss">` のように slide 要素に役割クラスを与える。

```css
/* ページ役割バッジ（議論駆動デッキ）: スライド右上に役割と時間目安を表示 */
.role-badge { position: absolute; top: 62px; right: 70px; display: flex; align-items: center; gap: 10px; }
.role-badge .tag { font-size: 14px; font-weight: 700; letter-spacing: 0.12em; padding: 6px 16px; border: 1.5px solid var(--border-soft); }
.role-badge .time { font-size: 13px; font-weight: 600; color: var(--pebble); }
.role-report    .role-badge .tag { background: var(--snow); color: var(--stone); }
.role-confirm   .role-badge .tag { background: var(--brand-blue-soft); border-color: var(--brand-blue-soft); color: var(--brand-klein); }
.role-discuss   .role-badge .tag { background: var(--brand-klein); border-color: var(--brand-klein); color: var(--white); }
.role-reference .role-badge .tag { background: var(--white); color: var(--pebble); }
```

```html
<!-- 各スライドの .slide-eyebrow の直前に置く -->
<div class="role-badge"><span class="tag">議論</span><span class="time">10 分</span></div>
```

【報告】= `role-report`、【確認】= `role-confirm`、【議論】= `role-discuss`、【参考】= `role-reference`。議論バッジだけ Klein Blue 塗り（このデッキの主役ページであることを示す）。

### 議論ページ本体

```css
.qd-options { display: grid; grid-template-columns: repeat(2, 1fr); gap: 26px; }
.qd-option { border: 1.5px solid var(--border-soft); background: var(--white); padding: 28px 30px; display: flex; flex-direction: column; gap: 14px; position: relative; }
.qd-option.recommended { border: 2px solid var(--brand-klein); }
.qd-reco { position: absolute; top: -14px; left: 26px; background: var(--brand-klein); color: var(--white); font-size: 13px; font-weight: 700; letter-spacing: 0.1em; padding: 4px 14px; }
.qd-name { font-size: 21px; font-weight: 700; color: var(--ink); }
.qd-sum { font-size: 16px; color: var(--stone); line-height: 1.7; }
.qd-points { list-style: none; display: flex; flex-direction: column; gap: 8px; font-size: 16px; color: var(--stone); }
.qd-points li { padding-left: 26px; position: relative; }
.qd-points li.pro::before { content: "○"; position: absolute; left: 0; color: var(--brand-klein); font-weight: 700; }
.qd-points li.con::before { content: "△"; position: absolute; left: 0; color: var(--pebble); font-weight: 700; }
.qd-criteria { margin-top: 24px; display: flex; align-items: center; gap: 14px; }
.qd-criteria .chip { font-size: 15px; font-weight: 600; color: var(--stone); background: var(--snow); padding: 7px 16px; }
```

```html
<section class="slide role-discuss" id="s4">
  <div class="role-badge"><span class="tag">議論</span><span class="time">10 分</span></div>
  <div class="slide-eyebrow">04 / DISCUSSION 1</div>
  <h1 class="slide-title">ハンズオンの開催形式</h1>
  <div class="title-rule"></div>
  <p class="top-message">
    <span class="accent">Q1.</span> ハンズオンは 1 回 90 分で通すか、2 回 × 45 分に分けるか。<br>
    案 A（90 分で通す）を推奨としつつ、本日はどちらで進めるかをこの場で決めたいと考えています。
  </p>

  <div class="body">
    <div class="qd-options">
      <div class="qd-option recommended">
        <span class="qd-reco">推奨</span>
        <div class="qd-name">案 A: 1 回 90 分で通す</div>
        <p class="qd-sum">準備〜レビュー〜commit までを 1 セッションで体験し、業務の一連の流れとして定着させる。</p>
        <ul class="qd-points">
          <li class="pro">流れが途切れず、当日中に「動いた」体験まで到達できる</li>
          <li class="pro">日程調整が 1 回で済む</li>
          <li class="con">90 分の拘束。途中離脱者へのフォローが必要</li>
        </ul>
      </div>
      <div class="qd-option">
        <div class="qd-name">案 B: 2 回 × 45 分に分ける</div>
        <p class="qd-sum">第 1 回で環境準備と基本操作、第 2 回でレビュー実践に分けて負荷を下げる。</p>
        <ul class="qd-points">
          <li class="pro">1 回あたりの拘束が短く参加しやすい</li>
          <li class="con">間が空くと第 1 回の内容を忘れる。環境トラブルの再発リスク</li>
        </ul>
      </div>
    </div>
    <div class="qd-criteria">
      <span class="label">判断基準</span>
      <span class="chip">参加者の拘束時間</span>
      <span class="chip">体験の定着度</span>
      <span class="chip">日程調整コスト</span>
    </div>
  </div>

  <div class="footer">
    <span class="left">資料名 | サブタイトル</span>
    <span>04 / 08</span>
  </div>
</section>
```

### 表紙の「本日の問い」リスト（議論駆動デッキの表紙部品）

表紙（または 2 枚目）に本日の問いを 2〜3 個宣言し、議論が逸れたときのアンカーにする。各問いは【議論】ページと 1:1 対応させ、ページ番号を添える。

```css
.today-questions { margin-top: 40px; display: flex; flex-direction: column; gap: 16px; max-width: 1100px; }
.today-questions .tq { display: grid; grid-template-columns: 64px 1fr 90px; align-items: center; gap: 18px; border: 1.5px solid var(--border-soft); background: var(--white); padding: 18px 24px; }
.today-questions .tq-no { font-size: 22px; font-weight: 800; color: var(--brand-klein); }
.today-questions .tq-text { font-size: 19px; font-weight: 600; color: var(--ink); }
.today-questions .tq-page { font-size: 14px; color: var(--pebble); text-align: right; }
```

```html
<div class="today-questions">
  <div class="tq"><span class="tq-no">Q1</span><span class="tq-text">ハンズオンは 1 回 90 分か、2 回 × 45 分か</span><span class="tq-page">→ p.4</span></div>
  <div class="tq"><span class="tq-no">Q2</span><span class="tq-text">対象テンプレートは最小版で開始してよいか</span><span class="tq-page">→ p.5</span></div>
</div>
```

**カスタマイズポイント**:
- 選択肢 3 個なら `.qd-options` を `repeat(3, 1fr)` に。カード内の文字量を減らして補う
- 「やる / やらない」型の問いなら選択肢カード 2 枚（実施案 / 見送り案）で、見送り案にも誠実に利点を書く
- 推奨を出さずフラットに問う場合は `.recommended` と `.qd-reco` を外す（ただし「推進リードとしての推奨はどちらか」を聞かれたら答えられるよう準備しておく）

---

## パターン組み合わせの推奨

8枚構成の場合の典型的なパターン配置:

| Slide | パターン | 内容例 |
|---|---|---|
| 1 | 01 comparison-cards | 目的・問いの再設計 |
| 2 | 02 dual-panel-diagram | 概念説明 |
| 3 | 03 + 04 table + axis | アプローチ比較 |
| 4 | 05 tiered-options | 設計の中核1 |
| 5 | 06 + 07 categories + estimand | 設計の中核2 |
| 6 | 08 step-flow-with-mockup | 実装手順とアウトプット |
| 7 | 09 limitation-matrix | 限界事項 |
| 8 | 10 phased-roadmap | ロードマップと議論項目 |

これは標準形であり、内容に応じて入れ替え可能。ただし「冒頭に目的、末尾に議論項目」は変えない。

**議論駆動デッキ（定例・部会）の場合**（SKILL.md「ページ役割設計」参照）:

| Slide | 役割 | パターン | 内容例 |
|---|---|---|---|
| 1 | 表紙 | 14 today-questions | 本日の問い 2〜3 個の宣言 |
| 2 | 【報告】 | 06 / 08 | 前回からの進捗（3 点以内） |
| 3 | 【確認】 | 02 / 11 | 前提・解釈の合意 |
| 4 | 【議論】 | **14 question-decision** | 問い 1（1 問い 1 ページ） |
| 5 | 【議論】 | **14 question-decision** | 問い 2 |
| 6 | まとめ | 10 | 決定事項＋持ち帰り論点＋次アクション |
| A1〜 | 【参考】 | 03 / 05 / 09 | 網羅情報（高密度可）。本編から「詳細は Appendix N」で参照 |

Pattern 11(concept-schematic)・12(visual-band)は任意の補助ビジュアル。カード・表が続いて視覚的に単調なときに、各スライドの主役オブジェクトを保ったまま追加して概念図・変化の見取り図を与える。詰め込みすぎると逆効果なので、効くスライド(仕組み説明・目的の AS-IS→TO-BE など)に絞る。
