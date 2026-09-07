"""Tests for the real-data layer.

Downloading needs a network; parsing, aligning, beta estimation and the refusal
to substitute simulated data for real data do not, and those are what is
covered here.
"""
import datetime as dt
import pathlib
import sys

import numpy as np
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from data import datakit
from data.marketdata import (align, parse_fred, parse_french_industry,
                             parse_stooq)

D = dt.date.fromisoformat


def test_parse_stooq_drops_halted_sessions():
    raw = (b"Date,Open,High,Low,Close,Volume\n"
           b"2024-01-02,470,472,469,471.5,8\n"
           b"2024-01-03,469,470,,,0\n"
           b"2024-01-04,470,474,470,473.0,7\n")
    # An empty close read as zero becomes a -100% return, which would dominate
    # every VaR estimate in the report.
    _, closes = parse_stooq(raw)
    assert closes == [471.5, 473.0]


def test_parse_stooq_rejects_the_200_ok_no_data_response():
    with pytest.raises(ValueError, match="market suffix"):
        parse_stooq(b"No data")


def test_parse_fred_skips_holiday_dots():
    _, vals = parse_fred(b"DATE,DGS3MO\n2024-01-01,.\n2024-01-02,5.40\n")
    assert vals == [5.40]


def test_align_drops_dates_missing_from_any_series():
    a = ([D("2024-01-02"), D("2024-01-03"), D("2024-01-04")], [1., 2., 3.])
    b = ([D("2024-01-02"), D("2024-01-04")], [10., 30.])
    common, out = align({"a": a, "b": b})
    assert common == [D("2024-01-02"), D("2024-01-04")]
    assert out["a"] == [1., 3.]


def _industry_zip() -> bytes:
    """A minimal 10-industry daily file with the block structure of the real one."""
    import io
    import zipfile
    inds = ["NoDur", "Durbl", "Manuf", "Enrgy", "HiTec",
            "Telcm", "Shops", "Hlth ", "Utils", "Other"]
    body = [
        "This file was created ... (preamble)",
        "",
        "  Average Value Weighted Returns -- Daily",
        "," + ",".join(inds),
    ]
    d = dt.date(2020, 1, 2)
    rng = np.random.default_rng(3)
    for _ in range(30):
        while d.weekday() >= 5:
            d += dt.timedelta(days=1)
        vals = ",".join(f"{v:7.2f}" for v in rng.normal(0, 1.0, len(inds)))
        body.append(f"{d.strftime('%Y%m%d')},{vals}")
        d += dt.timedelta(days=1)
    # A missing-data sentinel row that must be dropped, not divided by 100.
    body.append(d.strftime('%Y%m%d') + ("," + "-99.99") * len(inds))
    body.append("")
    body.append("  Average Equal Weighted Returns -- Daily")
    body.append("," + ",".join(inds))
    body.append("20200214," + ",".join(["9.99"] * len(inds)))   # must NOT be read
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("10_Industry_Portfolios_Daily.csv", "\n".join(body) + "\n")
    return buf.getvalue()


def test_parse_french_industry_reads_only_the_value_weighted_daily_block():
    dates, data = parse_french_industry(_industry_zip())
    assert list(data) == ["NoDur", "Durbl", "Manuf", "Enrgy", "HiTec",
                          "Telcm", "Shops", "Hlth", "Utils", "Other"]
    assert len(dates) == 30                     # sentinel row dropped, EW block ignored
    assert all(len(v) == 30 for v in data.values())
    assert abs(data["NoDur"][0]) < 0.2          # percent has been divided by 100


def test_load_market_prefers_cached_industry_returns(tmp_path):
    f = datakit.Fetcher(tmp_path)
    (f.raw / "french").mkdir(parents=True)
    raw = _industry_zip()
    dest = "french/10_industry_daily.zip"
    (f.raw / dest).write_bytes(raw)
    man = f.load_manifest()
    man["files"][dest] = {
        "source": "FF 10 industry", "url": "https://example/10ind.zip",
        "publisher": "French", "terms": "research",
        "sha256": datakit.sha256_file(f.raw / dest), "bytes": len(raw),
        "retrieved_utc": datakit.utc_now()}
    f._write_manifest(man)

    from data.load import load_market
    market, meta = load_market(root=tmp_path, min_days=20)
    assert meta["n_tickers"] == 10
    assert market.tickers[0] == "NoDur"
    assert meta["benchmark"].startswith("equal-weighted average")   # no factor file
    assert len(meta["betas"]) == 10


def test_load_market_refuses_when_nothing_is_cached(tmp_path):
    """--real must never fall back to the simulated tape."""
    from data.load import load_market
    with pytest.raises(datakit.FetchError, match="no real price data cached"):
        load_market(root=tmp_path)


