"""Pull the real return series the risk engine reports on.

    python -m data.fetch --list
    python -m data.fetch
    python -m data.fetch --verify

Eight liquid, long-history ETFs spanning equity, credit, duration, commodities
and real estate. Breadth is the point: a risk report over eight names that all
track the S&P shows one number three times, and the Euler risk decomposition --
which exists to show WHERE risk comes from -- has nothing to say.

Real returns also make the VaR comparison meaningful in a way simulation
struggles to. Historical, Gaussian and Cornish-Fisher VaR agree on Gaussian
data; they diverge on real data precisely because real equity returns are
skewed and fat-tailed, which is the finding the report is built to surface.
"""
from __future__ import annotations

import pathlib
import sys
from datetime import date, timedelta

from .datakit import Fetcher, FetchError, NetworkBlocked
from .marketdata import fred_source, stooq_source

ROOT = pathlib.Path(__file__).resolve().parent

END = date.today()
START = END - timedelta(days=8 * 365)     # long enough to contain a real crash

UNIVERSE = [
    ("spy.us", "US large-cap equity"),
    ("iwm.us", "US small-cap equity -- different tail behaviour from SPY"),
    ("efa.us", "developed non-US equity"),
    ("eem.us", "emerging-market equity -- the fattest tail in the basket"),
    ("agg.us", "US aggregate bonds"),
    ("tlt.us", "long duration -- the diversifier that sometimes is not one"),
    ("gld.us", "gold"),
    ("vnq.us", "US real estate"),
]

SOURCES = [stooq_source(sym, START.isoformat(), END.isoformat(), why)
           for sym, why in UNIVERSE] + [
    fred_source("DGS3MO", "3-month Treasury, the risk-free leg of the Sharpe ratio"),
]


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args(argv)
    f = Fetcher(ROOT)

    if args.list:
        for s in SOURCES:
            print(f"{s.name}\n  {s.url}\n  -> raw/{s.dest}\n  {s.note}")
        print(f"\n{len(SOURCES)} files, {START} .. {END}")
        return 0
    if args.verify:
        problems = f.verify()
        for p in problems:
            print("  " + p)
        print("VERIFICATION FAILED" if problems else
              f"all {len(f.load_manifest()['files'])} cached file(s) verified")
        return 1 if problems else 0

    print(f"fetching {len(SOURCES)} series, {START} .. {END}")
    try:
        f.get_all(SOURCES, refresh=args.refresh)
    except NetworkBlocked as e:
        print(f"\nBLOCKED: {e}", file=sys.stderr)
        return 2
    except FetchError as e:
        print(f"\nFAILED: {e}", file=sys.stderr)
        return 1
    print(f"\nwrote {f.manifest_path}")
    print("run `python -m src.demo --real` for a risk report on the real tape")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
