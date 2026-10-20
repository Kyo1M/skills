# テーブル定義の型（既定）

対象リポジトリの規約に型があればそちらを優先する。無い repo ではこの型を使い、初回に置き場（`docs/tables/`）と wiki「データ」表の新設を承認後に足す。この型の正本は [project-context-template](https://github.com/Kyo1M/project-context-template) の `docs/guide/data-definition-guide.md` 2 章で、2-1〜2-4 をそのまま写している（直すときはテンプレートを先に直し、`scripts/check-schema-copies.sh` で一致を確かめる）。

<!-- BEGIN: data-definition-guide 2-1..2-4 -->
### 2-1. YAML の型

記載例を兼ねます（架空の受注明細）。自分の案件に翻訳して使ってください。

```yaml
type: table                    # 種別（固定）
name: order-detail             # ファイル名と同じ slug（ASCII）
title: 受注明細                 # 日本語名
date: "YYYY-MM-DD"             # 作成・最終更新日
status: draft                  # AI 案=draft、原本と見比べ済み=active（人が変える）
derived_from:                  # もとにした定義書（配列）。口頭説明なら「口頭」、貼り付けなら「貼り付けの DDL」
  - sample_table_definition.xlsx の「列定義」シート
physical_names:                # 物理テーブル名（同じ構造が複数あれば列挙）
  - orders_jp
  - orders_tw
grain: 受注明細 1 行（1 注文 × 1 商品）   # 1 行が何を表すか
keys:
  primary: [order_id, line_no] # 一意性を決める列
  join: [customer_id, item_id] # 他テーブルとの結合に使う列
columns:                       # 列定義。定義書に無ければ空にして notes に「要確認」
  - name: order_id
    logical_name: 注文番号
    type: STRING               # 使うエンジンの物理型をそのまま
    nullable: false
    description: 注文単位の識別子
    note: ""                   # 使うときの注意（欠損が多い、コード値のまま、など）
  - name: order_date
    logical_name: 受注日
    type: DATE
    nullable: false
    description: 受注した日
    note: 締め処理の都合で月末分が翌月 1 日に入ることがある（要確認）
  - name: customer_id
    logical_name: 顧客 ID
    type: STRING
    nullable: true
    description: 会員の識別子
    note: 非会員は空
  - name: amount
    logical_name: 金額
    type: NUMERIC
    nullable: false
    description: 税抜の売上金額（現地通貨）
    note: 返品は負の値
relations:                     # 他テーブルとの参照関係
  - column: customer_id
    references: customer-master.customer_id
    cardinality: 多対1
    note: 非会員は customer_id が空
notes:                         # テーブル全体の注意点・集計時の前提
  - 返品は数量・金額が負で入る。正売上と返品額を分けて集計する
  - 通貨は現地通貨。円換算は為替マスタの換算方向を確認してから
```

### 2-2. 項目の書き方

| 項目 | 何を書くか |
|------|-----------|
| `status` | AI が案を出した時点は `draft`。原本と見比べて問題なければ人が `active` に変える |
| `derived_from` | もとにした定義書のファイル名（とシート名）の配列。口頭説明から作った場合は「口頭」、貼り付けなら「貼り付けの DDL」 |
| `physical_names` | 実際のテーブル名。同じ構造が複数あればすべて列挙する |
| `grain` | 1 行が何を表すか（「1 会員・1 日」「1 注文 × 1 商品」など） |
| `keys` | `primary` は一意性を決める列、`join` は他テーブルとの結合に使う列 |
| `columns` | 列ごとに物理名・論理名・型（使うエンジンの物理型をそのまま。BigQuery なら STRING・INT64 など）・NULL 可否・説明・注意 |
| `relations` | この列がどのテーブルのどの列を参照するか、多対 1 などの関係、注意 |
| `notes` | テーブル全体の注意点と集計時の前提。知らないと後で集計を作り直すことになりやすい情報（欠損が多い、重複しやすい、更新タイミングがずれる、対象外レコードが混ざる、換算方向が未確認、など）。定義書に無くても担当者に一言確認する |

**分からない項目**: 文字列の項目（`grain`・`type`・`description`）は「要確認」。配列の項目（`keys.primary` など）は空配列にして、`notes` に「主キーは要確認（store_code・sales_date で一意か）」のように 1 行置きます。参照先が分からない `relations` は行を作らず、`notes` に書きます。列の `note` は注意が無ければ空文字でよい。テーブル名や NOT NULL 列からの見立て（粒度・主キーの候補）は書いてよいですが、「（見立て。要確認）」を付けます。定義書の中の表記のぶれ（同じ列が別名で出る等）も `notes` に「要確認」として残します。

### 2-3. 生変換した Markdown（Excel）の読み方

定義書が Excel なら、原本を `docs/references/` に置き、Markdown に生変換してから読みます（例: `markitdown "docs/references/<定義書>.xlsx" -o docs/references/<名前>-raw.md`。変換ツールが無ければ、必要なシートを CSV に書き出すか列名の一覧を貼ってもらう）。

- 表題行・空行は `Unnamed: n` の見出しや `NaN` として残るので読み飛ばし、「列名」「物理名」「カラム名」「型」「論理名」などが並ぶ最初の行をヘッダとみなします。
- シートの役割を見分けます。テーブルの一覧（物理名・論理名・概要が並ぶ）は論理テーブルの候補と `physical_names`、列定義のシートは `columns`、結合設計・キーのシートは `keys`・`relations`・`notes`。検品結果や値が並ぶシートは読みません。
- 1 シートに同じ構造の物理テーブルが複数まとまっていたら、1 つの論理テーブルとして `physical_names` に列挙します。

### 2-4. wiki と llms.txt への載せ方

`docs/wiki/index.md` の「データ」節（「用語」の次）に、1 論理テーブル 1 行で載せます。データ列から YAML へリンクし、主キーが未確認なら「要確認（結合: …）」と書きます。

```markdown
## データ

| データ | 粒度 | 主なキー | 注意点 |
|--------|------|----------|--------|
| [受注明細](../tables/order-detail.yaml) | 1 注文 × 1 商品 | order_id, line_no（結合: customer_id, item_id） | 返品は負の値。円換算の方向は要確認 |
```

`llms.txt` の「Data」節には `- [受注明細](./docs/tables/order-detail.yaml): 1 注文 × 1 商品` の形で 1 行足します。

<!-- END -->
