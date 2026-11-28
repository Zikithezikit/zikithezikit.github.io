# Voice

Taken from the two newest posts and from the edits Yoav made to them
("Trim self-comments and filler", "Remove the shortcut callout at the top",
"Remove the 'what the paper does not say' section"). Those edits show what he cuts.

## Sentences

- Short. Subject, verb, object. Split anything with two "and"s or a semicolon.
- Present tense for how things work, past tense for what was measured.
- Concrete nouns. Name the thing: "a disk read", not "an expensive operation".
- Numbers in digits with thousands separators: 1,000,000 keys, 20 bytes, $1,300 a month.
- Round with "about": "about $1,300". Measured values stay exact: "I saw 78,121".

| Instead of | Write |
|---|---|
| Your bank accounts could be vulnerable within the next decade. | Most lookups in a big system find nothing. |
| This revolutionary approach leverages linear algebra. | It stores a table chosen so that one equation per key comes out true. |
| It's worth noting that the error only goes one way. | The error only goes one way. |
| In this section, we'll explore how the solver works. | (delete it, start with the content) |
| This results in significant space savings. | That is 8.99 bits per key, 22% less than Bloom. |

## Where numbers come from

Each number has exactly one of these labels, in the sentence or in the caption:

- **measured**: "measured at 1,000,000 keys with pyribbon 0.1.2"
- **formula**: "Bloom values are the 1.44 × r formula"
- **source**: `[\[3\]](#ref-3)`, with a page when it is a paper: `[\[1, p. 38\]](#ref-1)`
- **assumption**: "Take 100 microseconds... That is my assumption, not a measurement."
- **made up for the example**: "The $310 household is made up."

When a measured number and a predicted number both exist, show both:
"The design says 78,125 false positives in 20 million probes. I saw 78,121."

## Structure inside a section

1. The claim or the question, in one or two sentences.
2. The smallest example that shows it, worked out.
3. The figure or table, with an italic caption that says what it shows and where it is from.
4. What the figure means, in one short paragraph with the key number.

Bullets are for lists of separate things (uses, checks, assumptions). Not for an argument.

## First person

- Yes: "I wrote pyribbon", "I picked `fp_bits=16`", "my calculation", "I saw 303".
- No: "I think this is fascinating", "I hope this helps", "let me explain".

## What gets cut

- Openings that sell: hooks, rhetorical questions, "Imagine...".
- Self-comments: "this is the interesting part", "as we saw above", "simply put".
- Shortcut boxes at the top ("TL;DR", "jump to the chart"). The description field does that job.
- Sections about what the post or paper does not cover.
- Summary or conclusion sections. The last content section ends on a fact.
- Exclamation marks, emoji, bold for emphasis inside sentences.

## Callouts (Chirpy prompts)

```markdown
> Numbers marked "measured" are my own measurements with pyribbon 0.1.2.
{: .prompt-info }
```

- `.prompt-info`: how to read the numbers (units, rounding, exchange rate, version).
- `.prompt-warning`: a misreading the reader is likely to make, or a safety limit.
- `.prompt-tip`: rarely. `.prompt-danger`: almost never.
- At most one callout per section, and never as the first thing in the post.

## Sources section

Last section, titled `## Sources` (or `## NN. References` when sections are numbered to the end).
APA-like, one entry per paragraph, each with an anchor:

```markdown
<span id="ref-1"></span>\[1\] Author, A., & Author, B. (2021). _Title in italics_. Venue. [https://full.url](https://full.url)
```

Cite in text as `[\[1\]](#ref-1)` or `[\[1, p. 6\]](#ref-1)`. Number in order of first use.
Every cited number has an entry and every entry is cited. `tools/lint-post.py` checks this.

## Hebrew posts

Same rules. `lang: he`. Keep code, math and English names left-to-right: wrap mixed-direction
names in `<bdi>...</bdi>`. Put display math on its own lines, not inside a Hebrew sentence.
