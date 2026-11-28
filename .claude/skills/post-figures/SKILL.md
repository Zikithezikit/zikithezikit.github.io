---
name: post-figures
description: Make the charts, diagrams and cover image for a post in the site's visual style, from a script kept in the repo. Use when a post needs a chart, a diagram, a cover/preview image, or when a figure needs fixing (labels, colors, sizes, alt text).
---

# Figures

Every figure is made by a script in `_figures/<slug>/make_figures.py` and written to
`assets/images/<slug>/`. `_figures/` is not published (Jekyll skips folders starting with `_`)
but is kept in git, so a figure can be fixed later by editing the script and rerunning it.

Shared style: `tools/figures/blogstyle.py`.

```bash
python3 _figures/<slug>/make_figures.py
```

## Which kind

| Need | Make | Format |
|---|---|---|
| Measured or sourced numbers | chart (matplotlib + `blogstyle.apply()`) | PNG at 2x |
| A process, a structure, a flow | diagram (`blogstyle.Svg`) | SVG |
| The post's preview image | cover | PNG, exactly 1200 × 630 |

Pick the chart type from the question: compare amounts, bars; change over x, lines;
measured against predicted, dots with intervals and a reference line at 1.

## Style

- Palette (from the existing posts): ink `#1f2937`, muted `#6b7280`, grid `#e5e7eb`,
  blue `#2F6BFF`, green `#13805c`, gold `#c4972f`, red `#b8473d`, light fills
  `#e6eeff`, `#e8fbf3`, `#fff7dc`, `#f2f2f2`. Use the names in `blogstyle.COLORS`.
- White background, no shadows or gradients in the image itself (the page adds `.shadow`).
- Diagrams: rounded boxes, straight or 90° arrows, Arial for labels, Menlo for bits and code.
- Charts: title and a one-line subtitle in the figure, direct labels on bars and lines instead
  of a legend where possible, light horizontal grid only.
- Label numbers on the chart the way the text writes them (8.99, not 8.9912).
- The cover is readable at thumbnail size: two to six words and one visual. No paragraph.

## In the post

```markdown
![Alt text that states what the figure shows, with the key numbers](bits-per-key.png){: w="1191" h="721" .shadow }
_Caption: what is measured or where it is from. pyribbon values are measured at 1,000,000 keys._
```

- Paths are relative to `media_subpath` in the front matter.
- `w` and `h` are the real pixel size (stops layout jumps). `blogstyle` prints this line for you.
- Alt text is the takeaway in words, for someone who cannot see the image. Not "Chart of results".
- The italic caption line goes right under the image and names the source.
- The linter checks alt text, `w`/`h`, and that the file exists.

## Before committing

Look at every image (open the PNG/SVG). Check: no clipped labels, no overlapping text,
numbers match the text, readable in the site's dark mode (images sit on a white card, so mostly yes).
