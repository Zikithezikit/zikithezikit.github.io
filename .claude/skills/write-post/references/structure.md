# Post structure

## Numbered sections

H2 headings are numbered with two digits and name the question the section answers:

```markdown
## 01. The question
## 02. How much does "maybe" cost?
## 03. Store equations, not keys
## 04. A filter small enough to do by hand
...
## 11. Try it
## Sources
```

H3 subheadings are not numbered. Do not go below H3.

## Two templates that have worked

**Explaining a mechanism or a library** (the pyribbon post):

1. The question: what problem, where it shows up, what the post covers. One callout on how to read numbers.
2. The cost or the baseline: the classic answer and its formula.
3. The idea: the core trick, with the minimum maths to state it.
4. The worked example: shrunken parameters, done by hand step by step.
5. to N-2. The parts that make it work in practice, one per section (hashing, layout, file format, speed).
6. Does it do what it says? Measurements against the predicted numbers.
7. Real uses, each with a measured scenario.
8. Try it: install line plus a short runnable snippet.
9. Sources.

**Explaining a paper or a report** (the taxes post):

1. What the paper is: authors, venue, date, who funded it.
2. The question it asks.
3. The headline result, with the main chart.
4. Terms the reader needs.
5. Where the numbers come from (data and method), with a made-up household as a worked example.
6. to N-1. One section per chart or claim, each with its source page.
7. Stress tests: what changes when assumptions change.
8. References.

## Length

Long is fine when every section answers a question. Cut a section if removing it
does not leave a question unanswered.

## Title and description

- Title: short, says the subject. A colon for the angle: "Ribbon Filters: The Maths Inside pyribbon".
- Description: the finding with its number, in plain words. It shows in search results and on the home page.
