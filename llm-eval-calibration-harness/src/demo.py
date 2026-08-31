"""Run the suite over every stand-in answerer."""
from __future__ import annotations
import json, pathlib, sys
from datetime import datetime, timezone
from .graders import grade, score
from .models import ANSWERERS
from .suite import SUITE, suite_stats

ROOT = pathlib.Path(__file__).resolve().parent.parent


def run() -> dict:
    per_model = {}
    transcripts = {}
    for a in ANSWERERS:
        rows = []
        tr = []
        for q in SUITE:
            ans = a(q)
            g = grade(q, ans)
            rows.append(g)
            tr.append({"qid": q.qid, "question": q.text, "answer": ans,
                       "category": q.category, "ok": g["ok"],
                       "failure": g["failure"]})
        per_model[a.name] = {"score": score(rows), "rows": rows}
        transcripts[a.name] = tr

    # Does the harness separate the answerers it was built to separate?
    accs = {k: v["score"]["accuracy"] for k, v in per_model.items()}
    separation = {
        "best": max(accs, key=accs.get), "worst": min(accs, key=accs.get),
        "spread": round(max(accs.values()) - min(accs.values()), 4),
        "accuracies": {k: round(v, 4) for k, v in accs.items()},
    }

    results = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "is_synthetic": True,
        "data_source": "14 authored questions over 2 authored filing extracts",
        "any_language_model_run": False,
        "suite": suite_stats(),
        "models": {k: v["score"] for k, v in per_model.items()},
        "separation": separation,
        "transcripts": transcripts,
    }
    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "results" / "latest.json").write_text(
        json.dumps(results, indent=2) + "\n", encoding="utf8")
    return results


def main() -> int:
    r = run()
    s = r["suite"]
    print(f"suite: {s['n_questions']} questions over {s['n_sources']} sources")
    print(f"  {s['by_category']}")
    print(f"\n{'answerer':<16}{'overall':>9}{'answerable':>12}{'unanswer.':>11}"
          f"{'trap':>7}{'stale':>7}{'fabric.':>9}{'citation':>10}")
    for name, sc in r["models"].items():
        bc = sc["by_category"]
        def acc(k):
            return f"{bc[k]['accuracy']:.2f}" if k in bc else "—"
        print(f"{name:<16}{sc['accuracy']:>9.2f}{acc('answerable'):>12}"
              f"{acc('unanswerable'):>11}{acc('trap'):>7}{acc('stale'):>7}"
              f"{sc['fabrication_rate']:>9.2f}{sc['citation_accuracy']:>10.2f}")
    sep = r["separation"]
    print(f"\nseparation: {sep['best']} {sep['accuracies'][sep['best']]:.2f} vs "
          f"{sep['worst']} {sep['accuracies'][sep['worst']]:.2f} "
          f"(spread {sep['spread']:.2f})")
    print(f"any language model run: {r['any_language_model_run']}")
    try:
        from .site import build_site
        build_site(r); print("\nwebsite/ rebuilt from this run")
    except Exception as exc:
        print(f"\n(site not rebuilt: {exc})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
