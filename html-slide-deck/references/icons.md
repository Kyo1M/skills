# アイコン — 対応表・置き方・外部生成の指示書・取り込み手順

`design-system.md` §5 の詳細。アイコンの実体は `assets/icons/<id>.svg`（1 種 1 ファイル）と `assets/icons/sprite.svg`（全 symbol）。`assets/template.dc.html` の `<defs>` は sprite.svg と同内容に保つ。見本は `previews/parts-icons.png`。

## 1. 形式

- `viewBox="0 0 24 24"`、描画は 2〜22 の範囲（余白 2px）
- `fill:none; stroke:currentColor; stroke-width:1.5; stroke-linecap:round; stroke-linejoin:round`
- 角丸なし（rect の `rx` は 1.5 まで）、塗りなし、グラデなし、1 色
- `<symbol id="ic-<name>" viewBox="0 0 24 24">…</symbol>` でスプライトに定義し、`<svg width="32" height="32" style="color:#2F3135"><use href="#ic-<name>"/></svg>` で使う
- 表示サイズ 28〜40px。同じ枚では同じサイズ

## 2. 置き方（design-system.md §5 の再掲）

置く: カード・列の見出し／工程・ステップのノード／章扉・表紙の流れ項目・目次／表の行グループ名・トラック名。
置かない: 箇条書きの各行・文中・フッター・注意帯・タイトル横。
量: 1 枚 1 セット 3〜6 個。色は本文色、強調 1 個だけ Klein Blue。概念と 1:1。

## 3. 概念 → id 対応表

概念名は定例資料の語彙で固定する。同じ概念に別のアイコンを使わない。無い概念はここに行を足してから使う。

| 概念 | id | 形 | 由来 |
|---|---|---|---|
| 調査・探索・検索 | `ic-search` | 虫眼鏡 | 既存 |
| 仕組み・設定・自動化 | `ic-gear` | 歯車 | 既存 |
| 指標・推移・効果 | `ic-chart` | 折れ線 | 既存 |
| AI・生成 | `ic-spark` | 4 芒星 | 既存 |
| 目的・狙い・ゴール | `ic-target` | 同心円 | 既存 |
| 階層・ルール・レイヤ | `ic-layers` | 重なる菱形 | 既存 |
| 工程・流れ・ワークフロー | `ic-flow` | 分岐線 | 既存 |
| ドキュメント・議事録 | `ic-doc` | 折れ角の紙 | 既存 |
| メンバー・チーム | `ic-people` | 人 2 人 | 既存 |
| 画像・スクリーンショット | `ic-image` | 山の絵 | 既存 |
| スケジュール・日程 | `ic-calendar` | カレンダー | 既存 |
| 完了・確認 | `ic-check` | チェック | 既存 |
| ナレッジ・用語集・wiki | `ic-book` | 開いた本 | 既存 |
| リポジトリ・Git・ブランチ | `ic-branch` | ブランチ | 8/27 で追加 |
| コード・SQL・クエリ | `ic-code` | `</>` | 8/27 で追加 |
| チャット・Copilot Chat | `ic-chat` | 吹き出し | 8/27 で追加 |
| 反復・運用・サイクル | `ic-loop` | 循環矢印 | 8/27 で追加 |
| マイルストーン・節目 | `ic-flag` | 旗 | 8/27 で追加 |
| Pull Request・レビュー | `ic-review` | 吹き出し＋チェック | 新規 |
| テーブル定義・表 | `ic-table` | 格子 2×3 | 新規 |
| データベース・BigQuery | `ic-database` | 円筒 | 新規 |
| 検証・テスト | `ic-flask` | フラスコ | 新規 |
| ハンズオン・実践 | `ic-hand` | 手のひら | 新規 |
| 資料・スライド・提案書 | `ic-slide` | 横長の枠＋脚 | 新規 |
| 評価・KPI・計測 | `ic-gauge` | 半円メーター | 新規 |
| チェックリスト・観点 | `ic-list` | 3 行＋チェック | 新規 |
| フォルダ・置き場・SharePoint | `ic-folder` | フォルダ | 新規 |
| 連携・リンク・接続 | `ic-link` | 鎖 2 環 | 新規 |
| セキュリティ・ガードレール | `ic-shield` | 盾 | 新規 |
| 個人・担当者 | `ic-person` | 人 1 人 | 新規 |
| 着想・提案・テーマ候補 | `ic-bulb` | 電球 | 新規 |
| 注意・リスク | `ic-alert` | 三角＋！ | 新規 |
| 時間・工数・所要 | `ic-clock` | 時計 | 新規 |
| Excel・グリッド・元データ | `ic-grid` | 格子 3×3 | 新規 |
| 段階・ステップ・習熟 | `ic-steps` | 階段 | 新規 |
| 方針・方向・進め方 | `ic-compass` | 羅針盤 | 新規 |

