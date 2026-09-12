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
        years = {int(y) for t in q.sources.values()
                 for y in _YEAR_MENTION.findall(t)}
        val, src = _lookup(q, year=max(years) if years else None)
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


# --- shared lookup, read out of the documents themselves --------------------
#
# This was a hardcoded table of the authored corpus's values. That made every
# stand-in useless the moment the suite was built from filed data: the careful
# answerer, which by construction should be near-perfect on a suite generated
# FROM the documents it is shown, scored 2 of 24, because it was looking up
# figures from a different corpus and refusing everything else. A baseline that
# cannot answer the questions is not a baseline, and a comparison against one
# flatters whatever it is compared with.
#
# The lookup now reads the documents it is given, so the stand-ins behave the
# same way on any suite -- authored or filed.

_YEAR_MENTION = re.compile(r"fiscal\s+(\d{4})", re.I)
_FIGURE = re.compile(r"\d[\d,]*(?:\.\d+)?")

# Words that appear in almost any question and so distinguish nothing.
_STOP = {"what", "was", "were", "the", "a", "an", "in", "of", "for", "is", "are",
         "did", "does", "have", "has", "had", "how", "much", "many", "that",
         "this", "there", "they", "company", "companys", "fiscal", "year",
         "during", "from", "came", "end", "total", "and", "per", "its", "their",
         "at", "as", "by", "with", "s", "today", "current", "currently"}


def _year(text: str):
    m = re.search(r"(?:fiscal|FY)\s*(\d{4})", text, re.I)
    return int(m.group(1)) if m else None


def _terms(question: str) -> list:
    """The content words that name the metric being asked about."""
    body = question.split("'s ", 1)[-1]
    body = re.sub(r"\bin fiscal\s+\d{4}\b", " ", body, flags=re.I)
    words = re.findall(r"[a-z&]+", body.lower())
    return [w for w in words if w not in _STOP and len(w) > 1]


def _sentences(text: str) -> list:
    """Sentences, with the document's line wrapping removed first.

    The filings wrap mid-phrase, so "in fiscal\n2023." splits a period away from
    its year. Reading line by line attached figures to the wrong year, and did
    it silently -- the worst way for a baseline to be wrong.
    """
    flat = re.sub(r"\s+", " ", text)
    return [t.strip() for t in re.split(r"(?<=\.)\s+", flat) if t.strip()]


def _figures_by_year(sentence: str) -> dict:
    """Attach each figure in a sentence to the fiscal year mentioned nearest it.

    Both corpora state a figure beside its period, in either order:
      "Revenue for fiscal 2025 was 416,161."
      "R&D expense was 141,200 in fiscal 2024 and 128,900 in fiscal 2023."
    Nearest-mention wins, which covers both without a template per phrasing.
    """
    mentions = [(m.start(), m.end(), int(m.group(1)))
                for m in _YEAR_MENTION.finditer(sentence)]
    if not mentions:
        return {}
    out = {}
    for f in _FIGURE.finditer(sentence):
        # A year inside a "fiscal YYYY" mention is a period, not a figure.
        if any(a <= f.start() < b for a, b, _ in mentions):
            continue
        year = min(mentions, key=lambda m: abs(f.start() - m[0]))[2]
        out.setdefault(year, f.group(0))
    return out


def _lookup(q, year):
    """The figure the documents actually state for this metric and year.

    The sentence that shares the most words with the question wins. Requiring
    every word would refuse most natural questions; requiring any one of them
    would answer "cost of revenue" out of a revenue sentence.
    """
    terms = _terms(q.text)
    if year is None or not terms:
        return None, None
    best = None
    for doc_id, text in q.sources.items():
        for sentence in _sentences(text):
            low = sentence.lower()
            overlap = sum(1 for t in terms if t in low)
            if not overlap:
                continue
            got = _figures_by_year(sentence).get(year)
            if got and (best is None or overlap > best[0]):
                best = (overlap, got.rstrip(","), doc_id)
    return (best[1], best[2]) if best else (None, None)


def _first_number(q):
    for name, text in q.sources.items():
        m = re.search(r"([\d,]{4,})", text)
        if m:
            return m.group(1), name
    return "0", "A"


ANSWERERS = [CarefulAnswerer(), EagerAnswerer(), YearBlindAnswerer(),
             OverRefuser(), UncitedAnswerer()]