def _seed(tmp_path, n=600, seed=11):
    """Write Stooq-shaped CSVs with a shared factor and asset-specific betas."""
    rng = np.random.default_rng(seed)
    f = datakit.Fetcher(tmp_path)
    man = f.load_manifest()
    factor = rng.normal(0, 0.010, n)
    spec = {"spy.us": 1.00, "iwm.us": 1.25, "agg.us": 0.05, "gld.us": 0.00}
    (f.raw / "stooq").mkdir(parents=True, exist_ok=True)
    for sym, beta in spec.items():
        r = beta * factor + rng.normal(0, 0.004, n)
        px, p = [], 100.0
        for x in r:
            p *= (1 + x)
            px.append(p)
        d, lines = dt.date(2022, 1, 3), ["Date,Open,High,Low,Close,Volume"]
        for v in px:
            while d.weekday() >= 5:
                d += dt.timedelta(days=1)
            lines.append(f"{d.isoformat()},{v:.4f},{v:.4f},{v:.4f},{v:.4f},1000")
            d += dt.timedelta(days=1)
        raw = ("\n".join(lines) + "\n").encode()
        dest = f"stooq/{sym}.csv"
        (f.raw / dest).write_bytes(raw)
        man["files"][dest] = {
            "source": f"Stooq {sym}", "url": f"https://stooq.com/q/d/l/?s={sym}",
            "publisher": "Stooq", "terms": "free for research",
            "sha256": datakit.sha256_file(f.raw / dest), "bytes": len(raw),
            "retrieved_utc": datakit.utc_now()}
    f._write_manifest(man)
    return f, spec


def test_betas_are_estimated_not_assumed(tmp_path):
    """The synthetic market is told each beta; real data has to regress for it.

    The estimates come back systematically BELOW the loadings used to generate
    the data, and that is correct rather than a bug. SPY is not the factor; it
    is the factor plus its own idiosyncratic noise. Regressing on a noisy proxy
    attenuates every slope toward zero by var(factor)/var(benchmark) -- the
    errors-in-variables result. With var(factor)=0.010^2 and specific risk
    0.004^2 that ratio is about 0.86, so a generating loading of 1.25 should be
    recovered near 1.08, not 1.25.

    This matters outside the test: betas measured against a real index are
    attenuated the same way, so a beta reported from this pipeline is a beta to
    the ETF, not to the latent market factor.
    """
    _seed(tmp_path)
    from data.load import load_market
    _, meta = load_market(root=tmp_path)
    b = meta["betas"]

    attenuation = 0.010 ** 2 / (0.010 ** 2 + 0.004 ** 2)
    assert attenuation == pytest.approx(0.862, abs=0.001)

    assert b["spy.us"] == pytest.approx(1.0, abs=1e-9)   # beta to itself, exactly
    assert b["iwm.us"] == pytest.approx(1.25 * attenuation, abs=0.06)
    assert b["agg.us"] == pytest.approx(0.05 * attenuation, abs=0.05)
    # Gold's near-zero beta is the right answer, not a failed estimate.
    assert abs(b["gld.us"]) < 0.05
    # Whatever the attenuation, the ranking must survive it.
    assert b["iwm.us"] > b["spy.us"] > b["agg.us"] > b["gld.us"] - 0.05


def test_market_carries_provenance_for_every_ticker(tmp_path):
    _seed(tmp_path)
    from data.load import load_market
    _, meta = load_market(root=tmp_path)
    ok = [p for p in meta["series"] if p["status"] == "ok"]
    assert len(ok) == 4
    assert all(len(p["sha256"]) == 16 and p["url"].startswith("http") for p in ok)


def test_short_history_is_refused_rather_than_silently_used(tmp_path):
    """A 99th-percentile VaR from 60 days is fitted to a handful of points."""
    _seed(tmp_path, n=60)
    from data.load import load_market
    with pytest.raises(datakit.FetchError, match="overlapping trading days"):
        load_market(root=tmp_path, min_days=500)


def test_risk_report_runs_end_to_end_on_the_real_tape(tmp_path):
    _seed(tmp_path)
    from data.load import load_market
    from src.service import handle
    market, meta = load_market(root=tmp_path)

    n = len(market.tickers)
    out = handle({"portfolio_id": "EW", "as_of": meta["last_date"],
                  "tickers": market.tickers, "weights": [1 / n] * n}, market)
    assert out["ok"], out
    rep = out["report"]
    assert rep["observations"] == meta["n_days"]
    for k in ("var_historical", "var_gaussian", "var_cornish_fisher",
              "expected_shortfall", "max_drawdown", "annualised_volatility"):
        assert np.isfinite(rep["risk"][k]), k
    # Expected shortfall is an average of the losses beyond VaR, so it cannot
    # be smaller than VaR itself.
    assert rep["risk"]["expected_shortfall"] >= rep["risk"]["var_historical"]
    # Euler contributions decompose total risk and must therefore sum to it.
    assert sum(c["risk_share"] for c in rep["contributions"]) == pytest.approx(1.0, abs=1e-6)


def test_misaligned_portfolio_is_rejected_on_real_data(tmp_path):
    """The dangerous failure is a report that describes a different portfolio."""
    _seed(tmp_path)
    from data.load import load_market
    from src.service import handle
    market, meta = load_market(root=tmp_path)
    out = handle({"portfolio_id": "BAD", "as_of": meta["last_date"],
                  "tickers": ["spy.us", "NOTLISTED"], "weights": [0.5, 0.5]}, market)
    assert not out["ok"]
    assert "NOTLISTED" in (out.get("detail", "") + out.get("error", ""))
