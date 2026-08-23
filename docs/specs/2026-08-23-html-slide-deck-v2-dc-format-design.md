# html-slide-deck v2 — 事業用スライド DS（C案 Editorial）への載せ替えと `.dc.html` 出力 設計書

- 日付: 2026-08-23
- 対象: `~/Developer/Skills/html-slide-deck`（その場で v2 化）、周辺 skill（deck-outline / deck-critique）、利用リポジトリの規約（dxb-data-ai-workflow-context の AGENTS.md / lint）、Claude Design プロジェクトの CLAUDE.md
- 経緯: brainstorming（2026-08-23）。Claude Design で育てた「事業用スライド デザインシステム」（export: `~/Downloads/事業用スライドテンプレート作成/`）を正本にして、HTML 作成を Claude Code 側に戻す。pptx 化は Claude Design に持ち込む

---

## 1. 背景と目的

- 現行の定例資料づくりは「deck-outline で構成 md → Claude Design で `.dc.html` → pptx 出力 → PowerPoint で手直し」。Claude Design 側に蓄積した制作ルール（`CLAUDE.md`）と Claude Code 側の `html-slide-deck`（continova v1・1672×941・スクロール形式）が別系統で育ち、食い違っている。
- 8/27 定例資料（Claude Design 生成）で出た不満: (1) 文字ばかりでアイコンが少ない、(2) 構成 md から情報が省略されすぎる、(3) 「キーワード ── 説明」の後置き補足が多用されダサい。
  - 根因は Claude Design 側 `CLAUDE.md` の 8/23 指示「箇条書きは『太字キーワード ── 短い説明』1 行以内。理由・経緯は発表者ノートへ」と、「アイコンは意味と 1:1 のときだけ・各行に付けない」の抑制ルール。8/27 v2 には `──` が 62 箇所、アイコンは 17 枚で 18 個。
- 目的: ルールの正本を skill 側の 1 箇所に置き、HTML（`.dc.html`）を手元で作れるようにし、上記 3 点を解消した資料を 8/27 定例から出す。

## 2. 決定事項（brainstorming で確定）

| # | 論点 | 決定 |
|---|------|------|
| D1 | 出力形式 | Claude Design と同じ `.dc.html`（deck-stage・1920×1080）を手元で生成。pptx は Claude Design に持ち込む。持ち込み可否は spike で確認し、不可なら「HTML は手元・pptx は構成 md を Claude Design へ」の現運用に戻す |
| D2 | skill の置き方 | 既存 `html-slide-deck` をその場で v2 化。continova v1 は `references/legacy/` と git 履歴に退避 |
| D3 | 正本テンプレート | `事業用スライドテンプレート.dc.html`（export 内 v1・19 型）。readme の「v2」表記は参照間違い |
| D4 | ルールの正本 | skill の `references/design-system.md` が唯一の正本。Claude Design 側 CLAUDE.md はそこから作る貼り付け用ルール文で置き換える |
| D5 | リード文 | 結論＋判断理由・結果を 1〜3 行。ボディの縮約にしない。経緯の応答文（「前回ご指摘をいただきましたので」）は書かない |
| D6 | ボディ | 構成 md の項目を落とさない。1 項目 1〜2 行の短文＋子の箇条書き 2 階層まで。「太字キーワード ── 説明」の 1 行圧縮はしない |
| D7 | `──` | 全面禁止（タイトル副題・kicker・箇条書き見出し・ガントのトラック名とも）。代替: タイトルは副題なしの名詞句 1 本／見出し付き箇条書きは「太字見出し行＋本文」か全角コロン／トラック名は「実装／仕組みづくり」の 2 語並べ |
| D8 | 発表者ノート | 廃止（`data-speaker-notes` を使わない）。pptx をクライアントに渡すため内情が残るリスクがある。口頭補足は構成 md の「設計判断」節に残し、デッキには入れない |
| D9 | 文字量 | 1 枚 1 テーマ（1 メッセージ）を第一に。文字量（図表同居 7 本/350 字・文字だけ 10 本/600 字）は分割検討の目安であって上限ではない。分けすぎて分からなくなるのを避ける。フォントは 24px を割らない |
| D10 | 文字だけの枚 | 可。箇条書きだけの軽い枚、議論の論点を絞った枚は必要に応じて置く。主役の構造（表・フロー・進行表・カード列）は置けるときに置く |
| D11 | アイコン | 置く場所: カード・列の見出し／工程・ステップのノード／章扉・表紙の流れ項目／表の行グループ名。箇条書きの各行には付けない。1 枚 1 セット 3〜6 個、同サイズ 28〜40px、本文色、強調 1 個だけ Klein Blue。概念とアイコンは 1:1 固定。スプライトを 13 → 30 種前後へ拡張 |
| D12 | デザインイメージ | 19 型＋ボディ部品の PNG 見本を skill に持ち、外部生成 AI（Gemini 等）へのアイコン・図版依頼の指示書をセットにする |

