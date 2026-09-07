"""Detecting features that use information they could not have had.

The convention throughout: `feature[t]` is known at the end of period t and is
used to predict `target[t+1]`, the return realised over the NEXT period.

Under that convention lookahead means `feature[t]` carries information about
`target[t]` or later. Correlation with EARLIER targets is not lookahead -- a
momentum feature is literally the previous return, and correlating perfectly
with it is the definition of momentum, not a bug.

Getting that backwards is easy and was the first version of this module: it
tested correlation with past targets, flagged a momentum feature as
contaminated, and passed a feature that was a copy of next period's return. The
direction of the test is the whole content of it.

The detection rule is a plausibility bound rather than a significance test.
Genuine forward predictability in a liquid market is weak -- correlations of
0.02 to 0.10 are a real edge. A feature correlating 0.6 with a future return has
not found an edge; it has seen the answer.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class LookaheadFinding:
    feature: str
    max_forward_corr: float          # with target[t+k], k >= 0 -- suspicious
    lag_of_max: int                  # 0 = contemporaneous, 1 = next period
    max_backward_corr: float         # with target[t-k], k >= 1 -- legitimate
    contaminated: bool
    detail: str

    def as_dict(self) -> dict:
        return {"feature": self.feature,
                "max_forward_corr": round(self.max_forward_corr, 5),
                "lag_of_max": self.lag_of_max,
                "max_backward_corr": round(self.max_backward_corr, 5),
                "contaminated": self.contaminated, "detail": self.detail}


def _corr(a, b) -> float:
    if len(a) < 8 or np.std(a) < 1e-12 or np.std(b) < 1e-12:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


def detect_lookahead(feature: np.ndarray, target: np.ndarray,
                     name: str = "feature", max_lag: int = 3,
                     threshold: float = 0.50) -> LookaheadFinding:
    """Flag a feature that correlates implausibly with a contemporaneous or
    future target.

    `threshold` is a plausibility bound on forward predictability, not a
    p-value. Lowering it below about 0.3 starts flagging strong-but-real signals
    on short samples.
    """
    f = np.asarray(feature, float)
    y = np.asarray(target, float)
    n = min(len(f), len(y))
    f, y = f[:n], y[:n]

    # Forward: feature[t] against target[t + k] for k >= 0.
    fwd, fwd_lag = 0.0, 0
    for k in range(0, max_lag + 1):
        c = abs(_corr(f[:n - k], y[k:])) if k else abs(_corr(f, y))
        if c > fwd:
            fwd, fwd_lag = c, k

    # Backward: feature[t] against target[t - k] for k >= 1. Legitimate.
    bwd = 0.0
    for k in range(1, max_lag + 1):
        bwd = max(bwd, abs(_corr(f[k:], y[:-k])))

    bad = fwd > threshold
    when = ("the same period" if fwd_lag == 0
            else f"{fwd_lag} period(s) ahead")
    detail = (f"|corr(f[t], y[t+{fwd_lag}])| = {fwd:.3f} exceeds {threshold}; "
              f"the feature knows about {when}" if bad
              else f"max forward correlation {fwd:.3f} is within the plausible "
                   f"range (backward {bwd:.3f} is not evidence of lookahead)")
    return LookaheadFinding(name, fwd, fwd_lag, bwd, bad, detail)


def shift_safe(x: np.ndarray, periods: int = 1) -> np.ndarray:
    """Shift a feature so it can only use information already available.

    The one-line fix for most lookahead. It is in the package because the
    mistake is not knowing it is needed, not being unable to write it.
    """
    x = np.asarray(x, float)
    out = np.full_like(x, np.nan)
    if periods > 0:
        out[periods:] = x[:-periods]
    elif periods < 0:
        out[:periods] = x[-periods:]
    else:
        out[:] = x
    return out
