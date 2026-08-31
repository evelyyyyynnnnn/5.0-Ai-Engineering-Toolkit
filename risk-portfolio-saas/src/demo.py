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


def main() -> int:
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
