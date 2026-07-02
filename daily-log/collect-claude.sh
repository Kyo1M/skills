#!/bin/bash
# collect-claude.sh - Claude Code セッションログから指定日のアクティビティを収集
#
# Usage:
#   ./collect-claude.sh              # 今日分
#   ./collect-claude.sh 2026-04-12   # 指定日
#
# Output: JSON to stdout
#   {
#     "date": "2026-04-12",
#     "session_count": N,
#     "sessions": [
#       {
#         "project": "continova-hp",
#         "project_path": "-Users-murakamikyouichi-Documents-Develop-continova-hp",
#         "file": "/path/to/log.jsonl",
#         "user_messages": ["...", "..."],
#         "tool_counts": {"Edit": 5, "Bash": 12}
#       }
#     ]
#   }

set -euo pipefail

DATE="${1:-$(date +%Y-%m-%d)}"

SEARCH_PATHS=(
  "$HOME/.claude/projects"
  "$HOME/claude-data/projects"
)

# Date markers: start and end of target day (local time)
MARKER_START="/tmp/.daily-log-start-$$"
MARKER_END="/tmp/.daily-log-end-$$"
trap 'rm -f "$MARKER_START" "$MARKER_END"' EXIT

touch -t "$(echo "$DATE" | tr -d '-')0000" "$MARKER_START"
# Next day 00:00
NEXT_DATE=$(date -j -v+1d -f "%Y-%m-%d" "$DATE" "+%Y%m%d")
touch -t "${NEXT_DATE}0000" "$MARKER_END"

# Collect matching log files across both search paths
LOG_FILES=()
for search_path in "${SEARCH_PATHS[@]}"; do
  [ ! -d "$search_path" ] && continue
  while IFS= read -r -d '' logfile; do
    LOG_FILES+=("$logfile")
  done < <(find "$search_path" -type f -name "*.jsonl" -newer "$MARKER_START" ! -newer "$MARKER_END" -not -path "*/subagents/*" -print0 2>/dev/null)
done

# Derive a friendly project name from the encoded directory name
#   "-Users-foo-Documents-Develop-continova-hp" → "continova-hp"
# Takes the segment after the final match of a known dev-dir marker.
derive_project_name() {
  local encoded="$1"
  # Try common dev-dir markers in priority order
  for marker in "Develop-" "Projects-" "dev-" "src-" "repos-"; do
    if [[ "$encoded" == *"-$marker"* ]]; then
      echo "${encoded##*-$marker}"
      return
    fi
  done
  # Fallback: last path segment (after final '-')
  echo "${encoded##*-}"
}

# Build session array
SESSIONS_JSON="[]"
for logfile in "${LOG_FILES[@]:-}"; do
  [ -z "${logfile:-}" ] && continue
  encoded_dir="$(basename "$(dirname "$logfile")")"
  project_name="$(derive_project_name "$encoded_dir")"

  # User messages (up to 10, first 300 chars each)
  user_msgs=$(jq -c '[
    inputs
    | select(.type == "user")
    | .message.content
    | if type == "array" then map(select(.type == "text") | .text) | join(" ")
      elif type == "string" then .
      else empty end
    | select(. != null and . != "")
    | select(startswith("<") | not)
    | .[0:300]
  ] | unique | .[0:10]' < "$logfile" 2>/dev/null || echo "[]")

  # Tool use counts
  tool_counts=$(jq -c '[
    inputs
    | select(.type == "assistant")
    | .message.content // []
    | if type == "array" then .[] else empty end
    | select(.type == "tool_use")
    | .name
  ] | group_by(.) | map({key: .[0], value: length}) | from_entries' < "$logfile" 2>/dev/null || echo "{}")

  SESSIONS_JSON=$(jq -c \
    --arg project "$project_name" \
    --arg encoded "$encoded_dir" \
    --arg file "$logfile" \
    --argjson msgs "$user_msgs" \
    --argjson tools "$tool_counts" \
    '. + [{
      project: $project,
      project_path: $encoded,
      file: $file,
      user_messages: $msgs,
      tool_counts: $tools
    }]' <<< "$SESSIONS_JSON")
done

# Merge sessions by project (combine messages + sum tool counts)
MERGED=$(jq -c '
  group_by(.project) | map({
    project: .[0].project,
    project_path: .[0].project_path,
    file_count: length,
    user_messages: (map(.user_messages) | add | unique | .[0:15]),
    tool_counts: (map(.tool_counts) | add | to_entries | group_by(.key) | map({key: .[0].key, value: (map(.value) | add)}) | from_entries)
  })
' <<< "$SESSIONS_JSON")

jq -n \
  --arg date "$DATE" \
  --argjson sessions "$MERGED" \
  '{date: $date, session_count: ($sessions | length), sessions: $sessions}'
