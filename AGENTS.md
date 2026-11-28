# AGENTS.md: zikithezikit.github.io

Yoav Haimov's blog. Jekyll + the Chirpy theme (~> 7.4), Ruby 3.3, deployed to GitHub Pages
by `.github/workflows/pages-deploy.yml` on every push to `main`.

## Writing a post

Use the skills in `.claude/skills/`. Start with `write-post`; it calls the others.

| Skill | For |
|---|---|
| `write-post` | The whole workflow, voice and structure. Read `references/voice.md` before writing prose. |
| `worked-example` | The by-hand toy example and the runnable "Try it" snippet. |
| `math-latex` | Equations: `$$` rules, tables, Liquid clashes, macros. |
| `post-figures` | Charts, diagrams and the cover, from scripts in `_figures/`. |
| `humanize-post` | Final pass for AI-sounding prose. |

The reference posts for style are `_posts/2026-11-15-ribbon-filters-pyribbon.md` and
`_posts/2026-11-10-taxes-and-wonders-explainer-en.md`. The February 2026 posts are an older style.

```bash
bash tools/new-post.sh <slug> "<Title>" [--lang he] [--math]   # draft + figure script
bash tools/run.sh --drafts                                      # preview with drafts
python3 tools/lint-post.py _drafts/<slug>.md                    # structure + prose checks
bash tools/publish-post.sh <slug>                               # move to _posts/ with today's date
bash tools/test.sh                                              # build + lint changed + htmlproofer
```

## Layout

```
_posts/                 published posts, YYYY-MM-DD-kebab-slug.md
_drafts/                unpublished posts (shown only with --drafts)
_figures/<slug>/        scripts that make the post's figures (in git, not published)
assets/images/<slug>/   the figures themselves; posts set media_subpath to this
assets/js/data/mathjax.js   MathJax config and macros (overrides the theme)
tools/                  scripts; tools/figures/blogstyle.py is the shared figure style
.sources/<slug>/        PDFs and notes for a post (gitignored, local only)
.claude/skills/         the writing skills above
```

## Conventions

- Front matter: see `write-post/SKILL.md`. Dates use `+0200` in winter and `+0300` in summer (Asia/Jerusalem).
- Tags and categories: lowercase with hyphens (`data-structures`). Hebrew posts may use Hebrew tags.
- Permalinks are `/posts/<slug>/` (date and prefix dropped).
- Use `{% raw %}` / `{% endraw %}` around Liquid syntax shown in a post.
- Hebrew posts set `lang: he`; `_layouts/default.html` and `_sass/base/_rtl.scss` handle RTL.

## Build and test

```bash
bundle install
bash tools/run.sh               # dev server with live reload at http://127.0.0.1:4000
bash tools/run.sh -p            # production mode
bash tools/test.sh              # what CI runs, plus the linter on changed posts
```

Run `bash tools/test.sh` before committing. CI runs the build and htmlproofer, not the linter.

## Git

Work on a branch, one logical change per commit, short imperative messages
("Add post on X", "Fix chart labels in the X post"). Merge through a PR.
