# LLM Eval & Calibration Harness

> Grounding, citation accuracy and refusal behaviour for LLMs over financial filings — with questions that have no answer, because that is where a finance assistant actually fails.

**Repository:** `5.0-Ai-Engineering-Toolkit` &middot; **Pillar:** Cross-cutting

## Status

This is working code with a runnable demo and 0 tests. It is **not** a
finished result.

NO language model has been run through this harness. Every row below is a deterministic stand-in written to embody one failure mode, so the harness itself can be shown to separate careful behaviour from reckless behaviour before any real model is scored.

Last run: `2026-08-31T19:14:56+00:00`

## Quick start

```bash
pip install -r requirements.txt
python -m pytest tests/ -q     # 0 tests
python -m src.demo             # runs everything, rewrites results/ and website/
```

## Layout

```
README.md
data/
  |-- README.md
  |-- manifests/
  |-- sample/
docs/
  |-- DATA.md
  |-- EVIDENCE.md
  |-- METHOD.md
requirements.txt
results/
  |-- README.md
  |-- latest.json
src/
  |-- .gitkeep
  |-- __init__.py
  |-- demo.py
  |-- graders.py
  |-- models.py
  |-- site.py
  |-- sitekit.py
  |-- suite.py
tests/
  |-- .gitkeep
  |-- test_harness.py
website/
  |-- README.md
  |-- index.html
  |-- results.json
  |-- vercel.json
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
cp -r website/ ../my-2-llm-eval-calibration-harness-site && cd ../my-2-llm-eval-calibration-harness-site
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
