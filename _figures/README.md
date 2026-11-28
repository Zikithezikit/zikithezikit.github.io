# _figures

One folder per post, named after the post's slug. Each holds the scripts that make that
post's figures and worked-example numbers:

- `make_figures.py`: writes charts, diagrams and `cover.png` into `assets/images/<slug>/`.
- `toy.py` (optional): computes the by-hand example and prints the tables pasted into the post.

Jekyll does not publish this folder. Shared style: `tools/figures/blogstyle.py`.
See the `post-figures` and `worked-example` skills in `.claude/skills/`.
