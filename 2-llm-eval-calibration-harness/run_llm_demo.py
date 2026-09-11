"""Score a real language model with this harness.

The committed results say `any_language_model_run: false`, which is honest and
is also the gap: a calibration harness that has never been pointed at a model
has not been shown to measure a model. This runs one, locally, and writes
results/latest-llm.json.

    ollama pull qwen2.5-coder:7b
    ollama serve                       # usually already running
    python run_llm_demo.py             # authored suite (fast, offline)
    python run_llm_demo.py --real      # suite built from filed SEC values

Environment:
    CALIB_MODEL      model tag            (default qwen2.5-coder:7b)
    OPENAI_BASE_URL  chat endpoint        (default http://localhost:11434/v1)
    OPENAI_API_KEY   only for hosted endpoints; Ollama ignores it

The stub answerers are scored in the same run, over the same questions, by the
same grader. Without them the model's number has nothing to sit against.
"""

from __future__ import annotations

import json
import os
import pathlib
import sys
import time
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.demo import evaluate                       # noqa: E402
from src.llm_answerer import LLMAnswerer            # noqa: E402
from src.models import ANSWERERS                    # noqa: E402
from src.suite import SUITE, suite_stats            # noqa: E402


def main(argv: list) -> int:
    real = "--real" in argv[1:]
    model = os.environ.get("CALIB_MODEL", "qwen2.5-coder:7b")

    if real:
        from data.load import ROOT as DATA_ROOT
        from data.load import build_suite
        questions, prov = build_suite(root=DATA_ROOT)
        stats = {"n_questions": prov["n_questions"],
                 "by_category": prov["by_category"]}
        source = ("SEC EDGAR XBRL company-concept API -- every answer is a filed "
                  "value; see data/MANIFEST.json for hashes")
    else:
        questions, prov, stats = SUITE, None, suite_stats()
        source = "14 authored questions over 2 authored filing extracts"

    llm = LLMAnswerer(model=model)
    print(f"model    : {llm.name}")
    print(f"endpoint : {llm.base_url}")
    print(f"questions: {len(questions)} ({'filed values' if real else 'authored'})\n")

    t0 = time.time()
    per_model, transcripts = evaluate(questions, answerers=[llm, *ANSWERERS])
    elapsed = round(time.time() - t0, 1)

    failed = [c for c in llm.calls if c["error"]]
    if failed:
        print(f"!! {len(failed)} of {len(llm.calls)} calls failed; "
              f"first: {failed[0]['error']}", file=sys.stderr)
        print("   is `ollama serve` running, and is the model pulled?",
              file=sys.stderr)

    accs = {k: v["score"]["accuracy"] for k, v in per_model.items()}
    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "is_synthetic": not real,
        "data_source": source,
        "any_language_model_run": True,
        "model": {
            "name": llm.name, "endpoint": llm.base_url,
            "temperature": 0,
            "calls": len(llm.calls),
            "failed_calls": len(failed),
            "median_latency_s": sorted(c["latency_s"] for c in llm.calls)[
                len(llm.calls) // 2] if llm.calls else None,
            "wall_clock_s": elapsed,
        },
        "note": (
            "A real open language model scored by the same lexical grader as the "
            "deterministic stubs, over the same questions. The stubs are kept in "
            "the run because a model's accuracy means nothing without the "
            "behaviours the grader was built to separate sitting beside it. "
            "Replies reach the grader verbatim: nothing repairs, reformats or "
            "re-asks. A failed call is recorded as a failed call and scored as "
            "the empty answer it was, rather than being replaced by a refusal "
            "the model never gave."),
        "suite": stats,
        "models": {k: v["score"] for k, v in per_model.items()},
        "accuracies": {k: round(v, 4) for k, v in accs.items()},
        "model_vs_stubs": {
            "model_accuracy": round(accs.get(llm.name, 0.0), 4),
            "best_stub": max((k for k in accs if k != llm.name),
                             key=lambda k: accs[k], default=None),
            "best_stub_accuracy": round(
                max((v for k, v in accs.items() if k != llm.name), default=0.0), 4),
        },
        "call_log": llm.calls,
        "transcripts": transcripts,
    }
    if prov:
        out["provenance"] = prov

    (ROOT / "results").mkdir(exist_ok=True)
    dest = ROOT / "results" / "latest-llm.json"
    dest.write_text(json.dumps(out, indent=2) + "\n", encoding="utf8")

    print(f"{'answerer':<24}{'accuracy':>10}{'fabrication':>13}{'citation':>10}")
    for name, sc in out["models"].items():
        mark = " <-- real model" if name == llm.name else ""
        print(f"{name:<24}{sc['accuracy']:>10.4f}"
              f"{sc.get('fabrication_rate', 0):>13.4f}"
              f"{sc.get('citation_accuracy', 0):>10.4f}{mark}")
    print(f"\nwrote results/latest-llm.json  ({elapsed}s, "
          f"{len(failed)} failed calls)")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
