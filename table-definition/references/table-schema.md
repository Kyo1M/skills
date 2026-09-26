# テーブル定義の型（既定）

対象リポジトリの規約に型があればそちらを優先する。無い repo ではこの型を使い、初回に置き場（`docs/tables/`）と wiki「データ」表の新設を承認後に足す。

## YAML の型

`docs/tables/<slug>.yaml`。1 論理テーブル 1 ファイル。`slug` は論理テーブル名の英語 kebab-case で、`name` と同じにする。

```yaml
type: table                    # 種別（固定）
name: app-event-log            # ファイル名と同じ slug（ASCII）
title: アプリ操作ログ            # 日本語名
date: "YYYY-MM-DD"             # 作成・最終更新日
status: draft                  # AI 案=draft、原本と見比べ済み=active（人が変える）
derived_from: [<原本のファイル名>]  # もとにした定義書（配列）。口頭説明なら「口頭」、貼り付けなら「貼り付けの DDL」
physical_names:                # 物理テーブル名（同じ構造が複数あれば列挙）
  - app_events_2025
  - app_events_2026
grain: 1 ユーザーの 1 操作が 1 行     # 1 行が何を表すか
keys:
  primary: [event_id]          # 一意性を決める列
  join: [user_id, screen_id]   # 他テーブルとの結合に使う列
columns:                       # 列定義。定義書に無ければ空にして notes に「要確認」
  - name: event_id
    logical_name: イベント ID
    type: STRING
    nullable: false
    description: 操作ごとの識別子
    note: ""                   # 使うときの注意（欠損が多い、コード値のまま、など）
  - name: user_id
    logical_name: ユーザー ID
    type: STRING
    nullable: true
    description: ログイン済みユーザーの識別子
    note: 未ログインの操作は空
  - name: event_time
    logical_name: 操作日時
    type: TIMESTAMP
    nullable: false
    description: 端末で操作が起きた日時
    note: 端末時刻のため、タイムゾーンの扱いは要確認
  - name: screen_id
    logical_name: 画面 ID
    type: STRING
    nullable: false
    description: 操作が起きた画面
    note: 画面マスタに無い ID が混ざることがある
relations:                     # 他テーブルとの参照関係
  - column: user_id
    references: user-master.user_id
    cardinality: 多対1
    note: 退会済みユーザーはマスタに残らない
notes:                         # テーブル全体の注意点・集計時の前提
  - 同じ操作が二重送信で重複することがある（event_id は異なる）
  - 集計対象外のテスト端末の操作が混ざる。除外条件は要確認
```

| 項目 | 何を書くか |
|------|-----------|
| `status` | AI が案を出した時点は `draft`。原本と見比べて問題なければ人が `active` に変える |
| `derived_from` | もとにした定義書のファイル名の配列。口頭説明から作った場合は「口頭」、貼り付けなら「貼り付けの DDL」 |
| `physical_names` | 実際のテーブル名。同じ構造が複数あればすべて列挙する |
| `grain` | 1 行が何を表すか（「1 会員・1 日」「1 注文 × 1 商品」など） |
| `keys` | `primary` は一意性を決める列、`join` は他テーブルとの結合に使う列 |
| `columns` | 列ごとに物理名・論理名・型（使うエンジンの物理型をそのまま）・NULL 可否・説明・注意 |
| `relations` | この列がどのテーブルのどの列を参照するか、多対 1 などの関係、注意 |
| `notes` | テーブル全体の注意点と集計時の前提（欠損が多い、キーが重複する、換算方向が未確認、など） |

**書かないもの**: 件数・欠損率・最小・最大などの数値プロファイルと、値のサンプル。定義書に載っていても、注意点に定性で書く。

**分からない項目**: 文字列の項目は「要確認」。配列の項目（`keys.primary` など）は空配列にして `notes` に 1 行。参照先が分からない `relations` は行を作らず `notes` に書く。列の `note` は注意が無ければ空文字でよい。

## wiki「データ」表の型

`docs/wiki/index.md` に「データ」節を置き（「用語」の次）、1 論理テーブル 1 行。データ列から YAML へリンクする。主キーが未確認なら「要確認（結合: …）」。

```markdown
## データ

| データ | 粒度 | 主なキー | 注意点 |
|--------|------|----------|--------|
| [アプリ操作ログ](../tables/app-event-log.yaml) | 1 ユーザーの 1 操作が 1 行 | event_id（結合: user_id, screen_id） | 二重送信の重複あり。テスト端末の除外条件は要確認 |
```

## 生変換した Markdown（Excel）の読み方

表計算ソフトの定義書を Markdown に変換すると、シートごとに見出しと 1 つの表になり、表題行や空行が `Unnamed: n` の見出しや `NaN` として残る。次のように読む。

- 表題行・空行は読み飛ばし、「列名」「物理名」「カラム名」「型」「論理名」などが並ぶ最初の列名らしい行をヘッダとみなす。
- シートの役割を見分ける: テーブルの一覧（物理名・論理名・概要が並ぶ）は論理テーブルの候補と `physical_names`。列定義のシートは `columns`。結合設計・キーのシートは `keys`・`relations`・`notes`。検品結果や値が並ぶシートは読まない（数値プロファイルは `notes` に定性で残すだけ）。
- 1 シートに同じ構造の物理テーブルが複数まとまっていたら、1 つの論理テーブルとして `physical_names` に列挙する。