## 3. スコープ / 非スコープ

**スコープ**
- `html-slide-deck` の SKILL・references・assets を v2 に差し替える
- `deck-outline` / `deck-critique` / writing-principles / グローバル CLAUDE.md の整合更新
- dxb-data-ai-workflow-context の AGENTS.md・lint の出力規約更新（`.dc.html`・runtime JS の置き場）
- Claude Design に貼る制作ルール文の生成
- spike（8/27 S1〜S3 の `.dc.html` 化 → Claude Design 持ち込み確認）

**非スコープ**
- HTML → pptx の変換を Claude Code 側で実装すること（Claude Design の機能に任せる）
- 画像・イラストの生成（破線枠＋指示文で差し替え運用。アイコン SVG の外部生成は指示書のみ用意）
- 旧 continova v1 形式で作った既存 deliverable の作り直し

## 4. 成果物（skill の構成）

```
html-slide-deck/
├── SKILL.md                         # v2: .dc.html 出力、Phase 3〜5、構成 md 連携、repo 規約、表示・pptx 導線
├── assets/
│   ├── template.dc.html             # 正本 v1 を複製。スプライト拡張・data-speaker-notes 全廃・footer 構造維持
│   ├── runtime/support.js           # ローカル表示用 runtime（export からコピー。生成先にも同名で置く）
│   ├── runtime/deck-stage.js
│   ├── tokens/{colors,typography,spacing}.css
│   ├── icons/*.svg                  # 個別アイコン（24×24・stroke 1.5・currentColor）
│   ├── icons/sprite.svg             # <symbol> 集約。template.dc.html と同内容
│   ├── check-slides.mjs             # 1920×1080・section 単位・静的サーバ内蔵の機械チェック
│   ├── render-previews.mjs          # 19 型＋部品の PNG 書き出し
│   ├── previews-src/                # 見本 HTML（export の slides/・guidelines/ をコピー、styles.css/tokens 参照を相対に直す）
│   └── package.json                 # playwright-core（既存）
└── references/
    ├── design-system.md             # 正本（§6）
    ├── slide-patterns.md            # 19 型＋ボディ部品: 用途・構造・dc スニペット・PNG リンク
    ├── previews/*.png               # デザインイメージ
    ├── icons.md                     # 配置ルール・概念→id 対応表・外部生成指示書・取り込み手順
    ├── self-review-checklist.md     # v2 観点
    ├── claude-design-rules.md       # Claude Design の CLAUDE.md に貼る制作ルール
    └── legacy/continova-v1/         # 旧 design-system.md / slide-patterns.md / template.html / self-review-checklist.md
```

`~/.claude/skills/html-slide-deck` の symlink はそのまま（実体が v2 になる）。

## 5. 出力契約（生成する `.dc.html` の構造）

- ファイル名: `yyyymmdd_<slug>.dc.html`。repo 配置は `docs/deliverables/`。先頭に HTML コメントの frontmatter（`type: deliverable` / `format: slide` / `derived_from` 等、AGENTS.md 規約どおり）。その直後に `<!DOCTYPE html>`。
- 構造は正本テンプレートと同じ:
  - `<script src="./support.js">` → `<x-dc>` → `<helmet>`（Google Fonts・最小 style）→ アイコン `<svg><defs><symbol id="ic-…">` スプライト → `<x-import component-from-global-scope="deck-stage" from="./deck-stage.js" width="1920" height="1080" hint-size="100%,100%">` → `<section data-label="…" data-screen-label="NN" style="…">` × N → `</x-import></x-dc>` → `<script type="text/x-dc" data-dc-script …>` の logic class（ページ番号 `[data-page]`・資料名 `[data-footer-title]` の振り直し）。
  - `section` には `data-speaker-notes` を付けない。`data-deck-skip` は付録の区切り等に使ってよい。
  - footer の `<span data-footer-title>` と `<span data-page>` の 2 属性は必ず残す（Tweaks 連動）。
  - スタイルは inline（Claude Design の編集性を保つ）。共通 CSS 変数は helmet の `<style>` に `:root` で置いてよいが、色・サイズの実値は inline に書く（PPTX 化で解決されるのは inline のため）。
