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


def dilution_sweep(y: np.ndarray, windows=(3, 5, 9, 21, 63)) -> dict:
    """Where the leak becomes invisible, and why.

    A centred moving average of width w straddles t, so it contains the future.
    But it contains only 1/w of it. For an uncorrelated series the correlation
    between that feature and the next return works out to 1/sqrt(w), which
    falls as the window widens while the detector's plausibility threshold
    stays fixed.

    So there is a width past which a genuinely leaking feature stops being
    detectable by any fixed correlation bound. This reports where that width
    is, rather than leaving it as a silent miss. The right response is not a
    lower threshold -- that would flag every real predictor -- but to check how
    a feature was constructed, which no statistic can do for you.
    """
    y = np.asarray(y, float)
    rows = []
    for w in windows:
        f = np.nan_to_num(np.convolve(y, np.ones(w) / w, mode="same"))
        finding = detect_lookahead(f, y, f"centred mean, w={w}").as_dict()
        corr = float(np.corrcoef(f[:-1], y[1:])[0, 1])
        rows.append({
            "window": w,
            "correlation_with_next_return": round(corr, 4),
            "theoretical_1_over_sqrt_w": round(float(1.0 / np.sqrt(w)), 4),
            "detected": bool(finding["contaminated"]),
        })
    detected = [r["window"] for r in rows if r["detected"]]
    missed = [r["window"] for r in rows if not r["detected"]]
    return {
        "rows": rows,
        "detected_windows": detected,
        "missed_windows": missed,
        "detection_floor": max(detected) if detected else None,
        "finding": "every window here leaks -- each one contains the future. "
                   "Detection stops at the width where 1/sqrt(w) falls below "
                   "the plausibility bound, so a wide enough centred window is "
                   "invisible to any fixed correlation threshold. Lowering the "
                   "bound is not the fix: it would flag genuine predictors "
                   "instead. Reading how the feature was built is.",
    }


def lookahead_demo_real(dates, y, label):
    """The same feature constructions, over a real return series.

    This is a calibration test, and a harder one than it looks. Real returns
    are not the independent draws the synthetic version uses: they have mild
    autocorrelation and strong volatility clustering. A lookahead detector
    keyed on correlation with future returns could fire on a properly lagged
    feature purely because yesterday's return genuinely does predict a little
    of today's. Whether the properly lagged features stay clear on real data is
    the finding.
    """
    rng = np.random.default_rng(0)
    n = len(y)
    cases = {
        "copies next period's return": np.roll(y, -1),
        "copies this period's return": y.copy(),
        "centred rolling mean, 3-sample window": np.convolve(
            y, np.ones(3) / 3, mode="same"),
        "centred rolling mean, 9-sample window": np.convolve(
            y, np.ones(9) / 9, mode="same"),
        "momentum: last period's return": np.roll(y, 1),
        "trailing mean, properly lagged": shift_safe(
            np.convolve(y, np.ones(5) / 5, mode="full")[:n], 1),
        "pure noise": rng.normal(0, 1, n),
        "realised volatility, properly lagged": shift_safe(
            np.sqrt(np.convolve(y ** 2, np.ones(20) / 20, mode="full")[:n]), 1),
    }
    out = []
    for name, f in cases.items():
        out.append(detect_lookahead(np.nan_to_num(f), y, name).as_dict())
    lagged = [o for o in out
              if "properly lagged" in o["feature"] or o["feature"].startswith("momentum")]
    return {
        "series": label,
        "n_observations": int(n),
        "cases": out,
        "dilution": dilution_sweep(y),
        "n_flagged": sum(1 for o in out if o["contaminated"]),
        "true_leaks_caught": sum(1 for o in out if o["contaminated"]
                                 and ("copies" in o["feature"]
                                      or "straddles" in o["feature"])),
        "properly_lagged_features_falsely_flagged":
            sum(1 for o in lagged if o["contaminated"]),
        "note": "the last figure is the one to watch: a properly lagged feature "
                "flagged on real data is a false positive caused by genuine "
                "return autocorrelation, not by leakage",
    }


def selection_demo_real(strategies, label):
    """A real strategy sweep, deflated.

    Every rule here is a moving-average crossover on a real price series, and
    the sweep is the whole grid. The best of them will have a flattering Sharpe
    ratio; the question the deflated Sharpe answers is whether it survives
    being told how many rules were tried to find it.
    """
    scored = []
    for s in strategies:
        r = s["returns"]
        scored.append({"fast": s["fast"], "slow": s["slow"],
                       "n": int(len(r)),
                       "sharpe": round(sharpe(r), 4), "returns": r})
    scored.sort(key=lambda x: -x["sharpe"])
    best = scored[0]
    n_trials = len(scored)

    dsr = deflated_sharpe(best["returns"], n_trials=n_trials)
    psr = probabilistic_sharpe(best["returns"])
    naive = deflated_sharpe(best["returns"], n_trials=1)

    sharpes = np.array([s["sharpe"] for s in scored], float)
    return {
        "series": label,
        "n_strategies_tried": n_trials,
        "best": {"fast": best["fast"], "slow": best["slow"],
                 "sharpe": best["sharpe"], "n_observations": best["n"]},
        "sharpe_spread": {
            "max": round(float(sharpes.max()), 4),
            "median": round(float(np.median(sharpes)), 4),
            "min": round(float(sharpes.min()), 4),
        },
        "probabilistic_sharpe": round(float(psr), 4),
        "deflated_sharpe_one_trial": naive["deflated_sharpe_prob"],
        "deflated_sharpe_all_trials": dsr["deflated_sharpe_prob"],
        "expected_max_sharpe_from_noise": dsr["expected_max_sharpe_from_noise"],
        "survives_deflation": bool(dsr["survives"]),
        "note": "deflated Sharpe is the probability the true Sharpe exceeds "
                "zero AFTER accounting for how many rules were searched. The "
                "one-trial figure is what a paper reports when it does not say "
                "how many it tried.",
    }


