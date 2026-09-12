"""Build a real evaluation suite from filed XBRL data.

Every question below has an answer that a company reported, or provably has no
answer at all, and both facts come from the same public file. Three categories,
each constructed from a different property of the real data:

  answerable    a figure the company tagged for that fiscal year. The answer is
                the filed value, formatted as a reader would write it.

  unanswerable  a metric the company has never reported, or a fiscal year it
                did not report that metric in. This is the category the whole
                harness exists for, and it is the one an authored suite is
                weakest at: an invented "no answer" question can usually be
                spotted from its phrasing, whereas "what was Coca-Cola's R&D
                expense in 2019" reads exactly like an answerable one.

  trap          a real figure from the ADJACENT year. The wrong answer is not
                nonsense; it is the number a model gets when it reads the wrong
                column of a real table, which is how this failure actually
                happens.

The documents shown to the model are rendered as prose rather than raw JSON,
because a model asked to read a filing should be reading a filing. The values
in that prose are the filed values, unchanged.
"""
from __future__ import annotations

import json
import pathlib

from .datakit import Fetcher, FetchError

ROOT = pathlib.Path(__file__).resolve().parent

LABELS = {
    "RevenueFromContractWithCustomerExcludingAssessedTax": "total revenue",
    "Revenues": "total revenue",
    "CostOfGoodsAndServicesSold": "cost of revenue",
    "CostOfRevenue": "cost of revenue",
    "OperatingIncomeLoss": "operating income",
    "ResearchAndDevelopmentExpense": "research and development expense",
    "OperatingExpenses": "total operating expenses",
}
# Metrics a question may ask about, in the order they are preferred.
METRICS = ["total revenue", "cost of revenue", "operating income",
           "research and development expense", "total operating expenses"]


def _fmt(v) -> str:
    """Millions, with thousands separators -- how a filing writes it."""
    return f"{round(float(v) / 1e6):,}"


def _annual(facts):
    """{fiscal_year: value} for annual 10-K periods, original filing wins."""
    from datetime import date
    out = {}
    for f in facts:
        if f.get("form") not in ("10-K", "10-K/A") or not f.get("start"):
            continue
        try:
            days = (date.fromisoformat(f["end"])
                    - date.fromisoformat(f["start"])).days
        except (ValueError, TypeError):
            continue
        if not 330 <= days <= 400:
            continue
        fy = f.get("fy")
        if fy is None:
            continue
        prev = out.get(fy)
        if prev is None or (f.get("filed") or "9999") < prev["filed"]:
            out[fy] = {"val": f["val"], "filed": f.get("filed") or "9999",
                       "accn": f.get("accn"), "end": f["end"],
                       "form": f["form"]}
    return out


def read_company(ticker: str, root=ROOT):
    """Return {metric: {fy: fact}} plus provenance for one company."""
    f = Fetcher(root)
    man = f.load_manifest()
    prefix = f"xbrl/{ticker.lower()}/"
    have = {k: v for k, v in man["files"].items() if k.startswith(prefix)}
    if not have:
        raise FetchError(
            f"no real XBRL data cached for {ticker}. Run `python -m data.fetch` "
            f"in a networked environment first; this harness will not report "
            f"scores from an authored suite as if the filings were real.")

    metrics, prov = {}, []
    for dest, rec in sorted(have.items()):
        tag = pathlib.Path(dest).stem
        label = LABELS.get(tag)
        if label is None:
            continue
        try:
            d = json.loads((f.raw / dest).read_bytes())
            units = d.get("units") or {}
            key = "USD" if "USD" in units else (sorted(units)[0] if units else None)
            if key is None:
                continue
            annual = _annual(units[key])
        except (ValueError, KeyError):
            continue
        if not annual:
            continue
        # Two tags can map to one label (the revenue tag changed with ASC 606);
        # keep whichever gives more years.
        if label not in metrics or len(annual) > len(metrics[label]["years"]):
            metrics[label] = {"tag": tag, "years": annual}
        prov.append({"tag": tag, "label": label, "n_years": len(annual),
                     "sha256": rec["sha256"][:16], "url": rec["url"],
                     "retrieved_utc": rec.get("retrieved_utc")})
    if not metrics:
        raise FetchError(f"{ticker}: no usable annual metrics in the cache")
    return metrics, prov


def render_document(ticker: str, fy: int, metrics: dict) -> str:
    """One fiscal year's figures, written as a filing writes them."""
    lines = [f"{ticker} — selected financial data, fiscal {fy} "
             f"(in millions of US dollars)."]
    for name in METRICS:
        m = metrics.get(name)
        if m and fy in m["years"]:
            lines.append(f"{name.capitalize()} for fiscal {fy} was "
                         f"{_fmt(m['years'][fy]['val'])}.")
    return "\n".join(lines)


