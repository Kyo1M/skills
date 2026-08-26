# スライドの型（20 型）とボディ部品

実装時の「型の選び方」と「部品の書き方」。完全なマークアップは `assets/template.dc.html` の同名 `data-label` の `<section>` にある（**複製して中身を差し替える。ゼロから組まない**）。見本画像は `previews/`（`node assets/render-previews.mjs` で再生成）。ルールの正本は `design-system.md`。

構成 md（deck-outline）の「図版指示」にはここにある **型の名前** と、見出し帯カードを使う枚だけ **アイコンの概念名**（`icons.md` の対応表）を書いてもらう。書かれていないときは、この表で選ぶ。アイコンは見出し帯カードの見出しだけに置き、1 枚 0〜4 個（`design-system.md` §5）。

## 0. 型の選び方（早見）

| 伝えたいこと | 型 | 備考 |
|---|---|---|
| 資料の顔・本日の流れ | 01 表紙 | 定例名そのもの。流れは 4〜6 項目 |
| 章の並び | 02 目次 | 章が 3 つ以上のとき |
| 誰が話すか | 03 自己紹介 | 初回・外部向け |
| 章の切り替え | 04 章扉 | 章が 3 つ以上のとき。定例の簡易構成では省く |
| 前後の対比（いま／目指す） | 05 現状と目指す姿 | 右に画像枠 |
| 3〜4 本の柱 | 06 提供価値（3 軸） | 行ごとに見出し＋一文 |
| 選択肢の比較（依頼時のみ） | 07 比較表 | 推奨行に Klein Blue |
| 手順・段階 | 08 4 ステップ | 横並びのステップカード |
| 誰が何を担うか | 09 推進体制 | 2 者を対にして中央に連絡線 |
| 月単位の大きな流れ | 10 スケジュール（月帯） | 4〜6 ヶ月 |
| 週単位の実績・予定 | 11 ガント（タスク×週） | トラック別・実施済み ✓ |
| 数字で示す効果 | 12 KPI | 130px 明朝の数字 3 つ |
| フェーズの全体像 | 13 ロードマップ | 現在地に Klein Blue |
| 前回の振り返り／今週実施したこと | 14 振り返り | 定例の【振り返り】・左右 2 カラム |
| 方向性の確認（大きな判断なし） | 15 確認事項 | 番号付き 2〜3 件 |
| 1 論点の相談 | 16 議論 | 方針＝たたきを直接提示。比較は依頼時のみ |
| 締め | 17 まとめ | 本日の内容＋次回までの動き（＋お伺いしたいこと） |
| 迷ったとき引く 1 枚 | 18 付録 早見表 | 用語・コツ |
| 連絡先・終わり | 19 お問い合わせ | 外部向け |
| 案件ごとの現在地（仕組み／利用） | 20 進行表 | 定例で更新し続ける 1 枚 |
| 作ったもの・動いたものの報告 | 08 ステップ／20 進行表 ＋ スクショ枠（部品 G） | 上に簡略フローか進行表、下にスクショ 1〜2 枚＋結果 3 行。実物が本文 |
| 前回資料から流用する枚 | 流用枠（ボディ部品 L） | 元 pptx のページを差し替える前提 |
| 上のどれでもない箇条書きだけの枚 | 箇条書き型（ボディ部品 A） | 軽い共有・論点を絞った議論 |

**型を選ぶ前に `design-system.md` §4 の「骨格と詳細」を見る。** 1 枚の骨格（流れ・対比・階層・並列の論点）は型＝図で受け、その中身は箇条書きで書く。列で読む必然がないものを表にしない。

## 1. 各型の要点

表記: **用途**／**構造**（上から）／**アイコン**／**注意**。footer（`data-footer-title` と `data-page`）と右上バッジは全型共通で `position:absolute`。

