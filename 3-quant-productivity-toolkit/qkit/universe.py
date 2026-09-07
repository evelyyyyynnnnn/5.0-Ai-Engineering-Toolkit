"""Survivorship auditing.

A universe assembled from names that exist today has already excluded everything
that failed. The resulting backtest is not optimistic by a little; on a long
sample it can invert the sign of a result.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class SurvivorshipFinding:
    n_universe: int
    n_survivors: int
    n_delisted: int
    survivor_share: float
    biased: bool
    mean_return_all: float
    mean_return_survivors: float
    bias_bps: float

    def as_dict(self) -> dict:
        return {"n_universe": self.n_universe, "n_survivors": self.n_survivors,
                "n_delisted": self.n_delisted,
                "survivor_share": round(self.survivor_share, 4),
                "biased": self.biased,
                "mean_return_all": round(self.mean_return_all, 6),
                "mean_return_survivors": round(self.mean_return_survivors, 6),
                "bias_bps": round(self.bias_bps, 2)}


def audit_universe(returns: np.ndarray, alive_at_end: np.ndarray) -> SurvivorshipFinding:
    """Quantify what restricting to survivors would do to the mean return.

    Takes the full universe including the dead, which is exactly the data most
    survivorship-biased studies do not have. When it is unavailable the honest
    output is a warning, not an adjustment -- this function does not attempt to
    correct a bias it cannot measure.
    """
    R = np.asarray(returns, float)
    alive = np.asarray(alive_at_end, bool)
    all_mean = float(np.nanmean(R))
    surv_mean = float(np.nanmean(R[:, alive])) if alive.any() else float("nan")
    n = R.shape[1]
    return SurvivorshipFinding(
        n_universe=n, n_survivors=int(alive.sum()), n_delisted=int((~alive).sum()),
        survivor_share=float(alive.mean()), biased=bool((~alive).any()),
        mean_return_all=all_mean, mean_return_survivors=surv_mean,
        bias_bps=(surv_mean - all_mean) * 10_000)
