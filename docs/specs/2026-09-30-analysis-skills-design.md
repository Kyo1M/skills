# 分析用の共通 skill 設計書

- 日付: 2026-09-30
- ステータス: 承認済み（brainstorming で論点ごとに合意し、AI レビュー 2 件の指摘を反映）。実装中に、Google への自動アップロードをやめ gdocs-publish を docx-export に変えた（6 章）
- 対象: ワクチン分析の vac-nb・vac-report・vac-understand・vac-gdocs-report をもとに、どのリポジトリでも使える分析用の skill を `~/Developer/Skills` に作る。あわせてコテラスの分析（`~/Developer/coterrace-context`、台帳 T-27）を共通の skill に合わせる
- 対象外: vaccinechoice_HH の vac-* の変更・置き換え（AGENTS.md に使い分けの 1 行を足すだけ）、HTML・PDF のレポート（vac-report-html の共通化）、MCMC の収束診断

## 1. 決めたこと

| 論点 | 決定 | 理由 |
|---|---|---|
| レポートの出し先 | リポジトリの md が正本。Google Docs は共有のための写し | ワクチン分析の流れと、コテラスの「正本と転写先の同期ルール」に合う |
| HTML のレポート | 作らない。vac-report-html は共通にしない | レポートは Google Docs で渡せれば足りる |
| ワクチン分析の vac-* | 今のまま使う（置き換えない）。README の vaccinechoice_HH の行も変えない。vaccinechoice_HH の AGENTS.md に「この repo では vac-* を使う」と 1 行足す | 固有の分析環境（Julia・Docker）の専用の skill として成り立っている。共通の skill と同じ頼み方に反応し得るので、repo 側で使い分けを書く |
| skill の数と名前 | 4 つ: `analysis-notebook`・`analysis-report`・`understand`・`docx-export` | レポートだけ作り直す・分析以外の md を docx にする、を別々に呼べる |
| MCMC の収束診断 | 共通の skill に持たせない（vac-nb の `references/mcmc-convergence.md` に残す） | ワクチン分析でしか使っていない。他で要るようになったら足す |
| レポートの読み手 | 読み手の型を 2 つ持つ（クライアント向け・研究者向け）。どちらを使うかは規約で選ぶ | コテラスはクライアント（山永さん、その先の AP の役員）、ワクチン分析は共同研究者で、書き方が違う |
| notebook の形式 | 規約で指定。指定が無ければ marimo | marimo は notebook がそのまま `.py` で、変換・同期が要らない |
| Google Docs への出し方 | skill は md から画像を埋め込んだ docx を作るところまで（pandoc）。Google Drive へは手でアップロードして Google ドキュメントに変換する | docx が作れれば、アップロードは手で足りる。画像を公開リンクにする方式・アカウントの選択・アクセストークンの手順が要らない。どのアカウントの Drive に置くかは、アップロードする人がその場で決める |
| コテラスのレポートの形式 | 分析レポートは `docs/deliverables/yyyymmdd_<slug>-report.md`（`type: deliverable`）を正本にし、Google Docs に写す。スライドは今のまま `.dc.html` | コテラスの AGENTS.md は今、レポートを `-report.html`（HTML が主）としている。7.2 で直す |

## 2. 全体の構成

```
analysis-notebook ─→ analysis-report ─→ docx-export
 (問い駆動の notebook)   (md のレポート。正本)    (docx にする。Google Docs へは手で上げる)
          └──────────────┴─→ understand (notebook・レポート・任意の資料を teach-back で理解する)
```

どの skill も規約駆動にする。meeting-minutes・table-definition と同じく、対象リポジトリの AGENTS.md / CLAUDE.md（とそこが指すガイド）を最初に読み、下の項目の値を決める。規約に無い項目は既定を使う。決めないと進めない項目（レポートの読み手の型）だけ実行時に聞き、答えを AGENTS.md に足す案として出す。

### 2.1 規約から読む項目

