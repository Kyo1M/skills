# Slide Patterns

continova v1スライドで使える10種類のパターン。各パターンは `assets/template.html` の基本CSSをベースに、追加のスタイルとHTMLを示す。

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
