# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A Hugo-based personal website for Tyler Stapler. The build system uses **Bazel** as the primary build tool, with Hugo for static site generation and nginx for serving. Deployed to **Cloudflare Pages** via GitHub Actions.

## Build Commands

```bash
# Local development (no Bazel)
hugo serve -D --baseURL http://localhost       # serve with drafts
make serve                                     # same via Makefile

# Bazel builds
bazel build //:site                            # build raw Hugo site
bazel build //:site_optimized                 # full optimized build (PurgeCSS + critical CSS + gzip)
bazel build //:nginx_container_optimized      # build Docker image

# Test container locally
bazel run //:nginx_test_optimized             # builds + runs nginx container on :1314
```

## Architecture

### Build Pipeline (Bazel)

The Bazel pipeline in `BUILD.bazel` runs Hugo then applies a multi-step optimization:

1. **`:site`** — Hugo build (via `@build_stack_rules_hugo`)
2. **`:site_purgecss`** — removes unused CSS (`tools/purgecss/prune.py`)
3. **`:site_with_pruned_css`** — replaces `all.css` with pruned version
4. **`:critical_css`** — extracts above-fold CSS via headless browser (`tools/critical-css/extract.py`)
5. **`:site_with_critical_css`** — inlines critical CSS into all HTML files
6. **`:site_optimized`** — gzips all text files; this is what CI deploys

### CI/CD

- **`.github/workflows/deploy-cloudflare.yml`** — triggers on pushes to `master` and PRs; runs `bazel build //:site_optimized`, extracts the tar, deploys via `wrangler pages deploy`
- **`.github/workflows/main.yml`** — builds and pushes Docker image to `ghcr.io/tstapler/personal-website`

### Submodules

Two git submodules:
- **`themes/espouse`** — custom Hugo theme (fork at `github.com/tstapler/espouse`)
- **`tools/build-stack-rules-hugo`** — custom fork of Bazel rules for Hugo (`github.com/tstapler/rules_hugo`)

Always clone with `git clone --recurse-submodules` or run `git submodule update --init --recursive` after checkout.

### Content Structure

- `content/blog/` — blog posts
- `content/projects/` — project showcase pages
- `layouts/` — Hugo layout overrides on top of the `espouse` theme
- `config.toml` — Hugo config; site metadata, menu items, `[Params.Technologies]` list

### Tools

- `tools/purgecss/prune.py` — Python script to remove unused CSS selectors
- `tools/critical-css/extract.py` — extracts critical CSS using headless browser
- `tools/critical-css/inline.py` — inlines extracted critical CSS into HTML files
- `gulpfile.js` — legacy Gulp tasks (`critical`, `compress`) used by Earthfile/Docker path but not the Bazel path