### 01 表紙（`data-label="表紙"`）
- 用途: 資料の顔。本日の流れ。
- 構造: 左サイドバー 520px（青い正方形 52px、資料名 3 行、日付・区分）｜右: kicker（英字ラベル・日付）→ 明朝タイトル 74〜106px → ルール線 80×5 →「本日の流れ」番号付き 4〜6 項目。
- アイコン: 置かない。
- 注意: **リード文（概要説明）は置かない。** 定例の大タイトルは定例名そのもの。kicker の区切りは `·` か空白（`──` 不可）。区分は「Internal」「Confidential」等の 1 語。

### 02 目次（`目次`）
- 構造: 2 列グリッド。各行は `90px 1fr` で大きな番号（明朝 `#A9AAAD`）＋章名（太字）＋一文。
- アイコン: 置かない。
- 注意: 章が 2 つ以下なら置かない。時間配分は載せても 5 分単位。

### 03 自己紹介（`自己紹介`）
- 構造: 左 440px に写真枠（2:3 破線枠）、右に所属・氏名・役割、経歴 3〜4 行（1 テキストボックス）。
- 注意: 実名・実経歴に差し替え前提。写真は人柄の出る 1 枚。

### 04 章扉（`章扉`）
- 構造: 右上に大きな章番号（明朝 `#E7E5DF` 200px 級）、左に `SECTION 01` kicker → 章名 96px → 狙いの一文。
- アイコン: 章名の左に 40px で 1 個可（章扉は例外的に置いてよい）。
- 注意: 大きな章番号はここだけ。章が 3 つ以上のときに使う。

### 05 現状と目指す姿（`現状と目指す姿`）
- 構造: 左 `1fr` に AS-IS／TO-BE の 2 カード（見出し帯だけ `#F4F2EE`、本文は地）、右 `1.15fr` に画像枠（16:9 or 8:3）＋指示文。
- アイコン: 2 カードの見出しに各 1 個（見出し帯カードなので可）。
- 注意: 見出しは「現状」「目指す姿」の 2 語（`AS-IS` 等の英字は kicker に）。

### 06 提供価値 3 軸（`提供価値`）
- 構造: 3 行。各行 `72px 360px 1fr` = アイコン 40px｜見出し（太字 32px＋英字 kicker）｜一文。核の行だけ `#EAF1FF` 帯＋青罫線。
- アイコン: 行ごとに 1 個（3〜4 個）。行が罫線区切りだけで見出し帯を持たないなら置かない。
- 注意: 4 本以上なら 08 ステップか 20 進行表に。

### 07 比較表（`進め方の選択肢`）
- 構造: ヘッダ行＋3 行。列 `340px 1fr 220px 220px`（選択肢｜概要｜期間｜評価）。推奨行は `#EAF1FF` 地＋左罫 5px Klein Blue＋「推奨」バッジ。評価は ◎○△。
- 注意: 依頼されたときだけ使う（既定は方針の直接提示）。選択肢 2〜3・判断基準 3 つまで。

### 08 4 ステップ（`4ステップ`）
- 構造: `repeat(4,1fr)` のカード列。各カード: `STEP 01` kicker → アイコン 40px → 見出し 32px → 一文。カードは白地＋1px 罫線（塗らない）。
- アイコン: 置かない。現在のステップだけ罫線と kicker を Klein Blue にして示す。
- 注意: 手順が 6 以上なら縦フロー（箇条書き型）か 2 枚に。

### 09 推進体制（`推進体制`）
- 構造: `1fr 220px 1fr`。左右に役割カード 3 段（見出し帯 `#F4F2EE`）、中央に「週次定例」「随時レビュー」の連絡線。
- 注意: 固有名は載せる範囲を絞る（相手側の固有の約束を書かない）。

### 10 スケジュール 月帯（`スケジュール`）
- 構造: `280px repeat(6,1fr)`。フェーズ行に帯（`grid-column:a/b` の塗り矩形）、現在地の帯だけ Klein Blue、最下行にマイルストーン ◆。
- 注意: 週単位の実績・予定は 11 へ。

