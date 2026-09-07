"""The service layer: portfolios in, a risk report out.

Written as a plain callable API rather than a web framework so it has no
dependencies and can be tested directly. `handle()` takes and returns JSON-shaped
dicts, so putting FastAPI or Flask in front of it is a thin adapter and not a
rewrite.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import numpy as np

from . import risk


class ValidationError(ValueError):
    pass


@dataclass
class Portfolio:
    portfolio_id: str
    tickers: list
    weights: np.ndarray
    as_of: str = ""

    def validate(self) -> None:
        if len(self.tickers) != len(self.weights):
            raise ValidationError("tickers and weights have different lengths")
        if len(self.tickers) == 0:
            raise ValidationError("portfolio is empty")
        if len(set(self.tickers)) != len(self.tickers):
            raise ValidationError("duplicate tickers")
        if not np.all(np.isfinite(self.weights)):
            raise ValidationError("weights contain NaN or inf")
        s = float(np.sum(self.weights))
        if abs(s - 1.0) > 1e-6:
            raise ValidationError(f"weights sum to {s:.6f}, not 1.0")


@dataclass
class MarketData:
    tickers: list
    returns: np.ndarray          # T x N
    betas: np.ndarray = field(default_factory=lambda: np.array([]))

    def align(self, portfolio: Portfolio):
        """Reorder market data to the portfolio, failing on anything missing.

        Silent misalignment is the defect that makes a risk system dangerous
        rather than merely wrong: the numbers still come out, they just describe
        a different portfolio.
        """
        missing = [t for t in portfolio.tickers if t not in self.tickers]
        if missing:
            raise ValidationError(f"no market data for {missing}")
        idx = [self.tickers.index(t) for t in portfolio.tickers]
        betas = self.betas[idx] if len(self.betas) else np.ones(len(idx))
        return self.returns[:, idx], betas


def risk_report(portfolio: Portfolio, market: MarketData,
                alpha: float = 0.95) -> dict:
    portfolio.validate()
    R, betas = market.align(portfolio)
    w = portfolio.weights
    pr = risk.portfolio_returns(w, R)
    cov = np.cov(R, rowvar=False)
    rc = risk.risk_contributions(w, cov)
    total_vol = float(np.sqrt(max(1e-30, w @ cov @ w)))

    t0 = time.perf_counter()
    report = {
        "portfolio_id": portfolio.portfolio_id,
        "as_of": portfolio.as_of,
        "n_positions": len(portfolio.tickers),
        "observations": int(R.shape[0]),
        "alpha": alpha,
        "risk": {
            "annualised_volatility": round(risk.volatility(pr), 6),
            "var_historical": round(risk.historical_var(pr, alpha), 6),
            "var_gaussian": round(risk.gaussian_var(pr, alpha), 6),
            "var_cornish_fisher": round(risk.cornish_fisher_var(pr, alpha), 6),
            "expected_shortfall": round(risk.expected_shortfall(pr, alpha), 6),
            "max_drawdown": round(risk.max_drawdown(pr), 6),
        },
        "concentration": risk.concentration(w),
        "contributions": [
            {"ticker": t, "weight": round(float(wi), 5),
             "risk_contribution": round(float(c), 8),
             "risk_share": round(float(c / total_vol), 5) if total_vol else 0.0}
            for t, wi, c in sorted(zip(portfolio.tickers, w, rc),
                                   key=lambda x: -abs(x[2]))
        ],
        "stress": {
            "factor_shock_-10pct": round(
                risk.stress_scenario(w, betas, -0.10), 6),
            "factor_shock_-20pct": round(
                risk.stress_scenario(w, betas, -0.20), 6),
            "worst_20d_realised": risk.worst_historical_window(pr, 20),
        },
    }
    report["latency_ms"] = round((time.perf_counter() - t0) * 1000, 3)
    report["checks"] = _checks(report, total_vol)
    return report


def _checks(report: dict, total_vol: float) -> list:
    """Findings a risk system should surface without being asked."""
    out = []
    c = report["concentration"]
    n = report["n_positions"]
    # Concentration is relative to how many positions are held, not absolute.
    # An absolute floor of five effective positions marks a perfectly
    # equal-weighted four-name portfolio as concentrated, which is not a finding
    # about the portfolio -- it is the check failing to know its own units.
    diversification = c["effective_positions"] / n if n else 1.0
    if diversification < 0.55:
        out.append({"level": "warn", "code": "concentrated",
                    "detail": f"{c['effective_positions']:.1f} effective positions "
                              f"across {n} holdings "
                              f"({diversification:.0%} of equal weighting)"})
    top = report["contributions"][0]
    if top["risk_share"] > 0.40:
        out.append({"level": "warn", "code": "risk_concentration",
                    "detail": f"{top['ticker']} is {top['risk_share']:.0%} of risk "
                              f"on {top['weight']:.0%} of capital"})
    # The ratio matters more than the level. A position can pass an absolute
    # risk-share limit while carrying twice its weight in risk, and that is the
    # case a capital-based limit is structurally unable to see.
    for c in report["contributions"]:
        if c["weight"] > 0.02 and c["risk_share"] / c["weight"] > 1.4:
            out.append({"level": "warn", "code": "risk_capital_mismatch",
                        "detail": f"{c['ticker']} carries "
                                  f"{c['risk_share'] / c['weight']:.2f}x its capital "
                                  f"share in risk ({c['risk_share']:.0%} of risk on "
                                  f"{c['weight']:.0%} of capital)"})
            break
    r = report["risk"]
    gap = r["var_cornish_fisher"] - r["var_gaussian"]
    if r["var_gaussian"] > 0 and gap / r["var_gaussian"] > 0.05:
        out.append({"level": "info", "code": "non_normal_tail",
                    "detail": f"Cornish-Fisher VaR exceeds Gaussian by "
                              f"{gap / r['var_gaussian']:.0%}; the tail is fatter "
                              f"than normal"})
    if report["observations"] < 250:
        out.append({"level": "warn", "code": "short_history",
                    "detail": f"{report['observations']} observations is too few "
                              f"for a stable 95% historical VaR"})
    return out


def handle(request: dict, market: MarketData) -> dict:
    """JSON in, JSON out. The whole service surface."""
    try:
        p = Portfolio(
            portfolio_id=request.get("portfolio_id", "unnamed"),
            tickers=list(request["tickers"]),
            weights=np.asarray(request["weights"], float),
            as_of=request.get("as_of", ""))
        return {"ok": True, "report": risk_report(p, market,
                                                  request.get("alpha", 0.95))}
    except (ValidationError, KeyError, TypeError, ValueError) as exc:
        return {"ok": False, "error": type(exc).__name__, "detail": str(exc)}
