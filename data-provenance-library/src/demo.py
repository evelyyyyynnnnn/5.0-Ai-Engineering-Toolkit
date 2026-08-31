"""A four-stage financial pipeline that never loses its sources."""
from __future__ import annotations
import json, pathlib, subprocess, sys
from datetime import datetime, timezone
import spanlineage as L
from spanlineage.graph import build_graph, explain, to_dot

ROOT = pathlib.Path(__file__).resolve().parent.parent

FILING = """
CONSOLIDATED RESULTS (unaudited)

Total revenue for the period was 1,284,500 thousand, compared with 1,102,300
thousand in the prior year. Cost of revenue was 742,100 thousand.

Operating expenses totalled 318,400 thousand, of which research and development
was 141,200 thousand.

The Company had 12,450 employees at period end.
"""

NOTES = """
SUPPLEMENTARY NOTE

A one-time restructuring charge of 26,800 thousand is included within operating
expenses and is not expected to recur.
"""


def build_pipeline():
    filing = L.Source("FILING-2024", FILING)
    notes = L.Source("NOTES-2024", NOTES)
    sources = {s.doc_id: s for s in (filing, notes)}

    revenue = L.extract(filing, r"Total revenue for the period was ([\d,]+)")
    prior = L.extract(filing, r"compared with ([\d,]+)")
    cogs = L.extract(filing, r"Cost of revenue was ([\d,]+)")
    opex = L.extract(filing, r"Operating expenses totalled ([\d,]+)")
    rnd = L.extract(filing, r"research and development\s+was ([\d,]+)")
    heads = L.extract(filing, r"had ([\d,]+) employees")
    restructuring = L.extract(notes, r"restructuring charge of ([\d,]+)")

    # Four stages of derivation, spanning two documents.
    gross = (revenue - cogs)
    adj_opex = opex - restructuring              # crosses a document boundary
    operating_income = gross - adj_opex
    margin = operating_income / revenue
    growth = (revenue - prior) / prior
    rev_per_head = revenue / heads
    rnd_intensity = rnd / revenue

    return sources, {
        "revenue": revenue, "gross_profit": gross,
        "adjusted_opex": adj_opex, "operating_income": operating_income,
        "operating_margin": margin, "revenue_growth": growth,
        "revenue_per_employee": rev_per_head, "rnd_intensity": rnd_intensity,
    }


def cli_check() -> dict:
    out = subprocess.run([sys.executable, "-m", "spanlineage.cli", "--help"],
                         capture_output=True, text=True, timeout=60)
    return {"exit": out.returncode, "help_ok": "extract" in out.stdout,
            "subcommands": ["extract", "verify"]}


def run() -> dict:
    sources, metrics = build_pipeline()
    margin = metrics["operating_margin"]

    g = build_graph(margin)
    verification = L.verify_against(margin, sources)

    # Tampering: change a figure in the filing and re-verify.
    edited = L.Source("FILING-2024", FILING.replace("1,284,500", "1,384,500"))
    tampered = L.verify_against(margin, {**sources, "FILING-2024": edited})

    rows = {}
    for name, v in metrics.items():
        rows[name] = {
            "value": round(float(v.value), 6),
            "n_spans": len(v.spans),
            "documents": sorted({s.doc_id for s in v.spans}),
            "evidence": [e["text"] for e in v.evidence(sources) if e["text"]],
            "op": v.op,
            "depth": build_graph(v).depth(),
        }

    results = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "is_synthetic": True,
        "data_source": "two authored filing extracts (src/demo.py)",
        "package": {"name": "spanlineage", "version": L.__version__,
                    "exports": len(L.__all__), "published": False},
        "metrics": rows,
        "graph": g.stats(),
        "explanation": explain(margin, sources),
        "verification": verification,
        "tamper": {"detected": not tampered["ok"],
                   "problems": tampered["problems"][:3]},
        "cross_document": sorted({s.doc_id for s in metrics["operating_income"].spans}),
        "dot_lines": len(to_dot(margin).splitlines()),
        "cli": cli_check(),
    }
    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "results" / "latest.json").write_text(
        json.dumps(results, indent=2) + "\n", encoding="utf8")
    return results


