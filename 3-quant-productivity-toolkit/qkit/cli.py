"""qkit command line: audit a returns/feature CSV before you trust a backtest."""

from __future__ import annotations

import argparse
import csv
import json
import sys

import numpy as np

from .lookahead import detect_lookahead
from .statistics import deflated_sharpe, min_track_record_length, sharpe


def _load(path, cols):
    with open(path, newline="", encoding="utf8") as fh:
        rows = list(csv.DictReader(fh))
    return {c: np.array([float(r[c]) for r in rows]) for c in cols}


def cmd_lookahead(args) -> int:
    data = _load(args.csv, [args.target] + args.features)
    y = data[args.target]
    out = [detect_lookahead(data[f], y, f, threshold=args.threshold).as_dict()
           for f in args.features]
    json.dump({"findings": out,
               "n_contaminated": sum(o["contaminated"] for o in out)},
              sys.stdout, indent=2)
    print()
    return 1 if any(o["contaminated"] for o in out) else 0


def cmd_sharpe(args) -> int:
    r = _load(args.csv, [args.column])[args.column]
    out = {"sharpe": round(sharpe(r, args.periods), 4),
           "deflated": deflated_sharpe(r, args.trials, args.periods),
           "min_track_record_length": round(
               min_track_record_length(r, periods_per_year=args.periods), 1)}
    json.dump(out, sys.stdout, indent=2)
    print()
    return 0 if out["deflated"]["survives"] else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="qkit", description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("lookahead", help="flag features that see the future")
    a.add_argument("csv")
    a.add_argument("--target", required=True)
    a.add_argument("--features", nargs="+", required=True)
    a.add_argument("--threshold", type=float, default=0.50)
    a.set_defaults(fn=cmd_lookahead)

    b = sub.add_parser("sharpe", help="Sharpe, deflated for the number of trials")
    b.add_argument("csv")
    b.add_argument("--column", default="returns")
    b.add_argument("--trials", type=int, default=1)
    b.add_argument("--periods", type=int, default=252)
    b.set_defaults(fn=cmd_sharpe)

    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
