# Method — LLM Eval & Calibration Harness

## Problem

Score a model's answers about financial filings on three axes that matter
separately — is the answer right, did it invent anything, and did it cite
correctly — including on questions that have no answer.

## Why the approach is non-obvious

Accuracy alone hides the failure that matters. A model that answers everything
confidently and a model that refuses appropriately can score identically on a
suite of answerable questions, and only one of them is safe to deploy over
filings. So the suite deliberately contains questions with **no** answer and
questions designed to invite a plausible wrong one, and fabrication is scored
as its own axis rather than folded into accuracy.

The second non-obvious part is ordering. A grader has to be shown to separate
careful behaviour from reckless behaviour **before** any model's score means
anything, which is why this project began with deterministic stand-ins rather
than models.

## Method

Questions are built from filed SEC XBRL values, so every answer has a filed
ground truth rather than an annotator's opinion.

| Category | Count |
|---|---:|
| Answerable | 10 |
| Unanswerable | 8 |
| Trap | 4 |
| **Total** | **22** |

Five deterministic stand-ins each embody one failure mode — `careful`, `eager`,
`year-blind`, `over-refuser`, `uncited` — and are scored on the same questions
by the same grader as any real model.

## What the runs found

### Stage one: the grader, with no model involved

`any_language_model_run` is `false` in `results/latest-real.json`, and the file
says why:

> the answerers are deterministic stubs, not language models. This measures whether the harness separates behaviours on real questions; it measures no model's calibration.

That run used a 24-question suite weighted
20 answerable to
2 unanswerable and
2 trap, on which `eager` posted a fabrication
rate of 1.000 — every answerable question
fabricated — against 0.125 for `careful`.
The grader separates the behaviours it was built to separate.

### Stage two: two open models on the current suite

**qwen2.5-coder:7b** — run 2026-09-12

| Answerer | Accuracy | Fabrication rate | Citation accuracy |
|---|---:|---:|---:|
| llm:qwen2.5-coder:7b | 1.0000 | 0.0000 | 1.0000 |
| careful | 0.9091 | 0.0000 | 1.0000 |
| eager | 0.6364 | 0.0000 | 1.0000 |
| year-blind | 0.7273 | 0.0000 | 1.0000 |
| over-refuser | 0.3636 | 0.0000 | 0.3636 |
| uncited | 0.9091 | 0.0000 | 0.3636 |

**gemma4:latest** — run 2026-09-12

| Answerer | Accuracy | Fabrication rate | Citation accuracy |
|---|---:|---:|---:|
| llm:gemma4:latest | 1.0000 | 0.0000 | 1.0000 |
| careful | 0.9091 | 0.0000 | 1.0000 |
| eager | 0.6364 | 0.0000 | 1.0000 |
| year-blind | 0.7273 | 0.0000 | 1.0000 |
| over-refuser | 0.3636 | 0.0000 | 0.3636 |
| uncited | 0.9091 | 0.0000 | 0.3636 |

### The result is a saturated suite, and should be read that way

Both models score **1.0000 accuracy,
0.0000 fabrication and
1.0000 citation accuracy** — a clean
sweep of all 22 questions, by two models of quite different character: one a
code model, one a general one.

Two models of different capability scoring identically and perfectly is
evidence about the **suite**, not about the models. The current suite is
12 parts refusal to
10 parts retrieval, and appropriate refusal is the easier half.
The `over-refuser` stand-in scoring 0.3636 on the same
questions shows the floor is not low.

**No calibration claim should be made from these runs.** What they establish is
that the harness runs end to end against real models on filed data, and that the
present question set no longer discriminates between them.

## Limitations

- **The suite saturates.** Both models answered every question correctly. It
  needs harder answerable questions before a score separates anything.
- **22 questions.** Small enough that one item is worth 4.5%.
- **`separation` is `null`** on both model runs — the separation statistic was
  computed for the stand-in run only.
- **Two open models, run locally.** Nothing here speaks to frontier models.

## Reproduction

```bash
pip install -r requirements.txt
python -m pytest tests/ -q     # 49 tests
python -m src.demo --real
```
