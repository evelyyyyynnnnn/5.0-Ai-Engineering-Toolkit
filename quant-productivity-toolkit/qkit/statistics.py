"""Sharpe ratios that account for how many strategies were tried.

A Sharpe of 2.0 found after testing two hundred variants is not the same
quantity as a Sharpe of 2.0 from a single pre-registered strategy, and reporting
them identically is the most common way a backtest misleads.
"""

from __future__ import annotations

import math

import numpy as np


def sharpe(returns: np.ndarray, periods_per_year: int = 252) -> float:
    r = np.asarray(returns, float)
    sd = r.std(ddof=1)
    if sd < 1e-15:
        return 0.0
    return float(r.mean() / sd * math.sqrt(periods_per_year))


def _norm_cdf(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def _norm_ppf(p: float) -> float:
    lo, hi = -12.0, 12.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if _norm_cdf(mid) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def probabilistic_sharpe(returns: np.ndarray, benchmark_sr: float = 0.0,
                         periods_per_year: int = 252) -> float:
    """P(true Sharpe > benchmark), adjusting for skew and kurtosis.

    Non-normal returns are the norm, and a Sharpe ratio computed on them has a
    standard error the textbook formula understates.
    """
    r = np.asarray(returns, float)
    n = len(r)
    if n < 3:
        return float("nan")
    sr = sharpe(r, periods_per_year) / math.sqrt(periods_per_year)   # per period
    bench = benchmark_sr / math.sqrt(periods_per_year)
    sd = r.std(ddof=1)
    if sd < 1e-15:
        return float("nan")
    z = (r - r.mean()) / sd
    skew = float(np.mean(z ** 3))
    kurt = float(np.mean(z ** 4))
    denom = math.sqrt(max(1e-12,
                          (1 - skew * sr + (kurt - 1) / 4 * sr ** 2) / (n - 1)))
    return float(_norm_cdf((sr - bench) / denom))


def deflated_sharpe(returns: np.ndarray, n_trials: int,
                    periods_per_year: int = 252,
                    trial_sr_variance: float | None = None) -> dict:
    """Sharpe adjusted for the number of strategies tried.

    The expected maximum Sharpe across `n_trials` independent random strategies
    is not zero; it grows with the number tried. The deflated ratio asks whether
    the observed Sharpe beats that expectation.
    """
    r = np.asarray(returns, float)
    obs = sharpe(r, periods_per_year)
    v = trial_sr_variance if trial_sr_variance is not None else 1.0 / len(r)
    if n_trials < 2:
        expected_max = 0.0
    else:
        e = 0.5772156649
        expected_max = math.sqrt(v) * (
            (1 - e) * _norm_ppf(1 - 1.0 / n_trials)
            + e * _norm_ppf(1 - 1.0 / (n_trials * math.e)))
        expected_max *= math.sqrt(periods_per_year)
    psr = probabilistic_sharpe(r, benchmark_sr=expected_max,
                               periods_per_year=periods_per_year)
    return {"observed_sharpe": round(obs, 4), "n_trials": n_trials,
            "expected_max_sharpe_from_noise": round(expected_max, 4),
            "deflated_sharpe_prob": round(psr, 5),
            "survives": bool(psr > 0.95)}


def min_track_record_length(returns: np.ndarray, benchmark_sr: float = 0.0,
                            confidence: float = 0.95,
                            periods_per_year: int = 252) -> float:
    """Observations needed before a Sharpe is distinguishable from the benchmark."""
    r = np.asarray(returns, float)
    sr = sharpe(r, periods_per_year) / math.sqrt(periods_per_year)
    bench = benchmark_sr / math.sqrt(periods_per_year)
    if abs(sr - bench) < 1e-12:
        return float("inf")
    sd = r.std(ddof=1)
    z = (r - r.mean()) / sd if sd > 1e-15 else r * 0
    skew, kurt = float(np.mean(z ** 3)), float(np.mean(z ** 4))
    num = (1 - skew * sr + (kurt - 1) / 4 * sr ** 2)
    return float(1 + num * (_norm_ppf(confidence) / (sr - bench)) ** 2)
