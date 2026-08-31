"""Tests for locating real reported values inside the SEC's own JSON.

The substantive decision here is which of many duplicate entries to use. The
same annual figure appears in the original 10-K, again as a comparative in the
next year's filing, and again in year-to-date columns. Choosing the wrong one
does not error -- it produces a lineage that explains a number using characters
from a document published after the number was used.
"""
import json
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from data import datakit
from data.load import annual_fact, find_span, load_company, parse_concept


def _fact(val, start, end, fy, form, filed, accn):
    return {"start": start, "end": end, "val": val, "accn": accn, "fy": fy,
            "fp": "FY", "form": form, "filed": filed, "frame": f"CY{fy}"}


def _concept(tag="Revenues", facts=None):
    return json.dumps({
        "cik": 320193, "tag": tag, "taxonomy": "us-gaap",
        "units": {"USD": facts or []},
    }).encode()


FACTS = [
    # The original FY2023 report.
    _fact(383285000000, "2022-09-25", "2023-09-30", 2023, "10-K",
          "2023-11-03", "0000320193-23-000106"),
    # The same figure, restated as a comparative in the FY2024 filing.
    _fact(383290000000, "2022-09-25", "2023-09-30", 2023, "10-K",
          "2024-11-01", "0000320193-24-000123"),
    # A quarter, which is not an annual period.
    _fact(89498000000, "2023-07-02", "2023-09-30", 2023, "10-Q",
          "2023-11-03", "0000320193-23-000200"),
    # The most recent annual period.
    _fact(391035000000, "2023-10-01", "2024-09-28", 2024, "10-K",
          "2024-11-01", "0000320193-24-000123"),
]


def test_parse_concept_extracts_usd_facts():
    c = parse_concept(_concept(facts=FACTS))
    assert c["tag"] == "Revenues"
    assert c["unit"] == "USD"
    assert len(c["facts"]) == 4


def test_parse_concept_raises_when_there_are_no_units():
    with pytest.raises(ValueError, match="no units"):
        parse_concept(json.dumps({"tag": "X", "units": {}}).encode())


def test_annual_fact_ignores_quarterly_periods():
    """A 10-Q covering three months must never be used as an annual figure."""
    f = annual_fact(parse_concept(_concept(facts=FACTS)))
    assert f["form"] == "10-K"
    assert f["val"] == 391035000000


def test_annual_fact_prefers_the_original_filing_over_a_restatement():
    """For one period, the earliest FILED entry wins.

    Following the restatement would mean the lineage of an FY2023 figure points
    at characters in a document published in November 2024 -- after anyone
    could have used the number.
    """
    fy23 = [f for f in FACTS if f["fy"] == 2023 and f["form"] == "10-K"]
    c = {"tag": "Revenues", "unit": "USD", "facts": fy23}
    f = annual_fact(c)
    assert f["filed"] == "2023-11-03"
    assert f["val"] == 383285000000, "the restated value was chosen"
    assert f["accn"] == "0000320193-23-000106"


def test_annual_fact_raises_when_nothing_annual_exists():
    only_q = [f for f in FACTS if f["form"] == "10-Q"]
    with pytest.raises(ValueError, match="no annual fact"):
        annual_fact({"tag": "Revenues", "unit": "USD", "facts": only_q})


# --- spans -----------------------------------------------------------------

def test_find_span_points_at_the_right_entrys_value():
    """Two entries carry nearly identical numbers; the span must land on the
    one belonging to the chosen accession, not on the first match in the file."""
    raw = _concept(facts=FACTS)
    text = raw.decode()
    c = parse_concept(raw)
    fact = annual_fact(c)
    a, b = find_span(text, fact)

    assert text[a:b] == "391035000000"
    # The span must sit inside the object carrying that accession.
    obj_start = text.rfind("{", 0, a)
    obj_end = text.find("}", b)
    assert fact["accn"] in text[obj_start:obj_end]


