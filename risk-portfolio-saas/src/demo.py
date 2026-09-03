"""Score three portfolios and show what the service surfaces."""
from __future__ import annotations
import json, pathlib, sys, time
from datetime import datetime, timezone
import numpy as np
from .service import MarketData, handle
from . import risk

ROOT = pathlib.Path(__file__).resolve().parent.parent

TICKERS = ["ALPHA", "BETA", "GAMMA", "DELTA", "EPSILON", "ZETA", "ETA", "THETA"]


def make_market(T: int = 750, seed: int = 5) -> MarketData:
    """A market with a common factor and a fat-tailed crash regime.

    Fat tails are the point: on Gaussian returns the three VaR methods agree and
    the comparison that makes the report worth reading disappears.
    """
    rng = np.random.default_rng(seed)
    n = len(TICKERS)
    # Betas span the realistic equity range. A narrow 0.5-1.7 band was the
    # first choice and it made the hidden-risk portfolio impossible to build:
    # a position's risk share over its capital share is bounded by its beta over
    # the portfolio's average beta, so with a narrow band the ratio cannot
    # exceed about 1.5 and the mismatch a capital limit misses never appears.
    betas = rng.uniform(0.30, 2.40, n)
    factor = rng.standard_t(df=4, size=T) * 0.009      # fat-tailed
    idio = rng.normal(0, 0.006, (T, n))    # factor-dominated, so beta matters
    R = factor[:, None] * betas[None, :] + idio
    crash = rng.random(T) < 0.02
    R[crash] += rng.normal(-0.045, 0.02, (crash.sum(), n))
    return MarketData(tickers=TICKERS, returns=R, betas=betas)


PORTFOLIOS = [
    {"portfolio_id": "EQUAL-WEIGHT", "as_of": "2026-08-31",
     "tickers": TICKERS, "weights": [1 / 8] * 8},
    {"portfolio_id": "CONCENTRATED", "as_of": "2026-08-31",
     "tickers": TICKERS, "weights": [0.55, 0.20, 0.10, 0.05, 0.04, 0.03, 0.02, 0.01]},
]


def hidden_risk_portfolio(market) -> dict:
    """Looks diversified by capital; one high-beta name dominates the risk.

    Built from the market's actual betas rather than hand-written weights. An
    earlier version used near-equal weights and produced no hidden concentration
    at all -- the portfolio has to be constructed against the covariance to
    exhibit the property the check exists to catch.
    """
    order = np.argsort(-market.betas)
    w = np.zeros(len(TICKERS))
    w[order[0]] = 0.18                       # highest beta, modest capital
    w[order[1:]] = (1.0 - 0.18) / (len(TICKERS) - 1)
    return {"portfolio_id": "HIDDEN-RISK", "as_of": "2026-08-31",
            "tickers": TICKERS, "weights": [float(x) for x in w]}

BAD_REQUESTS = [
    ({"portfolio_id": "X", "tickers": TICKERS, "weights": [1 / 7] * 8},
     "weights that do not sum to one"),
    ({"portfolio_id": "X", "tickers": TICKERS[:3], "weights": [0.5, 0.5]},
     "mismatched lengths"),
    ({"portfolio_id": "X", "tickers": ["UNKNOWN"], "weights": [1.0]},
     "a ticker with no market data"),
    ({"portfolio_id": "X", "tickers": ["ALPHA", "ALPHA"], "weights": [0.5, 0.5]},
     "duplicate tickers"),
    ({"portfolio_id": "X", "tickers": TICKERS, "weights": [float("nan")] * 8},
     "NaN weights"),
    ({"portfolio_id": "X"}, "a missing field"),
]


def throughput(market: MarketData, n: int = 300) -> dict:
    req = PORTFOLIOS[0]
    t0 = time.perf_counter()
    for _ in range(n):
        handle(req, market)
    dt = time.perf_counter() - t0
    return {"requests": n, "seconds": round(dt, 4),
            "requests_per_second": round(n / dt, 1),
            "mean_latency_ms": round(dt / n * 1000, 3)}


def run() -> dict:
    market = make_market()
    portfolios = PORTFOLIOS + [hidden_risk_portfolio(market)]
    reports = {}
    for req in portfolios:
        out = handle(req, market)
        reports[req["portfolio_id"]] = out["report"] if out["ok"] else out

    rejected = []
    for req, why in BAD_REQUESTS:
        out = handle(req, market)
        rejected.append({"case": why, "rejected": not out["ok"],
                         "error": out.get("error", ""),
                         "detail": out.get("detail", "")[:90]})

    results = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "is_synthetic": True,
        "data_source": "synthetic factor market with fat tails (src/demo.py)",
        "n_tickers": len(TICKERS),
        "observations": int(market.returns.shape[0]),
        "reports": reports,
        "validation": {"cases": rejected,
                       "all_rejected": all(c["rejected"] for c in rejected)},
        "throughput": throughput(market),
    }
    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "results" / "latest.json").write_text(
        json.dumps(results, indent=2) + "\n", encoding="utf8")
    return results