### 11 ガント タスク×週（`ガントスケジュール`）
- 用途: 週単位の実績・予定を 1 枚に統合する。トラックが分かれても分割しない。
- 構造: **全体を 1 つの grid で組む**（部品 E）。`grid-template-columns:<ラベル幅> repeat(N,1fr)` を 1 箇所だけ宣言し、月ヘッダ・週ヘッダ・トラック見出し・ラベル・帯をすべてその直接の子に置く。週の縦線はオーバーレイ 1 枚。実施済みは緑帯＋「✓」。
- アイコン: 置かない（トラック名にも付けない）。
- 注意: **行ごとの flex ＋入れ子 grid にしない**（月・週・帯の縦線がずれる。この形式で繰り返し起きている不具合）。grid に `gap` を入れない。ラベル `line-height:1.25`。タスク名はラベル列に 1 行で収まる長さに。トラック名は「実装／仕組みづくり」（スラッシュ）。1 枚に載るのは 4 トラック 12 行程度が上限で、超えるならタスクをまとめる。

### 12 KPI（`期待効果`）
- 構造: `repeat(3,1fr)`。各列: 明朝 130px の数字＋単位 → 指標名 32px → 一文。
- 注意: 数値はプレースホルダ。注記は下に 24px で 1 行。

### 13 ロードマップ（`ロードマップ`）
- 構造: `repeat(4,1fr)` の PHASE カード（kicker → 見出し → 一文 → 成果物）。現在地のカードだけ Klein Blue 罫線。
- アイコン: 置かない。

### 14 振り返り（`進捗報告`）
- 用途: 定例の【振り返り】。1 枚で「前回の振り返り」と「今週実施したこと」を対にする。
- 構造: 右上「報告」バッジ。本文は `1fr 1fr` の 2 カラムを弱罫線（`border-left:1px solid #E6E4DE`）で分け、左に前回の振り返り（決定事項・その場で出たアクション）、右に今週実施したことを **箇条書き（部品 A）** で置く。各カラムの頭に太字の見出し行。
- アイコン: 置かない。
- 注意: 表にしない（列で読む用がない）。**「使った時間」の欄は置かない。** 画面共有で見せるものは項目末尾に「（テストの出力を投影）」の形で括弧書きにする。1 枚に収まらないときだけ 2 枚に分ける。

### 15 確認事項（`確認事項`）
- 構造: 右上「確認」バッジ。番号付き 2〜3 件（大きな番号 明朝 50px 超＋太字 1 文＋補足 1 行）。末尾に「ご異議がなければこの方針で進めます」相当の一文。
- 注意: 大きな判断を要するものは 16 へ。

### 16 議論（`ご相談事項`）
- 構造: 右上「議論」バッジ（＋時間）。リード文の末尾に聞きたいことを 1〜2 文（改行して添える）。ボディは方針＝たたきの具体（表・カード・箇条書きのどれか 1 つ）。
- 注意: テンプレートにある「Q.」「判断基準」「決めたいこと」の枠は **使わない**（問いはリード文へ）。比較表は依頼時のみ。1 論点 1 枚。

### 17 まとめ（`まとめ`）
- 構造: 左「本日ご相談した内容」番号付き 3 点｜右「次回までの動き」箇条書き（1 テキストボックス）。必要なときだけ下に「お伺いしたいこと」枠（その場で答えが返る問いのみ）。
- 注意: 「持ち帰り論点」は議論した回だけ。既に合意済みの事項を論点として並べない。

### 18 付録 早見表（`付録 早見表`）
- 構造: 右上「参考」バッジ。左 `1.2fr` に用語表（`280px 1fr`）、右にコツの箇条書き。
- 注意: 付録は「迷ったとき引く 1 枚」に絞る。

### 19 お問い合わせ（`お問い合わせ`）
- 構造: 表紙と同じ左サイドバー＋右に「お気軽にご相談ください」＋連絡先。
- 注意: 社内定例では省く。

