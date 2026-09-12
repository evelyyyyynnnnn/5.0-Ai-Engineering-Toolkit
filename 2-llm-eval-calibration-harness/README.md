# LLM Eval & Calibration Harness

> Grounding, citation accuracy and refusal behaviour for LLMs over financial filings — with questions that have no answer, because that is where a finance assistant actually fails.

**Repository:** `5.0-Ai-Engineering-Toolkit` &middot; **Pillar:** Cross-cutting

## Status

Working code, 49 tests, and two real language models scored on real filed data.

The committed results used to carry `any_language_model_run: false`, and that
was the honest description of them: every answerer was a deterministic stand-in
written to embody one failure mode — eager, year-blind, over-refusing, uncited.
They exist so the grader can be shown to separate careful behaviour from
reckless behaviour, which has to be established before any model's score means
anything.

That is no longer the state. On 2026-09-12 two open models were scored on 22
questions built from filed SEC XBRL values, alongside the stand-ins, on the same
questions, by the same grader:

| Answerer | Accuracy | Fabrication | Citation |
|---|---:|---:|---:|
| **qwen2.5-coder:7b** | **1.0000** | 0.0000 | 1.0000 |
| **gemma4:latest** | **1.0000** | 0.0000 | 1.0000 |
| careful (best stand-in) | 0.9091 | 0.0000 | 1.0000 |
| eager | 0.6364 | 0.0000 | 1.0000 |
| over-refuser | 0.3636 | 0.0000 | 0.3636 |

The models' entire margin over the lookup baseline is two cross-registrant
questions: shown one company's documents and asked about another, the lookup
reads the figure in front of it and both models decline. See
`results/README.md` for the full table, the run log, and what these runs do not
establish — starting with the fact that two models scoring identically means the
suite has not distinguished them.

**A real model can be scored on your own machine, with no key and no network
beyond it:**

```bash
ollama pull qwen2.5-coder:7b
python run_llm_demo.py              # authored suite
python run_llm_demo.py --real       # suite built from filed SEC values
```

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
python -m pytest tests/ -q     # 49 tests
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
