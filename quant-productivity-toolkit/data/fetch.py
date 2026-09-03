"""Pull the real return series these four checks are run against.

    python -m data.fetch --list
    python -m data.fetch
    python -m data.fetch --verify

Two sources, for two different reasons.

Fama-French daily factors are the canonical research series: decades of daily
market, size and value returns plus the risk-free rate, published by the people
whose papers defined the benchmarks. If a backtest check misbehaves on this
series it misbehaves on the series everyone uses.

Stooq gives individual ETF histories, which is what the strategy sweep needs --
the multiple-testing demonstration is only convincing when the strategies are
tried on something someone might actually have traded.

One of the four checks does NOT become real, and the reason is worth stating.
A survivorship audit needs the returns of the names that DIED, and no free
source publishes point-in-time index membership with delisted constituents.
Stooq serves surviving tickers; a ticker that returns no data has not
necessarily been delisted, it may simply be missing, and treating a fetch
failure as a delisting would manufacture the very bias the check exists to
measure. CRSP has this data and is not free. The check runs on constructed data
and says so.
"""
from __future__ import annotations

import pathlib
import sys
from datetime import date, timedelta

from .datakit import Fetcher, FetchError, NetworkBlocked
from .marketdata import french_source, stooq_source

ROOT = pathlib.Path(__file__).resolve().parent

END = date.today()
START = END - timedelta(days=15 * 365)

TICKERS = [
    ("spy.us", "US large-cap equity -- the strategy sweep runs on this"),
    ("qqq.us", "technology-heavy, a different volatility regime"),
    ("tlt.us", "long duration, so the sweep is not all one asset class"),
]

SOURCES = [french_source()] + [
    stooq_source(s, START.isoformat(), END.isoformat(), why)
    for s, why in TICKERS
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
            print(f"{s.name}\n  {s.url}\n  {s.note}")
        print(f"\n{len(SOURCES)} files, {START} .. {END}")
        print("the survivorship check stays on constructed data: no free source "
              "publishes delisted constituents")
        return 0
    if args.verify:
        problems = f.verify()
        for p in problems:
            print("  " + p)
        print("VERIFICATION FAILED" if problems else
              f"all {len(f.load_manifest()['files'])} cached file(s) verified")
        return 1 if problems else 0

    print(f"fetching {len(SOURCES)} series ...")
    try:
        f.get_all(SOURCES, refresh=args.refresh)
    except NetworkBlocked as e:
        print(f"\nBLOCKED: {e}", file=sys.stderr)
        return 2
    except FetchError as e:
        print(f"\nFAILED: {e}", file=sys.stderr)
        return 1
    print(f"\nwrote {f.manifest_path}")
    print("run `python -m src.demo --real` to run the checks on real returns")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