### 20 進行表（仕組み／利用の 2 段・横方向にステップ）
- 用途: 案件ごとの現在地を「仕組みの整備」と「メンバーの利用」に分けて示し、定例で更新し続ける。2 案件あれば同じ列構成で 1 枚ずつ。
- 構造: `grid-template-columns:242px repeat(N,1fr)`（N = 運用のステップ数 6〜7）。ヘッダ行: 空セル＋ステップ名（23px 太字）＋工程番号（Klein Blue）。行 1「仕組みの整備」（`#F7FAFF` 地）、行 2「メンバーの利用」（白地）。セルは 24px、先頭に状態記号（✓ 済＝緑 `#1F8A5B`、▶ 進行中＝Klein Blue、時期入り＝予定、未到達＝空欄）。今週動いたセルだけ `#EAF1FF` 地。凡例を表の下に 22px（`data-role="caption"`）で。
- アイコン: 置かない（行グループ名にも付けない）。行グループは地色（`#F7FAFF` / 白）と太字で分ける。
- 注意: 人の動きはセルに人名入りで書き、近況の箇条書きを別に立てない（重複を畳む）。セルは 2 行以内。
- スニペット（骨格。セル内容は差し替え）:

```html
<div style="border:1px solid #D8D6D0; display:grid; grid-template-columns:242px repeat(7,1fr);">
  <!-- ヘッダ -->
  <div style="background:#F4F2EE; border-right:1px solid #E6E4DE; border-bottom:2px solid #111;"></div>
  <div style="background:#F4F2EE; border-right:1px solid #E6E4DE; border-bottom:2px solid #111; padding:12px 14px 8px;">
    <div style="font-size:23px; font-weight:700; color:#2F3135; line-height:1.35;">セットアップ<br>（リポジトリ・環境）</div>
    <div style="font-size:22px; font-weight:700; color:#002FA7; margin-top:8px;">①</div>
  </div>
  <!-- …ステップ列を繰り返し。最後の列は border-right なし -->
  <!-- 行 1: 仕組みの整備 -->
  <div style="background:#F7FAFF; border-right:1px solid #E6E4DE; border-bottom:1px solid #E6E4DE; padding:20px 18px; display:flex; align-items:center; gap:12px;">
    <div style="font-size:25px; font-weight:700; color:#002FA7; line-height:1.35; white-space:nowrap;">仕組みの整備</div>
  </div>
  <div style="background:#F7FAFF; border-right:1px solid #E6E4DE; border-bottom:1px solid #E6E4DE; padding:20px 14px; font-size:24px; line-height:1.4; color:#2F3135;"><span style="color:#1F8A5B; font-weight:700;">✓</span> 完了</div>
  <div style="background:#EAF1FF; border-right:1px solid #E6E4DE; border-bottom:1px solid #E6E4DE; padding:20px 14px; font-size:24px; line-height:1.4; color:#2F3135;"><span style="color:#002FA7; font-weight:700;">▶</span> 段階 1 に着手</div>
  <!-- … -->
  <!-- 行 2: メンバーの利用（白地・border-bottom なし） -->
  <div style="border-right:1px solid #E6E4DE; padding:20px 18px; display:flex; align-items:center; gap:12px;">
    <div style="font-size:25px; font-weight:700; color:#111; line-height:1.35; white-space:nowrap;">メンバーの利用</div>
  </div>
  <div style="border-right:1px solid #E6E4DE; padding:20px 14px; font-size:24px; line-height:1.4; color:#2F3135;">根岸さんが議事録作成を開始</div>
  <!-- … -->
</div>
<div data-role="caption" style="font-size:22px; color:#6F7175; margin-top:14px;">凡例： ✓ 済み ／ ▶ 進行中 ／ 時期入り＝予定 ／ 空欄＝未到達 ／ 淡青地＝今週動いたセル</div>
```

## 2. ボディ部品

文字の役割は `data-role`（`caption` / `badge` / `kicker`）で示す（`design-system.md` §2）。付けない要素は本文（24px 以上）として機械チェックされる。