def run_real() -> dict:
    """Risk report over the real ETF tape.

    Everything the engine reports here is a measurement: the VaR numbers, the
    Euler decomposition and the drawdown all come from real returns. The
    portfolios are still authored -- an equal-weight and a concentrated basket
    over the same eight tickers -- because a portfolio is an input, not
    something a data feed provides.
    """
    import sys as _sys
    _sys.path.insert(0, str(ROOT))
    from data.load import load_market

    market, meta = load_market(root=ROOT / "data")
    tickers = market.tickers
    n = len(tickers)
    portfolios = [
        {"portfolio_id": "EQUAL-WEIGHT", "as_of": meta["last_date"],
         "tickers": tickers, "weights": [1 / n] * n},
        {"portfolio_id": "SIXTY-FORTY", "as_of": meta["last_date"],
         "tickers": tickers,
         "weights": _sixty_forty(tickers)},
    ]
    reports = {}
    for req in portfolios:
        out = handle(req, market)
        reports[req["portfolio_id"]] = out["report"] if out["ok"] else out

    results = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "is_synthetic": False,
        "data_source": "real daily closes from Stooq (see data/MANIFEST.json for "
                       "URLs, hashes and retrieval times)",
        "n_tickers": meta["n_tickers"],
        "observations": meta["n_days"],
        "window": {"first": meta["first_date"], "last": meta["last_date"]},
        "betas_estimated_against": meta["benchmark"],
        "betas": meta["betas"],
        "provenance": meta["series"],
        "portfolios_are_authored": True,
        "reports": reports,
    }
    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "results" / "latest-real.json").write_text(
        json.dumps(results, indent=2) + "\n", encoding="utf8")
    return results


def _sixty_forty(tickers) -> list:
    """60% to equity sleeves, 40% to bonds, spread evenly inside each sleeve."""
    bondish = {"agg.us", "tlt.us"}
    bonds = [t for t in tickers if t in bondish]
    eq = [t for t in tickers if t not in bondish]
    if not bonds or not eq:
        return [1 / len(tickers)] * len(tickers)
    w = {t: 0.60 / len(eq) for t in eq}
    w.update({t: 0.40 / len(bonds) for t in bonds})
    return [w[t] for t in tickers]


def main_real() -> int:
    from data.datakit import FetchError
    try:
        r = run_real()
    except FetchError as exc:
        print(f"cannot run on real data: {exc}", file=sys.stderr)
        return 2
    print(f"source: {r['data_source']}")
    print(f"{r['n_tickers']} tickers, {r['observations']} trading days "
          f"({r['window']['first']} .. {r['window']['last']})")
    print(f"betas vs {r['betas_estimated_against']}: " +
          ", ".join(f"{k} {v:+.2f}" for k, v in r["betas"].items()))
    for pid, rep in r["reports"].items():
        if "risk" not in rep:
            print(f"\n{pid}: {rep}")
            continue
        rk, cn = rep["risk"], rep["concentration"]
        print(f"\n{pid}  ({rep['n_positions']} positions, "
              f"alpha {rep['alpha']})")
        print(f"  VaR  historical {rk['var_historical']:.4f} | "
              f"gaussian {rk['var_gaussian']:.4f} | "
              f"cornish-fisher {rk['var_cornish_fisher']:.4f}")
        print(f"  expected shortfall {rk['expected_shortfall']:.4f} | "
              f"max drawdown {rk['max_drawdown']:.4f} | "
              f"annualised vol {rk['annualised_volatility']:.4f}")
        print(f"  effective positions {cn['effective_positions']:.2f} "
              f"of {rep['n_positions']} | top-3 share {cn['top3_share']:.1%}")
        for chk in rep.get("checks", []):
            print(f"  [{chk['level']}] {chk['detail']}")
    print("\nportfolios are authored; every risk number above is measured "
          "from real returns")
    print("wrote results/latest-real.json")
    return 0


def main() -> int:
    if "--real" in sys.argv[1:]:
        return main_real()
    r = run()
    print(f"market: {r['n_tickers']} names, {r['observations']} observations\n")
    print(f"{'portfolio':<16}{'vol':>9}{'VaR hist':>10}{'VaR gauss':>11}"
          f"{'VaR CF':>9}{'ES':>9}{'eff.pos':>9}{'top risk':>10}")
    for pid, rep in r["reports"].items():
        rk, c = rep["risk"], rep["concentration"]
        top = rep["contributions"][0]
        print(f"{pid:<16}{rk['annualised_volatility']:>9.3f}"
              f"{rk['var_historical']:>10.4f}{rk['var_gaussian']:>11.4f}"
              f"{rk['var_cornish_fisher']:>9.4f}{rk['expected_shortfall']:>9.4f}"
              f"{c['effective_positions']:>9.2f}"
              f"{top['ticker'][:5] + ' ' + format(top['risk_share'], '.0%'):>10}")

    print("\nchecks raised:")
    for pid, rep in r["reports"].items():
        for c in rep["checks"]:
            print(f"  [{c['level']:<4}] {pid:<14} {c['code']:<18} {c['detail']}")

    v = r["validation"]
    print(f"\nvalidation: {sum(c['rejected'] for c in v['cases'])}/"
          f"{len(v['cases'])} bad requests rejected")
    for c in v["cases"]:
        print(f"  {'ok ' if c['rejected'] else 'LET THROUGH'} {c['case']:<34}"
              f"{c['detail'][:52]}")

    t = r["throughput"]
    print(f"\nthroughput: {t['requests_per_second']:,.0f} reports/s "
          f"({t['mean_latency_ms']:.2f} ms mean latency)")
    try:
        from .site import build_site
        build_site(r); print("\nwebsite/ rebuilt from this run")
    except Exception as exc:
        print(f"\n(site not rebuilt: {exc})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