対応の取り方の例（定例資料）:
進行表の行「仕組みの整備」= `ic-gear`、「メンバーの利用」= `ic-people`／工程「要件・仕様のドキュメント化」= `ic-doc`、「分析設計」= `ic-compass`、「集計・コード」= `ic-code`、「検証・テスト」= `ic-flask`、「成果物作成」= `ic-slide`／章「評価」= `ic-gauge`、「テーマ候補」= `ic-bulb`、「ミニプロジェクト体制」= `ic-people`。

## 4. 外部の生成 AI に頼むときの指示書

足りないアイコンは Gemini / ChatGPT 等に SVG を作らせてよい。見本として `previews/parts-icons.png` を添え、次の定型文を渡す。

```
24×24 の線アイコンを SVG で 1 つ作ってください。概念: 「<概念名>」（<形の指示: 例「フラスコ、液面の線 1 本」>）。
条件:
- viewBox="0 0 24 24"。描画は 2〜22 の範囲に収める（余白 2px）
- 線のみ。stroke-width 1.5、fill なし、1 色（色は指定しない。currentColor で使います）
- 角丸・グラデ・影・テキスト・背景なし。path / circle / rect / line だけで、要素は 6 個以内
- <svg> 直下に図形要素だけを置く（<g>・<defs>・id・class・style 属性は付けない）
- 同梱の見本画像と同じ太さ・同じ密度に揃える
出力は SVG のコードだけ。
```

英語で頼むとき:

```
Draw one 24×24 line icon as SVG for the concept "<concept>" (<shape hint>). Rules: viewBox="0 0 24 24", keep strokes within 2–22; stroke only, stroke-width 1.5, no fill, single color (do not set color; it will use currentColor); no rounded corners, gradients, shadows, text or background; use only path/circle/rect/line, at most 6 elements, placed directly under <svg> without <g>, <defs>, id, class or style; match the stroke weight and density of the attached sample. Output the SVG code only.
```

## 5. 取り込み手順

1. 受け取った SVG から `fill`・`stroke`・`style`・`class`・`id`・`xmlns:*`・`<g>` を除去し、図形要素だけにする。`stroke-width` が 1.5 以外なら揃える。
2. `assets/icons/<id>.svg` に保存する。形式:
   ```svg
   <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
     <path d="…"/>
   </svg>
   ```
3. `assets/icons/sprite.svg` と `assets/template.dc.html` の `<defs>` に `<symbol id="ic-<id>" viewBox="0 0 24 24">…図形要素…</symbol>` を追記する（両方同内容）。
4. 本ファイル §3 の対応表に概念名・id・形・由来（外部生成なら「生成（Gemini 等）」）を追加する。
5. `assets/previews-src/guidelines/parts-icons.html` に見本を 1 個足し、`node assets/render-previews.mjs` で `previews/parts-icons.png` を更新する。
6. 既存デッキでその概念に別のアイコンを使っていたら、新しい id に揃える。
