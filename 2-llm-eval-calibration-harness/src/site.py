"""Builds website/ from the last demo run."""
from __future__ import annotations
import pathlib
from . import sitekit as sk

ROOT = pathlib.Path(__file__).resolve().parent.parent
META = {
    "name": "LLM Eval & Calibration Harness",
    "slug": "llm-eval-calibration-harness",
    "repo": "5.0-Ai-Engineering-Toolkit",
    "pillar": "Cross-cutting",
    "tagline": "Grounding, citation accuracy and refusal behaviour for LLMs over "
               "financial filings — with questions that have no answer, because that "
               "is where a finance assistant actually fails.",
    "tags": [("4 question categories", ""), ("lexical graders", ""),
             ("no LLM run yet", "warn"), ("authored suite", "demo")],
    "banner": "NO language model has been run through this harness. Every row below is "
              "a deterministic stand-in written to embody one failure mode, so the "
              "harness itself can be shown to separate careful behaviour from reckless "
              "behaviour before any real model is scored.",
}


def build_site(results: dict) -> pathlib.Path:
    # The real run and the authored run have different shapes; dispatch on the
    # flag the results file carries rather than on which keys happen to exist.
    if not results.get("is_synthetic", True):
        return build_site_real(results)

    s, sep = results["suite"], results["separation"]
    models = results["models"]

    metrics = sk.metric_grid([
        ("Questions", s["n_questions"], f"{len(s['by_category'])} categories"),
        ("Unanswerable", s["by_category"].get("unanswerable", 0),
         "should be refused"),
        ("Traps", s["by_category"].get("trap", 0),
         "a wrong number is present"),
        ("Separation", f"{sep['spread']:.2f}", f"{sep['best']} vs {sep['worst']}"),
    ])

    rows = []
    for name, sc in models.items():
        bc = sc["by_category"]
        def a(k):
            return f"{bc[k]['accuracy']:.2f}" if k in bc else "—"
        rows.append([name, f"{sc['accuracy']:.2f}", a("answerable"),
                     a("unanswerable"), a("trap"), a("stale"),
                     f"{sc['fabrication_rate']:.2f}",
                     f"{sc['citation_accuracy']:.2f}"])
    model_tbl = sk.table(
        ["Answerer", "Overall", "Answerable", "Unanswerable", "Trap", "Stale",
         "Fabrication", "Citation"], rows, numeric_cols=(1, 2, 3, 4, 5, 6, 7))

    acc_chart = sk.bar_chart(
        [(k, v["accuracy"]) for k, v in models.items()], fmt="{:.2f}")

    cat_tbl = sk.table(
        ["Category", "n", "What it tests"],
        [["answerable", s["by_category"].get("answerable", 0),
          "The value is present and should be found"],
         ["unanswerable", s["by_category"].get("unanswerable", 0),
          "Absent from the sources — the model should say so"],
         ["trap", s["by_category"].get("trap", 0),
          "A plausible wrong number IS present, usually the other fiscal year"],
         ["stale", s["by_category"].get("stale", 0),
          "The sources answer a different period than the one asked about"]],
        numeric_cols=(1,))

    tr = results["transcripts"]["eager"]
    fail_rows = [[t["qid"], t["question"][:56], t["answer"][:42], t["failure"]]
                 for t in tr if not t["ok"]]
    fail_tbl = sk.table(
        ["Q", "Question", "Answer given", "Failure"], fail_rows)

    body = f"""
<section>
  <h2>Questions with no answer are the point</h2>
  <div class="stack">
    <p>A harness that only asks answerable questions measures fluency. In a finance
    assistant the expensive failure is a confident wrong number in a filing summary,
    which is worse than no number at all — so more than half the suite is questions
    that should be refused or that contain a plausible wrong answer.</p>
    <p>Graders are lexical and inspectable. An LLM judge would grade more subtly and
    would also make the harness's reliability a function of the thing it is measuring,
    which is a poor foundation for a calibration study.</p>
  </div>
</section>

<section>
  <h2>The suite</h2>
  <div class="stack-lg">
    {metrics}
    {cat_tbl}
    <p class="mono" style="color:var(--muted);font-size:12.5px">
      generated {sk.esc(results['generated_at'])} &middot; {sk.esc(results['data_source'])}
    </p>
  </div>
</section>

<section>
  <h2>Does the harness separate good behaviour from bad?</h2>
  <div class="stack-lg">
    {acc_chart}
    {model_tbl}
    <div class="note">
      <h3>Read the columns, not the overall score</h3>
      <p>The <em>eager</em> answerer scores 1.00 on answerable questions and traps and
      <strong>0.00</strong> on everything that should be refused. That is the dominant
      real-world pattern — fluency rewarded over abstention — and an overall accuracy
      figure alone would report it as a middling model rather than a dangerous one.</p>
      <p>The <em>over-refuser</em> is its mirror: perfect on unanswerable and stale
      questions, useless on everything else. Both land near 0.5 overall while failing in
      opposite directions, which is exactly why the per-category breakdown is the
      product and the single number is not.</p>
      <p>The <em>year-blind</em> answerer finds the right metric and ignores the period,
      so it clears answerable questions and collapses on traps ({models['year-blind']['by_category']['trap']['accuracy']:.2f}).
      The <em>uncited</em> answerer gives correct values with no citations: accuracy
      {models['uncited']['accuracy']:.2f}, citation accuracy
      {models['uncited']['citation_accuracy']:.2f}. Grounding and attribution are
      separate axes and this shows them moving independently.</p>
    </div>
  </div>
</section>

<section>
  <h2>Every failure of the eager answerer</h2>
  <div class="stack-lg">
    {fail_tbl}
    <p>Each of these is a fabrication in the sense that matters: a number presented as
    an answer when the sources do not support it. None of them is a hallucinated
    <em>digit</em> — the values are all real numbers lifted from the documents — which
    is precisely why a fabrication check that only looks for invented digits misses
    them.</p>
  </div>
</section>

<section>
  <h2>Reproduce it</h2>
  <div class="stack">
    <pre>cd llm-eval-calibration-harness
pip install -r requirements.txt
python -m pytest tests/ -q
python -m src.demo</pre>
    <p>To score a real model, write a callable taking a <code>Question</code> and
    returning a string, and add it to <code>ANSWERERS</code>. The graders and the suite
    do not change.</p>
  </div>
</section>

<section>
  <h2>What this does not establish</h2>
  <div class="stack">
    <ul class="tight">
      <li><strong>No language model has been run.</strong> Every score is from a
      deterministic stand-in. Nothing here is evidence about any model's grounding,
      refusal or citation behaviour.</li>
      <li>The <em>careful</em> answerer scores 1.00 because it and the suite were
      written together. That number measures nothing except that the graders accept a
      correct answer.</li>
      <li>Fourteen questions over two short extracts. Real filings are thousands of
      times longer and the retrieval problem, which this harness does not touch,
      dominates at that length.</li>
      <li>Graders are lexical. A correct answer phrased unusually will be marked
      wrong, and a refusal phrased unusually will not be recognised.</li>
      <li>No cost, latency or token accounting, all of which matter for a harness
      that is meant to be run repeatedly.</li>
    </ul>
  </div>
</section>
"""
    return sk.build(ROOT, META, body, results)


