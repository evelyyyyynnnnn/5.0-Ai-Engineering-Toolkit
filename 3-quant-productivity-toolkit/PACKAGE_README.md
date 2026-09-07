# qkit-research

The checks a quantitative researcher forgets.

Not a backtester. Backtesters are plentiful and mostly fine; what goes wrong is
upstream of them, in four places that turn a strategy that does not work into a
beautiful equity curve:

| Check | What it catches |
|---|---|
| **Lookahead** | A feature that uses information from its own future |
| **Survivorship** | A universe that quietly excludes what died |
| **Label leakage** | Cross-validation folds sharing overlapping label windows |
| **Selection** | A Sharpe ratio reported after trying two hundred variants |

Each returns a *finding*, not a number, so it drops into a research loop and
fails loudly.

## Install

```bash
pip install qkit-research
```

Requires Python 3.9+ and numpy. Nothing else.

## Lookahead

The convention: `feature[t]` is known at the end of period `t` and predicts
`target[t+1]`. Lookahead therefore means correlation with the *contemporaneous
or future* target. Correlation with an earlier target is **not** lookahead — a
momentum feature *is* the previous return.

```python
import numpy as np
from qkit import detect_lookahead, shift_safe

returns = np.random.default_rng(0).normal(0, 0.01, 1000)

leaky = np.roll(returns, -1)          # copies next period's return
print(detect_lookahead(leaky, returns, "leaky").contaminated)      # True

momentum = np.roll(returns, 1)        # legitimate: last period's return
print(detect_lookahead(momentum, returns, "momentum").contaminated)  # False

fixed = shift_safe(leaky, 2)          # the one-line remedy
```

The threshold is a plausibility bound on forward predictability, not a
significance test. Genuine edges in liquid markets correlate 0.02–0.10; a
feature correlating 0.6 with a future return has seen the answer.

## Survivorship

```python
from qkit import audit_universe

finding = audit_universe(returns_matrix, alive_at_end)
print(finding.bias_bps)               # basis points per period
```

Takes the full universe *including the dead* — exactly the data most
survivorship-biased studies lack. When it is unavailable the honest output is a
warning; this library does not correct a bias it cannot measure.

## Purged cross-validation

Standard k-fold leaks whenever a label spans several periods. Purging removes
the overlap; an embargo removes the serial correlation that survives it.

```python
from qkit import PurgedKFold

cv = PurgedKFold(n_splits=5, label_span=20, embargo=20)
for train, test in cv.split(len(X)):
    model.fit(X[train], y[train])

print(cv.leakage_check(len(X)))       # folds_with_overlap should be 0
```

With `label_span=1` and `embargo=0` it reduces to ordinary contiguous k-fold.

## Deflated Sharpe

A Sharpe of 2.0 found after testing two hundred variants is not the same
quantity as a Sharpe of 2.0 from a single pre-registered strategy.

```python
from qkit import sharpe, deflated_sharpe, min_track_record_length

print(sharpe(r))
print(deflated_sharpe(r, n_trials=200))
print(min_track_record_length(r))
```

On 200 strategies generated from pure noise — true Sharpe exactly zero — the
best shows an observed Sharpe of 1.82 and a probabilistic Sharpe against zero of
0.999. Deflating for the trial count drops it to 0.65 and it does not survive.

Deflation assumes independent trials. Two hundred variants of one idea are not
independent, and the correction is then too weak.

## Command line

```bash
qkit lookahead features.csv --target fwd_return --features mom_5 vol_20 rsi
qkit sharpe backtest.csv --column returns --trials 200
```

Both exit non-zero on a finding, so they work as a pre-commit hook or a CI gate.

## Limitations

- The lookahead detector is correlational and univariate. A feature that leaks
  only in combination with another will pass, and a centred rolling window can
  sit just under the threshold.
- Purged k-fold assumes a fixed label span; variable-horizon labels need
  per-observation windows, which are not implemented.
- Nothing here validates a strategy. It tells you when a backtest cannot be
  believed, which is a different and smaller claim.

## Licence

MIT.
