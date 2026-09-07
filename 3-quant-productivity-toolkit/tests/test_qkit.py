import pathlib
import sys

import numpy as np
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import qkit
from qkit import (PurgedKFold, audit_universe, deflated_sharpe, detect_lookahead,
                  embargo_indices, min_track_record_length, probabilistic_sharpe,
                  sharpe, shift_safe)


@pytest.fixture
def y():
    return np.random.default_rng(0).normal(0, 0.011, 900)


# --- lookahead: direction is the whole test ------------------------------

def test_feature_copying_the_future_is_flagged(y):
    assert detect_lookahead(np.roll(y, -1), y, "leak").contaminated


def test_feature_copying_the_present_is_flagged(y):
    assert detect_lookahead(y.copy(), y, "leak").contaminated


def test_momentum_is_not_flagged(y):
    """Regression: the first version had the direction inverted.

    A momentum feature IS the previous return. Correlating perfectly with it is
    the definition of momentum, not evidence of lookahead.
    """
    f = detect_lookahead(np.roll(y, 1), y, "momentum")
    assert not f.contaminated
    assert f.max_backward_corr > 0.9      # the legitimate correlation is there
    assert f.max_forward_corr < 0.2


def test_noise_is_not_flagged(y):
    noise = np.random.default_rng(9).normal(0, 1, len(y))
    assert not detect_lookahead(noise, y, "noise").contaminated


def test_a_weak_genuine_edge_is_not_flagged(y):
    rng = np.random.default_rng(3)
    edge = 0.05 * np.roll(y, -1) / y.std() + rng.normal(0, 1, len(y))
    assert not detect_lookahead(edge, y, "edge").contaminated


def test_lag_of_max_identifies_where_the_leak_is(y):
    assert detect_lookahead(y.copy(), y).lag_of_max == 0
    assert detect_lookahead(np.roll(y, -1), y).lag_of_max == 1


def test_shift_safe_removes_the_leak(y):
    leaky = np.roll(y, -1)
    assert detect_lookahead(leaky, y).contaminated
    fixed = np.nan_to_num(shift_safe(leaky, 2))
    assert not detect_lookahead(fixed, y).contaminated


def test_shift_safe_directions():
    x = np.array([1.0, 2, 3, 4])
    assert np.array_equal(shift_safe(x, 1)[1:], x[:-1])
    assert np.isnan(shift_safe(x, 1)[0])
    assert np.array_equal(shift_safe(x, 0), x)


# --- survivorship --------------------------------------------------------

def test_survivorship_bias_is_positive_when_losers_delist():
    rng = np.random.default_rng(2)
    R = rng.normal(0.0003, 0.014, (400, 200))
    alive = R.sum(axis=0) > np.quantile(R.sum(axis=0), 0.3)
    f = audit_universe(R, alive)
    assert f.biased and f.bias_bps > 0
    assert f.mean_return_survivors > f.mean_return_all


def test_no_bias_when_nothing_delists():
    R = np.random.default_rng(4).normal(0, 0.01, (200, 50))
    f = audit_universe(R, np.ones(50, bool))
    assert not f.biased
    assert abs(f.bias_bps) < 1e-6


def test_survivor_counts_add_up():
    R = np.random.default_rng(5).normal(0, 0.01, (100, 60))
    alive = np.arange(60) % 3 != 0
    f = audit_universe(R, alive)
    assert f.n_survivors + f.n_delisted == f.n_universe == 60


# --- purged cross-validation --------------------------------------------

def test_folds_partition_the_sample():
    cv = PurgedKFold(n_splits=5, label_span=1, embargo=0)
    seen = np.zeros(500, int)
    for _, test in cv.split(500):
        seen += test.astype(int)
    assert (seen == 1).all()


def test_train_and_test_never_intersect():
    cv = PurgedKFold(n_splits=4, label_span=10, embargo=5)
    for train, test in cv.split(600):
        assert not (train & test).any()


def test_purging_removes_overlapping_labels():
    n, span = 1000, 20
    naive = PurgedKFold(n_splits=5, label_span=1, embargo=0)
    purged = PurgedKFold(n_splits=5, label_span=span, embargo=0)
    overlaps = 0
    for train, test in naive.split(n):
        tr, te = np.where(train)[0], np.where(test)[0]
        overlaps += sum(1 for t in tr if np.any((te >= t) & (te < t + span)))
    assert overlaps > 0, "the naive scheme should leak"
    assert purged.leakage_check(n)["folds_with_overlap"] == 0


