#!/bin/bash
# collect-linear.sh - Linear GraphQL で指定日の自分のアクティビティを収集
#
# Usage:
#   ./collect-linear.sh              # 今日分
#   ./collect-linear.sh 2026-04-12   # 指定日
#
# Requires:
#   - Linear Personal API token stored in macOS Keychain:
#       security add-generic-password -a $USER -s linear-api-token -w <token>
#   - Or via environment variable: LINEAR_API_TOKEN
#
# Output: JSON to stdout
#   { "date": "...", "viewer": {...}, "issues": [...], "comments": [...] }

set -euo pipefail

DATE="${1:-$(date +%Y-%m-%d)}"

# Resolve token
TOKEN="${LINEAR_API_TOKEN:-}"
if [ -z "$TOKEN" ]; then
  TOKEN=$(security find-generic-password -a "$USER" -s linear-api-token -w 2>/dev/null || echo "")
fi

if [ -z "$TOKEN" ]; then
  jq -n --arg date "$DATE" '{date: $date, error: "Linear API token not found (checked $LINEAR_API_TOKEN and Keychain)", issues: [], comments: []}'
  exit 0
fi

# Compute local timezone offset in +HH:MM format
TZ_OFFSET=$(date +%z)
TZ_FORMATTED="${TZ_OFFSET:0:3}:${TZ_OFFSET:3:2}"

SINCE="${DATE}T00:00:00${TZ_FORMATTED}"
NEXT_DATE=$(date -j -v+1d -f "%Y-%m-%d" "$DATE" "+%Y-%m-%d")
UNTIL="${NEXT_DATE}T00:00:00${TZ_FORMATTED}"

# GraphQL query
read -r -d '' QUERY <<'GQL' || true
query DailyActivity($since: DateTimeOrDuration!, $until: DateTimeOrDuration!) {
  viewer {
    id
    name
    email
  }
  issues(
    filter: {
      updatedAt: { gte: $since, lt: $until }
      assignee: { isMe: { eq: true } }
    }
    first: 50
    orderBy: updatedAt
  ) {
    nodes {
      identifier
      title
      state { name type }
      priority
      updatedAt
      url
      project { name }
      team { key name }
    }
  }
  comments(
    filter: {
      createdAt: { gte: $since, lt: $until }
      user: { isMe: { eq: true } }
    }
    first: 50
  ) {
    nodes {
      body
      createdAt
      url
      issue { identifier title url }
    }
  }
}
GQL

PAYLOAD=$(jq -n \
  --arg query "$QUERY" \
  --arg since "$SINCE" \
  --arg until "$UNTIL" \
  '{query: $query, variables: {since: $since, until: $until}}')

RESPONSE=$(curl -sS -X POST https://api.linear.app/graphql \
  -H "Authorization: $TOKEN" \
  -H "Content-Type: application/json" \
  --data "$PAYLOAD" \
  --max-time 20 2>&1) || {
    jq -n --arg date "$DATE" --arg err "$RESPONSE" \
      '{date: $date, error: $err, issues: [], comments: []}'
    exit 0
  }

# Surface GraphQL errors
if echo "$RESPONSE" | jq -e '.errors' > /dev/null 2>&1; then
  ERR=$(echo "$RESPONSE" | jq -c '.errors')
  jq -n --arg date "$DATE" --argjson err "$ERR" \
    '{date: $date, error: $err, issues: [], comments: []}'
  exit 0
fi

# Shape final output
echo "$RESPONSE" | jq --arg date "$DATE" '{
  date: $date,
  viewer: .data.viewer,
  issues: (.data.issues.nodes // []),
  comments: (.data.comments.nodes // [])
}'
