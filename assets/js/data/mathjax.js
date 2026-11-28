---
layout: compress
# Overrides the theme's assets/js/data/mathjax.js.
# WARNING: Don't use '//' to comment out code, use '{% comment %}' and '{% endcomment %}' instead.
---

{%- comment -%}
  See: <https://docs.mathjax.org/en/latest/options/input/tex.html#tex-options>
  Kramdown already turns $$...$$ into \(...\) or \[...\], so single $ is left out:
  dollar amounts like "$1,300" in a post with math stay plain text.
{%- endcomment -%}

MathJax = {
  tex: {
    inlineMath: [['\\(', '\\)']],
    displayMath: [
      ['$$', '$$'],
      ['\\[', '\\]']
    ],
    tags: 'ams',
    macros: {
      xor: '\\oplus',
      GF: ['\\mathrm{GF}(#1)', 1],
      R: '\\mathbb{R}',
      N: '\\mathbb{N}',
      Z: '\\mathbb{Z}',
      E: '\\mathbb{E}',
      Prob: '\\operatorname{Pr}',
      bigO: ['O\\left(#1\\right)', 1],
      floor: ['\\left\\lfloor #1 \\right\\rfloor', 1],
      ceil: ['\\left\\lceil #1 \\right\\rceil', 1]
    }
  }
};
