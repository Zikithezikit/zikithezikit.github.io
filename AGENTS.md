# AGENTS.md - Developer Guide for zikithezikit.github.io

This is a Jekyll-based blog site using the Chirpy theme.

## Project Overview

- **Type**: Static blog site (Jekyll + GitHub Pages)
- **Theme**: jekyll-theme-chirpy (~> 7.4)
- **Ruby Version**: 3.3
- **Content**: Markdown posts in `_posts/`

## Build Commands

```bash
# Install dependencies
bundle install

# Build the site (development)
bundle exec jekyll b

# Build for production
JEKYLL_ENV=production bundle exec jekyll b

# Serve locally with live reload
bundle exec jekyll s -l

# Or use the helper script
bash tools/run.sh           # Development server
bash tools/run.sh -p       # Production mode

# Serve on specific host
bash tools/run.sh -H 0.0.0.0
```

## Test Commands

```bash
# Run the full test suite (build + htmlproofer)
bash tools/test.sh

# Manual HTML validation
JEKYLL_ENV=production bundle exec jekyll b
bundle exec htmlproofer _site \
  --disable-external \
  --ignore-urls "/^http:\/\/127.0.0.1/,/^http:\/\/0.0.0.0/,/^http:\/\/localhost/"
```

## CI/CD

GitHub Actions (`.github/workflows/pages-deploy.yml`) automatically builds and deploys on push to main/master.

## Code Style Guidelines

### Markdown Posts (`_posts/`)

- Filename format: `YYYY-MM-DD-title.md`
- Use YAML front matter with these fields:
  ```yaml
  title: "Post Title"
  date: YYYY-MM-DD HH:MM:SS +0300
  tags: [tag1, tag2]
  categories: [category]
  ```
- Use Kramdown for markdown (supported by Jekyll)
- Code blocks use Rouge syntax highlighting

### Liquid Templates

- Theme files in `_includes`, `_layouts`, `_plugins`
- Use `{% raw %}` / `{% endraw %}` when displaying Liquid syntax

### Front Matter Defaults

Configured in `_config.yml`:
- Posts: layout `post`, comments enabled, TOC enabled
- Permalinks: `/posts/:title/`

## Naming Conventions

- **Posts**: kebab-case in filename, descriptive titles
- **Tags/Categories**: lowercase, use hyphens (e.g., `rust`, `web-development`)
- **Images**: Place in `assets/img/` with descriptive names

## Important Configuration

- **Baseurl**: Empty (`""`) in `_config.yml`
- **Timezone**: Asia/Jerusalem
- **Paginate**: 10 posts per page
- **PWA**: Enabled with offline cache

## Development Tips

1. Use `bundle exec jekyll s -l` for live reload during development
2. Run `bash tools/test.sh` before committing to catch link/image issues
3. Test with `JEKYLL_ENV=production` to match GitHub Pages environment
4. The site is deployed automatically via GitHub Actions on push to main

## Key Files

- `_config.yml` - Site configuration
- `_posts/` - Blog posts (Markdown)
- `_tabs/` - Navigation tabs
- `_data/` - Data files (locales, etc.)
- `assets/` - Images, CSS, JS
- `_plugins/` - Jekyll plugins