- runtime: 生成先ディレクトリに `support.js` / `deck-stage.js` を同名で置く（`./support.js` `./deck-stage.js` の相対参照を Claude Design と同じに保つ）。repo では `docs/deliverables/` 直下に 1 組だけ置き git 管理する。
- ローカル表示: `file://` では runtime の fetch が CORS で失敗するため、http 経由で開く（`python3 -m http.server` / `npx -y serve`）。`check-slides.mjs` は自前で静的サーバを立てる。runtime は React/Babel を unpkg から読むため、表示・チェックにはネットワークが要る。
- 画像は生成しない。破線枠 `2px dashed #B7B7B7`＋地 `#FAFAF8`＋「何を写すか」の指示文。

## 6. `references/design-system.md` の内容（正本）

構成: ① 位置づけと正本宣言 ② トークン（色・タイポ・余白。`tokens/*.css` と同値） ③ レイアウト ④ 脱ボックス ⑤ アイコン ⑥ 文章 ⑦ 構成 ⑧ PPTX 手直し前提の作り ⑨ 画像 ⑩ 読者配慮トーン ⑪ 禁止事項一覧

**② トークン（export の `tokens/` をそのまま採用）**
- 色: 地 `#FFFFFF`（オフホワイト版 `#F6F5F2`）／本文 `#2F3135`／タイトル `#111111`／注釈 `#6F7175`／罫線 `#D8D6D0`・弱罫線 `#E6E4DE`／淡ベージュパネル `#F4F2EE`／Klein Blue `#002FA7`（推奨・本命・キー数値・現在地のみ、面積 5〜12%）／淡ブルー `#EAF1FF`／注意帯 `#FFF4D7`+`#7A5200`+左罫 `#A66A00`。
- タイポ: タイトル＝游明朝 → Hiragino Mincho ProN → Noto Serif JP、本文＝Meiryo UI → Hiragino Sans → Yu Gothic → Noto Sans JP。サイズ: 表紙 106 / タイトル 64 / 章扉 96 / リード文 36（28〜38） / カード見出し 32 / 本文 28（26〜30・最低 24） / 補助・フッター・キャプション 24（最低 22） / 装飾的な小見出し（kicker `01 / 〜`・STEP ラベル）のみ 18〜20 可 / KPI 130 / コード最低 21。
- 余白: 1920×1080。本文スライド `padding:56px 96px 104px`＋天地中央寄せ。タイトル下ルール 72×4。footer `bottom:48px`。

**③ レイアウト** 本文スライドは flex column + justify-content:center で全高を使う。footer・右上バッジは absolute。章扉は章が 3 つ以上のときに挟み、大きな章番号は章扉だけ。

**④ 脱ボックス** 塗りボックスは区切る意味があるもの（対比・見出し帯・記入欄・表）だけ、1 枚 2〜3 個まで。列挙は 9px 角の青ビュレット＋弱罫線。カードは見出し帯だけ淡色地。グラデ・影・角丸・ブロブなし。濃ベタ＋白文字は最小限。

**⑤ アイコン** D11 のとおり。加えて: 線アイコンのみ（絵文字・アイコンフォント・ストック画像不可）。`<use href="#ic-…">` 参照。1 デッキ内で同じ概念に別アイコンを使わない。対応表は `icons.md`。

**⑥ 文章** D5〜D10 のとおり。加えて: タイトルは体言止めの名詞句（副題なし）。強調は 1 ブロック 1 箇所（Klein Blue＋太字）。数値はプレースホルダ、実データは確認のうえ差し替え。因果を断定しない。「お伺いしたいこと」枠はまとめにだけ（その場で答えが返る問いだけ）。

**⑦ 構成** 表紙（定例名そのもの・本日の流れ）→ 振り返り（定例は必須）→ 本編（議論駆動の役割タグ: 報告／確認／議論／参考。【議論】は 1 論点 1 枚）→ まとめ（振り返り＋次回までの動き＋お伺いしたいこと）→ 付録。【再掲】の全体像は議論の手前に 1 枚。

**⑧ PPTX 手直し前提** 箇条書き・複数行テキストは 1 つの div にまとめる（行ごとに要素分割しない。例外は行ごとに背景・罫線が要る表・ステップカード）。帯・カード・バッジは 1 つの塗り矩形で作る。ガントの縦線はオーバーレイ 1 枚に集約、帯の行は `padding`・`gap` なし。

