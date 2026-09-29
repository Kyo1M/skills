# archive

使わなくなった skill の退避先。`scripts/link-skills.sh` はこの `archive/` を symlink の対象にしない。戻すときは `git mv archive/<name> <name>` して `scripts/link-skills.sh` を走らせ、README の管理表に戻す。

| skill | 退避日 | 理由 |
|---|---|---|
| spec-to-readable-html | 2026-09-29 | 直近 30 日の呼び出しが Claude Code・Codex とも 0 回 |
| empirical-prompt-tuning | 2026-09-29 | 直近 30 日の呼び出しが Claude Code・Codex とも 0 回。skill の評価と改善は skill-creator でも回せる |
| claude-ai-skills/（note-writing-assistant、project-overview、kpi-structure） | 2026-09-18 | claude.ai にだけあった自作 skill の控え。claude.ai 側の同じ skill は 2026-09-29 時点でも同期されていたので、claude.ai での無効化もあわせて行う |
