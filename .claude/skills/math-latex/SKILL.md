---
name: math-latex
description: Write LaTeX math that renders correctly on this Jekyll + Chirpy + kramdown + MathJax site. Use whenever a post has equations, formulas, matrices or step-by-step calculations, when math renders wrong, or when adding a MathJax macro.
---

# Math on this site

Pipeline: kramdown turns `$$...$$` into `\(...\)` (inline) or `\[...\]` (display),
then MathJax 3 renders it in the browser. The MathJax config is
`assets/js/data/mathjax.js` (overrides the theme's copy).

## The rules

1. Put `math: true` in the front matter, or nothing renders. The linter checks this.
2. **Always `$$`**. Inline and display use the same delimiter. Kramdown decides by position:
   - inline: inside a sentence, `the rate is $$2^{-r}$$ for $$r$$ bits`;
   - display: `$$` on its own line, with a blank line before and after.
3. **Single `$` is plain text.** This site's config does not treat `$...$` as math, so
   "$1,300 a month" is safe. Do not write math with single dollars.
4. **Pipes in tables break the table.** Inside a Markdown table use `\vert` or `\mid`, not `|`.
5. **Liquid eats `{{` and `{%`.** Write `{ {` with a space, or wrap the block in
   `{% raw %}` ... `{% endraw %}`. Common in `\frac{{a}}{b}`: just drop the extra braces.
6. **Thousands separators** inside math: `9{,}500{,}000` (otherwise MathJax adds a space).
7. Say what an equation means in words, before or after it. The equation is not the explanation.

## Display patterns that work

Define then use:

```latex
$$
\varepsilon = \left(\tfrac{1}{2}\right)^{k}, \qquad k = \frac{m}{n}\ln 2
$$
```

Steps of a derivation, aligned on `=`:

```latex
$$
\begin{aligned}
\frac{m}{n} &= \frac{k}{\ln 2} \\
            &= \frac{\log_2(1/\varepsilon)}{\ln 2} \\
            &\approx 1.44\,\log_2(1/\varepsilon)
\end{aligned}
$$
```

A worked step with operands lined up (used for XOR steps in the pyribbon post):

```latex
$$
\begin{array}{lll}
\text{dave at row 1} & \texttt{1011} \mid \texttt{10} & \\
\oplus\ \text{bob, slot 1} & \texttt{1100} \mid \texttt{10} & \\ \hline
\text{result} & \texttt{0111} \mid \texttt{00} & \text{first 1 is at row 2: hop}
\end{array}
$$
```

Matrices: `\begin{bmatrix} ... \end{bmatrix}`. Cases: `\begin{cases} ... \end{cases}`.

Numbered equations you refer back to:

```latex
$$
\begin{equation} \varepsilon = 2^{-r} \label{eq:fpr} \end{equation}
$$

As equation $$\eqref{eq:fpr}$$ says...
```

Equations without `\label` or `\tag` are not numbered.

## Macros

Defined in `assets/js/data/mathjax.js`, available in every post:

| Macro | Renders as |
|---|---|
| `\xor` | ⊕ |
| `\GF{2}` | GF(2) |
| `\R`, `\N`, `\Z` | ℝ, ℕ, ℤ |
| `\E` | 𝔼 (expectation) |
| `\Prob` | Pr |
| `\bigO{n}` | O(n) |
| `\floor{x}`, `\ceil{x}` | ⌊x⌋, ⌈x⌉ |

Add a macro there only when two or more posts need it.

## Hebrew (RTL) posts

Keep display math on its own lines. Short inline math inside Hebrew text is fine.
Text inside math (`\text{...}`) stays English.

## Checking

```bash
bundle exec jekyll b && grep -l 'class="merror"\|\$\$' _site/posts/<slug>/index.html
```

No output means kramdown converted every `$$`. Then open the page and look: MathJax errors show up in red.
