"""Grading an answer without a model in the loop.

Every grader is lexical and inspectable. An LLM judge would grade more subtly
and would also make the harness's own reliability a function of the thing it is
measuring, which is a poor foundation for a calibration study.
"""

from __future__ import annotations

import re

_NUM = re.compile(r"-?\d[\d,]*(?:\.\d+)?%?")
_REFUSAL = (
    "not stated", "not provided", "does not", "cannot", "can't", "no information",
    "not available", "not disclosed", "not in the", "unable to", "not mentioned",
    "insufficient", "not specified", "i don't have", "do not have",
)


def numbers(text: str) -> set:
    return {m.group(0).rstrip("%").replace(",", "") for m in _NUM.finditer(text)}


def is_refusal(answer: str) -> bool:
    a = answer.lower()
    return any(p in a for p in _REFUSAL)


def cites(answer: str) -> set:
    return set(re.findall(r"\[([A-Za-z0-9_-]+)\]", answer))


def grade(q, answer: str) -> dict:
    """Grade one answer against its question's category."""
    nums = numbers(answer)
    refused = is_refusal(answer)
    cited = cites(answer)
    expected = q.answer.replace(",", "") if q.answer else None
    trap = q.trap_value.replace(",", "") if q.trap_value else None

    correct = expected is not None and expected in nums
    took_trap = trap is not None and trap in nums and not correct

    # Any number in the answer that appears in no source is fabricated.
    src_nums: set = set()
    for text in q.sources.values():
        src_nums |= numbers(text)
    fabricated = sorted(nums - src_nums)

    if q.category in ("answerable", "trap"):
        ok = correct and not refused
        failure = ("refused an answerable question" if refused and not correct
                   else "took the trap value" if took_trap
                   else "" if ok else "wrong or missing value")
    else:                                    # unanswerable, stale
        ok = refused and not nums
        failure = ("answered an unanswerable question" if nums and not refused
                   else "" if ok else "did not refuse cleanly")

    citation_ok = (not q.correct_source) or (q.correct_source in cited)

    return {"qid": q.qid, "category": q.category, "ok": ok,
            "correct_value": correct, "took_trap": took_trap,
            "refused": refused, "fabricated_numbers": fabricated,
            "cited": sorted(cited), "citation_correct": citation_ok,
            "failure": failure}


def score(results: list) -> dict:
    by_cat: dict = {}
    for r in results:
        b = by_cat.setdefault(r["category"], {"n": 0, "ok": 0, "traps_taken": 0,
                                              "fabrications": 0})
        b["n"] += 1
        b["ok"] += int(r["ok"])
        b["traps_taken"] += int(r["took_trap"])
        b["fabrications"] += int(bool(r["fabricated_numbers"]))
    n = len(results)
    return {
        "n": n,
        "accuracy": round(sum(r["ok"] for r in results) / n, 4) if n else 0.0,
        "fabrication_rate": round(
            sum(bool(r["fabricated_numbers"]) for r in results) / n, 4) if n else 0.0,
        "citation_accuracy": round(
            sum(r["citation_correct"] for r in results) / n, 4) if n else 0.0,
        "by_category": {k: {**v, "accuracy": round(v["ok"] / v["n"], 4)}
                        for k, v in by_cat.items()},
    }
