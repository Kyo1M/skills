# 前回以降に動いた Issue の読み方（GitHub Issue を使う repo だけ）

すべて読み取りだけ。`gh issue` 系には必ず `--repo <org>/<repo>` を付ける（省くと別のリモートの Issue が返ることがある）。リポジトリと Project は wiki「進行」表の「タスクのツール」行から読む。gh が無い・未ログインなら飛ばし、Step 5 で「前回からの進捗は読めなかった」と伝える。

## 1. 前回会議日以降に動いた Issue

```bash
gh issue list --repo <org>/<repo> --state all --search "updated:>=<前回会議日>" --limit 100 \
  --json number,title,state,closedAt,createdAt,url
gh issue view <n> --repo <org>/<repo> --json title,body,state,assignees,comments   # 動いた Issue ごと
```

| 群 | 判定 |
|---|---|
| 完了 | 前回会議日以降に closed（`closedAt`）。not planned で閉じたものは「（見送り）」 |
| 更新 | open のまま、前回会議日以降に作られたコメントがある（`comments[].createdAt`） |
| 新規 | 前回会議日以降に作られ（`createdAt`）、台帳に ID が無い。親が登録済みの Issue なら親ごとに畳む |

担当・期限・ラベル・Project フィールドの変更だけの Issue は載せない（Project 側で見える）。コメントの無い本文編集は編集時刻が取れないため拾わない。

## 2. 新規 Issue の親

```bash
gh api graphql -f query='{ repository(owner:"<org>", name:"<repo>") { issue(number:<n>) { parent { number } } } }'
```

## 3. Project の Status・期限（台帳へ写すとき）

`gh project item-list` には Status 以外のフィールドが出ないので GraphQL で読む。`<number>` は Project 番号、org 所有でなければ `organization(login:)` を `user(login:)` に読み替える。

```bash
gh api graphql -f query='
query { organization(login: "<org>") { projectV2(number: <number>) {
  items(first: 100) { nodes {
    content { ... on Issue { number repository { name } } }
    fieldValues(first: 20) { nodes {
      ... on ProjectV2ItemFieldSingleSelectValue { name field { ... on ProjectV2FieldCommon { name } } }
      ... on ProjectV2ItemFieldDateValue { date field { ... on ProjectV2FieldCommon { name } } } } } } } } } }'
```

台帳への写し: Status が Todo → `登録済み`、In Progress → `進行中`、closed → `完了`（完了節へ、完了日 = closedAt）。担当は assignee（wiki「メンバー」行の `名前: GitHub ID` で表示名に戻す）。期限は Project の日付フィールド（無ければ Issue の値のまま）。