### A. 箇条書き（1 テキストボックス方式）
- 項目は短い文 1〜2 行。見出しが要るときは「太字見出し行＋本文」か「見出し：本文」。`──` 不可。
- PPTX 手直しのため、箇条書き全体を **1 つの div** に `<br>` 区切りで書く。子の箇条書きは全角スペース 2 つでインデント。行ごとに要素分割しない。
```html
<div style="font-size:27px; line-height:1.65; color:#2F3135;">
  ・テーブル定義の YAML 化をテンプレートに追加し、クレド案件の 6 テーブルに適用しました<br>
  ・<b>正本は Excel</b>：YAML は AI とプログラムに読ませる出力形式で、実データの値は入れません<br>
  　・桁数・規模感・仕様変更の経緯はノート欄に注釈として残します<br>
  ・Excel が更新されたときの YAML の追随は運用を決めていません
</div>
```
- 区切りが要るときは塗りでなく弱罫線 `border-bottom:1px solid #E6E4DE`（1 項目 1 div にしてよい。このときはアイコンを付けない）。
- 青ビュレット版: `・` の代わりに 9px 角 `#002FA7` の `<span style="display:inline-block;width:9px;height:9px;background:#002FA7;margin-right:14px;vertical-align:middle"></span>`。

### B. 見出し帯カード（アイコン付き）
```html
<div style="border:1px solid #D8D6D0;">
  <div style="background:#EAF1FF; border-left:5px solid #002FA7; padding:14px 20px; display:flex; align-items:center; gap:14px;">
    <svg width="32" height="32" style="color:#002FA7; flex:none;"><use href="#ic-flask"/></svg>
    <div style="font-size:30px; font-weight:700; color:#111;">検証・テスト</div>
  </div>
  <div style="padding:18px 22px; font-size:26px; line-height:1.6; color:#2F3135;">・段階 1：AI がサンプルデータと期待値を作り、ローカルで単体テスト<br>・段階 2：BigQuery で実データと突合（ライセンス付与後）</div>
</div>
```
- 見出し帯だけ淡色地。本文は地のまま。強調しないカードは帯を `#F4F2EE`、左罫なし、アイコン色は本文色。

### C. ステップノード列（横フロー）
```html
<div style="display:grid; grid-template-columns:repeat(4,1fr); gap:0;">
  <div style="border:1px solid #D8D6D0; padding:22px 20px; position:relative;">
    <div data-role="kicker" style="font-size:18px; letter-spacing:0.16em; font-weight:700; color:#6F7175;">STEP 01</div>
    <svg width="40" height="40" style="color:#2F3135; margin:12px 0 8px;"><use href="#ic-doc"/></svg>
    <div style="font-size:30px; font-weight:700; color:#111;">要件・仕様のドキュメント化</div>
    <div style="font-size:25px; line-height:1.5; color:#2F3135; margin-top:8px;">議事録・提案書・テーブル定義を AI が読める形に整える</div>
  </div>
  <!-- … 現在のステップは border-color:#002FA7・アイコン color:#002FA7 -->
</div>
```
- 縦フローは同じカードを縦に並べ、間に `▼` 24px `#6F7175`。

### D. 表（一般）
- ヘッダ `#F4F2EE`・`border-bottom:2px solid #111`。セル 24〜26px、`line-height:1.4`。列は `grid` で組む（`<table>` は PPTX 化で崩れやすい）。
- 行グループ名の列にだけアイコン可。

### E. ガント（型 11 の部品）

**1 つの grid にすべてを直接置く。** 列の宣言は本体とオーバーレイの 2 箇所だけにし、同じ値を使う。行ごとの `flex`＋入れ子 `grid` は縦ずれの原因になるので使わない。