# --------------------------------------------------------------------------
# Real-model page: a real open language model scored by the same lexical
# grader as the deterministic stand-ins, on the same questions.
# --------------------------------------------------------------------------

REAL_META = dict(META)
REAL_META.update({
    "tags": [("real SEC EDGAR XBRL", "real"), ("real local model", "real"),
             ("a third of the suite unanswerable", ""), ("lexical grader", "")],
    "banner": "Questions built from values as filed in SEC EDGAR XBRL, with hashes "
              "recorded in data/MANIFEST.json. More than a third of the suite has no "
              "answer in the documents shown, because a harness that asks only "
              "answerable questions measures fluency. Replies reach the grader "
              "verbatim; a failed call is scored as the empty answer it was.",
    "datanote": "Built from results/latest-llm.json. The grader is lexical by design, "
                "which is what makes it deterministic and auditable, and also what "
                "bounds what it can detect.",
})


def build_site_real(results: dict) -> pathlib.Path:
    suite = results["suite"]
    by = suite.get("by_category", {})
    models = results.get("models", {})
    mdl = results.get("model", {})
    vs = results.get("model_vs_stubs", {})
    unans = by.get("unanswerable", 0)

    metrics = sk.metric_grid([
        ("Model accuracy", f"{vs.get('model_accuracy', 0):.3f}",
         sk.esc(mdl.get("name", ""))),
        ("Best non-model", f"{vs.get('best_stub_accuracy', 0):.4f}",
         f"the {vs.get('best_stub', '')} stand-in"),
        ("Unanswerable", f"{unans / suite['n_questions'] * 100:.1f}%",
         f"{unans} of {suite['n_questions']} questions"),
        ("Failed calls", mdl.get("failed_calls", 0),
         f"of {mdl.get('calls', 0)}, median {mdl.get('median_latency_s', 0):.2f} s"),
    ])

    order = sorted(models, key=lambda m: -models[m]["accuracy"])
    acc_tbl = sk.table(
        ["Answerer", "Accuracy", "Fabrication", "Citation", "Answerable",
         "Unanswerable", "Trap"],
        [[m, f"{models[m]['accuracy']:.4f}", f"{models[m]['fabrication_rate']:.3f}",
          f"{models[m]['citation_accuracy']:.4f}"]
         + [f"{models[m]['by_category'][c]['ok']}/{models[m]['by_category'][c]['n']}"
            for c in ("answerable", "unanswerable", "trap")]
         for m in order],
        numeric_cols=(1, 2, 3))
    acc_chart = sk.bar_chart(
        [(m, models[m]["accuracy"]) for m in order], fmt="{:.3f}")
    fab_chart = sk.bar_chart(
        [(m, models[m]["fabrication_rate"]) for m in order], fmt="{:.3f}")

    suite_tbl = sk.table(
        ["Question category", "Count", "Share"],
        [[c, n, f"{n / suite['n_questions'] * 100:.1f}%"] for c, n in by.items()],
        numeric_cols=(1, 2))

    call_tbl = sk.table(
        ["", "Value"],
        [["Model", mdl.get("name", "")],
         ["Temperature", mdl.get("temperature", "")],
         ["Calls", mdl.get("calls", 0)],
         ["Failed calls", mdl.get("failed_calls", 0)],
         ["Median latency", f"{mdl.get('median_latency_s', 0):.2f} s"],
         ["Wall clock", f"{mdl.get('wall_clock_s', 0):.1f} s"]],
        numeric_cols=(1,))

    body = f"""
<section>
  <h2>This run</h2>
  <div class="stack-lg">
    {metrics}
    <p class="mono" style="color:var(--muted);font-size:12.5px">
      generated {sk.esc(results['generated_at'])} &middot;
      a language model was run: {str(results.get('any_language_model_run', False)).lower()}
      &middot; {suite['n_questions']} questions
    </p>
  </div>
</section>

<section>
  <h2>Suite design</h2>
  <div class="stack-lg">
    {suite_tbl}
    <p>Declining correctly is worth as much as answering correctly, and the grader scores
    both. That is why more than a third of the questions have no answer in the documents
    shown.</p>
  </div>
</section>

<section>
  <h2>Every answerer, scored by the same grader on the same questions</h2>
  <div class="stack-lg">
    {acc_chart}
    {acc_tbl}
    <p>The deterministic stand-ins are scored first, and they are the reason the model's
    number means anything: a stand-in that answers everything scores zero on the
    unanswerable questions, and one that declines everything scores zero on the
    answerable ones. A grader that rewarded both equally would be useless.</p>
  </div>
</section>

<section>
  <h2>Fabrication &mdash; numbers appearing in no source document</h2>
  <div class="stack-lg">
    {fab_chart}
  </div>
</section>

<section>
  <h2>Call log</h2>
  <div class="stack-lg">
    {call_tbl}
    <p>{sk.esc(results.get('note', ''))}</p>
  </div>
</section>

<section>
  <h2>Reproduce</h2>
  <div class="stack">
    <pre>python -m data.fetch
python run_llm_demo.py --real
# -&gt; results/latest-llm.json
pytest -q</pre>
  </div>
</section>
"""
    return sk.build(ROOT, REAL_META, body, results)
