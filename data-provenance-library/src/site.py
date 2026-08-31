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
