# Data — LLM Eval & Calibration Harness

| Field | Value |
|---|---|
| Source | SEC EDGAR XBRL company-concept API |
| Questions | 22 |
| Answerable / unanswerable / trap | 10 / 8 / 4 |
| Ground truth | Filed XBRL values, not annotation |
| Licence | US Government work — SEC filings are public record |
| Access | Public API, no key required |
| Model runs recorded | 2026-09-12 |

Full source string as written by the run:

> SEC EDGAR XBRL company-concept API -- every answer is a filed value; see data/MANIFEST.json for hashes

## Why filed XBRL values

Every answer in this suite is a number a company filed with the SEC. That
removes the usual weakness of a question set about documents — that the "right"
answer is one annotator's reading. Here the ground truth is the filing, and
disagreement with it is simply wrong.

## The companies and concepts

Concept series are fetched per company from the XBRL company-concept API and
pinned by SHA-256 in `data/MANIFEST.json`. The first company in the manifest:

| Ticker | Fiscal years | Metrics reported | Questions |
|---|---|---|---|
| AAPL | 2024, 2025 | 5 | 12 |

`metrics_absent` is recorded alongside `metrics_reported` for each company,
because a metric a company did not file is the raw material for an
**unanswerable** question — and those are the questions this suite exists for.

## How the three categories are built

- **Answerable** — the value is in the filing; the model should return it and cite it.
- **Unanswerable** — the concept is genuinely absent for that company and year.
  The correct behaviour is refusal, and refusing is scored as correct.
- **Trap** — a plausible wrong value is available nearby, for instance the same
  metric from an adjacent fiscal year. Returning it is scored as a trap taken.

## What this data cannot tell you

The suite is 12 parts refusal to
10 parts retrieval, and both models tested answered
every question correctly. Until the answerable half is made harder, a score on
this set does not separate models. See [`METHOD.md`](METHOD.md).

## Rules for this folder

1. **Never commit raw API responses.** The manifest and hashes are committed instead.
2. **Ground truth comes from the filing**, never from a model and never from a note.
3. **Record the run.** Every reported figure needs a dated entry in
   [`results/README.md`](../results/README.md).
