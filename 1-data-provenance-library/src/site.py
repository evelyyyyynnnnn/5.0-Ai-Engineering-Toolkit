"""Builds website/ from the last demo run."""
from __future__ import annotations
import pathlib
from . import sitekit as sk

ROOT = pathlib.Path(__file__).resolve().parent.parent
META = {
    "name": "spanlineage",
    "slug": "data-provenance-library",
    "repo": "5.0-Ai-Engineering-Toolkit",
    "pillar": "Financial Stability",
    "tagline": "Span-level provenance that survives arithmetic: a derived number keeps "
               "the characters it came from, across every transformation and every "
               "document.",
    "tags": [("pip-installable", ""), ("no dependencies", ""), ("CLI", ""),
             ("not yet published", "warn")],
    "banner": "Release artifacts (sdist + wheel) are built and pass twine check, but "
              "the package is NOT published to PyPI, so it has no downloads and no "
              "users. The pipeline below runs on two authored filing extracts; the "
              "library is real, the filings are not.",
}


SAMPLE = """pip install -e .

python - <<'PY'
import spanlineage as L
src  = L.Source("D1", "Revenue was 1,250 and costs were 400.")
rev  = L.extract(src, r"Revenue was ([\\d,]+)")
cost = L.extract(src, r"costs were ([\\d,]+)")
margin = (rev - cost) / rev
print(margin.value, [e["text"] for e in margin.evidence({"D1": src})])
PY

spanlineage extract filing.txt 'revenue was ([0-9,]+)'
spanlineage verify filing.txt record.json"""


def build_site(results: dict) -> pathlib.Path:
    # The real run and the authored run have different shapes; dispatch on the
    # flag the results file carries rather than on which keys happen to exist.
    if not results.get("is_synthetic", True):
        return build_site_real(results)

    m, g, v, t = (results["metrics"], results["graph"], results["verification"],
                  results["tamper"])
    margin = m["operating_margin"]

    metrics = sk.metric_grid([
        ("Derivation depth", g["depth"], "transformations deep"),
        ("Spans retained", margin["n_spans"], "on the final margin"),
        ("Documents joined", len(results["cross_document"]), "in one metric"),
        ("Spans verified", f"{v['n_checked']}/{v['n_spans']}", "against sources"),
    ])

    metric_tbl = sk.table(
        ["Metric", "Value", "Spans", "Depth", "Documents", "Evidence"],
        [[k, f"{val['value']:,.4f}", val["n_spans"], val["depth"],
          ", ".join(d.split("-")[0] for d in val["documents"]),
          ", ".join(val["evidence"][:4])] for k, val in m.items()],
        numeric_cols=(1, 2, 3))

    lines = []
    for e in results["explanation"]:
        val = e["value"]
        vs = f"{val:,.4f}" if isinstance(val, float) else str(val)
        ev = f"   ← {', '.join(e['evidence'])}" if e["evidence"] else ""
        lines.append(f"{'  ' * e['depth']}{e['op']:<10}{vs}{ev}")
    trace = "<pre>" + sk.esc("\n".join(lines)) + "</pre>"

    sample = sk.esc(SAMPLE)
    body = f"""
<section>
  <h2>The problem</h2>
  <div class="stack">
    <p>A pipeline extracts a number from a document, transforms it four times, and
    lands it in a report. When somebody disputes the number, nobody can say which
    characters produced it. Logging the extraction does not help, because the
    transformations are where the value actually changed.</p>
    <p>So provenance is made a property of the <strong>value</strong> rather than of the
    pipeline. Arithmetic on tracked values propagates spans, and the final number knows
    every span that contributed to it — without any code between here and there having
    to thread anything through by hand.</p>
  </div>
</section>

<section>
  <h2>This run</h2>
  <div class="stack-lg">
    {metrics}
    <p class="mono" style="color:var(--muted);font-size:12.5px">
      generated {sk.esc(results['generated_at'])} &middot;
      spanlineage {sk.esc(results['package']['version'])} &middot;
      {sk.esc(results['data_source'])}
    </p>
    {metric_tbl}
  </div>
</section>

<section>
  <h2>A margin that remembers four numbers and two documents</h2>
  <div class="stack-lg">
    {trace}
    <p>Operating margin is <strong>{margin['value']:.4f}</strong>, three transformations
    deep, and it still points at the four extractions underneath it —
    {", ".join(margin["evidence"])} — across
    {len(results['cross_document'])} documents. The restructuring charge comes from a
    supplementary note, not the filing, and the adjusted-opex figure carries both
    document identities as a result.</p>
    <div class="note">
      <h3>What a span set does and does not say</h3>
      <p>The union records that the result <em>depends on</em> all of these spans. It
      deliberately does not say which input contributed how much — that is an
      attribution question, and a span set pretending to answer it would be worse than
      not answering. Attribution lives in the decision-audit project in repo 4.0, where
      it is done with Shapley values.</p>
    </div>
  </div>
</section>

<section>
  <h2>Records that notice when a source moves</h2>
  <div class="stack-lg">
    {sk.table(["Check", "Result"],
              [["Spans verified against the original sources",
                f"{v['n_checked']}/{v['n_spans']}, ok={v['ok']}"],
               ["Revenue edited from 1,284,500 to 1,384,500",
                "detected" if t["detected"] else "NOT DETECTED"],
               ["Reason reported",
                t["problems"][0]["issue"] if t["problems"] else "—"]])}
    <p>Two failure modes are reported separately because they mean different things. A
    changed document hash means the source moved underneath the record; an out-of-bounds
    or mismatched span means the record itself is wrong. Collapsing them into one
    "invalid" flag would hide which of the two happened, and only one of them is the
    pipeline's fault.</p>
  </div>
</section>

<section>
  <h2>Install and use</h2>
  <div class="stack">
    <pre>{sample}</pre>
  </div>
</section>

<section>
  <h2>What this does not establish</h2>
  <div class="stack">
    <ul class="tight">
      <li><strong>Not published.</strong> No PyPI release, no downloads, no users.
      Nothing here should be described as adopted.</li>
      <li>Span propagation covers arithmetic and lifted single-argument functions.
      Aggregations over collections, joins and group-bys are not implemented, and
      those are where real pipelines spend their time.</li>
      <li>Every operation widens the span set, so a value derived from many
      extractions ends up citing all of them. That is correct and it is also not
      very useful at scale; narrowing it needs the attribution machinery this
      library deliberately does not have.</li>
      <li>No PDF, OCR or layout handling. Spans index into plain text.</li>
      <li>Verification detects a changed document. It does not tell you whether the
      new document says something that would change the answer.</li>
    </ul>
  </div>
</section>
"""
    return sk.build(ROOT, META, body, results)


