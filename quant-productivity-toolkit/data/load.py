"""Load real return series for the backtest checks."""
from __future__ import annotations

import pathlib

import numpy as np

from .datakit import Fetcher, FetchError
from .marketdata import align, parse_french, parse_stooq, to_returns

ROOT = pathlib.Path(__file__).resolve().parent


def load_factors(root=ROOT):
    """Return (dates, {factor: array}, provenance) from the French daily file."""
    f = Fetcher(root)
    man = f.load_manifest()
    dest = "french/ff_daily.zip"
    if dest not in man["files"] or not (f.raw / dest).exists():
        raise FetchError(
            "the Fama-French daily factors are not cached. Run "
            "`python -m data.fetch` in a networked environment first.")
    dates, data = parse_french((f.raw / dest).read_bytes())
    rec = man["files"][dest]
    return dates, data, {
        "source": "Kenneth R. French Data Library, daily research factors",
        "n_days": len(dates), "first": str(dates[0]), "last": str(dates[-1]),
        "factors": sorted(data),
        "sha256": rec["sha256"][:16], "url": rec["url"],
        "retrieved_utc": rec.get("retrieved_utc"),
    }


def load_prices(root=ROOT, min_days: int = 750):
    """Return (dates, {ticker: closes}, provenance) from the Stooq CSVs."""
    f = Fetcher(root)
    man = f.load_manifest()
    cached = {k: v for k, v in man["files"].items() if k.startswith("stooq/")}
    if not cached:
        raise FetchError(
            "no real price data cached. Run `python -m data.fetch` in a "
            "networked environment first; these checks will not be reported as "
            "run on real returns when they were run on generated ones.")

    series, prov = {}, []
    for dest, rec in sorted(cached.items()):
        sym = pathlib.Path(dest).stem
        try:
            d, c = parse_stooq((f.raw / dest).read_bytes())
        except ValueError as exc:
            prov.append({"ticker": sym, "status": f"unusable: {exc}"})
            continue
        series[sym] = (d, c)
        prov.append({"ticker": sym, "status": "ok", "n_closes": len(c),
                     "first": str(d[0]), "last": str(d[-1]),
                     "sha256": rec["sha256"][:16], "url": rec["url"]})

    if not series:
        raise FetchError("no usable price series in the cache")
    dates, aligned = align(series) if len(series) > 1 else (
        series[next(iter(series))][0], {k: v[1] for k, v in series.items()})
    if len(dates) < min_days:
        raise FetchError(f"only {len(dates)} usable days; need {min_days}")
    return dates, aligned, prov


def strategy_grid(prices: np.ndarray, fast_range=range(2, 22, 2),
                  slow_range=range(20, 220, 10)):
    """Every fast/slow moving-average crossover rule on one price series.

    Strictly causal: the signal at t uses closes up to and including t, and is
    applied to the return from t to t+1. That matters more here than anywhere
    else in the toolkit -- a sweep that peeks would produce spectacular Sharpe
    ratios and the deflation check would then be arguing with a bug rather
    than with luck.
    """
    px = np.asarray(prices, float)
    r = np.diff(px) / px[:-1]
    out = []
    for fast in fast_range:
        for slow in slow_range:
            if fast >= slow:
                continue
            mf = _sma(px, fast)
            ms = _sma(px, slow)
            signal = (mf > ms).astype(float)
            # signal[:-1] is known at the close of t; r[t] is t -> t+1.
            strat = signal[:-1] * r
            valid = ~np.isnan(strat)
            if valid.sum() < 250:
                continue
            out.append({"fast": fast, "slow": slow,
                        "returns": strat[valid]})
    return out


def _sma(x: np.ndarray, w: int) -> np.ndarray:
    c = np.concatenate([[0.0], np.cumsum(x)])
    out = np.full(len(x), np.nan)
    out[w - 1:] = (c[w:] - c[:-w]) / w
    return out
