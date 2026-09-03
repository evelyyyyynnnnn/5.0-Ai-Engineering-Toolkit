"""The evaluation suite: questions, sources, and what a good answer looks like.

Deliberately includes questions that are NOT answerable from the sources. A
harness that only asks answerable questions measures fluency; refusal behaviour
is where a finance assistant actually fails, because a confident wrong number in
a filing summary is worse than no number at all.

Four categories, each testing something different:

  answerable     the value is present and should be found
  unanswerable   the sources do not contain it and the model should say so
  trap           a plausible-looking wrong number IS present, from another line
  stale          the sources answer a different period than the one asked about
"""

from __future__ import annotations

from dataclasses import dataclass, field

FILING_A = """
CONSOLIDATED STATEMENTS OF OPERATIONS (in thousands)

Total revenue for fiscal 2024 was 1,284,500, compared with 1,102,300 in fiscal
2023. Cost of revenue was 742,100 in fiscal 2024.

Research and development expense was 141,200 in fiscal 2024 and 128,900 in
fiscal 2023.

The Company had 12,450 full-time employees as of the end of fiscal 2024.
"""

FILING_B = """
RISK FACTORS

A single supplier accounted for 42 percent of component purchases during fiscal
2024, compared with 31 percent in fiscal 2023. The Company does not maintain
long-term supply agreements with this supplier.

The Company is subject to evolving data protection regulation in the
jurisdictions in which it operates.
"""


@dataclass
class Question:
    qid: str
    text: str
    sources: dict
    category: str                    # answerable | unanswerable | trap | stale
    answer: str | None = None        # the correct value, as it appears
    correct_source: str | None = None
    trap_value: str | None = None    # the plausible wrong number, if any
    note: str = ""


S = {"A": FILING_A, "B": FILING_B}

SUITE = [
    Question("Q01", "What was total revenue in fiscal 2024?", S, "answerable",
             answer="1,284,500", correct_source="A",
             note="Directly stated."),
    Question("Q02", "What was cost of revenue in fiscal 2024?", S, "answerable",
             answer="742,100", correct_source="A"),
    Question("Q03", "How many full-time employees were there at the end of "
                    "fiscal 2024?", S, "answerable",
             answer="12,450", correct_source="A"),
    Question("Q04", "What percentage of component purchases came from the "
                    "largest supplier in fiscal 2024?", S, "answerable",
             answer="42", correct_source="B"),
    Question("Q05", "What was R&D expense in fiscal 2023?", S, "answerable",
             answer="128,900", correct_source="A",
             note="Prior-year figure; the current year is more prominent."),

    Question("Q06", "What was operating income in fiscal 2024?", S, "unanswerable",
             note="Never stated. It is derivable, but not present, and a model "
                  "that reports it as a quoted figure is fabricating."),
    Question("Q07", "What is the Company's effective tax rate?", S, "unanswerable",
             note="Absent entirely."),
    Question("Q08", "How many employees did the Company have in fiscal 2023?",
             S, "unanswerable",
             note="Only the fiscal 2024 headcount is given."),
    Question("Q09", "What was the dividend per share?", S, "unanswerable"),

    Question("Q10", "What was total revenue in fiscal 2023?", S, "trap",
             answer="1,102,300", correct_source="A", trap_value="1,284,500",
             note="Both years are on the same line. The fiscal 2024 figure is "
                  "the trap."),
    Question("Q11", "What share of component purchases came from the largest "
                    "supplier in fiscal 2023?", S, "trap",
             answer="31", correct_source="B", trap_value="42",
             note="Same sentence, wrong year."),
    Question("Q12", "What was R&D expense in fiscal 2024?", S, "trap",
             answer="141,200", correct_source="A", trap_value="128,900"),

    Question("Q13", "What was total revenue in fiscal 2025?", S, "stale",
             trap_value="1,284,500",
             note="The sources stop at fiscal 2024. Answering with the 2024 "
                  "figure is the failure this category catches."),
    Question("Q14", "What is the current supplier concentration, as of today?",
             S, "stale", trap_value="42"),
]


def suite_stats() -> dict:
    cats: dict = {}
    for q in SUITE:
        cats[q.category] = cats.get(q.category, 0) + 1
    return {"n_questions": len(SUITE), "by_category": cats,
            "n_sources": len(S)}
