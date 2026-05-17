# skills

Claude Code 用に自作した Skill を管理するリポジトリ。

## 構成

- 実体: `~/Documents/Develop/Skills/<name>/SKILL.md`
- 参照: `~/.claude/skills/<name>` から symlink で参照

Claude Code は `~/.claude/skills/` 配下を読むため、本リポジトリのスキルは symlink 経由で認識させる。

## 新規スキル追加手順

```bash
NAME=<skill-name>
mkdir -p ~/Documents/Develop/Skills/$NAME
$EDITOR ~/Documents/Develop/Skills/$NAME/SKILL.md
ln -s ~/Documents/Develop/Skills/$NAME ~/.claude/skills/$NAME
```

Claude Code を再起動して認識を確認したら、リポジトリ側で `git add` & commit。

## 既存スキル

本リポジトリには取り込まず、`~/.claude/skills/` に直接残している（拾い物等の混在を避けるため）。今後新規に作る分のみ管理対象。

## 管理対象スキル

| skill | 説明 |
|-------|------|
| [meeting-minutes](./meeting-minutes/SKILL.md) | `project-context-template` リポジトリ専用の議事録作成スキル。`_drafts/` の議事メモから対話を通じて内容を補完し、`docs/minutes/` 正式版 + `decisions/` / `tasks/` への派生抽出までを一気通貫で行う |

## 注意

- 機密情報（API キー・トークン）は SKILL 内にハードコードしない。Keychain 等から参照する。
- 既存スキルと同名の symlink は作れない（`File exists`）。`ls ~/.claude/skills/` で事前確認すること。