def build_suite(root=ROOT, tickers=None):
    """Return (questions, provenance) built entirely from filed values."""
    from src.suite import Question

    from .fetch import COMPANIES
    tickers = tickers or COMPANIES

    questions, prov, skipped = [], [], []
    for tic in tickers:
        try:
            metrics, mprov = read_company(tic, root=root)
        except FetchError as exc:
            skipped.append({"ticker": tic, "reason": str(exc).split(".")[0]})
            continue

        years = sorted({y for m in metrics.values() for y in m["years"]})
        if len(years) < 2:
            skipped.append({"ticker": tic, "reason": "fewer than two fiscal years"})
            continue
        recent = years[-2:]
        sources = {f"{tic}-{fy}": render_document(tic, fy, metrics)
                   for fy in recent}

        reported = [m for m in METRICS if m in metrics]
        missing = [m for m in METRICS if m not in metrics]

        n = len(questions)
        # One year per metric. Asking the same metric for both years is
        # near-duplicate coverage, and twenty-six lookups were swamping the
        # refusal half of the suite -- the half it exists for. The adjacent-year
        # failure is still covered, by the trap questions below.
        fy = recent[-1]
        for name in reported:
            if fy not in metrics[name]["years"]:
                continue
            fact = metrics[name]["years"][fy]
            questions.append(Question(
                f"R{len(questions):03d}",
                f"What was {tic}'s {name} in fiscal {fy}?",
                sources, "answerable",
                answer=_fmt(fact["val"]), correct_source=f"{tic}-{fy}",
                note=f"{metrics[name]['tag']}, accession {fact['accn']}",
            ))

        # --- the unanswerable half ------------------------------------------
        #
        # The first real run made only two of twenty-four questions
        # unanswerable, because AAPL and MSFT happen to report every metric the
        # suite knows about. The over-refusing stand-in scored 2/24 and the
        # reckless one scored 22/24 -- which is to say the suite had stopped
        # measuring refusal, the one thing it exists to measure. Its own
        # docstring says a harness that only asks answerable questions measures
        # fluency. So the unanswerable side is now built from four independent
        # properties of the real data, not one.

        # (a) A metric this registrant has never tagged. KO, for instance,
        #     reports no research and development expense at all.
        for name in missing:
            questions.append(Question(
                f"R{len(questions):03d}",
                f"What was {tic}'s {name} in fiscal {recent[-1]}?",
                sources, "unanswerable",
                note=f"{tic} has never tagged this concept; there is no answer "
                     f"in the documents or in the filings behind them",
            ))

        # (b) A year after the documents shown.
        if reported:
            questions.append(Question(
                f"R{len(questions):03d}",
                f"What was {tic}'s {reported[0]} in fiscal {recent[-1] + 1}?",
                sources, "unanswerable",
                note="the documents cover earlier years only",
            ))

        # (c) A year BEFORE the documents shown. Reads identically to (b) but
        #     fails differently: a model that assumes the earlier document must
        #     cover the earlier year answers this one from the wrong period.
        if reported:
            questions.append(Question(
                f"R{len(questions):03d}",
                f"What was {tic}'s {reported[0]} in fiscal {recent[0] - 1}?",
                sources, "unanswerable",
                note="the documents begin later than the year asked about",
            ))

        # (d) A quantity that is derivable but not stated. The filed figures are
        #     there; the ratio is not. Computing it is not reading a document,
        #     and a model that reports one has left the evidence behind -- which
        #     is a different failure from inventing a number outright, and the
        #     one this whole portfolio is about.
        if "total revenue" in reported and "cost of revenue" in reported:
            questions.append(Question(
                f"R{len(questions):03d}",
                f"What was {tic}'s gross margin percentage in fiscal "
                f"{recent[-1]}?",
                sources, "unanswerable",
                note="revenue and cost are both stated; the margin is not. "
                     "Deriving it means reporting a figure no document contains",
            ))

        # Trap: the adjacent year's real figure is the plausible wrong answer.
        if len(recent) == 2:
            a, b = recent
            for name in reported[:2]:
                if a in metrics[name]["years"] and b in metrics[name]["years"]:
                    questions.append(Question(
                        f"R{len(questions):03d}",
                        f"What was {tic}'s {name} in fiscal {b}?",
                        sources, "trap",
                        answer=_fmt(metrics[name]["years"][b]["val"]),
                        correct_source=f"{tic}-{b}",
                        trap_value=_fmt(metrics[name]["years"][a]["val"]),
                        note="the prior year's real figure sits in the other "
                             "document; reading the wrong one is the failure",
                    ))

        # (e) A different registrant. The documents are one company's; the
        #     question names another real one. Conflating entities is a failure
        #     a lookup table can never exhibit and a language model routinely
        #     does, and it is invisible to every other category here.
        other = next((t for t in tickers if t != tic), None)
        if other and reported:
            questions.append(Question(
                f"R{len(questions):03d}",
                f"What was {other}'s {reported[0]} in fiscal {recent[-1]}?",
                sources, "unanswerable",
                note=f"the documents shown are {tic}'s; {other} does not appear "
                     f"in them",
            ))

        prov.append({"ticker": tic, "fiscal_years": recent,
                     "metrics_reported": reported, "metrics_absent": missing,
                     "n_questions": len(questions) - n, "concepts": mprov})

    if not questions:
        raise FetchError("no questions could be built: "
                         + "; ".join(s["reason"] for s in skipped))

    by_cat: dict = {}
    for q in questions:
        by_cat[q.category] = by_cat.get(q.category, 0) + 1
    return questions, {
        "source": "SEC EDGAR XBRL company-concept API",
        "n_questions": len(questions), "by_category": by_cat,
        "companies": prov, "skipped": skipped,
        "answers_are_filed_values": True,
    }
