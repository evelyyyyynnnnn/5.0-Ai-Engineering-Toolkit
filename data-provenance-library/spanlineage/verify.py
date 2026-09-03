"""Checking that a tracked value still describes its sources."""

from __future__ import annotations


class VerificationError(Exception):
    pass


def verify_against(value, sources: dict, expected_text: dict | None = None) -> dict:
    """Do this value's spans still point at the text they claim?

    Two failure modes, reported separately because they mean different things.
    A changed document hash means the source moved underneath the record. An
    out-of-bounds or mismatched span means the record itself is wrong.
    """
    problems, checked = [], 0
    for sp in value.spans:
        src = sources.get(sp.doc_id)
        if src is None:
            problems.append({"span": sp.as_dict(), "issue": "source not supplied"})
            continue
        checked += 1
        if sp.doc_sha and sp.doc_sha != src.sha:
            problems.append({"span": sp.as_dict(), "issue": "document has changed",
                             "recorded_sha": sp.doc_sha, "current_sha": src.sha})
            continue
        if not (0 <= sp.start < sp.end <= len(src.text)):
            problems.append({"span": sp.as_dict(), "issue": "span out of bounds"})
            continue
        if expected_text and sp in expected_text:
            actual = src.slice(sp.start, sp.end)
            if actual != expected_text[sp]:
                problems.append({"span": sp.as_dict(), "issue": "text mismatch",
                                 "expected": expected_text[sp], "actual": actual})
    return {"ok": not problems, "n_spans": len(value.spans),
            "n_checked": checked, "problems": problems}
