# task-issue が使うコマンド

`<org>/<repo>` と Project の番号は wiki「進行」表の「タスクのツール」行から読む。Project がユーザー所有なら `organization(login:)` を `user(login:)` に読み替える。1 は読み取り（承認不要）、2〜4 は書き込み（登録計画の承認後だけ）。

## 1. Project のフィールドを読む（承認不要）

```bash
gh api graphql -f query='
query { organization(login: "<org>") { projectV2(number: <number>) { id
  fields(first: 30) { nodes {
    ... on ProjectV2FieldCommon { id name dataType }
    ... on ProjectV2SingleSelectField { id name options { id name } } } } } } }'
```

出力から、Project の node ID（`PVT_...`）、日付フィールド（開始日・期限に相当するもの）の ID、`Status` と他の単一選択フィールドの ID と選択肢 ID を控える。

似たタイトルの open Issue を探す:

```bash
gh issue list --repo <org>/<repo> --state open --search "<語>" --json number,title,url
```

## 2. Issue を作る

```bash
gh issue create --repo <org>/<repo> --title "<タイトル>" --assignee <id1>,<id2> --body "$(cat <<'BODY'
<本文>
BODY
)"
```

出力の URL から番号を控える。`未定` の担当は `--assignee` を省く。

## 3. 親がある子を Sub-issue にする

```bash
gh issue view <親番号> --repo <org>/<repo> --json id --jq .id
gh issue view <子番号> --repo <org>/<repo> --json id --jq .id
gh api graphql -f query='mutation($p:ID!,$s:ID!){
  addSubIssue(input:{issueId:$p, subIssueId:$s}){ issue{ number } }}' -f p=<親の node ID> -f s=<子の node ID>
```

## 4. Project に取り込み、フィールドを入れる

```bash
# 取り込み（出力の id が item-id）
gh project item-add <number> --owner <org> --url https://github.com/<org>/<repo>/issues/<番号> --format json --jq .id

# 日付フィールド
gh project item-edit --id <item-id> --project-id <PVT_...> --field-id <開始日の ID> --date <YYYY-MM-DD>
gh project item-edit --id <item-id> --project-id <PVT_...> --field-id <期限の ID>   --date <YYYY-MM-DD>

# 単一選択フィールド
gh project item-edit --id <item-id> --project-id <PVT_...> --field-id <フィールド ID> --single-select-option-id <option-id>
```

## 5. 既存の親 Issue に「詳細:」行を足す（タスクファイルがあり本文に無いときだけ）

```bash
gh issue view <番号> --repo <org>/<repo> --json body --jq .body > /tmp/body.md
# 先頭の箇条書きに「- 詳細: <blob URL>」を 1 行足してから
gh issue edit <番号> --repo <org>/<repo> --body-file /tmp/body.md
```