| 項目 | 使う skill | 既定（規約に無いとき） | コテラスでの値 |
|---|---|---|---|
| notebook の形式 | notebook・report・understand | marimo | marimo |
| 言語・実行環境・実行のコマンド | notebook | 形式ごとの references の既定 | Python 3.12・uv（`analysis/README.md`） |
| notebook の置き場・名前の付け方 | notebook | `notebooks/<snake_case>.py` | `analysis/notebooks/<snake_case>.py` |
| データの読み方 | notebook | 決まり無し | `load_table("<slug>")` だけ。S3 やファイルを直接読まない |
| コードに書いてはいけない値 | notebook | ID・個人を指す値はコードに書かない | 実際の値（店舗名・ID・特定店舗の絞り込み条件）を書かない |
| notebook の説明文に書いてよい数値 | notebook | 集計した値を書く（個人の値は書かない） | 集計した値だけ。計算した値を `mo.md(f"…")` で差し込む |
| 個人の行・自由記述の原文 | notebook・report・understand・docx-export | notebook の出力では展開してよい。notebook の外（説明文・レポート・explainer・図・メモ）には出さない | 既定と同じ（外に出すときは分類などに言い換える） |
| 人数の少ない集計値 | report・understand・docx-export | 個人が推測できる少人数の区分（目安 5 人未満）はレポートに出す前に確かめる | 7.2 で決める |
| 外に出してよいかの確認 | report・understand・docx-export | レポート・explainer・図を書くとき、docx を作る前にユーザーに確かめる | 載せてよい粒度を山永さんに確かめる。実店舗名が入る結果は近内さんの判断を仰ぐ（AGENTS.md「データの扱い」「テーブル定義の型」） |
| 図の文字の制約 | notebook | 無し | 無し（Plotly は日本語を描ける） |
| 成果物の置き場・名前の付け方 | report・understand | レポートは `docs/reports/YYYYMMDD_<name>/`（本文と `figs/`）、explainer は `docs/explainers/YYYYMMDD_<元の名前>_explainer.md` | レポートは `docs/deliverables/yyyymmdd_<slug>-report.md`。explainer と図の置き場は 7.2 で決める（lint がファイル名を `yyyymmdd_<kebab-case>` に限る） |
| frontmatter | report・understand | 無し | `type`・`title`・`date`・`status` が必須。`type` は lint が許す 8 種から選ぶ（レポートは `deliverable`） |
| 検査のコマンド | report・understand | 無し | `npm run lint --prefix scripts` |
| git の運用 | notebook・report・understand | リポジトリの決まりに従う。無ければコミットしない | ブランチを切り、lint を通し、コミットメッセージの案を見せてから commit。push しない |
| 他の成果物の扱い | report・understand | 上書きせず、新しい日付のファイルで並べる | 既定と同じ |
| レポートの読み手の型 | report | 実行時に聞く | クライアント向け |
| 共有前の理解の確認 | notebook・report・understand | understand を勧める（必須にしない） | 既定と同じ |
| docx の置き場・書式の雛形 | docx-export | `~/Downloads/`（リポジトリの外）。雛形は無し（表の罫線だけ足す） | 既定と同じ |

完成の目安: コテラスとワクチン分析のどちらも、この表の値を埋めれば共通の skill で動く。実際に確かめるのはコテラスだけ（vac-* は置き換えない）。

## 3. analysis-notebook

### 3.1 ファイル

```
analysis-notebook/
├── SKILL.md
├── references/
│   ├── marimo.md     既定の形式
│   └── jupytext.md   スクリプトを書いて notebook に変換する形式
└── scripts/
    └── read_session.py   marimo の session の出力（JSON）を、セルごとの文字・表・図の要約・エラーで出す
```

### 3.2 SKILL.md に書くこと（vac-nb の形式に依らない部分）

- 使い方: `/analysis-notebook [分析テーマ / 問い / 既存の notebook のパス]`
- 最初に規約を読む（2.1 の項目）。形式に合う references を読む
- 入力のモード 3 つ: 新規作成／既存 notebook の改修（既存の問い・用語・出力を監査してから直す）／既存の結果の読み直し
- 分析サイクル（5 フェーズ、固定）
  1. 問い定義: 問い・仮説・判定単位・YES／NO／部分的の判断基準・用語の operational definition。コーディング前に問いの批判的チェック（どの意思決定に効くか、反証可能か、先行 notebook と重複・矛盾しないか、答えが出なかったら次に何を見るか、ユーザーの問いも鵜呑みにしない）。問いの立て方から整理したいときは先に grill-me
  2. 最小分析設計: 各ステップにどの問いのためかを書く。直接答えない分析は削るか「補助分析」と明示する。少数件数（目安 20 件以下）は全件を確認する。回答の出力の形を先に決める。誤解しやすい指標は「意味すること／意味しないこと」を 1〜3 行で先に書く
  3. 実装: 各問いの最後に回答の型を置く。件数・割合は判定単位とセットで書く。誤読されやすい表現には「読み方の補足」を置く
  4. 実行・検証: 形式の references の手順で最後まで実行し、出力を読んで回答検証チェックリストを通す。問いに答えられていなければ直して再実行する。データを取り込み直したときも再実行する
  5. 結論要約: 各問いの回答と、全問いのまとめ表。「言えない」を無理に断定しない。ユーザーへの報告は要約 → 根拠 → 限界の順