def test_embargo_drops_more_than_purging_alone():
    a = PurgedKFold(5, label_span=10, embargo=0).leakage_check(800)
    b = PurgedKFold(5, label_span=10, embargo=25).leakage_check(800)
    assert sum(b["dropped_per_fold"]) > sum(a["dropped_per_fold"])


def test_reduces_to_plain_kfold_with_span_one_and_no_embargo():
    cv = PurgedKFold(5, label_span=1, embargo=0)
    assert max(cv.leakage_check(1000)["dropped_per_fold"]) <= 1


def test_embargo_indices_are_bounded():
    m = embargo_indices(100, 80, 95, 20)
    assert m.sum() == 5 and m[95:].all()


def test_too_few_splits_raises():
    with pytest.raises(ValueError):
        PurgedKFold(n_splits=1)


# --- Sharpe statistics ---------------------------------------------------

def test_sharpe_of_constant_returns_is_zero():
    assert sharpe(np.full(100, 0.001)) == 0.0


def test_sharpe_scales_with_the_square_root_of_frequency():
    """Magnitude scales; sign does not.

    The first version asserted sharpe(r, 252) > sharpe(r, 12), which holds only
    when the mean return is positive -- and the sample it used happened to have
    a negative one, so annualising made it MORE negative. Testing the scaling
    relationship directly avoids depending on the sign of a random draw.
    """
    import math
    r = np.random.default_rng(1).normal(0.0005, 0.01, 1000)
    assert abs(sharpe(r, 252) - sharpe(r, 1) * math.sqrt(252)) < 1e-9
    assert abs(sharpe(r, 12) - sharpe(r, 1) * math.sqrt(12)) < 1e-9
    assert abs(sharpe(r, 252)) > abs(sharpe(r, 12))


def test_sharpe_sign_follows_the_mean_return():
    up = np.random.default_rng(11).normal(0.002, 0.005, 1500)
    down = np.random.default_rng(12).normal(-0.002, 0.005, 1500)
    assert sharpe(up) > 0 > sharpe(down)


def test_psr_is_high_for_a_clearly_positive_sharpe():
    r = np.random.default_rng(2).normal(0.002, 0.005, 2000)
    assert probabilistic_sharpe(r) > 0.99


def test_psr_is_near_half_for_a_zero_sharpe():
    r = np.random.default_rng(3).normal(0.0, 0.01, 4000)
    assert 0.2 < probabilistic_sharpe(r) < 0.8


def test_expected_max_sharpe_grows_with_trials():
    r = np.random.default_rng(4).normal(0, 0.01, 750)
    a = deflated_sharpe(r, 10)["expected_max_sharpe_from_noise"]
    b = deflated_sharpe(r, 500)["expected_max_sharpe_from_noise"]
    assert b > a > 0


def test_best_of_many_noise_strategies_does_not_survive_deflation():
    """The result the whole module exists for.

    Pure noise, true Sharpe zero. The best of 200 looks decisively significant
    against zero and must not survive once the trial count is admitted.
    """
    rng = np.random.default_rng(7)
    paths = rng.normal(0, 0.01, (200, 750))
    best = paths[int(np.argmax([sharpe(p) for p in paths]))]
    assert probabilistic_sharpe(best) > 0.95      # looks significant
    assert not deflated_sharpe(best, 200)["survives"]


def test_a_single_pretested_strategy_is_judged_differently():
    rng = np.random.default_rng(7)
    paths = rng.normal(0, 0.01, (200, 750))
    best = paths[int(np.argmax([sharpe(p) for p in paths]))]
    assert deflated_sharpe(best, 1)["survives"]
    assert not deflated_sharpe(best, 200)["survives"]


def test_min_track_record_length_is_infinite_at_the_benchmark():
    r = np.full(100, 0.0)
    assert min_track_record_length(r) == float("inf")


def test_package_is_not_claimed_to_be_published():
    import json
    p = pathlib.Path(__file__).resolve().parent.parent / "results" / "latest.json"
    if p.exists():
        assert json.loads(p.read_text())["package"]["published"] is False
