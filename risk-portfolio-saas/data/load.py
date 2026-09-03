"""Build MarketData from the cached real ETF tape.

Betas are estimated against SPY rather than assumed. The synthetic market knows
each asset's factor loading because it built them; on real data the loading has
to be regressed out of the returns, and an asset like GLD will come back with a
beta near zero, which is the honest answer and not a bug.
"""
from __future__ import annotations

import pathlib

import numpy as np

from .datakit import Fetcher, FetchError
from .marketdata import align, parse_stooq, to_returns

ROOT = pathlib.Path(__file__).resolve().parent
BENCHMARK = "spy.us"


def load_market(root=ROOT, min_days: int = 500):
    """Return (MarketData, provenance). Refuses if the real cache is empty."""
    from src.service import MarketData

    f = Fetcher(root)
    man = f.load_manifest()
    cached = {k: v for k, v in man["files"].items() if k.startswith("stooq/")}
    if not cached:
        raise FetchError(
            "no real price data cached. Run `python -m data.fetch` in a "
            "networked environment first; this project will not report risk on "
            "a simulated tape while labelling it real.")

    series, prov = {}, []
    for dest, rec in sorted(cached.items()):
        sym = pathlib.Path(dest).stem
        try:
            dates, closes = parse_stooq((f.raw / dest).read_bytes())
        except ValueError as exc:
            prov.append({"ticker": sym, "status": f"unusable: {exc}"})
            continue
        series[sym] = (dates, closes)
        prov.append({"ticker": sym, "status": "ok", "n_closes": len(closes),
                     "first": str(dates[0]), "last": str(dates[-1]),
                     "sha256": rec["sha256"][:16], "url": rec["url"]})

    if len(series) < 2:
        raise FetchError(f"only {len(series)} usable series; need at least 2")

    dates, aligned = align(series)
    if len(dates) < min_days:
        raise FetchError(
            f"only {len(dates)} overlapping trading days; need {min_days}. "
            f"A VaR estimate at the 99th percentile from fewer than about two "
            f"years of data is fitted to a handful of observations.")

    tickers = sorted(aligned)
    R = np.column_stack([to_returns(aligned[t]) for t in tickers])
    betas = _betas(tickers, R)

    meta = {
        "n_days": int(R.shape[0]), "n_tickers": len(tickers),
        "first_date": str(dates[0]), "last_date": str(dates[-1]),
        "benchmark": BENCHMARK if BENCHMARK in tickers else None,
        "series": prov,
        "betas": {t: round(float(b), 4) for t, b in zip(tickers, betas)},
    }
    return MarketData(tickers=tickers, returns=R, betas=betas), meta


def _betas(tickers, R: np.ndarray) -> np.ndarray:
    """OLS beta of each asset against the benchmark's own return series."""
    if BENCHMARK not in tickers:
        # Without a benchmark, the equal-weighted mean is the usable proxy.
        bench = R.mean(axis=1)
    else:
        bench = R[:, tickers.index(BENCHMARK)]
    var = float(np.var(bench))
    if var == 0:
        raise FetchError("benchmark series has zero variance")
    return np.array([float(np.cov(R[:, i], bench, ddof=0)[0, 1] / var)
                     for i in range(R.shape[1])])
