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


# --- the real-model path, exercised without a model ---------------------------
#
# The harness had never been pointed at a language model. What makes that
# runnable is an answerer that speaks the OpenAI chat protocol; what makes it
# trustworthy is that the reply reaches the grader unaltered. Both are checked
# here with a scripted stand-in, so the wiring is known-good before anyone
# spends a CPU-hour on it.

def test_the_prompt_carries_every_source_and_the_question():
    from src.llm_answerer import render_prompt
    from src.suite import SUITE

    q = SUITE[0]
    prompt = render_prompt(q)

    for doc_id, text in q.sources.items():
        assert f"--- DOCUMENT {doc_id} ---" in prompt
        assert text.strip()[:40] in prompt
    assert q.text in prompt


def test_the_prompt_never_contains_the_expected_answer_as_a_hint():
    """The value may legitimately appear inside a source document. It must not
    appear anywhere else in the prompt -- that would be handing over the key."""
    from src.llm_answerer import render_prompt
    from src.suite import SUITE

    for q in SUITE:
        if not q.answer:
            continue
        prompt = render_prompt(q)
        after_sources = prompt.split("--- QUESTION ---")[1]
        assert q.answer not in after_sources


def test_a_scripted_reply_reaches_the_grader_verbatim():
    from src.demo import evaluate
    from src.llm_answerer import ScriptedAnswerer
    from src.suite import SUITE

    q = SUITE[0]
    scripted = ScriptedAnswerer({q.qid: f"{q.answer} [{q.correct_source}]"})
    per_model, transcripts = evaluate([q], answerers=[scripted])

    assert transcripts["scripted"][0]["answer"] == f"{q.answer} [{q.correct_source}]"
    assert per_model["scripted"]["score"]["accuracy"] == 1.0


def test_a_failed_call_is_scored_as_the_empty_answer_it_was():
    """Substituting a refusal for a network error would credit the model with
    behaviour it never produced -- on an unanswerable question, generously."""
    from src.demo import evaluate
    from src.llm_answerer import LLMAnswerer
    from src.suite import SUITE

    llm = LLMAnswerer(base_url="http://127.0.0.1:9")     # nothing listens here
    unanswerable = [q for q in SUITE if q.category == "unanswerable"][:1]
    per_model, transcripts = evaluate(unanswerable, answerers=[llm])

    assert transcripts[llm.name][0]["answer"] == ""
    assert per_model[llm.name]["score"]["accuracy"] == 0.0
    assert len(llm.calls) == 1 and llm.calls[0]["error"]


def test_the_answerer_defaults_to_a_local_ollama_endpoint():
    from src.llm_answerer import LLMAnswerer

    llm = LLMAnswerer()

    assert llm.base_url == "http://localhost:11434/v1"
    assert llm.is_language_model is True
    assert llm.name.startswith("llm:")


# --- what the first real-data run exposed ------------------------------------
#
# Pointing the harness at questions built from filed values produced a result
# that could not be true: the model scored 1.0000 accuracy and 0.9167
# fabrication at the same time, while the careful stand-in -- which by
# construction should be near-perfect on a suite generated FROM the documents
# it is shown -- scored 2 of 24. Two separate defects, both invisible on the
# authored corpus because of how its documents happen to be named and written.

def _filed_style_question(qid="R000", year=2025, category="answerable",
                          answer="416,161"):
    """A question shaped like data/load.py builds them: the document id carries
    a ticker and a year, and the text wraps mid-phrase the way a filing does."""
    from src.suite import Question

    doc = ("AAPL - selected financial data, fiscal 2025 (in millions of US\n"
           "dollars).\nRevenue for fiscal 2025 was 416,161.\nRevenue for\n"
           "fiscal 2024 was 391,035.")
    return Question(qid, "What was AAPL's revenue in fiscal %d?" % year,
                    {"AAPL-2025": doc}, category,
                    answer=answer, correct_source="AAPL-2025")


def test_a_citation_id_containing_a_year_is_not_read_as_a_fabricated_number():
    """The number regex read '-2025' out of '[AAPL-2025]' as a negative figure
    appearing in no source, so every correctly cited answer scored as a
    fabrication. The model was right; the grader was wrong."""
    from src.graders import grade

    q = _filed_style_question()
    g = grade(q, "416,161 [AAPL-2025]")

    assert g["ok"] is True
    assert g["fabricated_numbers"] == [], g["fabricated_numbers"]
    assert g["citation_correct"] is True


def test_a_genuinely_invented_number_is_still_caught():
    """The fix must not blind the detector it was fixing."""
    from src.graders import grade

    q = _filed_style_question()
    g = grade(q, "416,161 and also 999,999 [AAPL-2025]")

    assert "999999" in g["fabricated_numbers"]


def test_the_careful_stand_in_answers_a_suite_built_from_its_own_documents():
    """It scored 2 of 24 on the filed suite because it looked figures up in a
    hardcoded table of the authored corpus. A baseline that cannot answer the
    questions is not a baseline."""
    from src.graders import grade
    from src.models import CarefulAnswerer

    q = _filed_style_question()
    answer = CarefulAnswerer()(q)

    assert "416,161" in answer
    assert grade(q, answer)["ok"] is True


def test_line_wrapping_does_not_attach_a_figure_to_the_wrong_year():
    """The documents wrap mid-phrase, so 'in fiscal\\n2023.' splits a period from
    its year. Read line by line, the prior year's figure answered this year's
    question -- silently."""
    from src.models import CarefulAnswerer

    this_year = CarefulAnswerer()(_filed_style_question(year=2025))
    prior_year = CarefulAnswerer()(_filed_style_question(year=2024))

    assert "416,161" in this_year
    assert "391,035" in prior_year


def test_a_year_mention_is_never_returned_as_the_figure():
    from src.models import _figures_by_year

    got = _figures_by_year("Revenue for fiscal 2025 was 416,161.")

    assert got == {2025: "416,161"}


def test_removing_the_hardcoded_table_left_the_authored_scores_unchanged():
    """The regression check that makes the rewrite trustworthy: the lookup now
    reads the documents, and reproduces exactly what the table produced on the
    corpus the table was written for."""
    from src.demo import evaluate
    from src.suite import SUITE

    per_model, _ = evaluate(SUITE)
    acc = {k: round(v["score"]["accuracy"], 4) for k, v in per_model.items()}

    assert acc == {"careful": 1.0, "eager": 0.5714, "year-blind": 0.5714,
                   "over-refuser": 0.4286, "uncited": 1.0}
