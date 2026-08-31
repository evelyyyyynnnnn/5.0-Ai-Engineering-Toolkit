"""Tests for building the evaluation suite from filed data.

The category that carries the weight is `unanswerable`. An authored suite's
unanswerable questions can often be spotted from their phrasing; one built from
a concept a registrant genuinely never tagged reads exactly like an answerable
question and is not. These tests check that such questions really have no
answer in the documents shown.
"""
import json
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from data import datakit
from data.load import _annual, _fmt, build_suite, read_company, render_document


def _fact(val, start, end, fy, form="10-K", filed="2024-11-01", accn="A-1"):
    return {"start": start, "end": end, "val": val, "accn": accn, "fy": fy,
            "fp": "FY", "form": form, "filed": filed}


def _concept(tag, facts):
    return json.dumps({"cik": 1, "tag": tag, "taxonomy": "us-gaap",
                       "units": {"USD": facts}}).encode()


REV = [
    _fact(383285000000, "2022-09-25", "2023-09-30", 2023, filed="2023-11-03",
          accn="ORIG-23"),
    # The same year restated in the following filing.
    _fact(383290000000, "2022-09-25", "2023-09-30", 2023, filed="2024-11-01",
          accn="LATER-24"),
    _fact(391035000000, "2023-10-01", "2024-09-28", 2024, accn="ORIG-24"),
    # A quarter, which is not an annual period.
    _fact(89498000000, "2023-07-02", "2023-09-30", 2023, form="10-Q",
          accn="Q-23"),
]
COST = [_fact(214137000000, "2022-09-25", "2023-09-30", 2023, accn="ORIG-23"),
        _fact(210352000000, "2023-10-01", "2024-09-28", 2024, accn="ORIG-24")]


def test_annual_keeps_only_year_long_10k_periods():
    got = _annual(REV)
    assert set(got) == {2023, 2024}


def test_annual_prefers_the_original_filing_over_the_restatement():
    got = _annual(REV)
    assert got[2023]["val"] == 383285000000
    assert got[2023]["accn"] == "ORIG-23"


def test_values_are_formatted_in_millions_as_a_filing_writes_them():
    assert _fmt(391035000000) == "391,035"
    assert _fmt(1284600000) == "1,285"
    assert _fmt(29915000000) == "29,915"


def test_refuses_when_nothing_is_cached(tmp_path):
    with pytest.raises(datakit.FetchError, match="no real XBRL data cached"):
        read_company("AAPL", root=tmp_path)


def _seed(tmp_path, ticker="AAPL", with_rnd=True):
    f = datakit.Fetcher(tmp_path)
    man = f.load_manifest()
    payloads = {"Revenues": REV, "CostOfRevenue": COST}
    if with_rnd:
        payloads["ResearchAndDevelopmentExpense"] = [
            _fact(29915000000, "2022-09-25", "2023-09-30", 2023, accn="ORIG-23"),
            _fact(31370000000, "2023-10-01", "2024-09-28", 2024, accn="ORIG-24")]
    for tag, facts in payloads.items():
        dest = f"xbrl/{ticker.lower()}/{tag}.json"
        p = f.raw / dest
        p.parent.mkdir(parents=True, exist_ok=True)
        raw = _concept(tag, facts)
        p.write_bytes(raw)
        man["files"][dest] = {
            "source": f"{ticker} {tag}", "url": f"https://data.sec.gov/{tag}",
            "publisher": "U.S. SEC", "terms": "public domain",
            "sha256": datakit.sha256_file(p), "bytes": len(raw),
            "retrieved_utc": datakit.utc_now()}
    f._write_manifest(man)
    return f


def test_rendered_document_states_the_filed_values(tmp_path):
    _seed(tmp_path)
    metrics, _ = read_company("AAPL", root=tmp_path)
    doc = render_document("AAPL", 2024, metrics)
    assert "391,035" in doc
    assert "fiscal 2024" in doc
    # A different year's figure must not appear in this year's document.
    assert "383,285" not in doc


