---
name: humanize-post
description: Review a post draft for AI-sounding prose and fix it without changing what it says. Use before publishing any post, when a draft "sounds like ChatGPT", or when asked to humanize, tighten or de-fluff a post. Runs the repo linter for mechanical tells, then a manual pass for the patterns a script cannot catch.
---

# Humanize a post

Goal: the post reads like Yoav wrote it (see `write-post/references/voice.md`).
Meaning, numbers, sources and structure stay the same. Only the wording changes.

## Pass 1: the linter

```bash
python3 tools/lint-post.py <post.md>
```

It flags em and en dashes used as punctuation, stock AI words, filler phrases,
exclamation marks and "not X, but Y" constructions, outside code and math.
Fix every hit, or leave it with a reason (a quoted title, a proper name).

## Pass 2: read it for the patterns a script misses

Go section by section. For each paragraph ask "would Yoav cut this?"

| Pattern | Example | Fix |
|---|---|---|
| Hook opening | "Imagine you have a secret password..." | Start with the fact: "A password check normally reveals the password to the server." |
| Rhetorical question then answer | "So what does this mean? It means..." | State the answer. |
| Rule of three for rhythm | "fast, efficient, and scalable" | Keep the one that is true and measured. |
| Inflated stakes | "fundamentally transforms", "a game-changer" | Say what changed, with the number. |
| Hedging stack | "could potentially help to some extent" | One hedge, or none if measured. |
| Signposting | "Let's dive in", "Now, let's look at" | Delete. The heading does this. |
| Restating the heading | "## Hashing" then "Hashing is an important part..." | Start with the content. |
| One-line closer | "And that's the beauty of it." | Delete. End on the last fact. |
| Fake balance | "While X has benefits, it also has drawbacks." | Name the drawback and its size. |
| Vague attribution | "Experts say", "studies show" | Cite: `[\[3\]](#ref-3)`, or cut. |
| Bold sprinkled in sentences | "This is **very important**" | Remove bold. Bold only defines a term once. |
| Synonym cycling | filter / structure / data structure / sketch for the same thing | Pick one name and keep it. |
| Bullet list as an argument | five bullets that are really one paragraph | Rewrite as sentences. |

## Pass 3: numbers and claims

- Every number has a label (measured, formula, source, assumption, made up). Add the missing ones.
- Adjectives that hide a number ("much faster", "significantly smaller") get the number.
- Claims with no source and no measurement get cut or sourced.

## Output

Edit the file in place. Then report in a few lines: what kinds of changes you made,
and anything you left on purpose. Do not paste the whole post back.
