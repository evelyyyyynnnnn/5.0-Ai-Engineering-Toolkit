# Data Provenance / Lineage Library

> **Status: scaffold.** Structure only — no method, data or result is claimed
> yet. Every "not yet measured" below is a real gap, not a placeholder to be
> filled in with an estimate.

**Repository:** `5.0-Ai-Engineering-Toolkit`
**NIW pillar (Dhanasar prong 1):** Financial Stability
**Evidence value:** CORE — the through-line of the whole endeavor

## Core idea

Span-level citations from extracted values back to their source documents.

## Why it earns its place

Shared infrastructure with the private-credit project in 3.0; provenance is the through-line of your whole endeavor.

## The petition claim it supports

> Auditable, traceable data pipelines underpinning financial decision systems.

**What the portfolio shows today:** Provenance is implemented ad hoc inside individual projects, if at all.

**Action required:** Extract it as a shared library and have 3.0 private-credit-data-provenance depend on it, so one artifact serves two pillars.

Prior work to build on: `3.0-Financial-Ai-Systems — private-credit-data-provenance`.

## Petition-grade checklist

A project counts as petition-grade only when all five are true. None are yet.

- [ ] Original work, authored here
- [ ] A stated method (`docs/METHOD.md`)
- [ ] Real data at a stated scale (`docs/DATA.md` — target: Shared across repos 3.0 and 5.0)
- [ ] A measured result (`results/README.md`)
- [ ] A README a reviewer can follow, start to finish

## Measured results

Target scale: **Shared across repos 3.0 and 5.0**

| Metric | Baseline | Result | Out-of-sample |
|---|---|---|---|
| Span-citation precision / recall | _not yet measured_ | _not yet measured_ | _pending_ |
| Lineage-graph completeness | _not yet measured_ | _not yet measured_ | _pending_ |
| Overhead vs. an unprovenanced pipeline | _not yet measured_ | _not yet measured_ | _pending_ |

Populate this from `results/`. Do not cite any number in the petition that does
not appear here with a run date behind it.

## Layout

```
data-provenance-library/
├── README.md        this file
├── docs/
│   ├── METHOD.md    what the method is and why it is non-obvious
│   ├── DATA.md      source, scale, licence, and how to reproduce the pull
│   └── EVIDENCE.md  the petition claim, the gap, and the exhibit it becomes
├── src/             implementation
├── data/            pointers and manifests — never raw licensed data
├── results/         measured results, run logs, and the baseline comparison
└── tests/           tests that establish the result is reproducible
```

---
Scaffold generated from `NIW_Project_Portfolio_and_Gap_Plan.xlsx` (sheets: Repo Build-Out Plan, Core Ideas at a Glance, NIW Claim vs Repo Evidence, Notion 创业 Alignment). Structure only — no results are claimed here yet.