# --------------------------------------------------------------------------
# Real-data page: lineage carried through arithmetic on values as filed.
# --------------------------------------------------------------------------

REAL_META = dict(META)
REAL_META.update({
    "tags": [("real SEC EDGAR XBRL", "real"), ("values as filed", ""),
             ("span-level lineage", ""), ("not published", "warn")],
    "banner": "Run against the SEC EDGAR XBRL company-concept API: every value is a "
              "figure as filed, carrying the accession number of the filing that "
              "reported it, with hashes recorded in data/MANIFEST.json.",
    "datanote": "Built from results/latest-real.json. The package is installable from "
                "this repository and is not published, so it has no downloads and no "
                "users.",
})


def build_site_real(results: dict) -> pathlib.Path:
    pkg = results["package"]
    comps = results.get("companies", [])
    fails = results.get("failures", [])
    rows, deepest = [], 0
    for c in comps:
        for name, m in c["metrics"].items():
            deepest = max(deepest, m["depth"])
            rows.append([c["ticker"], name, f"{m['value']:,.6g}", m["op"],
                         m["depth"], m["n_spans"], ", ".join(m["documents"])])

    metrics = sk.metric_grid([
        ("Public API", pkg["exports"], f"exports in {pkg['name']} {pkg['version']}"),
        ("Filers traced", len(comps), "to the span each value was filed in"),
        ("Deepest derivation", f"{deepest} operations",
         "and it still names its sources"),
        ("Failures recorded", len(fails), "not silently dropped"),
    ])

    lin_tbl = sk.table(
        ["Filer", "Metric", "Value", "Operation", "Depth", "Spans", "Source concepts"],
        rows, numeric_cols=(2, 4, 5))
    depth_chart = sk.bar_chart(
        [(f"{r[0]} {r[1]} (depth {r[4]})", r[5]) for r in rows], fmt="{:.0f}")

    fail_tbl = sk.table(["Filer", "Recorded failure"],
                        [[f["ticker"], f["error"]] for f in fails]) if fails else ""
    fail_section = ""
    if fails:
        fail_section = (
            '<section><h2>Failures</h2><div class="stack-lg">' + fail_tbl
            + "<p>A fetch that failed is in the results file as a failure rather than "
              "absent from the companies list. A provenance library that quietly drops "
              "what it could not retrieve is the one thing it must not be.</p>"
              "</div></section>")

    body = f"""
<section>
  <h2>This run</h2>
  <div class="stack-lg">
    {metrics}
    <p class="mono" style="color:var(--muted);font-size:12.5px">
      generated {sk.esc(results['generated_at'])} &middot;
      {pkg['name']} {pkg['version']} &middot;
      published: {str(pkg.get('published', False)).lower()}
    </p>
  </div>
</section>

<section>
  <h2>Lineage carried through arithmetic</h2>
  <div class="stack-lg">
    {depth_chart}
    {lin_tbl}
    <p>The rows that matter are the derived ones. A ratio two operations away from
    anything anyone filed still names every filed fact it came from, so if the ratio is
    wrong the wrong input can be located rather than guessed at.</p>
  </div>
</section>

<section>
  <h2>Why the earliest filing wins</h2>
  <div class="stack-lg">
    <div class="note">
      <h3>The same figure is filed many times</h3>
      <p>{sk.esc(results.get('duplicate_policy', ''))}</p>
    </div>
  </div>
</section>

{fail_section}

<section>
  <h2>Reproduce</h2>
  <div class="stack">
    <pre>python -m src.demo --real
# -&gt; results/latest-real.json
pytest -q</pre>
  </div>
</section>
"""
    return sk.build(ROOT, REAL_META, body, results)