**⑨ 画像** 生成しない。破線枠＋指示文。比率の目安（写真 2:3、概念カード 1:1、横フロー 8:3、スクショ 16:9、QR 1:1）。正確さが要る図は HTML で描いてよい。

**⑩ 読者配慮** 「皆様」「お気軽に」の包摂的トーン。メンバー本人が読んでも評価的に響かない書き方。議事録・タスクのパス・内部運用メモを本文に書かない。相手側の宿題・固有の約束を書かない。

**⑪ 禁止事項一覧**（チェックに直結）`──` ／ `data-speaker-notes` ／ 箇条書き各行のアイコン ／ 本文 24px 未満 ／ 絵文字 ／ グラデ・影・角丸カード ／ 青ベタ広面 ／ 1 枚に塗りボックス 4 個以上 ／ 議事録・内部パス ／ 「前回ご指摘をいただきましたので」型の応答文 ／ 「〜を、〜に。」構文 ／ 1 枚に複数テーマ。

## 7. アイコン（`references/icons.md`）

- 形式: viewBox `0 0 24 24`、stroke 1.5、`fill:none; stroke:currentColor; stroke-linecap:round; stroke-linejoin:round`、角丸なし。表示サイズ 28〜40px。
- 配置・量: D11。
- 対応表（初期 30 種前後。既存 13 を含む。概念名は定例資料の語彙で固定）:

| 概念 | id | 備考 |
|---|---|---|
| 調査・探索 | ic-search | 既存 |
| 仕組み・設定 | ic-gear | 既存 |
| 指標・推移 | ic-chart | 既存 |
| AI・生成 | ic-spark | 既存 |
| 目的・狙い | ic-target | 既存 |
| 階層・ルール | ic-layers | 既存 |
| 工程・流れ | ic-flow | 既存 |
| ドキュメント・議事録 | ic-doc | 既存 |
| メンバー・チーム | ic-people | 既存 |
| 画像 | ic-image | 既存 |
| スケジュール | ic-calendar | 既存 |
| 完了・確認 | ic-check | 既存 |
| ナレッジ・用語集 | ic-book | 既存 |
| リポジトリ・Git | ic-branch | 8/27 で追加済み |
| コード・SQL | ic-code | 同上 |
| チャット・Copilot | ic-chat | 同上 |
| 反復・運用 | ic-loop | 同上 |
| マイルストーン | ic-flag | 同上 |
| Pull Request・レビュー | ic-review | 新規（吹き出し＋チェック） |
| テーブル定義・表 | ic-table | 新規 |
| データベース・BigQuery | ic-database | 新規 |
| 検証・テスト | ic-flask | 新規 |
| ハンズオン・実践 | ic-hand | 新規 |
| 資料・スライド | ic-slide | 新規 |
| 評価・KPI | ic-gauge | 新規 |
| チェックリスト | ic-list | 新規 |
| フォルダ・置き場 | ic-folder | 新規 |
| 連携・リンク | ic-link | 新規 |
| セキュリティ・ガードレール | ic-shield | 新規 |
| 個人・担当 | ic-person | 新規 |
| 着想・提案 | ic-bulb | 新規 |
| 注意 | ic-alert | 新規 |
| 時間・工数 | ic-clock | 新規 |
| Excel・グリッド | ic-grid | 新規 |
| 段階・ステップ | ic-steps | 新規 |
| 方針・方向 | ic-compass | 新規 |

- 外部生成の指示書（Gemini / ChatGPT 向け、英日併記）: 「24×24 の線アイコン、stroke 1.5、単色、塗りなし、角丸なし、余白 2px、SVG パスのみで出力、`<symbol>` 化しやすい単純な path」＋参照として `previews/parts-icons.png` を添える、という定型文。
- 取り込み手順: 受け取った SVG → 不要属性・色を除去（`currentColor` に）→ `assets/icons/<id>.svg` に保存 → `sprite.svg` と `template.dc.html` の `<defs>` に `<symbol>` を追記 → `icons.md` の対応表に概念を登録 → `render-previews.mjs` で `parts-icons.png` を更新。

## 8. `assets/check-slides.mjs` の仕様

