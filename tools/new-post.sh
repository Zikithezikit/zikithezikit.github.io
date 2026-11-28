#!/usr/bin/env bash
#
# Scaffold a new post as a draft.
#
# Usage: bash tools/new-post.sh <slug> "<Title>" [--lang he] [--math]
#
# Creates:
#   _drafts/<slug>.md                    the post, from tools/templates/post.md
#   assets/images/<slug>/                where figures are written
#   _figures/<slug>/make_figures.py      the script that makes them (kept in git, not published)
#   .sources/<slug>/                     PDFs and notes (gitignored)

set -eu

cd "$(dirname "$0")/.."

if (($# < 2)); then
  sed -n '3,12p' "$0" | sed 's/^# \{0,1\}//'
  exit 1
fi

slug="$1"
title="$2"
shift 2
lang="en"
math="false"
while (($#)); do
  case "$1" in
  --lang) lang="$2"; shift 2 ;;
  --math) math="true"; shift ;;
  *) echo "unknown option: $1"; exit 1 ;;
  esac
done

if [[ ! $slug =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
  echo "slug must be kebab-case: $slug"
  exit 1
fi

draft="_drafts/$slug.md"
if [[ -e $draft ]] || ls _posts/*-"$slug".md >/dev/null 2>&1; then
  echo "a post with slug '$slug' already exists"
  exit 1
fi

mkdir -p _drafts "assets/images/$slug" "_figures/$slug" ".sources/$slug"

sed -e "s|{{TITLE}}|${title//|/\\|}|" \
  -e "s|{{SLUG}}|$slug|g" \
  -e "s|{{LANG}}|$lang|" \
  -e "s|{{MATH}}|$math|" \
  tools/templates/post.md >"$draft"

fig="_figures/$slug/make_figures.py"
sed -e "s|{{SLUG}}|$slug|g" tools/templates/make_figures.py >"$fig"

echo "created $draft"
echo "created $fig  (writes into assets/images/$slug/)"
echo "sources go in .sources/$slug/ (not committed)"
echo
echo "preview: bash tools/run.sh --drafts"
echo "check:   python3 tools/lint-post.py $draft"
echo "publish: bash tools/publish-post.sh $slug"
