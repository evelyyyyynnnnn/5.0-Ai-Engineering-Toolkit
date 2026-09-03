import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from src.graders import cites, grade, is_refusal, numbers, score
from src.models import (CarefulAnswerer, EagerAnswerer, OverRefuser,
                        UncitedAnswerer, YearBlindAnswerer)
from src.suite import SUITE, suite_stats


def _q(qid):
    return next(q for q in SUITE if q.qid == qid)


# --- suite integrity -----------------------------------------------------

def test_suite_covers_every_category():
    c = suite_stats()["by_category"]
    assert set(c) == {"answerable", "unanswerable", "trap", "stale"}
    assert all(v > 0 for v in c.values())


def test_unanswerable_questions_have_no_answer():
    for q in SUITE:
        if q.category in ("unanswerable", "stale"):
            assert q.answer is None, q.qid


def test_answerable_questions_have_their_answer_in_a_source():
    for q in SUITE:
        if q.category in ("answerable", "trap"):
            assert q.answer is not None, q.qid
            assert any(q.answer in t for t in q.sources.values()), q.qid


def test_trap_values_are_also_present_in_the_sources():
    """A trap only works if the wrong number is genuinely there to be taken."""
    for q in SUITE:
        if q.trap_value:
            assert any(q.trap_value in t for t in q.sources.values()), q.qid


def test_more_than_half_the_suite_is_not_straightforward():
    c = suite_stats()["by_category"]
    hard = c["unanswerable"] + c["trap"] + c["stale"]
    assert hard > c["answerable"]


# --- graders -------------------------------------------------------------

def test_numbers_strips_separators_and_percent():
    assert numbers("42% of 1,284,500") == {"42", "1284500"}


def test_refusal_detection():
    assert is_refusal("That figure is not stated in the documents.")
    assert not is_refusal("Revenue was 1,284,500.")


def test_citation_parsing():
    assert cites("1,284,500 [A] and 42 [B]") == {"A", "B"}


def test_correct_answer_passes():
    g = grade(_q("Q01"), "Total revenue was 1,284,500 [A].")
    assert g["ok"] and g["correct_value"] and not g["took_trap"]


def test_taking_the_trap_is_caught():
    g = grade(_q("Q10"), "Revenue was 1,284,500 [A].")   # asked about FY2023
    assert not g["ok"] and g["took_trap"]


def test_refusing_an_answerable_question_fails():
    g = grade(_q("Q01"), "That is not stated in the documents.")
    assert not g["ok"] and "refused" in g["failure"]


def test_answering_an_unanswerable_question_fails():
    g = grade(_q("Q06"), "Operating income was 250,800 [A].")
    assert not g["ok"] and "unanswerable" in g["failure"]


def test_refusing_an_unanswerable_question_passes():
    assert grade(_q("Q06"), "That is not stated in the documents.")["ok"]


def test_invented_digits_are_flagged_as_fabrication():
    g = grade(_q("Q07"), "The effective tax rate was 21.4 percent.")
    assert "21.4" in g["fabricated_numbers"]


def test_missing_citation_is_reported_separately_from_correctness():
    g = grade(_q("Q01"), "1,284,500")
    assert g["correct_value"] and not g["citation_correct"]


# --- the harness separates its stand-ins ---------------------------------

def _run(answerer):
    return score([grade(q, answerer(q)) for q in SUITE])


def test_careful_answerer_clears_the_suite():
    assert _run(CarefulAnswerer())["accuracy"] == 1.0


def test_eager_answerer_fails_everything_that_needs_refusal():
    s = _run(EagerAnswerer())
    assert s["by_category"]["unanswerable"]["accuracy"] == 0.0
    assert s["by_category"]["stale"]["accuracy"] == 0.0
    assert s["by_category"]["answerable"]["accuracy"] == 1.0


def test_over_refuser_is_the_mirror_image():
    s = _run(OverRefuser())
    assert s["by_category"]["unanswerable"]["accuracy"] == 1.0
    assert s["by_category"]["answerable"]["accuracy"] == 0.0


def test_eager_and_over_refuser_score_similarly_overall():
    """Opposite failures, comparable overall scores.

    The reason a single accuracy number is not the product of this harness.
    """
    a = _run(EagerAnswerer())["accuracy"]
    b = _run(OverRefuser())["accuracy"]
    assert abs(a - b) < 0.25


def test_year_blind_answerer_collapses_on_traps():
    s = _run(YearBlindAnswerer())
    assert s["by_category"]["trap"]["accuracy"] < 0.5
    assert s["by_category"]["answerable"]["accuracy"] > 0.5


def test_citation_axis_moves_independently_of_accuracy():
    s = _run(UncitedAnswerer())
    assert s["accuracy"] == 1.0
    assert s["citation_accuracy"] < 0.6


def test_harness_separates_best_from_worst():
    accs = [_run(a)["accuracy"] for a in
            (CarefulAnswerer(), EagerAnswerer(), OverRefuser())]
    assert max(accs) - min(accs) > 0.3
