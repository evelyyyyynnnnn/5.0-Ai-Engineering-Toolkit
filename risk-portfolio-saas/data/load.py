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
from .marketdata import (align, parse_french, parse_french_industry,
                         parse_stooq, to_returns)

ROOT = pathlib.Path(__file__).resolve().parent
BENCHMARK = "spy.us"
INDUSTRY_DEST = "french/10_industry_daily.zip"
FACTORS_DEST = "french/ff_daily.zip"


def load_market(root=ROOT, min_days: int = 500):
    """Return (MarketData, provenance). Refuses if the real cache is empty.

    Prefers the Fama-French 10-industry daily portfolios when they are cached
    (the reproducible market data this project reports on); falls back to a
    cached per-ticker Stooq tape when that is what is present instead.
    """
    from src.service import MarketData

    f = Fetcher(root)
    man = f.load_manifest()

    if INDUSTRY_DEST in man["files"] and (f.raw / INDUSTRY_DEST).exists():
        return _load_industries(f, man, min_days)

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


def _load_industries(f, man, min_days: int, lookback_days: int = 2600):
    """Build MarketData from the Fama-French 10-industry daily returns.

    The industries are treated as the portfolio constituents. The returns are
    already daily returns in the source, so no price-to-return step is needed.
    Betas are estimated against the Fama-French US market factor (Mkt-RF + RF)
    when the research-factor file is also cached; without it, the cross-sectional
    average of the ten industries is used as a market proxy and labelled as such.
    """
    from src.service import MarketData

    rec = man["files"][INDUSTRY_DEST]
    idates, imap = parse_french_industry((f.raw / INDUSTRY_DEST).read_bytes())
    inds = list(imap.keys())

    market_series, bench_label = None, ("equal-weighted average of the 10 "
                                        "industry portfolios (market proxy)")
    if FACTORS_DEST in man["files"] and (f.raw / FACTORS_DEST).exists():
        fdates, fmap = parse_french((f.raw / FACTORS_DEST).read_bytes())
        if "Mkt-RF" in fmap and "RF" in fmap:
            market_series = {d: mr + rf for d, mr, rf
                             in zip(fdates, fmap["Mkt-RF"], fmap["RF"])}
            bench_label = "Fama-French US market factor (Mkt-RF + RF)"

    common = ([d for d in idates if d in market_series]
              if market_series is not None else list(idates))
    if lookback_days and len(common) > lookback_days:
        common = common[-lookback_days:]
    if len(common) < min_days:
        raise FetchError(
            f"only {len(common)} overlapping trading days; need {min_days}. "
            f"A VaR estimate at the 99th percentile from fewer than about two "
            f"years of data is fitted to a handful of observations.")

    pos = {d: i for i, d in enumerate(idates)}
    R = np.array([[imap[ind][pos[d]] for ind in inds] for d in common], float)
    bench = (np.array([market_series[d] for d in common])
             if market_series is not None else R.mean(axis=1))
    var = float(np.var(bench))
    if var == 0:
        raise FetchError("benchmark series has zero variance")
    betas = np.array([float(np.cov(R[:, i], bench, ddof=0)[0, 1] / var)
                      for i in range(R.shape[1])])

    prov = [{"ticker": ind, "status": "ok", "n_obs": int(R.shape[0]),
             "first": str(common[0]), "last": str(common[-1]),
             "sha256": rec["sha256"][:16], "url": rec["url"]} for ind in inds]
    meta = {
        "n_days": int(R.shape[0]), "n_tickers": len(inds),
        "first_date": str(common[0]), "last_date": str(common[-1]),
        "benchmark": bench_label,
        "series": prov,
        "betas": {t: round(float(b), 4) for t, b in zip(inds, betas)},
    }
    return MarketData(tickers=inds, returns=R, betas=betas), meta


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
