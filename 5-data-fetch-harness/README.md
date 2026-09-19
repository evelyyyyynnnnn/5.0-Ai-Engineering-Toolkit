# Data-fetch harness

One command that re-fetches every project's real data across all five
repositories and re-runs each project's demo against what came back.

This folder is tooling, not a research project. It has no result of its own and
contributes no figure to the portfolio. It exists for a different reason: the
portfolio states that 20 of its 22 measured projects run on real public data,
and a statement like that is worth only as much as someone else's ability to
check it. This is how they check it.

## What a reader can do with it

Look at the plan without making a single network request:

```bash
bash 5.0-Ai-Engineering-Toolkit/5-data-fetch-harness/fetch-all.sh --list
```

```
portfolio root: /home/you/niw
17 project(s) would be fetched and re-run:
  1.0-Secure-Ai-Agent-Infrastructure/1-agent-verification-harness
  1.0-Secure-Ai-Agent-Infrastructure/2-chaintrust-bench
  2.0-Healthcare-Ai-Systems/1-clinical-empathy-analysis
  ...
Nothing was fetched. Drop --list to run them.
```

Then, if they want to, actually run it:

```bash
export DATAKIT_UA="Your Name your@email"    # the SEC refuses anonymous requests
bash 5.0-Ai-Engineering-Toolkit/5-data-fetch-harness/fetch-all.sh
```

## Layout it expects

All five repositories checked out side by side:

```
niw/
  1.0-Secure-Ai-Agent-Infrastructure/
  2.0-Healthcare-Ai-Systems/
  3.0-Financial-Ai-Systems/
  4.0-Decision-Intelligence-Framework/
  5.0-Ai-Engineering-Toolkit/
```

`--root DIR` overrides this if the repositories live somewhere else.

## Which projects it visits

A project qualifies by owning a `data/fetch.py`. That file is the project's own
statement of where its data comes from, and running it is the only way this
script knows how to fetch anything.

`historical-archive/` is excluded by name. Those folders hold prior work kept
for the record; they back no claim in the portfolio, and at least one of them
does own a `data/fetch.py`. Excluding them by name rather than by how deep the
glob happens to reach keeps the exclusion a decision instead of an accident of
layout — a property the test suite pins.

## What it does per project

1. `python3 -m data.fetch` in the project directory, against the real source.
2. If that succeeded, `python3 -m src.demo --real`, so the project's own
   results file is rewritten from the data that was just fetched.

The exit code of the fetch is classified rather than collapsed:

| Exit | Meaning |
|---|---|
| 0 | fetched |
| 2 | the network blocked the request — a proxy or firewall, not the source |
| other | the fetch failed: a URL moved, or the source refused |

A failure never stops the run. Every project is attempted, so one moved URL
does not cost the whole pass.

## What it leaves behind

- `fetch-all.log` in the portfolio root — full output from every project.
- `runs/last-run.json` — which projects fetched, which were blocked, which
  failed, and which demos then produced real results.

That second file is the point. A run that leaves no record is a claim without
evidence, which is the failure mode this portfolio is built against.

The name deliberately avoids `results/latest.json`, `results/latest-real.json`
and `results/latest-llm.json`: the roll-up in
`3.0-Financial-Ai-Systems/7-portfolio-results-rollup` treats those filenames as
evidence that a directory is a project with a measured result. Writing one here
would add a twenty-third project to a portfolio that has twenty-two. A test
pins that too.

## Tests

```bash
python3 -m pytest tests/ -q
```

Ten tests, all driving the real script in `--list` mode against fixture trees:
project selection, the archive exclusion, `--list` working without
`DATAKIT_UA`, a run refusing to start without one, an empty portfolio reporting
itself rather than succeeding quietly, and the two argument-error exit codes.
Each was mutation-checked — removing the behaviour it describes turns that test
red.
