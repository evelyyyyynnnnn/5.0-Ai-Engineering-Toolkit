"""Pull the real return series the risk engine reports on.

    python -m data.fetch --list
    python -m data.fetch
    python -m data.fetch --verify

The Fama-French 10-industry daily portfolios (Kenneth R. French Data Library)
are the constituents: ten value-weighted US industry return series -- NoDur,
Durbl, Manuf, Enrgy, HiTec, Telcm, Shops, Hlth, Utils, Other. Breadth is the
point: a risk report over ten names that all track the S&P shows one number
three times, and the Euler risk decomposition -- which exists to show WHERE
risk comes from -- has nothing to say. Ten distinct industries do.

The file is a single reproducible download that anyone can re-pull without an
account, which is why it is chosen over a per-ticker vendor feed. Real returns
also make the VaR comparison meaningful in a way simulation struggles to:
historical, Gaussian and Cornish-Fisher VaR agree on Gaussian data and diverge
on real returns precisely because industry returns are skewed and fat-tailed,
which is the finding the report is built to surface. The daily research factors
are pulled alongside so betas can be estimated against the real market factor.
"""
from __future__ import annotations

import pathlib
import sys

from .datakit import Fetcher, FetchError, NetworkBlocked
from .marketdata import french_industry_source, french_source, fred_source

ROOT = pathlib.Path(__file__).resolve().parent

SOURCES = [
    french_industry_source(),
    french_source(),   # Mkt-RF, SMB, HML and RF -- the market factor for betas
    fred_source("DGS3MO", "3-month Treasury, a real risk-free reference series"),
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
        print(f"\n{len(SOURCES)} files")
        return 0
    if args.verify:
        problems = f.verify()
        for p in problems:
            print("  " + p)
        print("VERIFICATION FAILED" if problems else
              f"all {len(f.load_manifest()['files'])} cached file(s) verified")
        return 1 if problems else 0

    print(f"fetching {len(SOURCES)} series")
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
