"""qkit — the checks a quantitative researcher forgets.

Not a backtester. Backtesters are plentiful and mostly fine; what goes wrong is
upstream of them, in four places that produce a beautiful equity curve from a
strategy that does not work:

  lookahead     a feature that uses information from its own future
  survivorship  a universe that quietly excludes what died
  leakage       cross-validation folds that share overlapping label windows
  selection     a Sharpe ratio reported after trying two hundred variants

Each is a function that returns a finding, not a number, so it can be dropped
into an existing research loop and fail loudly.
"""

from .lookahead import LookaheadFinding, detect_lookahead, shift_safe
from .universe import SurvivorshipFinding, audit_universe
from .validation import PurgedKFold, embargo_indices
from .statistics import (deflated_sharpe, min_track_record_length,
                         probabilistic_sharpe, sharpe)

__version__ = "0.1.0"

__all__ = ["LookaheadFinding", "detect_lookahead", "shift_safe",
           "SurvivorshipFinding", "audit_universe",
           "PurgedKFold", "embargo_indices",
           "sharpe", "probabilistic_sharpe", "deflated_sharpe",
           "min_track_record_length", "__version__"]