```html
<!-- ラベル幅 560px・週 5 列。列の値は本体とオーバーレイで同一にする -->
<div style="position:relative; border:1px solid #D8D6D0;">
  <div style="display:grid; grid-template-columns:560px repeat(5,1fr); align-items:stretch;">
    <!-- 月ヘッダ: ラベル列は空セル、月は grid-column で束ねる -->
    <div style="background:#F4F2EE; border-right:1px solid #E6E4DE;"></div>
    <div data-role="caption" style="grid-column:2/3; text-align:center; padding:5px 0; background:#EAF1FF; border-right:1px solid #E6E4DE; font-size:22px; font-weight:700; color:#002FA7; line-height:1.25;">8 月</div>
    <div data-role="caption" style="grid-column:3/7; text-align:center; padding:5px 0; background:#F4F2EE; font-size:22px; font-weight:700; color:#6F7175; line-height:1.25;">9 月</div>
    <!-- 週ヘッダ -->
    <div data-role="caption" style="padding:5px 20px; background:#F4F2EE; border-right:1px solid #E6E4DE; border-bottom:2px solid #111; font-size:22px; font-weight:700; color:#6F7175; line-height:1.25;">タスク ／ トラック</div>
    <div data-role="caption" style="text-align:center; padding:4px 0; background:#FBFAF8; border-bottom:2px solid #111; font-size:22px; font-weight:700; color:#002FA7; line-height:1.25;">第4週<span data-role="kicker" style="font-size:19px; font-weight:700; color:#fff; background:#002FA7; padding:0 8px; margin-left:6px;">今週</span></div>
    <!-- …残りの週セルを繰り返し（背景 #FBFAF8・border-bottom:2px solid #111） -->
    <!-- トラック見出し: 全幅 -->
    <div data-role="caption" style="grid-column:1/-1; background:#EAF1FF; border-bottom:1px solid #E6E4DE; padding:3px 20px; font-size:22px; font-weight:700; color:#002FA7; letter-spacing:0.06em; line-height:1.25;">実装／仕組みづくり</div>
    <!-- タスク行: ラベル 1 セル＋帯を週の位置に直接置く。帯の無い週もプレースホルダで埋める -->
    <div style="padding:6px 20px; border-bottom:1px solid #F1F0EC; font-size:24px; font-weight:700; color:#111; line-height:1.25; white-space:nowrap;">検証・テスト 段階 1（単体テスト）</div>
    <div style="grid-column:2/4; border-bottom:1px solid #F1F0EC; display:flex; align-items:center;"><div data-role="caption" style="flex:1; margin:0 3px; height:26px; background:#1F8A5B; display:flex; align-items:center; justify-content:center; color:#fff; font-size:22px; font-weight:700; line-height:1.25;">✓ 着手 → 第 1 週に試行</div></div>
    <div style="grid-column:4/7; border-bottom:1px solid #F1F0EC;"></div>
  </div>
  <!-- 週の縦線: オーバーレイ 1 枚。本体と同じ列の値 -->
  <div style="position:absolute; inset:0; display:grid; grid-template-columns:560px repeat(5,1fr); pointer-events:none;"><div></div><div></div><div style="border-left:1px solid #EFEEEA;"></div><div style="border-left:1px solid #EFEEEA;"></div><div style="border-left:1px solid #EFEEEA;"></div><div style="border-left:1px solid #EFEEEA;"></div></div>
</div>
```

- 帯を持たない週も **必ずプレースホルダの div で埋める**（grid の自動配置がずれる）。1 行に置くセルは常に「ラベル 1 ＋ 週を覆う分」。
- 色: 実施済み＝`#1F8A5B`（緑）、予定・進行中＝`#002FA7`、見込み・仮置き＝`#C9D8F5`（文字は `#2F3135`）。
- 行高は帯の `height`（26px）とラベルの `padding`（6px）で決まる。ラベルが折り返すと行が伸びて崩れるので `white-space:nowrap` を付け、名前を 1 行に収める。

### L. 流用枠（前回資料のページを差し替える）

前回資料から流用する枚に置く。デッキ上はタイトル・kicker・役割バッジを通常どおり入れ、ボディをこの枠にする。pptx 化のあと、作り手が元ファイルの該当ページを貼り替える。

```html
<div style="border:2px dashed #B7B7B7; background:#FAFAF8; flex:1; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:14px; padding:40px; color:#6F7175;">
  <div data-role="kicker" style="font-size:20px; letter-spacing:0.16em; font-weight:700; color:#6F7175;">既存ページを流用</div>
  <div style="font-size:30px; font-weight:700; color:#2F3135; text-align:center; line-height:1.5;">20260820_BI部定例.pptx　p.2<br>「（再掲）分析ワークフロー全体像」</div>
  <div style="font-size:24px; line-height:1.5; text-align:center; max-width:1100px;">工程 ①〜⑥ の帯と実装状況。日付だけ更新して差し替える。</div>
</div>
```

