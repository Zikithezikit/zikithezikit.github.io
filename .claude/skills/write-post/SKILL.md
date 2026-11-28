---
name: write-post
description: Write or rewrite a blog post for this site in Yoav's voice, from idea to a post that builds cleanly. Use for any new post, a rewrite of an old post, or when asked to "write it in my style". Covers structure, voice, sources, the worked example, math, figures and the final checks, and hands off to the other skills in this repo for each part.
---

# Writing a post for this blog

The reference posts are `_posts/2026-11-15-ribbon-filters-pyribbon.md` and
`_posts/2026-11-10-taxes-and-wonders-explainer-en.md`. When a rule here and those
posts disagree, the posts win. The February 2026 posts use an older style: do not copy
their openings, headings or tone.

## Workflow

1. **Scaffold.** `bash tools/new-post.sh <slug> "<Title>" [--lang he] [--math]`.
   It creates `_drafts/<slug>.md`, `assets/images/<slug>/` and `_figures/<slug>/make_figures.py`.
2. **Gather sources first.** Put PDFs and raw notes in `.sources/<slug>/` (gitignored).
   Write down every number you plan to use, with where it came from, before writing prose.
3. **Outline as numbered questions.** One `## NN.` section per question the reader would ask,
   in the order they would ask it. See `references/structure.md`.
4. **Build the worked example** with the `worked-example` skill. Run its script; paste numbers from the output.
5. **Write the prose** following `references/voice.md`.
6. **Math** follows the `math-latex` skill. **Figures** follow the `post-figures` skill.
7. **Check.** Run the `humanize-post` skill, then:
   ```bash
   python3 tools/lint-post.py _drafts/<slug>.md
   bash tools/run.sh --drafts      # look at it at http://127.0.0.1:4000
   ```
8. **Publish** when Yoav says so: `bash tools/publish-post.sh <slug>` moves the draft into
   `_posts/` with today's date, then `bash tools/test.sh`.

Commit on a branch, one logical change per commit, short imperative messages
("Add post on X", "Trim filler in the X post"). Do not push or open a PR unless asked.

## The voice in ten rules

Full version with examples in `references/voice.md`.

1. Short declarative sentences. One idea per sentence. Present tense.
2. Start with the concrete problem, not a hook. No "Imagine...", no "In today's world".
3. Plain words. "use", not "leverage". "shows", not "showcases".
4. Every number says where it came from: measured, a formula, or a source with a page `[\[1, p. 6\]](#ref-1)`.
5. Say what is an assumption: "That is my assumption, not a measurement."
6. "I" only for what Yoav did, measured, chose or assumed.
7. Do the arithmetic in the text. Show one case by hand before the general claim.
8. No narration of the post itself ("In this section we will..."), no recap, no conclusion section.
9. Callouts are rare and earn their place: `.prompt-info` for how to read numbers, `.prompt-warning` for a likely misreading.
10. End with "Try it" (when there is code) and then "Sources". Nothing after the sources.

## Front matter

```yaml
---
title: "Short Title: What It Is"
author: yoav
description: "One or two plain sentences with the main finding and its number."
date: 2026-11-15 08:00:00 +0200   # +0300 during Israeli summer time
lang: en                           # he for Hebrew (RTL is handled by the layout)
categories: [algorithms, data-structures]
tags: [lowercase, hyphenated-tags]
pin: false
math: true                         # only if the post has $$...$$
mermaid: false
media_subpath: /assets/images/<slug>/
image:
  path: cover.png
  alt: "What the cover shows, in words, with its key number"
---
```