- 入力: `.dc.html` のパス。内蔵の静的サーバ（node `http`）で入力ファイルのディレクトリを配信し、playwright-core（`channel:'chrome'`）で `http://localhost:<port>/<file>` を開く。`deck-stage` の描画を待つ（`section[data-label]` が可視になるまで、上限 15 秒）。
- 検査（section ごと）:
  1. はみ出し: 1920×1080 の section 内で、`getBoundingClientRect` が section の box を越える子孫要素（右端・下端）。footer 領域（bottom 48px の帯）に本文要素が重なっていないか。
  2. 内側クリップ: `overflow:hidden` 要素の `scrollHeight > clientHeight`。
  3. フォント下限: 本文テキスト要素 24px 未満、補助・フッター 22px 未満、kicker・STEP ラベル 18px 未満（要素の役割は `data-role` 属性か既定のクラス名で判定。付けていない要素は本文扱い）。
  4. `──`（U+2500 の連続）と `―`（U+2015）の残存。
  5. `data-speaker-notes` の残存。
  6. アイコン数: `<use href="#ic-">` が 1 枚に 7 個以上で警告。
  7. 塗りボックス数: 背景色付きブロック要素（`background` が白・透明以外、面積 > 40,000px²）が 4 個以上で警告。
  8. 絵文字・アイコンフォントの使用。
- 出力: section 番号・`data-label`・該当要素の抜粋。FAIL（1・2・3・4・5）／WARN（6・7・8）。終了コード 0/1/2。
- オプション `--shots <dir>`: 各 section を PNG 保存（レビュー・Artifact 用）。

## 9. `assets/render-previews.mjs` の仕様

- `assets/previews-src/slides/*.html`・`assets/previews-src/guidelines/*.html` を playwright で開き、`@dsCard` コメントの `viewport` に従って PNG を `references/previews/` に書き出す。ファイル名は元 HTML と同じ（`01-cover.png` / `parts-icons.png`）。
- `slide-patterns.md` の各型の先頭に `![](previews/NN-xxx.png)` を置く。

## 10. `references/slide-patterns.md`（19 型＋ボディ部品）

- 型: 表紙／目次／自己紹介／章扉／現状と目指す姿（画像枠）／提供価値 3 軸／進め方の選択肢（比較表）／4 ステップ／推進体制／スケジュール（月帯）／ガントスケジュール（タスク×週）／期待効果（KPI）／ロードマップ／進捗報告（定例）／確認事項（定例）／ご相談事項（議論）／まとめ／付録 早見表／お問い合わせ。これに **進行表（仕組み／利用の 2 段・横方向にステップ）** を 20 型目として追加（8/20・8/27 で使った形を標準化）。
- ボディ部品: 箇条書き（1 テキストボックス方式・子階層）／見出し帯カード（アイコン付き）／ステップノード列（アイコン付き）／表／進行表／ガント／KPI 数字／画像枠／役割バッジ（報告・確認・議論・参考・再掲）／注意帯／お伺いしたいこと枠。
- 各型: 用途・構造（ラベル・見出し・主役・箇条書きの位置）・アイコンを置く場所・`section` の dc スニペット・PNG 見本。

## 11. `references/self-review-checklist.md`（v2 観点）

1. 構成 md からの脱落（各スライド・各ボディ項目・数値・固有名詞が残っているか。間引いた箇所は「構成 md からの変更点」として明示）
2. 1 枚 1 テーマ
3. リード文が結論＋理由・結果の 1〜3 行か／縮約・応答文になっていないか
4. `──` ゼロ、`data-speaker-notes` ゼロ
5. アイコン: 置き場所が規定の 4 箇所か、1 セット 3〜6 個か、概念と 1:1 か、各行に付いていないか
6. 文字量: 目安超過なら分割を検討したか（分けすぎていないか）
7. 機械チェック（check-slides.mjs）FAIL ゼロ
8. 章間整合・表記揺れ・役割タグ
9. 読者配慮トーン・内部パス・相手側の宿題
10. 画像枠の指示文・プレースホルダ数値

## 12. 周辺の更新

