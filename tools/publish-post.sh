#!/usr/bin/env bash
#
# Move a draft into _posts/ with today's date and the current Israel time offset.
#
# Usage: bash tools/publish-post.sh <slug> [YYYY-MM-DD]

set -eu

cd "$(dirname "$0")/.."

slug="${1:?usage: bash tools/publish-post.sh <slug> [YYYY-MM-DD]}"
draft="_drafts/$slug.md"
[[ -f $draft ]] || { echo "no draft at $draft"; exit 1; }

day="${2:-$(TZ=Asia/Jerusalem date +%F)}"
offset="$(TZ=Asia/Jerusalem date -d "$day 08:00" +%z)"
target="_posts/$day-$slug.md"

python3 tools/lint-post.py "$draft"

# insert or replace the date line after the title
if grep -q '^date:' "$draft"; then
  sed -i "s|^date:.*|date: $day 08:00:00 $offset|" "$draft"
else
  sed -i "0,/^title:/s|^\(title:.*\)|\1\ndate: $day 08:00:00 $offset|" "$draft"
fi

if git ls-files --error-unmatch "$draft" >/dev/null 2>&1; then
  git mv "$draft" "$target"
else
  mv "$draft" "$target"
fi

echo "published as $target"
echo "next: bash tools/test.sh"
