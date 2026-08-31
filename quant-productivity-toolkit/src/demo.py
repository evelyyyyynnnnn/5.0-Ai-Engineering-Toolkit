"""Each check, demonstrated on data where the answer is known."""
from __future__ import annotations
import json, pathlib, subprocess, sys
from datetime import datetime, timezone
import numpy as np
import qkit
from qkit import (PurgedKFold, audit_universe, deflated_sharpe, detect_lookahead,
                  min_track_record_length, probabilistic_sharpe, sharpe, shift_safe)

ROOT = pathlib.Path(__file__).resolve().parent.parent


def lookahead_demo() -> dict:
    rng = np.random.default_rng(0)
    y = rng.normal(0, 0.011, 900)
    cases = {
        "copies next period's return": np.roll(y, -1),
        "copies this period's return": y.copy(),
        "centred rolling mean (window straddles t)": np.convolve(
            y, np.ones(5) / 5, mode="same"),
        "momentum: last period's return": np.roll(y, 1),
        "trailing mean, properly lagged": shift_safe(
            np.convolve(y, np.ones(5) / 5, mode="full")[:len(y)], 1),
        "pure noise": rng.normal(0, 1, 900),
        "weak genuine edge (~5%)": 0.05 * np.roll(y, -1) / y.std()
        + rng.normal(0, 1, 900),
    }
    out = []
    for name, f in cases.items():
        f = np.nan_to_num(f)
        out.append(detect_lookahead(f, y, name).as_dict())
    caught = [o for o in out if o["contaminated"]]
    return {"cases": out, "n_flagged": len(caught),
            "momentum_cleared": not next(
                o for o in out if o["feature"].startswith("momentum"))["contaminated"]}


def survivorship_demo() -> dict:
    rng = np.random.default_rng(2)
    n_names, T = 300, 500
    quality = rng.normal(0, 1, n_names)
    R = rng.normal(0.0003 + 0.0006 * quality, 0.014, (T, n_names))
    # Names that did badly are the ones that delist.
    cum = R.sum(axis=0)
    alive = cum > np.quantile(cum, 0.28)
    return audit_universe(R, alive).as_dict()


def validation_demo() -> dict:
    n, span = 1000, 20
    out = {}
    for embargo in (0, 20):
        cv = PurgedKFold(n_splits=5, label_span=span, embargo=embargo)
        out[f"purged_embargo_{embargo}"] = cv.leakage_check(n)
    naive = PurgedKFold(n_splits=5, label_span=1, embargo=0)
    out["naive_kfold"] = naive.leakage_check(n)
    # A naive fold under overlapping labels: how many training points overlap?
    plain = PurgedKFold(n_splits=5, label_span=1, embargo=0)
    overlaps = 0
    for train, test in plain.split(n):
        tr, te = np.where(train)[0], np.where(test)[0]
        overlaps += sum(1 for t in tr if np.any((te >= t) & (te < t + span)))
    out["naive_overlapping_train_points"] = int(overlaps)
    out["label_span"] = span
    return out


def selection_demo() -> dict:
    """Try many random strategies, keep the best, and see what survives."""
    rng = np.random.default_rng(7)
    T = 750
    trials = 200
    paths = rng.normal(0, 0.01, (trials, T))
    srs = np.array([sharpe(p) for p in paths])
    best = int(np.argmax(srs))
    best_r = paths[best]
    rows = []
    for n in (1, 10, 50, 200):
        rows.append({"n_trials": n, **deflated_sharpe(best_r, n)})
    return {
        "n_trials_run": trials,
        "best_observed_sharpe": round(float(srs[best]), 4),
        "true_sharpe": 0.0,
        "psr_vs_zero": round(probabilistic_sharpe(best_r), 5),
        "min_track_record_length": round(min_track_record_length(best_r), 1),
        "by_assumed_trials": rows,
    }


def cli_check() -> dict:
    out = subprocess.run([sys.executable, "-m", "qkit.cli", "--help"],
                         capture_output=True, text=True, timeout=60)
    return {"exit": out.returncode, "help_ok": "lookahead" in out.stdout}


def run() -> dict:
    results = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "is_synthetic": True,
        "data_source": "synthetic return series with known contamination",
        "package": {"name": "qkit-research", "version": qkit.__version__,
                    "exports": len(qkit.__all__), "published": False},
        "lookahead": lookahead_demo(),
        "survivorship": survivorship_demo(),
        "validation": validation_demo(),
        "selection": selection_demo(),
        "cli": cli_check(),
    }
    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "results" / "latest.json").write_text(
        json.dumps(results, indent=2) + "\n", encoding="utf8")
    return results


def main() -> int:
    r = run()
    print(f"qkit-research {r['package']['version']}, "
          f"{r['package']['exports']} exports\n")
    print("lookahead detection:")
    print(f"  {'feature':<44}{'fwd':>7}{'lag':>5}{'bwd':>7}  flagged")
    for c in r["lookahead"]["cases"]:
        print(f"  {c['feature']:<44}{c['max_forward_corr']:>7.3f}"
              f"{c['lag_of_max']:>5}{c['max_backward_corr']:>7.3f}"
              f"  {'YES' if c['contaminated'] else '-'}")
    print(f"  momentum correctly cleared: {r['lookahead']['momentum_cleared']}")

    s = r["survivorship"]
    print(f"\nsurvivorship: {s['n_universe']} names, {s['n_delisted']} delisted "
          f"({1 - s['survivor_share']:.0%})")
    print(f"  mean return all {s['mean_return_all']:.6f} vs survivors "
          f"{s['mean_return_survivors']:.6f}  -> bias {s['bias_bps']:.1f} bps/period")

    v = r["validation"]
    print(f"\npurged CV (label span {v['label_span']}):")
    for k in ("naive_kfold", "purged_embargo_0", "purged_embargo_20"):
        c = v[k]
        print(f"  {k:<20} drops/fold {c['dropped_per_fold']}  "
              f"folds with overlap {c['folds_with_overlap']}")
    print(f"  naive folds' overlapping training points: "
          f"{v['naive_overlapping_train_points']}")

    sel = r["selection"]
    print(f"\nselection bias: best of {sel['n_trials_run']} random strategies "
          f"(true Sharpe {sel['true_sharpe']})")
    print(f"  observed Sharpe {sel['best_observed_sharpe']:.3f}, "
          f"PSR vs zero {sel['psr_vs_zero']:.4f}")
    print(f"  {'assumed trials':>15}{'E[max from noise]':>20}{'deflated P':>13}"
          f"{'survives':>10}")
    for row in sel["by_assumed_trials"]:
        print(f"  {row['n_trials']:>15}{row['expected_max_sharpe_from_noise']:>20.3f}"
              f"{row['deflated_sharpe_prob']:>13.4f}{str(row['survives']):>10}")
    try:
        from .site import build_site
        build_site(r); print("\nwebsite/ rebuilt from this run")
    except Exception as exc:
        print(f"\n(site not rebuilt: {exc})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
