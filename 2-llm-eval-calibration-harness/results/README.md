# Results — LLM Evaluation & Calibration Harness for Finance

This file is the only source for numbers cited from this project; a figure that
is not here with a run date does not get cited.

## Measured results

Two open language models, scored on the same questions, by the same lexical
grader, alongside the deterministic stand-ins.

| Answerer | Accuracy | Fabrication | Citation |
|---|---:|---:|---:|
| **qwen2.5-coder:7b** (real model) | **1.0000** | 0.0000 | 1.0000 |
| **gemma4:latest** (real model) | **1.0000** | 0.0000 | 1.0000 |
| careful (best stand-in) | 0.9091 | 0.0000 | 1.0000 |
| uncited | 0.9091 | 0.0000 | 0.3636 |
| year-blind | 0.7273 | 0.0000 | 1.0000 |
| eager | 0.6364 | 0.0000 | 1.0000 |
| over-refuser | 0.3636 | 0.0000 | 0.3636 |

**Suite:** 22 questions built from filed SEC XBRL values — 10 answerable,
8 with no answer, 4 traps. 36.4% of the suite has no answer, because a harness
that only asks answerable questions measures fluency.

**Run date:** 2026-09-12. **Data vintage:** SEC EDGAR company-concept API,
retrieved 2026-09-12; file hashes and URLs in `data/MANIFEST.json`.

**Commands:** `python -m data.fetch` then `python run_llm_demo.py --real`
(`CALIB_MODEL=gemma4:latest` for the second model). 22 of 22 calls succeeded in
each run; median latency 0.89 s and 1.74 s respectively.

## The one place the models beat the baseline

Both models scored 1.0000 and the careful stand-in scored 0.9091. The entire
margin is two questions, and they are the same two:

| Question | careful answered | Both models answered |
|---|---|---|
| What was **MSFT**'s total revenue in fiscal 2025? | `383,285 [AAPL-2025]` | *not stated in the provided documents* |
| What was **AAPL**'s total revenue in fiscal 2026? | `245,122 [MSFT-2026]` | *not stated in the provided documents* |

Both are cross-registrant questions: the documents shown belong to one company
and the question names another. A keyword lookup reads the figure off the page
in front of it without checking whose page it is. Both models checked.

That is a real difference and a narrow one. It is the only thing these runs
establish about the models that the stand-ins do not already establish about
the grader.

## Run log

| Run | Date | Scale | Command | Notes |
|---|---|---|---|---|
| Stand-ins, authored suite | 2026-08-31 | 14 questions | `python -m src.demo` | No model. Establishes that the grader separates behaviours |
| Stand-ins, filed suite | 2026-09-06 | 24 questions | `python -m src.demo --real` | No model. Superseded: only 2 of 24 questions had no answer |
| qwen2.5-coder:7b, authored | 2026-09-12 | 14 questions | `python run_llm_demo.py` | 1.0000, ties the careful stand-in |
| **qwen2.5-coder:7b, filed** | **2026-09-12** | **22 questions** | `python run_llm_demo.py --real` | **1.0000, 0 fabrication** |
| **gemma4:latest, filed** | **2026-09-12** | **22 questions** | `CALIB_MODEL=gemma4:latest python run_llm_demo.py --real` | **1.0000, 0 fabrication** |

## What this project does *not* establish

- **It does not rank the two models.** Both scored 1.0000. A suite on which two
  different architectures are indistinguishable has not measured either of them
  against the other; it has hit its ceiling.
- **It does not establish calibration.** These runs measure whether a model
  reports a stated figure, cites it, and declines when there is nothing to
  report. Calibration — whether stated confidence tracks correctness — is not
  measured anywhere here.
- **Twenty-two questions is small**, drawn from three registrants and two
  fiscal years. Nothing here generalises to other filings, other periods, or
  other question types.
- **The grader is lexical**, by design: an LLM judge would make this harness's
  reliability a function of the thing it measures. That choice costs subtlety.
  A correct figure phrased unusually could be marked wrong.
- **Two earlier runs were wrong and are superseded.** The first filed-suite run
  scored a model at 1.0000 accuracy and 0.9167 fabrication simultaneously — the
  number regex was reading the year out of a citation like `[AAPL-2025]` as a
  negative figure appearing in no source. The stand-ins were also consulting a
  hardcoded table of a different corpus and so could not answer a filed question
  at all. Both are fixed, both are covered by tests, and the run log above
  marks which results predate the fixes.
