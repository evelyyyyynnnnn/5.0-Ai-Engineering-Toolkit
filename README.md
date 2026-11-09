# 5.0 — AI Engineering Toolkit

[![tests](https://github.com/evelyyyyynnnnn/5.0-Ai-Engineering-Toolkit/actions/workflows/tests.yml/badge.svg)](https://github.com/evelyyyyynnnnn/5.0-Ai-Engineering-Toolkit/actions/workflows/tests.yml)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24094775.svg)](https://doi.org/10.5281/zenodo.24094775)

Shared, installable engineering infrastructure behind the endeavor. Four rebuilt projects carry it.

Part of a five-repository portfolio on one theme: **optimization-driven,
system-level decision frameworks** —
integrating operations research, mathematical optimization and applied AI — for
domains where a wrong decision carries systemic consequences. The three pillars
are financial stability, healthcare safety and secure digital infrastructure.

| | |
|---|---|
| Projects with measured results | **4 of 5** |
| Tests across the suites | **172** |
| Running on real third-party data | **4 of 5** |
| Most recent reportable run | 2026-09-07 |
| Verdict | **Four of five projects measured on real data** |

> "Measured" means: original work, a stated method, real data at a stated
> scale, a measured result, and a README a reviewer can follow. Counts exclude
> duplicates, forks of third-party work, retired projects, and asset-only
> folders.

## Projects

| Folder | Project | Pillar | Evidence value |
|---|---|---|---|
| [`3-quant-productivity-toolkit/`](3-quant-productivity-toolkit/) | Quant Researcher Productivity Toolkit | Financial Stability | CORE — the only honest route to the downloads claim |
| [`2-llm-eval-calibration-harness/`](2-llm-eval-calibration-harness/) | LLM Evaluation & Calibration Harness for Finance | Cross-cutting | CORE — serves the hallucination and verification argument |
| [`1-data-provenance-library/`](1-data-provenance-library/) | Data Provenance / Lineage Library | Financial Stability | CORE — the through-line of the whole endeavor |
| [`4-risk-portfolio-saas/`](4-risk-portfolio-saas/) | Risk-Portfolio SaaS Prototype | Financial Stability | CORE — the strongest of the four Notion tool ideas |

## What each one is

### 1. Quant Researcher Productivity Toolkit — [`3-quant-productivity-toolkit/`](3-quant-productivity-toolkit/)

The Notion 综合性工具 idea shipped as a real, installable package with public download statistics.

*Why it earns its place:* The credible home for the "LLM agent platform, 2,000+ downloads" claim, which currently has no package behind it.

*Target scale:* Public registry download statistics

### 2. LLM Evaluation & Calibration Harness for Finance — [`2-llm-eval-calibration-harness/`](2-llm-eval-calibration-harness/)

Grounding, citation accuracy and refusal behaviour evaluation for LLMs applied to finance.

*Why it earns its place:* Accuracy and calibration come apart: a model can be right often and confidently wrong on the rest, and it is refusal behaviour that decides whether such an error ever reaches a user. Scoring grounding, citation accuracy and refusal together — rather than accuracy alone — is the point of the harness.

*Target scale:* Public filings and public financial corpora

### 3. Data Provenance / Lineage Library — [`1-data-provenance-library/`](1-data-provenance-library/)

Span-level citations from extracted values back to their source documents.

*Why it earns its place:* Shared infrastructure with the private-credit project in 3.0; provenance is the through-line of your whole endeavor.

*Target scale:* Shared across repos 3.0 and 5.0

### 4. Risk-Portfolio SaaS Prototype — [`4-risk-portfolio-saas/`](4-risk-portfolio-saas/)

The Notion 风控组合SaaS idea built as a working risk-portfolio prototype.

*Why it earns its place:* Risk tooling maps directly onto the financial-stability pillar. Of the four items in the Notion 综合性工具 section, this is the one to build.

*Target scale:* Portfolio universes from repo 3.0

## Repository layout

```
5.0-Ai-Engineering-Toolkit/
├── 3-quant-productivity-toolkit/
├── 4-risk-portfolio-saas/
├── 1-data-provenance-library/
└── 2-llm-eval-calibration-harness/
```

Every rebuilt project carries the same skeleton: `README.md`, `src/`, `data/`, `results/`, `tests/`, `website/`.

> Earlier and off-theme prior work (dashboards, consumer apps, templates, and other non-endeavor folders) has been moved to a separate `archive-prior-work` repository to keep this repository focused on the endeavor. It remains recoverable from this repository's git history.

## Ground rules

1. **No number without a run log.** Any figure quoted anywhere in this
   repository must appear in that project's `results/README.md` with a run
   date behind it.
2. **No simulated data under a real claim.** Sample data lives in
   `data/sample/`, labelled, and is never the source of a cited figure.
3. **Adoption must be documentable** — named institutions, dated
   correspondence, registry statistics. Never an inflated count.
4. **Third-party and forked code stays labelled** and is never counted.

---
Structure only — no results are claimed here unless a project's `results/README.md` records a dated run.

## Licence

[Apache License 2.0](LICENSE). The code, benchmarks and documentation in this
repository may be reused, modified and redistributed under its terms, including
by projects that need a patent grant to incorporate them.

Third-party data and vendored code kept under `*/data/` and
`historical-archive/` carry their own terms and are labelled where they appear.
