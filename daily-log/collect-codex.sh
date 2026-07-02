#!/bin/bash
# collect-codex.sh - Codex (OpenAI) セッションログから指定日のアクティビティを収集
#
# Usage:
#   ./collect-codex.sh              # 今日分
#   ./collect-codex.sh 2026-04-25   # 指定日
#
# Output: JSON to stdout
#   {
#     "date": "2026-04-25",
#     "session_count": N,
#     "sessions": [
#       {
#         "project": "continova-slides",
#         "cwd": "/Users/.../continova-slides",
#         "session_count": 1,
#         "event_count": 883,
#         "first_ts": "2026-04-24T15:04:40Z",
#         "last_ts": "2026-04-24T15:57:28Z",
#         "user_messages": ["..."],
#         "tool_counts": {"exec_command": 126, "apply_patch": 23}
#       }
#     ]
#   }

set -eu
# pipefail intentionally off: `jq ... | head -1` triggers SIGPIPE on jq and
# would abort the script. We check exit status per call instead.

DATE="${1:-$(date +%Y-%m-%d)}"
SESSIONS_ROOT="$HOME/.codex/sessions"

if [ ! -d "$SESSIONS_ROOT" ]; then
  jq -n --arg date "$DATE" '{date: $date, session_count: 0, sessions: [], note: "codex sessions dir not found"}'
  exit 0
fi

# Local-time day boundaries converted to UTC for content-timestamp filtering
START_EPOCH=$(date -j -f "%Y-%m-%d %H:%M:%S" "$DATE 00:00:00" "+%s")
END_EPOCH=$((START_EPOCH + 86400))
START_UTC=$(date -u -r "$START_EPOCH" "+%Y-%m-%dT%H:%M:%SZ")
END_UTC=$(date -u -r "$END_EPOCH" "+%Y-%m-%dT%H:%M:%SZ")

# Candidate directories: prev/target/next day to catch sessions spanning midnight
PREV_DATE=$(date -j -v-1d -f "%Y-%m-%d" "$DATE" "+%Y-%m-%d")
NEXT_DATE=$(date -j -v+1d -f "%Y-%m-%d" "$DATE" "+%Y-%m-%d")

LOG_FILES=()
for d in "$PREV_DATE" "$DATE" "$NEXT_DATE"; do
  yyyy=$(echo "$d" | cut -d- -f1)
  mm=$(echo "$d" | cut -d- -f2)
  dd=$(echo "$d" | cut -d- -f3)
  dir="$SESSIONS_ROOT/$yyyy/$mm/$dd"
  [ -d "$dir" ] || continue
  for f in "$dir"/rollout-*.jsonl; do
    [ -f "$f" ] || continue
    has=$(jq -rc --arg s "$START_UTC" --arg e "$END_UTC" '
      select(.timestamp != null and .timestamp >= $s and .timestamp < $e)
      | .timestamp' "$f" 2>/dev/null | head -1)
    if [ -n "$has" ]; then
      LOG_FILES+=("$f")
    fi
  done
done

# Derive a project name from the cwd (last path component)
derive_project_name() {
  local cwd="$1"
  if [ -z "$cwd" ] || [ "$cwd" = "null" ]; then
    echo "(unknown)"
  else
    basename "$cwd"
  fi
}

SESSIONS_JSON="[]"
for f in "${LOG_FILES[@]:-}"; do
  [ -z "${f:-}" ] && continue

  cwd=$(jq -rc 'select(.type=="session_meta") | .payload.cwd // empty' "$f" 2>/dev/null | head -1)
  project_name="$(derive_project_name "$cwd")"

  # User messages in range. Strip Codex shell context (<cwd>/<shell>/<current_date>/<timezone>)
  # and prefer content after the "## My request for Codex:" marker when present.
  user_msgs=$(jq -c --arg s "$START_UTC" --arg e "$END_UTC" '
    [
      inputs
      | select(.type=="response_item"
               and .payload.type=="message"
               and .payload.role=="user"
               and .timestamp >= $s and .timestamp < $e)
      | .payload.content[]?
      | select(.type=="input_text")
      | .text
      | select(. != null and . != "")
      | if test("## My request for Codex:")
          then (split("## My request for Codex:") | .[1] | ltrimstr("\n") | ltrimstr(" "))
          else .
        end
      | # drop XML-style shell context lines
        split("\n") | map(select(test("^\\s*<[^>]+>") | not)) | join("\n")
      | # drop "# Files mentioned by the user:" preamble if present
        sub("^# Files mentioned by the user:.*?\n(?=[^#])"; ""; "s")
      | gsub("^\\s+|\\s+$"; "")
      | select(. != "")
      | .[0:400]
    ] | unique | .[0:10]
  ' < "$f" 2>/dev/null || echo "[]")

  # Tool use counts (function_call + custom_tool_call). Names: exec_command, apply_patch, ...
  tool_counts=$(jq -c --arg s "$START_UTC" --arg e "$END_UTC" '
    [
      inputs
      | select(.type=="response_item" and .timestamp >= $s and .timestamp < $e)
      | .payload
      | if .type=="function_call" then .name
        elif .type=="custom_tool_call" then .name
        else empty end
    ] | group_by(.) | map({key: .[0], value: length}) | from_entries
  ' < "$f" 2>/dev/null || echo "{}")

  first_ts=$(jq -rc --arg s "$START_UTC" --arg e "$END_UTC" 'select(.timestamp != null and .timestamp >= $s and .timestamp < $e) | .timestamp' "$f" 2>/dev/null | head -1)
  last_ts=$(jq -rc --arg s "$START_UTC" --arg e "$END_UTC" 'select(.timestamp != null and .timestamp >= $s and .timestamp < $e) | .timestamp' "$f" 2>/dev/null | tail -1)
  event_count=$(jq -rc --arg s "$START_UTC" --arg e "$END_UTC" 'select(.timestamp != null and .timestamp >= $s and .timestamp < $e)' "$f" 2>/dev/null | wc -l | tr -d ' ')

  SESSIONS_JSON=$(jq -c \
    --arg project "$project_name" \
    --arg cwd "$cwd" \
    --arg file "$f" \
    --arg first "$first_ts" \
    --arg last "$last_ts" \
    --argjson event_count "${event_count:-0}" \
    --argjson msgs "$user_msgs" \
    --argjson tools "$tool_counts" \
    '. + [{
      project: $project,
      cwd: $cwd,
      file: $file,
      first_ts: $first,
      last_ts: $last,
      event_count: $event_count,
      user_messages: $msgs,
      tool_counts: $tools
    }]' <<< "$SESSIONS_JSON")
done

# Merge sessions by project
MERGED=$(jq -c '
  group_by(.project) | map({
    project: .[0].project,
    cwd: .[0].cwd,
    session_count: length,
    event_count: (map(.event_count) | add),
    first_ts: (map(.first_ts) | min),
    last_ts: (map(.last_ts) | max),
    user_messages: (map(.user_messages) | add | unique | .[0:15]),
    tool_counts: (map(.tool_counts) | add | to_entries | group_by(.key) | map({key: .[0].key, value: (map(.value) | add)}) | from_entries)
  })
' <<< "$SESSIONS_JSON")

jq -n \
  --arg date "$DATE" \
  --argjson sessions "$MERGED" \
  '{date: $date, session_count: ($sessions | length), sessions: $sessions}'
