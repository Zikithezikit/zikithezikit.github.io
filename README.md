# zikithezikit.github.io

Source of [zikithezikit.github.io](https://zikithezikit.github.io), Yoav Haimov's blog.
Built with Jekyll and the [Chirpy](https://github.com/cotes2020/jekyll-theme-chirpy) theme.

## Run it

```bash
bundle install
bash tools/run.sh --drafts
```

Then open http://127.0.0.1:4000.

## Write a post

```bash
bash tools/new-post.sh my-topic "My Topic: The Angle" --math
# write _drafts/my-topic.md, make figures with _figures/my-topic/make_figures.py
python3 tools/lint-post.py _drafts/my-topic.md
bash tools/publish-post.sh my-topic
bash tools/test.sh
```

How posts are written here (voice, structure, worked examples, math, figures) is in
[AGENTS.md](AGENTS.md) and `.claude/skills/`.

## Deploy

Every push to `main` builds and deploys through GitHub Actions.

## License

The theme setup is MIT (see [LICENSE](LICENSE)). The posts and images are the author's.