def run_real() -> dict:
    """Derive metrics from figures companies actually reported, with spans.

    The tamper check is the one worth watching here. It edits the SEC's own
    JSON, re-verifies, and must fail -- which is the whole claim of the library
    stated against a document anyone can re-download and hash for themselves.
    """
    import sys as _sys
    _sys.path.insert(0, str(ROOT))
    from data.fetch import COMPANIES
    from data.load import ROOT as DATA_ROOT
    from data.load import load_company

    companies, failures = [], []
    for tic in COMPANIES:
        try:
            sources, metrics, prov = load_company(tic, root=DATA_ROOT)
        except Exception as exc:
            failures.append({"ticker": tic, "error": f"{type(exc).__name__}: {exc}"})
            continue

        rows = {}
        for name, v in metrics.items():
            rows[name] = {
                "value": round(float(v.value), 6),
                "n_spans": len(v.spans),
                "documents": sorted({s.doc_id for s in v.spans}),
                "evidence": [e["text"] for e in v.evidence(sources) if e["text"]],
                "op": v.op,
                "depth": build_graph(v).depth(),
            }

        headline = metrics.get("gross_margin") or metrics["revenue"]
        verification = L.verify_against(headline, sources)

        # Tamper: change a digit inside a span this metric actually depends
        # on, in the SEC's own JSON, and re-verify. Editing an unrelated
        # document would prove nothing.
        span = headline.spans[0]
        doc_id = span.doc_id
        original = sources[doc_id]
        a, b = span.start, span.end
        digits = original.text[a:b]
        broken_digits = ("9" + digits[1:]) if digits[:1] != "9" else "8" + digits[1:]
        broken = L.Source(doc_id,
                          original.text[:a] + broken_digits + original.text[b:])
        tampered = L.verify_against(headline, {**sources, doc_id: broken})

        companies.append({
            "ticker": tic,
            "metrics": rows,
            "provenance": prov,
            "graph": build_graph(headline).stats(),
            "explanation": explain(headline, sources),
            "verification": verification,
            "tamper": {"detected": not tampered["ok"],
                       "problems": tampered["problems"][:3]},
            "cross_document": sorted({s.doc_id for s in headline.spans}),
        })

    if not companies:
        from data.datakit import FetchError
        raise FetchError("no company could be loaded: "
                         + "; ".join(f["error"] for f in failures))

    results = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "is_synthetic": False,
        "data_source": "SEC EDGAR XBRL company-concept API -- values as filed, "
                       "each carrying the accession number of the filing it was "
                       "reported in; see data/MANIFEST.json for hashes",
        "package": {"name": "spanlineage", "version": L.__version__,
                    "exports": len(L.__all__), "published": False},
        "duplicate_policy":
            "the same figure is reported many times -- in the original 10-K, "
            "again as a comparative the next year, again in each quarter's "
            "year-to-date column. The earliest FILED entry for a period is "
            "used, because a lineage that followed restatements would explain "
            "a number using characters from a document published after it.",
        "companies": companies,
        "failures": failures,
    }
    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "results" / "latest-real.json").write_text(
        json.dumps(results, indent=2) + "\n", encoding="utf8")
    return results


def main_real() -> int:
    from data.datakit import FetchError
    try:
        r = run_real()
    except FetchError as exc:
        print(f"cannot run on real data: {exc}", file=sys.stderr)
        return 2
    print(f"source: {r['data_source']}")
    for c in r["companies"]:
        print(f"\n=== {c['ticker']} ===")
        for pv in c["provenance"]:
            if pv["status"] != "ok":
                print(f"  {pv['field']:<10} unavailable: {pv['status'][:70]}")
                continue
            print(f"  {pv['field']:<10} {pv['value']:>18,.0f} {pv['unit']}  "
                  f"FY{pv['fy']} {pv['form']} accession {pv['accession']}")
            print(f"  {'':<10} span {pv['span']} reads {pv['span_text']!r} "
                  f"in [{pv['document_sha256']}]")
        print("  derived:")
        for name, m in c["metrics"].items():
            if m["op"]:
                print(f"    {name:<16}{m['value']:>16.6f}  "
                      f"{m['n_spans']} span(s) across {len(m['documents'])} "
                      f"document(s), depth {m['depth']}")
        v = c["verification"]
        print(f"  verifies against the filed documents: {v['ok']}")
        print(f"  tamper detected after editing the SEC's JSON: "
              f"{c['tamper']['detected']}")
    if r["failures"]:
        print("\ncould not load:")
        for f_ in r["failures"]:
            print(f"  {f_['ticker']}: {f_['error'][:100]}")
    print("\nduplicate policy: " + r["duplicate_policy"])
    print("wrote results/latest-real.json")
    return 0


def main() -> int:
    if "--real" in sys.argv[1:]:
        return main_real()
    r = run()
    print(f"spanlineage {r['package']['version']}, {r['package']['exports']} exports")
    print(f"\n{'metric':<24}{'value':>16}{'spans':>7}{'depth':>7}  documents")
    for name, m in r["metrics"].items():
        print(f"{name:<24}{m['value']:>16.4f}{m['n_spans']:>7}{m['depth']:>7}  "
              f"{','.join(d.split('-')[0] for d in m['documents'])}")
    print(f"\nderivation graph for operating_margin: {r['graph']}")
    print("\nexplanation (root first):")
    for e in r["explanation"]:
        ev = f"  <- {e['evidence']}" if e["evidence"] else ""
        val = e["value"]
        vs = f"{val:.4f}" if isinstance(val, float) else str(val)
        print(f"  {'  ' * e['depth']}{e['op']:<10}{vs}{ev}")
    v, t = r["verification"], r["tamper"]
    print(f"\nverification: ok={v['ok']} ({v['n_checked']}/{v['n_spans']} spans checked)")
    print(f"tamper detected after editing revenue: {t['detected']}")
    if t["problems"]:
        print(f"  {t['problems'][0]['issue']}")
    print(f"cross-document metric draws on: {r['cross_document']}")
    try:
        from .site import build_site
        build_site(r); print("\nwebsite/ rebuilt from this run")
    except Exception as exc:
        print(f"\n(site not rebuilt: {exc})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
