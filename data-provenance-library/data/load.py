"""Locate real reported values inside the SEC's own JSON, with spans.

The SEC's company-concept response is a list of every value a registrant has
reported under one tag, each with the accession number of the filing it came
from, the fiscal period, the form type, and the filing date. The response text
is the source document; a value's span is the byte range where that number
appears in it.

Two things this makes possible that an authored corpus cannot:

  A span that can be checked against a public record. The document is hashed at
  fetch time, so anyone can pull the same URL, hash it, and re-read the same
  characters.

  A duplicate problem that is real. The same figure is reported many times --
  in the original 10-K, then again as a comparative in the next year's filing,
  and again in each quarter's year-to-date column. Picking "the" revenue for a
  period means choosing among genuinely conflicting entries, and this module
  chooses the ORIGINAL filing rather than the most recent restatement, because
  a lineage that silently followed restatements would explain a number using
  characters from a document published after the number was used.
"""
from __future__ import annotations

import json
import pathlib
import re

from .datakit import Fetcher, FetchError

ROOT = pathlib.Path(__file__).resolve().parent

REVENUE_TAGS = ("RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues")
COST_TAGS = ("CostOfGoodsAndServicesSold", "CostOfRevenue")


def parse_concept(raw: bytes) -> dict:
    """Return {'tag', 'units', 'facts': [...]} from a company-concept response."""
    d = json.loads(raw)
    tag = d.get("tag") or ""
    units = d.get("units") or {}
    key = "USD" if "USD" in units else (sorted(units)[0] if units else None)
    if key is None:
        raise ValueError(f"no units in the response for {tag!r}")
    facts = []
    for fact in units[key]:
        if fact.get("val") is None or not fact.get("end"):
            continue
        facts.append({
            "val": fact["val"], "start": fact.get("start"), "end": fact["end"],
            "fy": fact.get("fy"), "fp": fact.get("fp"),
            "form": fact.get("form"), "filed": fact.get("filed"),
            "accn": fact.get("accn"), "frame": fact.get("frame"),
        })
    if not facts:
        raise ValueError(f"no usable facts for {tag!r}")
    return {"tag": tag, "unit": key, "facts": facts}


def annual_fact(concept: dict, fy: int | None = None) -> dict:
    """Pick one annual figure, preferring the filing that first reported it.

    Annual facts are the ones on a 10-K whose period spans about a year. Among
    duplicates for the same period, the earliest FILED wins: that is the
    original report, not a later restatement or a comparative column.
    """
    from datetime import date

    def is_annual(f):
        if f["form"] not in ("10-K", "10-K/A"):
            return False
        if not f["start"]:
            return False
        try:
            days = (date.fromisoformat(f["end"])
                    - date.fromisoformat(f["start"])).days
        except ValueError:
            return False
        return 330 <= days <= 400

    annual = [f for f in concept["facts"] if is_annual(f)]
    if fy is not None:
        annual = [f for f in annual if f["fy"] == fy]
    if not annual:
        raise ValueError(f"no annual fact for {concept['tag']}"
                         + (f" in FY{fy}" if fy else ""))
    # Latest period, and within it the earliest filing.
    latest_end = max(f["end"] for f in annual)
    same = [f for f in annual if f["end"] == latest_end]
    return min(same, key=lambda f: (f["filed"] or "9999-99-99"))


def find_span(text: str, fact: dict) -> tuple:
    """Locate the exact characters of this fact's value in the document.

    The value is matched inside its own JSON object rather than anywhere in the
    file, because the same number appears in many entries and a span pointing
    at a different period's identical figure would be provenance in form only.
    """
    val = fact["val"]
    rendered = repr(int(val)) if float(val).is_integer() else repr(val)
    accn = re.escape(str(fact["accn"]))
    end = re.escape(str(fact["end"]))
    # The object containing this accession and period end.
    for m in re.finditer(r"\{[^{}]*\}", text):
        obj = m.group(0)
        if not re.search(accn, obj) or not re.search(end, obj):
            continue
        vm = re.search(r'"val"\s*:\s*(-?[\d.]+)', obj)
        if vm and vm.group(1).rstrip(".0") == rendered.rstrip(".0"):
            return m.start() + vm.start(1), m.start() + vm.end(1)
    raise ValueError(f"could not locate the value {val} for accession "
                     f"{fact['accn']} in the document")


def load_company(ticker: str, root=ROOT):
    """Return (source, values, provenance) for one company's real figures."""
    import spanlineage as L

    f = Fetcher(root)
    man = f.load_manifest()
    prefix = f"xbrl/{ticker.lower()}/"
    have = {k: v for k, v in man["files"].items() if k.startswith(prefix)}
    if not have:
        raise FetchError(
            f"no real XBRL data cached for {ticker}. Run `python -m data.fetch` "
            f"in a networked environment first; this library will not derive "
            f"numbers from an authored filing and describe them as reported.")

    def read(tags):
        for tag in tags:
            dest = f"{prefix}{tag}.json"
            if dest in have and (f.raw / dest).exists():
                raw = (f.raw / dest).read_bytes()
                try:
                    return tag, raw.decode("utf-8", errors="replace"), \
                        parse_concept(raw), have[dest]
                except ValueError:
                    continue
        return None

    rev = read(REVENUE_TAGS)
    if rev is None:
        raise FetchError(f"{ticker}: no usable revenue concept in the cache")
    cost = read(COST_TAGS)
    rnd = read(("ResearchAndDevelopmentExpense",))

    out, prov = {}, []
    tracked = {}
    for label, got in (("revenue", rev), ("cost", cost), ("rnd", rnd)):
        if got is None:
            continue
        tag, text, concept, rec = got
        try:
            fact = annual_fact(concept)
            a, b = find_span(text, fact)
        except ValueError as exc:
            prov.append({"field": label, "tag": tag, "status": str(exc)})
            continue
        src = L.Source(f"{ticker}:{tag}", text)
        tracked[label] = (src, L.track(float(fact["val"]), src, a, b,
                                       note=f"{tag} {fact['fy']} {fact['form']}"))
        prov.append({
            "field": label, "tag": tag, "status": "ok",
            "value": fact["val"], "unit": concept["unit"],
            "period": f"{fact['start']}..{fact['end']}",
            "fy": fact["fy"], "form": fact["form"],
            "accession": fact["accn"], "filed": fact["filed"],
            "span": [a, b], "span_text": text[a:b],
            "document_sha256": rec["sha256"][:16], "url": rec["url"],
            "retrieved_utc": rec.get("retrieved_utc"),
        })

    if "revenue" not in tracked:
        raise FetchError(f"{ticker}: could not locate an annual revenue figure")

    sources = {s.doc_id: s for s, _ in tracked.values()}
    revenue = tracked["revenue"][1]
    out["revenue"] = revenue
    if "cost" in tracked:
        gross = revenue - tracked["cost"][1]
        out["gross_profit"] = gross
        out["gross_margin"] = gross / revenue      # crosses two documents
    if "rnd" in tracked:
        out["rnd_intensity"] = tracked["rnd"][1] / revenue

    return sources, out, prov