- 回答の型: 回答（YES／NO／部分的／まだ言えない）・読み方の補足（必要時）・根拠（主要な数値 1〜3 個）・確度（高／中／低）・限界・次アクション
- 推奨の notebook 構成（見出しと項目だけ。セルの書き方は references）: 0. 概要（問い・仮説・判定単位・判断基準・用語定義・データソース・出力先）→ 1. データの読み込みと基礎確認 → N. 問い N（この章が答える問い・仮説・分析ステップ、N.1 ステップ、N.x 補助分析、N.y 回答）→ まとめ（問い／回答／根拠／確度／限界の表）。問いが固まっていない初期だけ探索モードを使い、後で問い駆動に戻す
- 分析方針: 代表インスタンスの可視化（各章に代表の具体例を 1 件以上。冒頭で定数として決めるのは選ぶ規則（例: 指標が中央値に最も近い行）で、ID や個人を指す値はコードに書かず実行時に求める。全章で同じものを追う。偏る論点は対照を足す）。集計表の注目行（少数サンプル・外れ値・結論を左右する行）は行の単位で展開する。展開は notebook の出力の中だけで、外に出してよい範囲は規約に従う
- 回答検証チェックリスト（vac-nb の 12 項目。例を中立なものに差し替える）
- 命名と解釈のガード: 曖昧なラベルは何を指すかを定義してから使う（例: 「候補」がどの段階の候補か）。「高確度」を使うなら条件を先に並べる。直接の根拠が無ければ「部分的」か「まだ言えない」。支持的な結果は答えでなく補助根拠
- 実装の決まり: 共通処理は関数にする。図は軸ラベル・凡例・タイトルが揃い、単体で意味が分かる。抽象的な指標は実数や分布の図で見せる。パスや重要なパラメータには理由を添える。コメントは日本語で意図を書く
- 大きな分析では監査やレビューにサブエージェントを使ってよいが、結論の責任は 1 つに保つ
- 結論を共有する前に understand で理解を確かめるよう勧める（必須かは規約）。レポートにするときは analysis-report へ

### 3.3 references/marimo.md

- セルの書き方（`@app.cell`、`mo.md`）。説明文の数値は計算した値を `mo.md(f"…")` で差し込み、手で書き写さない
- 表の出し方（DataFrame をそのまま出すか `mo.ui.table`）
- リアクティブな実行の注意（同じ変数名を 2 つのセルで定義しない、セル内だけで使う名前は `_` で始める）
- 注目行を展開するヘルパーの書き方
- 実行と検証（実行のコマンドの前置き `uv run` 等は規約から読む）:
  1. `marimo check --strict <file>`（warning でも失敗にする）
  2. `marimo export session --force-overwrite --no-sandbox <file>`（既定ではコードが変わらないと実行を飛ばし、データを取り込み直しても古い出力が残るため、毎回強制する）
  3. 出力は `<notebook のフォルダ>/__marimo__/session/<file>.py.json`。終了コードが 0 でないか、JSON の出力に `type: error` があれば失敗とする
  4. JSON の出力を読み、回答と出力が食い違っていないかを見る
- `__marimo__/` はコミットしない
- 図を png に書き出す方法（Plotly は `fig.write_image`。kaleido と Chrome が要る）。書き出した png を開き、日本語の文字欠け・軸の文字の切れが無いかを確かめる

### 3.4 references/jupytext.md

- percent format の書き方（`# %% [markdown]` と `# %%`）
- スクリプトだけを編集し、`.ipynb` は直接編集しない。スクリプト内の相対パスは `.ipynb` を実行するフォルダ基準
- `jupytext --sync <script>` で同期し、`jupyter nbconvert --execute` で出力ごと確かめる。実行の言語・コマンド・コンテナは規約から読む
- 表示ヘルパーは、notebook の外で実行したときに文字の表示へ切り替える fallback を付ける

