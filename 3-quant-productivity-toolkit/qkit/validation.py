"""Purged, embargoed cross-validation for overlapping labels.

Standard k-fold leaks whenever a label spans several periods: a training
observation whose label window overlaps a test observation shares information
with it, and the model sees the answer. Purging removes the overlap; an embargo
removes the serial correlation that survives it.
"""

from __future__ import annotations

import numpy as np


def embargo_indices(n: int, test_start: int, test_end: int,
                    embargo: int) -> np.ndarray:
    """Indices to drop after the test block, as a boolean mask of length n."""
    mask = np.zeros(n, bool)
    mask[test_end:min(n, test_end + embargo)] = True
    return mask


class PurgedKFold:
    """K-fold that purges overlapping labels and applies an embargo.

    `label_span` is how many periods a label covers. With span 1 and embargo 0
    this reduces to ordinary contiguous k-fold, which is the check that the
    implementation is not doing something exotic.
    """

    def __init__(self, n_splits: int = 5, label_span: int = 1, embargo: int = 0):
        if n_splits < 2:
            raise ValueError("n_splits must be at least 2")
        self.n_splits = n_splits
        self.label_span = label_span
        self.embargo = embargo

    def split(self, n: int):
        fold_edges = np.linspace(0, n, self.n_splits + 1).astype(int)
        for i in range(self.n_splits):
            a, b = fold_edges[i], fold_edges[i + 1]
            test = np.zeros(n, bool)
            test[a:b] = True

            train = ~test
            # Purge: any training label whose window reaches into the test block.
            lo = max(0, a - self.label_span)
            train[lo:b] = False
            # Embargo: drop the periods immediately after the test block.
            train &= ~embargo_indices(n, a, b, self.embargo)
            yield train, test

    def leakage_check(self, n: int) -> dict:
        """How many observations each fold drops, and whether any overlap remains."""
        drops, overlaps = [], 0
        for train, test in self.split(n):
            drops.append(int(n - train.sum() - test.sum()))
            tr = np.where(train)[0]
            te = np.where(test)[0]
            if len(tr) and len(te):
                # An overlap survives if a training index's label window reaches
                # a test index.
                for t in tr:
                    if np.any((te >= t) & (te < t + self.label_span)):
                        overlaps += 1
                        break
        return {"n_splits": self.n_splits, "label_span": self.label_span,
                "embargo": self.embargo, "dropped_per_fold": drops,
                "folds_with_overlap": overlaps}
