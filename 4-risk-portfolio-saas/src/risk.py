"""Portfolio risk measures.

Every measure here is computed from a returns panel and a weight vector, and
every one is reported with the assumption that produces it. A VaR number without
its method attached is not interpretable: historical, Gaussian and Cornish-Fisher
VaR disagree by a wide margin on the same portfolio, and the disagreement IS the
information.
"""

from __future__ import annotations

import math

import numpy as np


def portfolio_returns(weights: np.ndarray, returns: np.ndarray) -> np.ndarray:
    return np.asarray(returns, float) @ np.asarray(weights, float)


def historical_var(r: np.ndarray, alpha: float = 0.95) -> float:
    """Empirical quantile. No distributional assumption, needs a lot of data."""
    return float(-np.quantile(np.asarray(r, float), 1 - alpha))


def gaussian_var(r: np.ndarray, alpha: float = 0.95) -> float:
    """Normal VaR. Understates the tail whenever returns are not normal."""
    r = np.asarray(r, float)
    z = _norm_ppf(alpha)
    return float(-(r.mean() - z * r.std(ddof=1)))


def cornish_fisher_var(r: np.ndarray, alpha: float = 0.95) -> float:
    """Gaussian VaR corrected for skew and excess kurtosis.

    A middle path: keeps the parametric form but stops pretending the third and
    fourth moments are those of a normal.

    The expansion must be applied to the LEFT-tail quantile. Applying it to the
    positive quantile and negating afterwards flips the sign of the skew term,
    and the first version of this did exactly that -- reporting a Cornish-Fisher
    VaR BELOW the Gaussian one on returns with a fat left tail, which is the
    opposite of the correction's entire purpose. The bug was invisible in the
    formula and obvious the moment the two numbers were printed side by side.
    """
    r = np.asarray(r, float)
    z = _norm_ppf(1.0 - alpha)          # negative: the left-tail quantile
    sd = r.std(ddof=1)
    if sd < 1e-15:
        return 0.0
    zs = (r - r.mean()) / sd
    s = float(np.mean(zs ** 3))
    k = float(np.mean(zs ** 4)) - 3.0
    zc = (z + (z ** 2 - 1) * s / 6 + (z ** 3 - 3 * z) * k / 24
          - (2 * z ** 3 - 5 * z) * s ** 2 / 36)
    return float(-(r.mean() + zc * sd))


def expected_shortfall(r: np.ndarray, alpha: float = 0.95) -> float:
    r = np.asarray(r, float)
    cut = np.quantile(r, 1 - alpha)
    tail = r[r <= cut]
    return float(-tail.mean()) if len(tail) else float(-cut)


def max_drawdown(r: np.ndarray) -> float:
    curve = np.cumprod(1 + np.asarray(r, float))
    peak = np.maximum.accumulate(curve)
    return float(np.max((peak - curve) / peak))


def volatility(r: np.ndarray, periods_per_year: int = 252) -> float:
    return float(np.std(r, ddof=1) * math.sqrt(periods_per_year))


def _norm_ppf(p: float) -> float:
    lo, hi = -12.0, 12.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if 0.5 * (1 + math.erf(mid / math.sqrt(2))) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


# --- attribution ----------------------------------------------------------

def risk_contributions(weights: np.ndarray, cov: np.ndarray) -> np.ndarray:
    """Euler decomposition of portfolio volatility.

    Contributions sum exactly to total volatility, which is the property that
    makes them an allocation of risk rather than a set of scores. A position can
    be 5% of capital and 30% of risk, and only this view shows it.
    """
    w = np.asarray(weights, float)
    S = np.asarray(cov, float)
    total = math.sqrt(max(1e-30, float(w @ S @ w)))
    marginal = S @ w / total
    return w * marginal


def concentration(weights: np.ndarray) -> dict:
    w = np.abs(np.asarray(weights, float))
    s = w.sum()
    if s <= 0:
        return {"hhi": 0.0, "effective_positions": 0.0, "top3_share": 0.0}
    p = w / s
    hhi = float(np.sum(p ** 2))
    return {"hhi": round(hhi, 5),
            "effective_positions": round(1.0 / hhi, 2),
            "top3_share": round(float(np.sort(p)[::-1][:3].sum()), 4)}


# --- stress ---------------------------------------------------------------

def stress_scenario(weights: np.ndarray, betas: np.ndarray,
                    factor_shock: float) -> float:
    """Portfolio move under a factor shock, via position betas."""
    return float(np.asarray(weights, float) @ np.asarray(betas, float)
                 * factor_shock)