- 書くのは **元ファイル名・ページ番号・そのページの見出し**、および差し替え時に更新する箇所を 1 行。
- 元が HTML 資料でまだ pptx 化していないときは、その旨と HTML のファイル名を書く。
- 流用枠は塗りボックスに数えない（地は `#FAFAF8`）。

### F. KPI 数字
- 明朝 130px＋単位 48px、指標名 32px、一文 26px。3 つ横並び。

### G. 画像枠
```html
<div style="border:2px dashed #B7B7B7; background:#FAFAF8; border-radius:6px; aspect-ratio:16/9; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:10px; color:#6F7175;">
  <svg width="40" height="40"><use href="#ic-image"/></svg>
  <div style="font-size:26px; font-weight:700;">イメージ画像</div>
  <div style="font-size:24px; line-height:1.5; text-align:center;">Copilot Chat の画面：モード／モデル選択・# 参照・/ プロンプトが分かる実画面</div>
</div>
```

- 実物のスクショ（報告ページ）: `assets/` に実体があれば破線枠の代わりに `<img src="assets/<deck>/sN-shotM-<slug>.png" style="width:100%; aspect-ratio:16/9; object-fit:cover; border:1px solid #D8D6D0; border-radius:6px;">` を置き、直下にキャプション `<div style="font-size:24px; color:#6F7175; margin-top:8px;">…</div>` を 1 行。無ければ上の破線枠に「何の画面か・どの状態か」の指示文を入れる。2 枚並べるときは同じ高さ、横長の一覧・ツリーは `aspect-ratio:8/3`。

### H. 役割バッジ（右上）
```html
<div style="position:absolute; top:52px; right:96px; display:flex; align-items:center; gap:12px;">
  <span data-role="badge" style="font-size:23px; font-weight:700; letter-spacing:0.1em; padding:8px 22px; border:1.5px solid #D8D6D0; background:#F4F2EE; color:#2F3135;">報告</span>
</div>
```
- 語彙: 報告／確認／議論／参考／再掲。【議論】は `background:#EAF1FF; border-color:#002FA7; color:#002FA7`。時間を添えるなら 5 分単位の 1 語。

### I. 注意帯
- リード文の直下。`background:#FFF4D7; color:#7A5200; border-left:4px solid #A66A00; padding:10px 16px; font-size:23px;`。不要なら置かない。最下部に小さく置かない。

### J. お伺いしたいこと枠（まとめ専用）
```html
<div style="border:1.5px solid #002FA7; background:#EAF1FF; padding:18px 24px;">
  <div style="font-size:22px; letter-spacing:0.14em; font-weight:700; color:#002FA7;">お伺いしたいこと</div>
  <div style="font-size:26px; line-height:1.6; color:#2F3135; margin-top:8px;">・評価のまとめで見る範囲：8 月末までの実績で見て、テーマ B 以降は続けて追う形でよいか</div>
</div>
```
- その場で答えが返る問いだけ。議論ページには置かない。

### K. 強調語句
- `<span style="color:#002FA7; font-weight:700;">…</span>` を 1 ブロック 1 箇所。

## 3. 文字だけの枚の作り方

- タイトル → リード文 1〜3 行 → 部品 A（箇条書き 1 テキストボックス）だけ。天地中央寄せで余白を活かす。
- 議論の論点を絞る枚: 16 議論の骨格（バッジ＋リード文末尾の問い）＋部品 A 3〜5 本。
- 10 本／約 600 字を超えるなら、テーマが割れない範囲で分割を検討する。

## 4. 改訂履歴

- 2026-08-24: アイコンの置き場を見出し帯カードの見出し（と章扉）だけに絞り各型の規定を更新。型 01 のリード文を廃止。型 14 を「振り返り」（左右 2 カラムの箇条書き・時間の欄なし）に作り直し。型 11 と部品 E のガントを 1 grid 構造に。部品 L（流用枠）を追加。
- 2026-08-23: v2 初版。Claude Design export の 19 型＋進行表を標準化。部品 A〜K を整理。