### 3.5 入れないもの（vac-nb に残る）

Julia、`BrowseTables.HTMLTable`、Docker での実行、図の文字を ASCII にする決まり、MCMC の収束診断、`docs/analysis_notebook_agent_guide.md` への参照、pairwise／family の例。

## 4. analysis-report

### 4.1 ファイル

```
analysis-report/
├── SKILL.md
└── references/
    ├── reader-client.md       クライアント向け
    └── reader-researcher.md   研究者向け
```

### 4.2 SKILL.md に書くこと（どの読み手にも使える決まり）

- 使い方: `/analysis-report [notebook のパス]`
- 最初に規約を読み、読み手の型を決める（規約に無ければ聞く）
- 一次ソースと読む順番: まとめ表 → 各問いの回答 → 根拠の図表 → 補助分析。途中の出力や図から結論を作らない。まとめ表が無いときだけ回答から組み立てる。marimo の出力は `__marimo__/session/*.json` から読み、古い出力で書かないよう、書く前に analysis-notebook の手順で再実行する
- 数値は実行の結果から引く。再現情報（末尾に短く）に notebook のパス・データを確かめた日・図のパスを書く
- 構成の核（読み手の型が章立てを決め、どちらにも次を入れる）: 問いごとの結果、総合解釈（問い同士の関係、何が言えて何がまだ言えないか、上位の問いにとっての意味を数値の再掲でなく解釈で、その解釈と競合する説明（交絡・データの偏り・手法の仮定）の検討、結果から次に立てる問い）、次アクション
- 記述の決まり: 問い／回答／根拠／限界が基本形。未解決は未解決と書き、「部分的」を YES に丸めない。補助分析は確度や解釈への寄与を 1 文で書く。コードの内部の語は言い換える（必要なら初出で定義）。進行管理の語（決定日・MTG・宿題・前回のご指摘への回答）は書かない。口語・比喩は使わない。用語を本文・図の凡例・表のキャプションで揃える
- 事実の裏取り: 外部データは正式名称で書き、略語を推測で展開しない。母数・件数は実数で書き、全体／除外後／集計に寄与した分のどれかを明示する。結果に効く定数は出所と役割を 1 文で書けるまで調べる
- 付録は必須にしない。本文だけで完結させ、「付録に回す」で本文を中断しない
- 1 論点主義。作業の層（出所・理解度のタグ、未消化の棚卸し）はレポートに出さない。AI が補った部分を確定として書かない。定型の見出し・全項目同型の表・冗長な前置きを避ける
- 持ち出しのガード（書く前と保存の前）: 個人の行・自由記述の原文・コードに書いてはいけない値が本文・表・図に入っていないかを確かめ、入っていれば分類・集計に言い換える。人数の少ない区分と、外に出してよいかの確認は 2.1 の規約に従う
- 図: 根拠になる図だけ。直前にどの問いに効くかを書き、目的・軸・計算の仕方・わかったことを添える。参照は `![キャプション](相対パス)` に揃える。図は notebook から png に書き出す
- 保存: 置き場・名前・frontmatter・検査のコマンド・git は規約に従う（既定は 2.1）。他の成果物は上書きせず、新しい日付のファイルで並べる
- 仕上げ: 共有の前に understand を勧める。docx や Google Docs で渡すなら docx-export を案内する
- チェックリスト: vac-report のうち、どの読み手にも使える項目（要約表との一致、回答／根拠／限界、未解決の扱い、図の説明、1 論点、説明できない記述のカット、定型構造、考察が数値の再掲で終わっていないか（上位の問いへの意味・競合する説明・次の問い）、指標の定義、記号の一意性、入力と出力の母数の突合、件数の実数、外部データの正式名称、定数の出所、内部の語、付録なしで完結、進行管理の語、用語の一致、まとめが「やったこと → 結果」中心、要旨が限界も運ぶ）と、持ち出しのガード

### 4.3 references/reader-client.md

- 構成: 結論（何が分かり、何を判断できるか）→ 背景と問い → 問いごとに分かったこと（図が中心）→ 解釈とまだ言えないこと（競合する説明を含む）→ 次にやること → 再現情報
- 本文に数式を出さない。指標は業務の言葉で定義し、統計の用語は言い換える
- 判断を誤らせる前提（データの期間・範囲・欠け）は、限界の節に回さず結論の近くに書く
- 文章はグローバルの書き方原則（`deck-outline/references/writing-principles.md`）に従う

