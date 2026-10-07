# AGENTS.md の「ドキュメントの点検」の節の雛形

置き場・時期・再確認の手順をリポジトリに合わせて直して、AGENTS.md に入れる。

```markdown
## ドキュメントの点検

文書の数値・状態・一覧が、元のファイルの変更に追いついているかを定期的に点検する（`doc-maintenance` skill。無ければこの節の手順で手で行う）。

- 時期：月初と、文書を外に共有する前
- 点検：`python3 scripts/check_docs.py`（Python 3.11 以上。対象は `scripts/check_docs.toml`）。スクリプトは一覧を出すだけで、ファイルは書き換えない
- 見ること：元のファイル（frontmatter の `derived_from`・`related`）が後で更新された文書、draft のまま日数が過ぎた文書、`related` が置き換え済みの文書を指しているもの、リンクの切れ、確かめた日の古い記録、一覧に載っていないファイル
- 直し方：1 件ずつ文書と元のファイルの差分を読み、直す案をまとめて見せてから直す。共有物（`audience: client`）は変える文を先に見せる。本文に更新の経緯は書かない
- 確かめて直さなかった文書にも、frontmatter の `reviewed: "YYYY-MM-DD"` を付ける（付けないと次の点検でまた出る）
- 確かめた日の古い記録の再確認：（リポジトリの手順を書く。例：値の一覧を取り直すスクリプト）
- 点検スクリプトの正本は Kyo1M/skills の `doc-maintenance/scripts/check_docs.py`。直すときは正本を直して写す
```
