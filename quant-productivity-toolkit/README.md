# qkit-research

> The four checks that decide whether a backtest means anything: lookahead, survivorship, label leakage, and how many strategies you tried before this one.

**Repository:** `5.0-Ai-Engineering-Toolkit` &middot; **Pillar:** Financial Stability

## Status

This is working code with a runnable demo and 28 tests. It is **not** a
finished result.

Release artifacts (sdist + wheel) are built and pass twine check, but the package is NOT published to PyPI — no downloads, no users. Every demonstration below runs on synthetic series where the contamination was put there deliberately, which is the only way to show a detector finds it.

Last run: `2026-08-31T21:08:19+00:00`

## Quick start

```bash
pip install -r requirements.txt
python -m pytest tests/ -q     # 28 tests
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
  |-- qkit_research-0.1.0-py3-none-any.whl
  |-- qkit_research-0.1.0.tar.gz
docs/
  |-- DATA.md
  |-- EVIDENCE.md
  |-- METHOD.md
pyproject.toml
qkit/
  |-- __init__.py
  |-- cli.py
  |-- lookahead.py
  |-- statistics.py
  |-- universe.py
  |-- validation.py
qkit_research.egg-info/
  |-- PKG-INFO
  |-- SOURCES.txt
  |-- dependency_links.txt
  |-- entry_points.txt
  |-- requires.txt
  |-- top_level.txt
requirements.txt
results/
  |-- README.md
  |-- latest.json
src/
  |-- .gitkeep
  |-- __init__.py
  |-- demo.py
  |-- site.py
  |-- sitekit.py
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
cp -r website/ ../my-quant-productivity-toolkit-site && cd ../my-quant-productivity-toolkit-site
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
