# spanlineage

> Span-level provenance that survives arithmetic: a derived number keeps the characters it came from, across every transformation and every document.

**Repository:** `5.0-Ai-Engineering-Toolkit` &middot; **Pillar:** Financial Stability

## Status

This is working code with a runnable demo and 20 tests. It is **not** a
finished result.

Release artifacts (sdist + wheel) are built and pass twine check, but the package is NOT published to PyPI, so it has no downloads and no users. The pipeline below runs on two authored filing extracts; the library is real, the filings are not.

Last run: `2026-08-31T21:08:19+00:00`

## Quick start

```bash
pip install -r requirements.txt
python -m pytest tests/ -q     # 20 tests
python -m src.demo             # runs everything, rewrites results/ and website/
```

## Layout

```
LICENSE
MANIFEST.in
PACKAGE_README.md
README.md
data/
  |-- README.md
  |-- manifests/
  |-- sample/
dist/
  |-- spanlineage-0.1.0-py3-none-any.whl
  |-- spanlineage-0.1.0.tar.gz
docs/
  |-- DATA.md
  |-- EVIDENCE.md
  |-- METHOD.md
pyproject.toml
requirements.txt
results/
  |-- README.md
  |-- latest.json
spanlineage/
  |-- __init__.py
  |-- cli.py
  |-- core.py
  |-- graph.py
  |-- verify.py
spanlineage.egg-info/
  |-- PKG-INFO
  |-- SOURCES.txt
  |-- dependency_links.txt
  |-- entry_points.txt
  |-- requires.txt
  |-- top_level.txt
src/
  |-- .gitkeep
  |-- __init__.py
  |-- demo.py
  |-- site.py
  |-- sitekit.py
tests/
```

- `src/` &mdash; the implementation.
- `tests/` &mdash; pytest suite. These guard behaviour, not just imports.
- `results/latest.json` &mdash; the output of the last demo run. Every figure quoted
  anywhere in this project traces back to this file.
- `website/` &mdash; a self-contained static site, deployable to Vercel by copying the
  folder into its own repository. See `website/README.md`.

## The website

`website/` has no build step. To deploy it independently:

```bash
cp -r website/ ../my-1-data-provenance-library-site && cd ../my-1-data-provenance-library-site
git init && git add -A && git commit -m "site"
vercel deploy --prod
```

The page is regenerated from `results.json` on every `python -m src.demo`, so the
figures on the site and the figures the code produces cannot drift apart. Do not edit
numbers on the page by hand.

## Honesty note

Everything in this project runs on clearly-labelled synthetic or authored data.
Swap in the real source and the same pipeline reports real numbers &mdash; that is
what the structure is for. Until that happens, nothing here should be cited as a
measured result, and the site's closing section states explicitly what the project
does not establish.