### 4.4 references/reader-researcher.md

- vac-report の「研究的 self-contained 版（物語型）」の構成と記述ルール（概要 → 背景・課題・目的 → 方針 → 実施 → 結果 → まとめ・今後 → 再現情報）
- 手法の説明の 4 項目（目的関数の全体式から入る、モデルを式で定義しベースラインとの違いを示す、説明を後の章へ送らない、因果はメカニズム・用語の定義・対処の妥当性で書く）と、対応するチェックリスト（目的関数の式、モデルの定義、先送り、因果の説明）
- 学術論文の体裁が要るときの章立て
- 外すもの: 「兄弟」の用字（用字は規約に従う）、`build_html.py`、vac-report-html、MCMC の記述

## 5. understand

### 5.1 ファイル

`understand/SKILL.md` だけ。

### 5.2 vac-understand から変えるところ

- ワクチン分析の AGENTS.md「数理研究タスクの進め方」への参照を外し、「規約に共有前の理解の確認があれば、それとして使う。説明できない記述は共有する成果物から外す判断材料にする」とする
- 説明する相手の選択肢: クライアント／共同研究者／自分用／一般
- notebook は marimo の `.py` か変換型のスクリプトを読み、出力は形式ごとの置き場から読む
- explainer の置き場・名前・frontmatter・検査のコマンドは規約に従う（既定は 2.1）。explainer は notebook の外なので持ち出しのガードを守る
- 関連の skill: grill-me（対話の作法）、analysis-notebook（回答検証チェックリスト）、docx-export（配布）。`spec-to-readable-html` と vac-gdocs-report への案内は外す

### 5.3 変えないところ

- 入力の扱い: 同じ内容が複数の形式であれば md を優先する。PDF は `pdftotext <pdf> -` で読む（元の md があれば併読）。読んだら構造マップ（章立て・各章の主張・数式・図・章の依存）を原文に忠実に作る。パスの指定が無ければ、直近に作成・言及した資料を候補として聞く
- 理解のサイクル（把握と目的設定 → 全体像 → セクションごとに直感・数式・妥当性・よくある誤解 → 質問と想定回答の組で teach-back → explainer の生成 → 仕上げの確認）
- 理解度チェックリスト、explainer の構成（元ドキュメント・説明台本・用語と数式・想定問答・残課題）
- ガード（原文に忠実、原文に無いことを足さない、1 セクション・1 問ずつ）

## 6. docx-export

実装中の判断（2026-09-30）: docx が作れれば Google Drive へのアップロードは手で足りるので、Google への自動アップロード（`gog drive upload --convert`、公開リンク方式）はやめ、名前を gdocs-publish から docx-export に変えた。

### 6.1 ファイル

```
docx-export/
├── SKILL.md
└── scripts/md_to_docx.py   画像の一覧・docx の作成・照合（標準ライブラリと pandoc）
```

### 6.2 手順

1. md を読む。無ければ中断。docx の名前は `YYYYMMDD_<最初の # 見出し、無ければ frontmatter の title>.docx`（Google ドキュメントに変換したときの文書名になる）
2. 外に出してよいかを規約で確かめる（2.1 の「外に出してよいかの確認」「個人の行・自由記述の原文」「人数の少ない集計値」）。出してはいけないものがあれば作らずに止める
3. 画像の参照（`![cap](path)` は md のフォルダ基準、`[FIG] path` はリポジトリの root 基準）の一覧を出し、除外する画像を聞く
4. `md_to_docx.py` で docx を作る: 写しを一時フォルダに作り、frontmatter を消し、除外した画像を消し、`[FIG]` を画像の記法に直して、`pandoc -f gfm+implicit_figures` にかける（キャプションが図の下に付く）。表には罫線を直接付ける（pandoc の既定では罫線が無いため）。規約に reference docx があれば使う
5. 見出し・表・画像の数を md と docx（pandoc で md に戻したもの）で照合する。不一致なら未完了として報告する
6. docx のパスと、Google ドキュメントにする手順（Drive にアップロード →「アプリで開く」→「Google ドキュメント」）を報告する

### 6.3 確かめたこと（2026-09-30、架空の md）

