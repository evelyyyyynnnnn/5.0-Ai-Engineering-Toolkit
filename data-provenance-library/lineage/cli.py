"""lineage command line: extract with provenance, or verify a record."""

from __future__ import annotations

import argparse
import json
import sys

from .core import Source, extract
from .graph import explain, to_dot
from .verify import verify_against


def cmd_extract(args) -> int:
    text = open(args.file, encoding="utf8").read()
    src = Source(args.doc_id or args.file, text)
    val = extract(src, args.pattern, cast=float)
    if val is None:
        print(f"no match for {args.pattern!r}", file=sys.stderr)
        return 1
    out = {"value": val.value, "doc_sha": src.sha,
           "spans": [s.as_dict() for s in val.spans],
           "evidence": [e["text"] for e in val.evidence({src.doc_id: src})]}
    json.dump(out, sys.stdout, indent=2)
    print()
    return 0


def cmd_verify(args) -> int:
    text = open(args.file, encoding="utf8").read()
    src = Source(args.doc_id or args.file, text)
    rec = json.load(open(args.record, encoding="utf8"))
    from .core import Span, Tracked
    spans = tuple(Span(**s) for s in rec["spans"])
    val = Tracked(value=rec["value"], spans=spans)
    out = verify_against(val, {src.doc_id: src})
    json.dump(out, sys.stdout, indent=2)
    print()
    return 0 if out["ok"] else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="lineage", description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    e = sub.add_parser("extract", help="extract a number and record its span")
    e.add_argument("file")
    e.add_argument("pattern")
    e.add_argument("--doc-id", default=None)
    e.set_defaults(fn=cmd_extract)

    v = sub.add_parser("verify", help="check a record against a document")
    v.add_argument("file")
    v.add_argument("record")
    v.add_argument("--doc-id", default=None)
    v.set_defaults(fn=cmd_verify)

    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