| 対象 | 変更 |
|---|---|
| `deck-outline/SKILL.md`・`references/output-template.md` | リード文「結論＋判断理由・結果を 1〜3 行」。`──` 禁止。各スライドの「図版指示」に **使う型の名前（slide-patterns の名称）とアイコン指示（概念名）** を書く。「設計判断」節を口頭補足の置き場として明記（デッキには入れない）。「次アクション」の実装先を「html-slide-deck（.dc.html）→ Claude Design で pptx」に |
| `deck-outline/references/writing-principles.md` | 原則 8（リード文）・原則 15（守りの理屈の置き場）を D5/D8 に合わせて改訂。`──` 禁止と見出し付き箇条書きの代替を追加 |
| グローバル `~/.claude/CLAUDE.md` 書き方原則 | 8・15 の文言を同じく改訂。資料作成フローの記述を「deck-outline → html-slide-deck（.dc.html）→ deck-critique →（pptx は Claude Design）」に |
| `deck-critique/SKILL.md` | 批評観点に `──`・アイコン密度と置き場所・構成 md からの脱落・発表者ノートの残存を追加 |
| dxb-data-ai-workflow-context `AGENTS.md` | §5 クライアント説明資料作成: 出力 `docs/deliverables/yyyymmdd_<slug>.dc.html`、runtime JS 2 本を `docs/deliverables/` 直下に置く、ローカル表示は http 経由、pptx は Claude Design。§8 定例準備フロー: 構成 md → html-slide-deck → deck-critique → pptx の導線 |
| 同 `scripts/lint-frontmatter.ts` | `FILENAME_RE` の拡張子に `dc\.html` を許可。`.js` は対象外のまま |
| Claude Design プロジェクト `CLAUDE.md` | `references/claude-design-rules.md` の内容で置き換え（貼るのはユーザー）。既存の「コピー」節（8/23 指示）を削除し、D5〜D11 を反映 |
| Skills リポジトリ `README.md` | 管理表の html-slide-deck 行を v2 の説明に |

## 13. 検証と受け入れ条件

1. **spike（最初に実施）**: 8/27 構成 md（`docs/explorations/20260822_bi-consulting-sync-slides-outline.md`）の S1〜S3 を新 skill で `.dc.html` 化 → `check-slides.mjs` FAIL ゼロ → ユーザーが Claude Design に持ち込み、(a) 開ける (b) 要素を編集できる (c) pptx 出力できる、を確認。(c) まで通れば D1 確定。通らなければ SKILL.md の導線を「pptx は構成 md を Claude Design へ」に書き換え、それ以外はそのまま進める。
2. `render-previews.mjs` で 19 型＋部品の PNG が生成され、`slide-patterns.md` から参照できる。
3. `check-slides.mjs` を 8/27 v2（Claude Design 生成）にかけると `──` 62 件・speaker-notes 17 件が FAIL として検出される（検査の有効性確認）。
4. 8/27 デッキ全体を新 skill で再生成し、`deck-critique` を通して提示版にする。

## 14. 実装順序と分担

| 順 | 作業 | 規模 | 任せ先 |
|---|---|---|---|
| 1 | export から assets を取り込み（template・runtime・tokens・previews-src・既存 icons）。legacy 退避 | 小・機械的 | Opus 可 |
| 2 | `design-system.md`・`icons.md`・`slide-patterns.md`・`self-review-checklist.md`・`claude-design-rules.md` の執筆 | 中・判断を伴う | Fable |
| 3 | アイコン 17 種の新規 SVG 作成、sprite・template への追記 | 小〜中・手作業 | Opus 可 |
| 4 | `check-slides.mjs` 改修、`render-previews.mjs` 新規 | 中・コード | Opus 可 |
| 5 | `SKILL.md` 書き直し | 中 | Fable |
| 6 | 周辺更新（deck-outline / writing-principles / グローバル CLAUDE.md / deck-critique / AGENTS.md / lint / Skills README） | 小・多箇所 | Opus 可 |
| 7 | spike（S1〜S3 生成 → ユーザー確認） | 小 | Fable |
| 8 | 8/27 デッキ全体の生成・批評 | 中 | Fable |

## 15. オープンな論点

- Claude Design が外部で作った `.dc.html` を取り込めるか（spike で確認）。代替候補: Claude Code の `design` skill で Artifact 公開 → Claude Design で開く導線が使えるか。
- フォント: runtime は Google Fonts（Noto）を読み、pptx 化では游明朝／Meiryo UI に解決される。手元表示と pptx で字幅が変わる前提で、はみ出し余裕（下 30px）を check に持たせるか。
- `.dc.html` 先頭の frontmatter コメントを Claude Design が無視するか（spike で確認。ダメなら持ち込み時に剥がす 1 行スクリプトを用意）。
- アイコン 17 種の新規分は手描き SVG で十分か、外部生成を最初から使うか（初回は手描きで揃え、足りないものから外部生成に回す）。
