"""Stand-in answerers with deliberately different failure modes.

None of these is a language model. They exist so the harness itself can be
validated: a grader that cannot tell a careful answerer from a reckless one is
not measuring anything, and that has to be demonstrated before any real model is
run through it.

Each stand-in embodies one failure pattern seen in real finance assistants.
"""

from __future__ import annotations

import re


class CarefulAnswerer:
    """Reads the year in the question, refuses when the value is absent."""

    name = "careful"

    def __call__(self, q) -> str:
        year = _year(q.text)
        val, src = _lookup(q, year)
        if val is None:
            return "That figure is not stated in the provided documents."
        return f"{val} [{src}]"


class EagerAnswerer:
    """Never refuses. Returns the most prominent number it can find.

    The dominant real-world failure: fluency rewarded over abstention.
    """

    name = "eager"

    def __call__(self, q) -> str:
        year = _year(q.text)
        val, src = _lookup(q, year)
        if val is not None:
            return f"{val} [{src}]"
        any_val, any_src = _first_number(q)
        return f"{any_val} [{any_src}]"


class YearBlindAnswerer:
    """Finds the right metric and ignores which period was asked about."""

    name = "year-blind"

    def __call__(self, q) -> str:
        val, src = _lookup(q, year=2024)          # always the latest
        if val is None:
            return "Not stated in the documents."
        return f"{val} [{src}]"


class OverRefuser:
    """Refuses almost everything. Safe, and useless."""

    name = "over-refuser"

    def __call__(self, q) -> str:
        return "I cannot determine that from the provided documents."


class UncitedAnswerer:
    """Correct values, no citations. Tests the citation axis independently."""

    name = "uncited"

    def __call__(self, q) -> str:
        year = _year(q.text)
        val, _ = _lookup(q, year)
        return f"{val}" if val else "Not stated in the documents."


# --- shared lookup over the authored sources -----------------------------

_TABLE = {
    ("revenue", 2024): ("1,284,500", "A"),
    ("revenue", 2023): ("1,102,300", "A"),
    ("cost of revenue", 2024): ("742,100", "A"),
    ("research", 2024): ("141,200", "A"),
    ("research", 2023): ("128,900", "A"),
    ("employees", 2024): ("12,450", "A"),
    ("supplier", 2024): ("42", "B"),
    ("supplier", 2023): ("31", "B"),
}


def _year(text: str):
    m = re.search(r"(?:fiscal|FY)\s*(\d{4})", text, re.I)
    return int(m.group(1)) if m else None


def _metric(text: str):
    t = text.lower()
    if "cost of revenue" in t:
        return "cost of revenue"
    if "revenue" in t:
        return "revenue"
    if "r&d" in t or "research" in t:
        return "research"
    if "employee" in t:
        return "employees"
    if "supplier" in t or "component purchases" in t:
        return "supplier"
    return None


def _lookup(q, year):
    metric = _metric(q.text)
    if metric is None or year is None:
        return None, None
    return _TABLE.get((metric, year), (None, None))


def _first_number(q):
    for name, text in q.sources.items():
        m = re.search(r"([\d,]{4,})", text)
        if m:
            return m.group(1), name
    return "0", "A"


ANSWERERS = [CarefulAnswerer(), EagerAnswerer(), YearBlindAnswerer(),
             OverRefuser(), UncitedAnswerer()]
