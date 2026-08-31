# LLM Evaluation & Calibration Harness for Finance

> **Status: scaffold.** Structure only — no method, data or result is claimed
> yet. Every "not yet measured" below is a real gap, not a placeholder to be
> filled in with an estimate.

**Repository:** `5.0-Ai-Engineering-Toolkit`
**NIW pillar (Dhanasar prong 1):** Cross-cutting
**Evidence value:** CORE — serves the hallucination and verification argument

## Core idea

Grounding, citation accuracy and refusal behaviour evaluation for LLMs applied to finance.

## Why it earns its place

Directly serves the hallucination and verification argument in Section 2 of the petition.

## The petition claim it supports

> Verification and robustness of LLM systems in high-stakes domains (Petition Section 2).

**What the portfolio shows today:** No evaluation harness exists in any repository.

**Action required:** Build it on public filings and public data only. Pairs with the agent-verification-harness in repo 1.0 — keep the two scopes distinct.

Prior work to build on: `1.0-Secure-Ai-Agent-Infrastructure — agent-verification-harness`.

## Petition-grade checklist

A project counts as petition-grade only when all five are true. None are yet.

- [ ] Original work, authored here
- [ ] A stated method (`docs/METHOD.md`)
- [ ] Real data at a stated scale (`docs/DATA.md` — target: Public filings and public financial corpora)
- [ ] A measured result (`results/README.md`)
- [ ] A README a reviewer can follow, start to finish

## Measured results

Target scale: **Public filings and public financial corpora**

| Metric | Baseline | Result | Out-of-sample |
|---|---|---|---|
| Grounding accuracy | _not yet measured_ | _not yet measured_ | _pending_ |
| Citation precision | _not yet measured_ | _not yet measured_ | _pending_ |
| Refusal calibration on unanswerable queries | _not yet measured_ | _not yet measured_ | _pending_ |
| Hallucination rate by task type | _not yet measured_ | _not yet measured_ | _pending_ |

Populate this from `results/`. Do not cite any number in the petition that does
not appear here with a run date behind it.

## Layout

```
llm-eval-calibration-harness/
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
