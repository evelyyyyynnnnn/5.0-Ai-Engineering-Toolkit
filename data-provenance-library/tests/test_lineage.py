import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import spanlineage as L
from spanlineage.graph import build_graph, explain, to_dot

TEXT = "Revenue was 1,250 and costs were 400 in FY2024."


@pytest.fixture
def src():
    return L.Source("D1", TEXT)


# --- extraction ----------------------------------------------------------

def test_extract_records_the_matched_span(src):
    v = L.extract(src, r"Revenue was ([\d,]+)")
    assert v.value == 1250.0
    sp = v.spans[0]
    assert src.slice(sp.start, sp.end) == "1,250"


def test_extract_returns_none_when_no_match(src):
    assert L.extract(src, r"Profit was ([\d,]+)") is None


def test_extract_returns_none_on_an_uncastable_match(src):
    assert L.extract(src, r"(FY\d+)", cast=float) is None


def test_source_sha_is_sensitive_to_content():
    assert L.Source("D", "a").sha != L.Source("D", "b").sha
    assert L.Source("D", "a").sha == L.Source("D2", "a").sha


# --- propagation ---------------------------------------------------------

def test_arithmetic_unions_the_spans(src):
    rev = L.extract(src, r"Revenue was ([\d,]+)")
    cost = L.extract(src, r"costs were ([\d,]+)")
    assert len((rev - cost).spans) == 2


def test_spans_are_deduplicated(src):
    rev = L.extract(src, r"Revenue was ([\d,]+)")
    assert len((rev + rev).spans) == 1


def test_deep_derivation_keeps_every_leaf(src):
    rev = L.extract(src, r"Revenue was ([\d,]+)")
    cost = L.extract(src, r"costs were ([\d,]+)")
    margin = (rev - cost) / rev
    assert len(margin.spans) == 2
    assert build_graph(margin).depth() == 2


def test_untracked_operand_does_not_add_spans(src):
    rev = L.extract(src, r"Revenue was ([\d,]+)")
    assert len((rev * 2).spans) == 1
    assert (rev * 2).value == 2500.0


def test_reflected_operators_work(src):
    rev = L.extract(src, r"Revenue was ([\d,]+)")
    assert (2 * rev).value == 2500.0
    assert (100 + rev).value == 1350.0


def test_apply_lifts_a_function_and_keeps_spans(src):
    rev = L.extract(src, r"Revenue was ([\d,]+)")
    out = rev.apply(lambda x: x / 1000.0, "to_millions")
    assert out.value == 1.25 and len(out.spans) == 1 and out.op == "to_millions"


def test_cross_document_derivation_carries_both_ids():
    a = L.Source("A", "value 10")
    b = L.Source("B", "value 4")
    x = L.extract(a, r"value (\d+)")
    y = L.extract(b, r"value (\d+)")
    assert sorted({s.doc_id for s in (x - y).spans}) == ["A", "B"]


def test_untrack_unwraps(src):
    rev = L.extract(src, r"Revenue was ([\d,]+)")
    assert L.untrack(rev) == 1250.0
    assert L.untrack(7) == 7


# --- graph ---------------------------------------------------------------

def test_graph_stats_are_consistent(src):
    rev = L.extract(src, r"Revenue was ([\d,]+)")
    cost = L.extract(src, r"costs were ([\d,]+)")
    g = build_graph((rev - cost) / rev)
    s = g.stats()
    assert s["n_leaves"] == 2
    assert s["depth"] == 2
    assert "extract" in s["ops"]


def test_explain_is_ordered_root_first(src):
    rev = L.extract(src, r"Revenue was ([\d,]+)")
    cost = L.extract(src, r"costs were ([\d,]+)")
    steps = explain((rev - cost) / rev, {"D1": src})
    assert steps[0]["depth"] == 0 and steps[0]["op"] == "div"
    assert any(s["evidence"] for s in steps)


def test_dot_output_is_wellformed(src):
    rev = L.extract(src, r"Revenue was ([\d,]+)")
    dot = to_dot(rev * 2)
    assert dot.startswith("digraph") and dot.rstrip().endswith("}")


# --- verification --------------------------------------------------------

def test_verify_passes_on_the_original_source(src):
    rev = L.extract(src, r"Revenue was ([\d,]+)")
    assert L.verify_against(rev, {"D1": src})["ok"]


def test_verify_detects_a_changed_document(src):
    rev = L.extract(src, r"Revenue was ([\d,]+)")
    edited = L.Source("D1", TEXT.replace("1,250", "9,999"))
    out = L.verify_against(rev, {"D1": edited})
    assert not out["ok"]
    assert out["problems"][0]["issue"] == "document has changed"


def test_verify_reports_a_missing_source(src):
    rev = L.extract(src, r"Revenue was ([\d,]+)")
    out = L.verify_against(rev, {})
    assert not out["ok"]
    assert out["problems"][0]["issue"] == "source not supplied"


def test_verify_checks_every_span_of_a_derived_value(src):
    rev = L.extract(src, r"Revenue was ([\d,]+)")
    cost = L.extract(src, r"costs were ([\d,]+)")
    out = L.verify_against(rev - cost, {"D1": src})
    assert out["n_spans"] == 2 and out["n_checked"] == 2


def test_package_is_not_claimed_to_be_published():
    """Guards the site banner."""
    import json
    p = pathlib.Path(__file__).resolve().parent.parent / "results" / "latest.json"
    if p.exists():
        assert json.loads(p.read_text())["package"]["published"] is False