def test_find_span_locates_the_original_not_the_restatement():
    raw = _concept(facts=FACTS)
    text = raw.decode()
    fy23 = [f for f in parse_concept(raw)["facts"]
            if f["fy"] == 2023 and f["form"] == "10-K"]
    fact = annual_fact({"tag": "Revenues", "unit": "USD", "facts": fy23})
    a, b = find_span(text, fact)
    assert text[a:b] == "383285000000"


def test_find_span_raises_when_the_value_is_absent():
    raw = _concept(facts=FACTS)
    ghost = _fact(1, "2020-01-01", "2020-12-31", 2020, "10-K", "2021-01-01", "X-1")
    with pytest.raises(ValueError, match="could not locate"):
        find_span(raw.decode(), ghost)


# --- end to end ------------------------------------------------------------

def test_refuses_when_nothing_is_cached(tmp_path):
    with pytest.raises(datakit.FetchError, match="no real XBRL data cached"):
        load_company("AAPL", root=tmp_path)


def _seed(tmp_path, ticker="AAPL"):
    f = datakit.Fetcher(tmp_path)
    man = f.load_manifest()
    payloads = {
        "Revenues": FACTS,
        "CostOfRevenue": [_fact(210352000000, "2023-10-01", "2024-09-28", 2024,
                                "10-K", "2024-11-01", "0000320193-24-000123")],
        "ResearchAndDevelopmentExpense": [
            _fact(31370000000, "2023-10-01", "2024-09-28", 2024, "10-K",
                  "2024-11-01", "0000320193-24-000123")],
    }
    for tag, facts in payloads.items():
        dest = f"xbrl/{ticker.lower()}/{tag}.json"
        p = f.raw / dest
        p.parent.mkdir(parents=True, exist_ok=True)
        raw = _concept(tag, facts)
        p.write_bytes(raw)
        man["files"][dest] = {
            "source": f"{ticker} {tag}",
            "url": f"https://data.sec.gov/api/xbrl/companyconcept/CIK.../{tag}.json",
            "publisher": "U.S. SEC", "terms": "public domain",
            "sha256": datakit.sha256_file(p), "bytes": len(raw),
            "retrieved_utc": datakit.utc_now()}
    f._write_manifest(man)
    return f


def test_derives_a_margin_across_two_real_documents(tmp_path):
    _seed(tmp_path)
    sources, metrics, prov = load_company("AAPL", root=tmp_path)

    assert "gross_margin" in metrics
    margin = metrics["gross_margin"]
    expected = (391035000000 - 210352000000) / 391035000000
    assert float(margin.value) == pytest.approx(expected)
    # The lineage crosses two separate filed documents.
    assert len({s.doc_id for s in margin.spans}) == 2


def test_every_span_reads_back_the_value_it_supports(tmp_path):
    """Provenance that cannot be re-read is provenance in name only."""
    _seed(tmp_path)
    _, _, prov = load_company("AAPL", root=tmp_path)
    ok = [p for p in prov if p["status"] == "ok"]
    assert ok
    for p in ok:
        assert p["span_text"] == str(int(p["value"]))
        assert len(p["document_sha256"]) == 16
        assert p["accession"]


def test_verification_passes_and_tampering_is_caught(tmp_path):
    """The library's claim, against a document anyone can re-download."""
    import spanlineage as L
    _seed(tmp_path)
    sources, metrics, _ = load_company("AAPL", root=tmp_path)
    margin = metrics["gross_margin"]

    assert L.verify_against(margin, sources)["ok"] is True

    # Edit the document the margin's own spans point into, not just any one.
    doc = next(d for d in sources if "391035000000" in sources[d].text)
    edited = L.Source(doc, sources[doc].text.replace("391035000000",
                                                     "491035000000"))
    out = L.verify_against(margin, {**sources, doc: edited})
    assert out["ok"] is False
    assert out["problems"]


def test_a_missing_revenue_concept_is_refused(tmp_path):
    f = _seed(tmp_path)
    (f.raw / "xbrl/aapl/Revenues.json").unlink()
    man = f.load_manifest()
    man["files"].pop("xbrl/aapl/Revenues.json")
    f._write_manifest(man)
    with pytest.raises(datakit.FetchError, match="no usable revenue concept"):
        load_company("AAPL", root=tmp_path)
