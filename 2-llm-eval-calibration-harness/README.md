# LLM Eval & Calibration Harness

> Grounding, citation accuracy and refusal behaviour for LLMs over financial filings — with questions that have no answer, because that is where a finance assistant actually fails.

**Repository:** `5.0-Ai-Engineering-Toolkit` &middot; **Pillar:** Cross-cutting

## Status

Working code with a runnable demo and 40 tests.

The committed results carry `any_language_model_run: false`, and that is the
honest description of them: every answerer scored so far is a deterministic
stand-in written to embody one failure mode — eager, year-blind, over-refusing,
uncited. They exist so the grader can be shown to separate careful behaviour
from reckless behaviour, which has to be established before any model's score
means anything. That part is done.

**A real model can now be scored.** `src/llm_answerer.py` speaks the OpenAI chat
protocol, so it runs against Ollama on localhost with no key and no network
beyond the machine:

```bash
ollama pull qwen2.5-coder:7b
python run_llm_demo.py              # authored suite
python run_llm_demo.py --real       # suite built from filed SEC values
```

The stubs are scored in the same run, over the same questions, by the same
grader — a model's accuracy means nothing without the behaviours the grader was
built to separate sitting beside it. The run writes `results/latest-llm.json`
with `any_language_model_run: true`.

Two properties the wiring holds to, both covered by tests that need no model
server:

- **The reply reaches the grader verbatim.** Nothing repairs, reformats or
  re-asks. A wrapper that tidied the answer first would be measuring the wrapper.
- **A failed call is scored as the empty answer it was**, not replaced by a
  refusal the model never gave — which on an unanswerable question would credit
  it with exactly the behaviour under test.

## Quick start

```bash
pip install -r requirements.txt
python -m pytest tests/ -q     # 40 tests
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
