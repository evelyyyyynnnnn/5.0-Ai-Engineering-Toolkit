"""Tests for running the backtest checks on real series.

One property matters above all: the strategy sweep must be strictly causal. A
sweep that peeks produces spectacular Sharpe ratios, and the deflation check
then argues with a bug instead of with luck -- which is the most misleading
failure this toolkit could have, because the output looks like a finding.
"""
import datetime as dt
import io
import pathlib
import sys
import zipfile

import numpy as np
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from data import datakit
from data.load import _sma, load_factors, load_prices, strategy_grid


def test_sma_is_trailing_not_centred():
    """A centred mean at t uses prices from after t. That is the leak."""
    x = np.arange(1.0, 11.0)
    m = _sma(x, 3)
    assert np.isnan(m[:2]).all()          # no value before the window fills
    assert m[2] == pytest.approx(2.0)     # mean of 1,2,3
    assert m[9] == pytest.approx(9.0)     # mean of 8,9,10


def test_strategy_returns_are_aligned_one_step_forward():
    """The signal known at the close of t is applied to the t -> t+1 return.

    Built explicitly here: a price series that rises then falls, where an
    aligned strategy cannot capture the turn it has not yet seen.
    """
    px = np.concatenate([np.linspace(100, 150, 400), np.linspace(150, 90, 400)])
    grid = strategy_grid(px, fast_range=range(2, 6, 2), slow_range=range(20, 41, 10))
    assert grid
    r = np.diff(px) / px[:-1]
    for s in grid:
        assert len(s["returns"]) <= len(r)
        # A perfectly-timed (peeking) strategy would have no losing days at the
        # turn; an aligned one must eat some of the reversal.
        assert (s["returns"] < 0).any(), (s["fast"], s["slow"])


def test_strategy_grid_skips_degenerate_and_short_combinations():
    px = 100 + np.cumsum(np.random.default_rng(0).normal(0, 1, 400))
    grid = strategy_grid(px)
    assert all(s["fast"] < s["slow"] for s in grid)
    assert all(len(s["returns"]) >= 250 for s in grid)
    assert len(grid) > 20, "the sweep needs enough rules for deflation to bite"


def test_strategy_grid_returns_contain_no_nan():
    px = 100 + np.cumsum(np.random.default_rng(1).normal(0, 1, 600))
    for s in strategy_grid(px):
        assert np.isfinite(s["returns"]).all()


# --- loading ---------------------------------------------------------------

def test_refuses_without_the_factor_file(tmp_path):
    with pytest.raises(datakit.FetchError, match="Fama-French"):
        load_factors(root=tmp_path)


def test_refuses_without_price_data(tmp_path):
    with pytest.raises(datakit.FetchError, match="no real price data cached"):
        load_prices(root=tmp_path)


def _french_zip():
    lines = ["created by CMPT_ME_BEDAY", "", ",Mkt-RF,SMB,HML,RF"]
    d = dt.date(2015, 1, 2)
    rng = np.random.default_rng(3)
    for _ in range(1200):
        while d.weekday() >= 5:
            d += dt.timedelta(days=1)
        lines.append(f"{d.strftime('%Y%m%d')},{rng.normal(0, 1.0):.2f},"
                     f"{rng.normal(0, 0.5):.2f},{rng.normal(0, 0.5):.2f},0.021")
        d += dt.timedelta(days=1)
    lines += ["", "Annual Factors: January-December", "",
              ",Mkt-RF,SMB,HML,RF", "2024,23.53,-3.60,-9.20,5.32"]
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("F-F_Research_Data_Factors_daily.CSV", "\n".join(lines))
    return buf.getvalue()


def _seed(tmp_path, n=1500):
    f = datakit.Fetcher(tmp_path)
    man = f.load_manifest()

    def put(dest, raw):
        p = f.raw / dest
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(raw)
        man["files"][dest] = {
            "source": dest, "url": f"https://example/{dest}",
            "publisher": "test", "terms": "test",
            "sha256": datakit.sha256_file(p), "bytes": len(raw),
            "retrieved_utc": datakit.utc_now()}

    put("french/ff_daily.zip", _french_zip())
    rng = np.random.default_rng(7)
    for sym in ("spy.us", "qqq.us"):
        px, p = [], 100.0
        for x in rng.normal(0.0003, 0.011, n):
            p *= (1 + x)
            px.append(p)
        d, lines = dt.date(2015, 1, 2), ["Date,Open,High,Low,Close,Volume"]
        for v in px:
            while d.weekday() >= 5:
                d += dt.timedelta(days=1)
            lines.append(f"{d.isoformat()},{v:.4f},{v:.4f},{v:.4f},{v:.4f},1000")
            d += dt.timedelta(days=1)
        put(f"stooq/{sym}.csv", ("\n".join(lines) + "\n").encode())
    f._write_manifest(man)
    return f