- pandoc 3.11 で、日本語・frontmatter・表・画像 2 枚（`![]()` と `[FIG]`）の md から docx を作り、見出し 4・表 1・画像 2 が一致した。除外の指定も効いた。元の md は変わらなかった
- Quick Look のプレビューで、見出し・表（罫線付き）・画像・キャプションを目で確かめた。箇条書きは docx に番号付けとして入っている（Quick Look は記号を描かない）
- Google Drive へのアップロードと Google ドキュメントへの変換は手で行うので、skill では確かめていない

## 7. 作業の順番と完了の条件

### 7.1 Skills リポジトリ（この設計書の範囲の実装）

グローバルの CLAUDE.md に従い、ファイルと完了の条件がこの設計書で決まっているので、実装計画は挟まない。

1. docx-export の変換を 6.3 のとおり確かめる
2. 4 つの skill を作る（`analysis-notebook`・`analysis-report`・`understand`・`docx-export`）
3. analysis-notebook の marimo の手順を、scratchpad の試験用 notebook（架空のデータ）で試す（`check --strict`、`export session --force-overwrite`、失敗したセルの検出、png の書き出し）
4. `scripts/link-skills.sh` を実行し、README の管理表に 4 行を足す（vaccinechoice_HH の行は変えない）。スキル間の使い分けに分析のレーン（analysis-notebook → analysis-report → docx-export、共有前に understand）を足す
5. `scripts/link-skills.sh --check` で報告が 0 件になることを確かめる
6. コミットする

完了の条件:

- 4 つの skill が `~/.claude/skills/` と `~/.agents/skills/` から見える（`--check` が 0 件）
- 4 つの skill のフォルダ全体（SKILL.md と references/）に、Julia・Docker・`BrowseTables`・ASCII の図・MCMC・`analysis_notebook_agent_guide.md`・vaccinechoice_HH のパスが残っていない（grep で確かめる）
- 2.1 の各項目が、どの skill のどこで読まれるかを SKILL.md に書いてある
- 試験用の notebook で、`export session` がセルの失敗を検出し、再実行で出力が更新されることを確かめた
- docx-export でテスト用の md から docx を作り、画像が入り、見出し・表・画像の数が md と一致することを確かめた

### 7.2 コテラス側（T-27、別の作業）

T-23 のセッションが `chore/20260930-load-table-key-check` で作業中なので、T-23 のマージを取り込んでから、worktree か別のセッションで行う。コテラスの Git の決まり（push しない、ブランチを切る、`npm run lint --prefix scripts`、コミットメッセージの案を見せる、ローカルで `main` にマージしてブランチを消す）に従う。

1. ~~AGENTS.md「データの扱い」を 2026-09-30 の決定に合わせて直す~~（コテラスの main の `7049bcc` で反映済み。`template.py` も同じ）
2. AGENTS.md のレポートの形式を直す（ディレクトリ構造・置き場の表・「クライアント説明資料作成」で `-report.html` としている行を、分析レポートは `-report.md` を正本にして Google Docs に写す、に変える）
3. 2.1 のコテラスの値を AGENTS.md に書く（「データの扱い」と重ねず、参照で済むところは参照にする）。あわせて決める: explainer の置き場と名前（lint の `type` と名前の形に合わせる）、図の置き場と commit する時点（png は `.gitignore` の対象外なので、載せてよい粒度を確かめる前に commit されないようにする）、人数の少ない集計値の扱い
4. `template.py` と `data_coverage.py` を analysis-notebook に合わせ、`marimo export session --force-overwrite` で最後まで動くことと回答検証チェックリストを確かめる
5. kaleido を足すかを相談する（今は入っていない。Chrome は手元にある）
6. T-11（分析用テンプレートの切り出し、期限 11 月末）との重なりを確かめる
7. `tasks/index.md` の T-27 を完了の節へ移す（完了日を書く）

コテラス側でやることの控えは、コテラスの `tasks/20261001_analysis-skills-alignment.md`（T-27 のタスクファイル）に置く。

### 7.3 ワクチン分析側（済み）

skill の使い分けは、共有の AGENTS.md ではなく個人用の `ops/AGENTS.md`（private の Kyo1M/vaccinechoice-ops）に書かれているので、そこに「この研究の分析・レポート・理解の確認は vac-* を使い、共通の分析 skill は使わない」と 1 行足した（ops の `52529a1`、2026-10-01）。vac-* のフォルダは触っていない。