def _ll(k: int, n: int, p: float) -> float:
    """Log-likelihood of k hits in n Bernoulli trials at rate p, 0*log0 := 0."""
    if n == 0:
        return 0.0
    out = 0.0
    if k > 0:
        out += k * math.log(p) if p > 0 else -math.inf
    if n - k > 0:
        out += (n - k) * math.log(1 - p) if p < 1 else -math.inf
    return out


def _chi2_sf(x: float, df: int) -> float:
    """Upper-tail probability of a chi-square variate. Closed forms for 1, 2 df."""
    if x <= 0:
        return 1.0
    if df == 1:
        return math.erfc(math.sqrt(x / 2.0))
    if df == 2:
        return math.exp(-x / 2.0)
    raise ValueError("only 1 and 2 degrees of freedom are supported")


def var_backtest(r: np.ndarray, alpha: float = 0.95, window: int = 250) -> dict:
    """Out-of-sample backtest of the rolling historical VaR.

    At each day t the VaR is estimated from the trailing `window` returns and
    an exception is recorded when the next day's loss exceeds it. Two standard
    tests are then reported on the exception series:

      * Kupiec's proportion-of-failures test (unconditional coverage): are there
        about (1-alpha) exceptions, no more and no fewer?
      * Christoffersen's independence test: do exceptions cluster, or arrive
        independently? Their sum is the conditional-coverage test.

    A high p-value means the model is not rejected; it is not proof the model is
    correct. The observed and expected exception counts are reported alongside
    so the coverage can be read directly rather than only through a p-value.
    """
    r = np.asarray(r, float)
    T = len(r)
    p = 1.0 - alpha
    if T <= window + 1:
        return {"tested": False,
                "reason": f"need more than window+1={window + 1} returns to "
                          f"backtest; have {T}",
                "window": window, "confidence": alpha}

    hits = []
    for t in range(window, T):
        var_t = historical_var(r[t - window:t], alpha)   # loss is reported +ve
        hits.append(1 if r[t] < -var_t else 0)
    hits = np.asarray(hits, int)
    n = len(hits)
    x = int(hits.sum())
    pi = x / n

    # Kupiec unconditional coverage.
    lr_uc = -2.0 * (_ll(x, n, p) - _ll(x, n, pi))
    lr_uc = max(0.0, lr_uc)

    # Christoffersen independence: transition counts n_ij of hit_{t-1}->hit_t.
    prev, cur = hits[:-1], hits[1:]
    n00 = int(np.sum((prev == 0) & (cur == 0)))
    n01 = int(np.sum((prev == 0) & (cur == 1)))
    n10 = int(np.sum((prev == 1) & (cur == 0)))
    n11 = int(np.sum((prev == 1) & (cur == 1)))
    pi01 = n01 / (n00 + n01) if (n00 + n01) else 0.0
    pi11 = n11 / (n10 + n11) if (n10 + n11) else 0.0
    pi_hit = (n01 + n11) / (n00 + n01 + n10 + n11) if n > 1 else 0.0
    ll_ind = _ll(n01, n00 + n01, pi01) + _ll(n11, n10 + n11, pi11)
    ll_pooled = _ll(n01 + n11, n00 + n01 + n10 + n11, pi_hit)
    lr_ind = max(0.0, -2.0 * (ll_pooled - ll_ind))
    lr_cc = lr_uc + lr_ind

    return {
        "tested": True,
        "confidence": alpha,
        "window": window,
        "test_observations": n,
        "expected_exceptions": round(p * n, 2),
        "observed_exceptions": x,
        "exception_rate": round(pi, 5),
        "expected_rate": round(p, 5),
        "kupiec_lr": round(lr_uc, 4),
        "kupiec_p": round(_chi2_sf(lr_uc, 1), 4),
        "independence_lr": round(lr_ind, 4),
        "independence_p": round(_chi2_sf(lr_ind, 1), 4),
        "christoffersen_cc_lr": round(lr_cc, 4),
        "christoffersen_cc_p": round(_chi2_sf(lr_cc, 2), 4),
    }


def worst_historical_window(r: np.ndarray, window: int = 20) -> dict:
    """The worst realised run of `window` periods. A stress test with no model."""
    r = np.asarray(r, float)
    if len(r) < window:
        return {"window": window, "loss": 0.0, "start": 0}
    cum = np.array([np.prod(1 + r[i:i + window]) - 1
                    for i in range(len(r) - window + 1)])
    i = int(np.argmin(cum))
    return {"window": window, "loss": round(float(-cum[i]), 6), "start": i}