def test_answerable_questions_have_their_answer_in_the_cited_document(tmp_path):
    _seed(tmp_path)
    questions, prov = build_suite(root=tmp_path, tickers=["AAPL"])
    answerable = [q for q in questions if q.category == "answerable"]
    assert answerable
    for q in answerable:
        assert q.answer in q.sources[q.correct_source], q.text


def test_unanswerable_questions_really_have_no_answer(tmp_path):
    """The property that makes this suite worth running."""
    _seed(tmp_path, with_rnd=False)
    questions, prov = build_suite(root=tmp_path, tickers=["AAPL"])
    unanswerable = [q for q in questions if q.category == "unanswerable"]
    assert unanswerable, "no unanswerable questions were built"
    for q in unanswerable:
        assert q.answer is None
        # The precise property: no line in any document states this metric FOR
        # THIS YEAR. A metric may well appear for another year -- that is what
        # makes the question hard rather than obviously unanswerable.
        metric = q.text.split("'s ", 1)[1].rsplit(" in fiscal", 1)[0].lower()
        year = q.text.rsplit("fiscal ", 1)[1].rstrip("?")
        for doc in q.sources.values():
            for line in doc.lower().splitlines():
                assert not (metric in line and year in line), (q.text, line)


def test_an_unreported_metric_becomes_an_unanswerable_question(tmp_path):
    _seed(tmp_path, with_rnd=False)
    _, prov = build_suite(root=tmp_path, tickers=["AAPL"])
    company = prov["companies"][0]
    assert "research and development expense" in company["metrics_absent"]


def test_the_trap_value_is_a_real_figure_from_the_adjacent_year(tmp_path):
    """The wrong answer must be plausible: the number a model gets from
    reading the wrong document, not nonsense."""
    _seed(tmp_path)
    questions, _ = build_suite(root=tmp_path, tickers=["AAPL"])
    traps = [q for q in questions if q.category == "trap"]
    assert traps
    for q in traps:
        assert q.trap_value and q.trap_value != q.answer
        assert q.answer in q.sources[q.correct_source]
        # The trap value is real and sits in the OTHER document.
        other = [d for k, d in q.sources.items() if k != q.correct_source]
        assert any(q.trap_value in d for d in other)


def test_provenance_records_the_concepts_behind_every_question(tmp_path):
    _seed(tmp_path)
    _, prov = build_suite(root=tmp_path, tickers=["AAPL"])
    assert prov["answers_are_filed_values"] is True
    concepts = prov["companies"][0]["concepts"]
    assert concepts and all(len(c["sha256"]) == 16 for c in concepts)


def test_the_harness_separates_the_answerers_on_real_questions(tmp_path):
    """The harness's own claim, exercised on a suite built from filed data."""
    _seed(tmp_path)
    from src.demo import evaluate
    questions, _ = build_suite(root=tmp_path, tickers=["AAPL"])
    per_model, transcripts = evaluate(questions)

    accs = {k: v["score"]["accuracy"] for k, v in per_model.items()}
    assert len(accs) >= 3
    assert max(accs.values()) > min(accs.values()), \
        "the harness should separate a careful answerer from an eager one"
    assert accs["careful"] == max(accs.values())


def test_the_eager_answerer_is_caught_by_the_unanswerable_questions(tmp_path):
    _seed(tmp_path, with_rnd=False)
    from src.demo import evaluate
    questions, _ = build_suite(root=tmp_path, tickers=["AAPL"])
    per_model, _ = evaluate(questions)
    n_unans = sum(1 for q in questions if q.category == "unanswerable")
    assert n_unans >= 1
    assert per_model["eager"]["score"]["accuracy"] < \
        per_model["careful"]["score"]["accuracy"]


def test_evaluation_is_shared_between_both_runs():
    from src import demo
    import inspect
    assert "evaluate(" in inspect.getsource(demo.run)
    assert "evaluate(" in inspect.getsource(demo.run_real)
