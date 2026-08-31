import pathlib
import sys

import numpy as np
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from src import risk
from src.service import (MarketData, Portfolio, ValidationError, handle,
                         risk_report)

TICKERS = ["A", "B", "C", "D"]


@pytest.fixture
def market():
    rng = np.random.default_rng(0)
    betas = np.array([0.4, 1.0, 1.6, 2.2])
    f = rng.standard_t(df=4, size=800) * 0.009
    R = f[:, None] * betas[None, :] + rng.normal(0, 0.005, (800, 4))
    return MarketData(tickers=TICKERS, returns=R, betas=betas)


def _req(weights, tickers=None):
    return {"portfolio_id": "P", "tickers": tickers or TICKERS,
            "weights": weights}


# --- risk measures on known inputs ---------------------------------------

def test_historical_var_is_the_empirical_quantile():
    r = np.linspace(-0.10, 0.10, 1001)
    assert abs(risk.historical_var(r, 0.95) - 0.09) < 1e-3


def test_expected_shortfall_exceeds_var():
    r = np.random.default_rng(1).standard_t(4, 5000) * 0.01
    assert risk.expected_shortfall(r, 0.95) > risk.historical_var(r, 0.95)


def test_cornish_fisher_exceeds_gaussian_on_a_fat_left_tail():
    """Regression: applying the expansion to the positive quantile and negating
    flips the skew term and reports the corrected VaR BELOW the uncorrected one."""
    rng = np.random.default_rng(2)
    r = rng.normal(0, 0.01, 6000)
    r[rng.random(6000) < 0.03] -= 0.06          # fat, negatively skewed tail
    assert risk.cornish_fisher_var(r, 0.95) > risk.gaussian_var(r, 0.95)


def test_cornish_fisher_matches_gaussian_on_normal_returns():
    r = np.random.default_rng(3).normal(0, 0.01, 40000)
    a = risk.cornish_fisher_var(r, 0.95)
    b = risk.gaussian_var(r, 0.95)
    assert abs(a - b) / b < 0.05


def test_max_drawdown_of_a_rising_series_is_zero():
    assert risk.max_drawdown(np.full(50, 0.001)) == 0.0


def test_max_drawdown_recovers_a_known_fall():
    r = np.array([0.0, -0.5, 0.0])
    assert abs(risk.max_drawdown(r) - 0.5) < 1e-9


def test_risk_contributions_sum_to_total_volatility():
    """The Euler property. Without it these are scores, not an allocation."""
    rng = np.random.default_rng(4)
    R = rng.normal(0, 0.01, (600, 5))
    cov = np.cov(R, rowvar=False)
    w = np.array([0.4, 0.25, 0.15, 0.15, 0.05])
    total = float(np.sqrt(w @ cov @ w))
    assert abs(risk.risk_contributions(w, cov).sum() - total) < 1e-12


def test_concentration_of_equal_weights():
    c = risk.concentration(np.full(10, 0.1))
    assert abs(c["effective_positions"] - 10) < 1e-6


def test_worst_window_finds_a_planted_crash():
    r = np.full(200, 0.001)
    r[100:110] = -0.05
    out = risk.worst_historical_window(r, 10)
    assert 95 <= out["start"] <= 105 and out["loss"] > 0.3


# --- service behaviour ---------------------------------------------------

def test_valid_request_produces_a_report(market):
    out = handle(_req([0.25] * 4), market)
    assert out["ok"]
    r = out["report"]
    assert r["n_positions"] == 4
    assert set(r["risk"]) >= {"var_historical", "var_gaussian",
                              "var_cornish_fisher", "expected_shortfall"}


def test_weights_must_sum_to_one(market):
    out = handle(_req([0.3] * 4), market)
    assert not out["ok"] and "sum" in out["detail"]


def test_mismatched_lengths_are_rejected(market):
    out = handle(_req([0.5, 0.5], TICKERS), market)
    assert not out["ok"]


def test_duplicate_tickers_are_rejected(market):
    out = handle(_req([0.5, 0.5], ["A", "A"]), market)
    assert not out["ok"] and "duplicate" in out["detail"]


def test_nan_weights_are_rejected(market):
    out = handle(_req([float("nan")] * 4), market)
    assert not out["ok"]


def test_unknown_ticker_is_refused_not_dropped(market):
    """Silent misalignment is what makes a risk system dangerous."""
    out = handle(_req([0.5, 0.5], ["A", "ZZZ"]), market)
    assert not out["ok"] and "ZZZ" in out["detail"]


def test_missing_field_is_handled(market):
    out = handle({"portfolio_id": "P"}, market)
    assert not out["ok"] and out["error"] == "KeyError"


def test_alignment_reorders_rather_than_assuming(market):
    """A permuted request must give the same answer as the canonical order."""
    a = handle(_req([0.4, 0.3, 0.2, 0.1], ["A", "B", "C", "D"]), market)
    b = handle(_req([0.1, 0.2, 0.3, 0.4], ["D", "C", "B", "A"]), market)
    assert (abs(a["report"]["risk"]["annualised_volatility"]
                - b["report"]["risk"]["annualised_volatility"]) < 1e-9)


def test_contributions_are_ordered_by_magnitude(market):
    c = handle(_req([0.25] * 4), market)["report"]["contributions"]
    shares = [abs(x["risk_contribution"]) for x in c]
    assert shares == sorted(shares, reverse=True)


def test_high_beta_position_carries_more_risk_than_capital(market):
    """The finding a capital-based limit cannot see."""
    rep = handle(_req([0.25] * 4), market)["report"]
    top = rep["contributions"][0]
    assert top["risk_share"] > top["weight"]


def test_concentrated_portfolio_raises_a_check(market):
    rep = handle(_req([0.85, 0.05, 0.05, 0.05]), market)["report"]
    codes = {c["code"] for c in rep["checks"]}
    assert "concentrated" in codes or "risk_concentration" in codes


def test_equal_weight_portfolio_is_not_flagged_as_concentrated(market):
    rep = handle(_req([0.25] * 4), market)["report"]
    assert "concentrated" not in {c["code"] for c in rep["checks"]}


def test_short_history_is_flagged():
    rng = np.random.default_rng(6)
    m = MarketData(tickers=TICKERS, returns=rng.normal(0, 0.01, (100, 4)),
                   betas=np.ones(4))
    rep = handle(_req([0.25] * 4), m)["report"]
    assert "short_history" in {c["code"] for c in rep["checks"]}


def test_report_is_json_serialisable(market):
    import json
    json.dumps(handle(_req([0.25] * 4), market))
