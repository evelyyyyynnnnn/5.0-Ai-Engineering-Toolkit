"""Run the suite over every stand-in answerer."""
from __future__ import annotations
import json, pathlib, sys
from datetime import datetime, timezone
from .graders import grade, score
from .models import ANSWERERS
from .suite import SUITE, suite_stats

ROOT = pathlib.Path(__file__).resolve().parent.parent


def evaluate(questions, answerers=None):
    """Run every answerer over every question. Shared by both runs, so the
    simulated and real evaluations cannot differ in method."""
    per_model, transcripts = {}, {}
    for a in (answerers or ANSWERERS):
        rows, tr = [], []
        for q in questions:
            ans = a(q)
            g = grade(q, ans)
            rows.append(g)
            tr.append({"qid": q.qid, "question": q.text, "answer": ans,
                       "category": q.category, "ok": g["ok"],
                       "failure": g["failure"]})
        per_model[a.name] = {"score": score(rows), "rows": rows}
        transcripts[a.name] = tr
    return per_model, transcripts


def run() -> dict:
    per_model, transcripts = evaluate(SUITE)

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


def run_real() -> dict:
    """Evaluate the stub answerers against questions built from filed data.

    One thing does NOT change and must be said plainly: no language model is
    run here either. The answerers are the same deterministic stubs -- careful,
    eager, year-blind, over-refusing, uncited -- and they exist to show that the
    harness separates behaviours, not to measure any model. What becomes real is
    the suite: the questions ask about figures companies filed, the answers are
    those filed values, and the unanswerable questions are unanswerable because
    the registrant never reported that concept.

    That matters most for the unanswerable category. An invented "no answer"
    question can often be spotted from its phrasing; "what was Coca-Cola's R&D
    expense in fiscal 2024" reads exactly like an answerable one, and is not.

    To score a real model, pass a callable taking a Question and returning a
    string to `evaluate(answerers=[...])`. It needs your own API key, so it is
    not wired in here.
    """
    import sys as _sys
    _sys.path.insert(0, str(ROOT))
    from data.load import ROOT as DATA_ROOT
    from data.load import build_suite

    questions, prov = build_suite(root=DATA_ROOT)
    per_model, transcripts = evaluate(questions)

    accs = {k: v["score"]["accuracy"] for k, v in per_model.items()}
    separation = {
        "best": max(accs, key=accs.get), "worst": min(accs, key=accs.get),
        "spread": round(max(accs.values()) - min(accs.values()), 4),
        "accuracies": {k: round(v, 4) for k, v in accs.items()},
    }

    results = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "is_synthetic": False,
        "data_source": "SEC EDGAR XBRL company-concept API -- every answer is a "
                       "filed value; see data/MANIFEST.json for hashes",
        "any_language_model_run": False,
        "no_model_caveat":
            "the answerers are deterministic stubs, not language models. This "
            "measures whether the harness separates behaviours on real "
            "questions; it measures no model's calibration.",
        "provenance": prov,
        "suite": {"n_questions": prov["n_questions"],
                  "by_category": prov["by_category"]},
        "models": {k: v["score"] for k, v in per_model.items()},
        "separation": separation,
        "transcripts": transcripts,
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
    pv = r["provenance"]
    print(f"source: {r['data_source']}")
    print(f"{pv['n_questions']} questions: " +
          ", ".join(f"{k} {v}" for k, v in sorted(pv["by_category"].items())))
    for c in pv["companies"]:
        print(f"  {c['ticker']:<6} FY{c['fiscal_years']}  "
              f"{c['n_questions']:>2} questions  "
              f"reports {len(c['metrics_reported'])} of "
              f"{len(c['metrics_reported']) + len(c['metrics_absent'])} metrics")
        if c["metrics_absent"]:
            print(f"  {'':<6} never reports: {', '.join(c['metrics_absent'])}")
    if pv["skipped"]:
        for s in pv["skipped"]:
            print(f"  skipped {s['ticker']}: {s['reason']}")

    print(f"\n{'answerer':<14}{'accuracy':>10}{'refusal':>10}"
          f"{'wrong':>8}{'uncited':>9}")
    for name, sc in r["models"].items():
        print(f"{name:<14}{sc['accuracy']:>10.3f}"
              f"{sc.get('refusal_rate', 0):>10.3f}"
              f"{sc.get('wrong_answers', 0):>8}"
              f"{sc.get('uncited', 0):>9}")
    sep = r["separation"]
    print(f"\nseparation: {sep['best']} {sep['accuracies'][sep['best']]:.3f} vs "
          f"{sep['worst']} {sep['accuracies'][sep['worst']]:.3f} "
          f"(spread {sep['spread']:.3f})")
    print("\n" + r["no_model_caveat"])
    print("wrote results/latest-real.json")
    return 0


def main() -> int:
    if "--real" in sys.argv[1:]:
        return main_real()
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