def run_real() -> dict:
    import sys as _sys
    _sys.path.insert(0, str(ROOT))
    from data.load import ROOT as DATA_ROOT
    from data.load import load_factors, load_prices, strategy_grid

    dates, factors, fprov = load_factors(root=DATA_ROOT)
    mkt = np.asarray(factors.get("Mkt-RF", []), float)

    pdates, prices, pprov = load_prices(root=DATA_ROOT)
    ticker = "spy.us" if "spy.us" in prices else sorted(prices)[0]
    px = np.asarray(prices[ticker], float)

    look = lookahead_demo_real(dates, mkt, "Fama-French daily market factor")
    sweep = selection_demo_real(strategy_grid(px), f"{ticker} moving-average grid")

    results = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "is_synthetic": False,
        "data_source": "Fama-French daily research factors and Stooq daily "
                       "closes; see data/MANIFEST.json for URLs, hashes and "
                       "retrieval times",
        "package": {"name": "qkit-research", "version": qkit.__version__,
                    "exports": len(qkit.__all__), "published": False},
        "factors": fprov,
        "prices": pprov,
        "lookahead": look,
        "selection": sweep,
        "validation": validation_demo(),
        "survivorship_reported": False,
        "survivorship_withheld_because":
            "a survivorship audit needs the returns of the names that died, and "
            "no free source publishes point-in-time index membership with "
            "delisted constituents. A ticker that returns no data has not "
            "necessarily been delisted, so treating a fetch failure as a "
            "delisting would manufacture the very bias the check measures.",
        "cli": cli_check(),
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
    fp = r["factors"]
    print(f"source: {r['data_source']}")
    print(f"factors: {fp['n_days']:,} daily observations, "
          f"{fp['first']} .. {fp['last']}  [{fp['sha256']}]")
    for p in r["prices"]:
        if p["status"] == "ok":
            print(f"  {p['ticker']:<9}{p['n_closes']:>7,} closes  "
                  f"{p['first']} .. {p['last']}")

    lk = r["lookahead"]
    print(f"\nlookahead detection on {lk['series']} "
          f"({lk['n_observations']:,} observations):")
    for c in lk["cases"]:
        mark = "FLAGGED" if c["contaminated"] else "clear  "
        print(f"  {mark}  {c['feature']}")
    print(f"  properly lagged features falsely flagged: "
          f"{lk['properly_lagged_features_falsely_flagged']}")
    print(f"  {lk['note']}")

    dl = lk["dilution"]
    print(f"\n  how far a leak can be diluted before it stops being detected:")
    print(f"  {'window':>7}{'corr w/ next':>14}{'1/sqrt(w)':>11}{'detected':>10}")
    for row in dl["rows"]:
        print(f"  {row['window']:>7}{row['correlation_with_next_return']:>14.4f}"
              f"{row['theoretical_1_over_sqrt_w']:>11.4f}"
              f"{str(row['detected']):>10}")
    print(f"  detection floor: width {dl['detection_floor']} "
          f"(missed at {dl['missed_windows']})")
    print(f"  {dl['finding']}")

    s = r["selection"]
    print(f"\nstrategy sweep on {s['series']}: {s['n_strategies_tried']} rules")
    print(f"  best: fast {s['best']['fast']} / slow {s['best']['slow']}, "
          f"Sharpe {s['best']['sharpe']:.3f} over {s['best']['n_observations']:,} days")
    sp = s["sharpe_spread"]
    print(f"  Sharpe across the grid: min {sp['min']:.3f}, "
          f"median {sp['median']:.3f}, max {sp['max']:.3f}")
    print(f"  probabilistic Sharpe (one trial):  {s['probabilistic_sharpe']:.4f}")
    print(f"  deflated Sharpe, 1 trial claimed:  "
          f"{s['deflated_sharpe_one_trial']:.4f}")
    print(f"  deflated Sharpe, {s['n_strategies_tried']} trials admitted: "
          f"{s['deflated_sharpe_all_trials']:.4f}")
    print(f"  best Sharpe expected from noise alone across that many rules: "
          f"{s['expected_max_sharpe_from_noise']:.3f}")
    print(f"  survives deflation: {s['survives_deflation']}")
    print(f"  {s['note']}")

    print("\nSURVIVORSHIP IS NOT REPORTED ON REAL DATA: " +
          r["survivorship_withheld_because"])
    print("wrote results/latest-real.json")
    return 0


def main() -> int:
    if "--real" in sys.argv[1:]:
        return main_real()
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