def test_factors_parse_without_the_annual_block(tmp_path):
    _seed(tmp_path)
    dates, data, prov = load_factors(root=tmp_path)
    assert len(dates) == 1200
    assert prov["n_days"] == 1200
    # A leaked annual row would put a +23% "daily" return in the series.
    assert max(abs(v) for v in data["Mkt-RF"]) < 0.10
    assert len(prov["sha256"]) == 16


def test_prices_load_and_align(tmp_path):
    _seed(tmp_path)
    dates, prices, prov = load_prices(root=tmp_path)
    assert set(prices) == {"spy.us", "qqq.us"}
    assert all(len(v) == len(dates) for v in prices.values())
    assert all(p["status"] == "ok" for p in prov)


# --- the checks, on real-shaped series -------------------------------------

def test_lookahead_detector_catches_leaks_on_a_real_return_series(tmp_path):
    _seed(tmp_path)
    from src.demo import lookahead_demo_real
    dates, data, _ = load_factors(root=tmp_path)
    out = lookahead_demo_real(dates, np.asarray(data["Mkt-RF"]), "test factor")

    flagged = {c["feature"] for c in out["cases"] if c["contaminated"]}
    assert any("copies next period" in f for f in flagged)
    assert any("copies this period" in f for f in flagged)
    # A 3-sample centred window straddles t hard enough to be caught.
    assert any("3-sample" in f for f in flagged)


def test_properly_lagged_features_are_not_flagged_on_real_returns(tmp_path):
    """The calibration question: does genuine autocorrelation cause false
    positives?"""
    _seed(tmp_path)
    from src.demo import lookahead_demo_real
    dates, data, _ = load_factors(root=tmp_path)
    out = lookahead_demo_real(dates, np.asarray(data["Mkt-RF"]), "test factor")
    assert out["properly_lagged_features_falsely_flagged"] == 0


def test_the_sweep_deflates_a_lucky_winner(tmp_path):
    """Hundreds of rules on a random walk: the best one must not survive."""
    _seed(tmp_path)
    from src.demo import selection_demo_real
    _, prices, _ = load_prices(root=tmp_path)
    out = selection_demo_real(strategy_grid(np.asarray(prices["spy.us"])), "test")

    assert out["n_strategies_tried"] > 50
    # The one-trial figure is what a paper reports when it does not say how
    # many rules it tried; deflation must be strictly harsher.
    assert out["deflated_sharpe_all_trials"] <= out["deflated_sharpe_one_trial"]
    assert out["survives_deflation"] is False, (
        "a crossover rule found by searching a grid on a random walk should "
        "not survive being told how many rules were searched")


def test_the_sweep_reports_its_spread(tmp_path):
    _seed(tmp_path)
    from src.demo import selection_demo_real
    _, prices, _ = load_prices(root=tmp_path)
    out = selection_demo_real(strategy_grid(np.asarray(prices["spy.us"])), "test")
    sp = out["sharpe_spread"]
    assert sp["min"] <= sp["median"] <= sp["max"]
    assert out["best"]["sharpe"] == sp["max"]


def test_a_leak_can_be_diluted_below_any_fixed_threshold(tmp_path):
    """The detector's limit, measured rather than left as a silent miss.

    A centred window of width w contains the future but only 1/w of it, and
    for an uncorrelated series the correlation with the next return is
    1/sqrt(w). That falls as the window widens while the plausibility bound
    stays fixed, so past some width a genuinely leaking feature is invisible
    to any correlation test.
    """
    _seed(tmp_path)
    from src.demo import dilution_sweep
    _, data, _ = load_factors(root=tmp_path)
    out = dilution_sweep(np.asarray(data["Mkt-RF"]))

    for row in out["rows"]:
        # The measured correlation must track the theory it is explained by.
        assert row["correlation_with_next_return"] == pytest.approx(
            row["theoretical_1_over_sqrt_w"], abs=0.08), row

    # Narrow windows are caught, wide ones are not, and the boundary is real.
    assert 3 in out["detected_windows"]
    assert out["missed_windows"], "no window escaped detection; the floor moved"
    assert max(out["detected_windows"]) < min(out["missed_windows"])
    assert out["detection_floor"] == max(out["detected_windows"])


def test_the_dilution_finding_is_reported_not_hidden(tmp_path):
    _seed(tmp_path)
    from src.demo import lookahead_demo_real
    _, data, _ = load_factors(root=tmp_path)
    out = lookahead_demo_real(None, np.asarray(data["Mkt-RF"]), "test")
    assert "dilution" in out
    assert "invisible to any fixed correlation threshold" in \
        out["dilution"]["finding"]
