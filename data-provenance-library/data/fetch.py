"""Pull real reported financials from SEC EDGAR's XBRL company-concept API.

    python -m data.fetch --list
    DATAKIT_UA="Your Name you@email" python -m data.fetch
    python -m data.fetch --verify

Why the XBRL API rather than the filing prose: this library's claim is that a
derived number keeps the characters it came from. That claim is only worth
testing against numbers someone will actually check, and a figure pulled from
a company's own tagged submission is exactly that -- it carries the accession
number of the filing it was reported in, the fiscal period it covers, and the
form it appeared on.

The JSON response is itself the source document here, and the spans point at
byte ranges inside it. That is not a workaround: the file is what the SEC
published, its hash pins it, and a value's span can be re-read from it and
checked. Provenance into a structured document is still provenance.

SEC requires a User-Agent naming a real contact; set DATAKIT_UA or the
requests are refused with a 403.
"""
from __future__ import annotations

import pathlib
import sys

from .datakit import Fetcher, FetchError, NetworkBlocked, Source
from .edgar_api import TICKERS, cik_for_ticker

ROOT = pathlib.Path(__file__).resolve().parent

CONCEPT = ("https://data.sec.gov/api/xbrl/companyconcept/"
           "CIK{cik10}/us-gaap/{tag}.json")

COMPANIES = ["AAPL", "MSFT", "KO"]

# The tags a margin calculation needs. Registrants do not all use the same
# ones -- the revenue tag in particular changed with ASC 606 -- so several
# candidates are fetched and whichever is present is used.
TAGS = [
    "RevenueFromContractWithCustomerExcludingAssessedTax",
    "Revenues",
    "CostOfGoodsAndServicesSold",
    "CostOfRevenue",
    "OperatingIncomeLoss",
    "ResearchAndDevelopmentExpense",
    "OperatingExpenses",
]

INDEX = Source(name="EDGAR ticker-to-CIK map", url=TICKERS,
               dest="company_tickers.json", publisher="U.S. SEC (EDGAR)",
               terms="U.S. government work, public domain")


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args(argv)
    f = Fetcher(ROOT)

    if args.list:
        print(f"{INDEX.name}\n  {INDEX.url}\n")
        print(f"then, for each of {', '.join(COMPANIES)}, these us-gaap tags:")
        for tag in TAGS:
            print(f"  {tag}")
        print(f"\n{CONCEPT.format(cik10='<CIK>', tag='<TAG>')}")
        print(f"\n{1 + len(COMPANIES) * len(TAGS)} requests; a tag a registrant "
              f"does not report answers 404 and is skipped")
        return 0
    if args.verify:
        problems = f.verify()
        for p in problems:
            print("  " + p)
        print("VERIFICATION FAILED" if problems else
              f"all {len(f.load_manifest()['files'])} cached file(s) verified")
        return 1 if problems else 0

    try:
        tickers_json = f.get(INDEX, refresh=args.refresh).read_bytes()
        got = 0
        for tic in COMPANIES:
            cik10 = cik_for_ticker(tickers_json, tic)
            print(f"\n{tic} (CIK {cik10})")
            for tag in TAGS:
                src = Source(
                    name=f"{tic} {tag}",
                    url=CONCEPT.format(cik10=cik10, tag=tag),
                    dest=f"xbrl/{tic.lower()}/{tag}.json",
                    publisher="U.S. SEC (EDGAR XBRL frames API)",
                    terms="U.S. government work, public domain",
                    note=f"every {tag} value {tic} has reported, with the "
                         f"accession number and period of each",
                )
                try:
                    p = f.get(src, refresh=args.refresh)
                    print(f"  {tag:<52} {p.stat().st_size:>9,} bytes")
                    got += 1
                except FetchError as exc:
                    # A registrant that does not use a tag returns 404. That is
                    # information, not a failure.
                    print(f"  {tag:<52} not reported")
    except NetworkBlocked as e:
        print(f"\nBLOCKED: {e}", file=sys.stderr)
        return 2
    except FetchError as e:
        print(f"\nFAILED: {e}", file=sys.stderr)
        return 1

    if not got:
        print("\nno concepts retrieved", file=sys.stderr)
        return 1
    print(f"\nwrote {f.manifest_path} ({got} concept files)")
    print("run `python -m src.demo --real` to derive metrics with provenance")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
