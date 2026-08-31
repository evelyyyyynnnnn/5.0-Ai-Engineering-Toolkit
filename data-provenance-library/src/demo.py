"""A four-stage financial pipeline that never loses its sources."""
from __future__ import annotations
import json, pathlib, subprocess, sys
from datetime import datetime, timezone
import lineage as L
from lineage.graph import build_graph, explain, to_dot

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
    out = subprocess.run([sys.executable, "-m", "lineage.cli", "--help"],
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
        "package": {"name": "lineage", "version": L.__version__,
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


def main() -> int:
    r = run()
    print(f"lineage {r['package']['version']}, {r['package']['exports']} exports")
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
