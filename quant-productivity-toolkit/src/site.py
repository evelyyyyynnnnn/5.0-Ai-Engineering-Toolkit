"""Builds website/ from the last demo run."""
from __future__ import annotations
import pathlib
from . import sitekit as sk

ROOT = pathlib.Path(__file__).resolve().parent.parent
META = {
    "name": "qkit-research",
    "slug": "quant-productivity-toolkit",
    "repo": "5.0-Ai-Engineering-Toolkit",
    "pillar": "Financial Stability",
    "tagline": "The four checks that decide whether a backtest means anything: "
               "lookahead, survivorship, label leakage, and how many strategies you "
               "tried before this one.",
    "tags": [("pip-installable", ""), ("CLI", ""), ("4 checks", ""),
             ("not yet published", "warn")],
    "banner": "Release artifacts (sdist + wheel) are built and pass twine check, but "
              "the package is NOT published to PyPI — no downloads, no users. Every "
              "demonstration below runs on synthetic series where the "
              "contamination was put there deliberately, which is the only way to show "
              "a detector finds it.",
}


def build_site(results: dict) -> pathlib.Path:
    la, sv, va, sel = (results["lookahead"], results["survivorship"],
                       results["validation"], results["selection"])

    metrics = sk.metric_grid([
        ("Leaks caught", f"{la['n_flagged']}/2", "of the deliberate ones"),
        ("Survivorship bias", f"{sv['bias_bps']:.1f} bps",
         "per period, from dropping the dead"),
        ("Leaking train points", va["naive_overlapping_train_points"],
         "in naive k-fold, 0 after purging"),
        ("Noise Sharpe", f"{sel['best_observed_sharpe']:.2f}",
         f"best of {sel['n_trials_run']} random strategies"),
    ])

    la_tbl = sk.table(
        ["Feature", "Forward corr", "At lag", "Backward corr", "Flagged"],
        [[c["feature"], f"{c['max_forward_corr']:.3f}", c["lag_of_max"],
          f"{c['max_backward_corr']:.3f}", "YES" if c["contaminated"] else "—"]
         for c in la["cases"]], numeric_cols=(1, 2, 3))

    sv_tbl = sk.table(
        ["", "Full universe", "Survivors only"],
        [["Names", sv["n_universe"], sv["n_survivors"]],
         ["Mean return per period", f"{sv['mean_return_all']:.6f}",
          f"{sv['mean_return_survivors']:.6f}"]],
        numeric_cols=(1, 2))

    va_tbl = sk.table(
        ["Scheme", "Observations dropped per fold", "Folds with residual overlap"],
        [["Naive k-fold", str(va["naive_kfold"]["dropped_per_fold"]),
          va["naive_kfold"]["folds_with_overlap"]],
         ["Purged, no embargo", str(va["purged_embargo_0"]["dropped_per_fold"]),
          va["purged_embargo_0"]["folds_with_overlap"]],
         ["Purged + 20-period embargo",
          str(va["purged_embargo_20"]["dropped_per_fold"]),
          va["purged_embargo_20"]["folds_with_overlap"]]],
        numeric_cols=(2,))

    sel_tbl = sk.table(
        ["Trials assumed", "E[max Sharpe from noise]", "Deflated probability",
         "Survives"],
        [[r["n_trials"], f"{r['expected_max_sharpe_from_noise']:.3f}",
          f"{r['deflated_sharpe_prob']:.4f}", "yes" if r["survives"] else "no"]
         for r in sel["by_assumed_trials"]], numeric_cols=(0, 1, 2))

    sel_chart = sk.bar_chart(
        [(f"{r['n_trials']} trials", r["deflated_sharpe_prob"])
         for r in sel["by_assumed_trials"]], fmt="{:.3f}")

    body = f"""
<section>
  <h2>Not a backtester</h2>
  <div class="stack">
    <p>Backtesters are plentiful and mostly fine. What goes wrong is upstream of them,
    in four places that turn a strategy that does not work into a beautiful equity
    curve. Each check returns a finding rather than a number, so it can be dropped into
    a research loop and fail loudly.</p>
  </div>
</section>

<section>
  <h2>This run</h2>
  <div class="stack-lg">
    {metrics}
    <p class="mono" style="color:var(--muted);font-size:12.5px">
      generated {sk.esc(results['generated_at'])} &middot;
      qkit-research {sk.esc(results['package']['version'])} &middot;
      {sk.esc(results['data_source'])}
    </p>
  </div>
</section>

<section>
  <h2>1 · Lookahead</h2>
  <div class="stack-lg">
    {la_tbl}
    <div class="note">
      <h3>The direction of this test is its entire content</h3>
      <p>The convention is that <code>feature[t]</code> is known at the end of period t
      and predicts <code>target[t+1]</code>. Lookahead therefore means correlation with
      the <em>contemporaneous or future</em> target. Correlation with an earlier target
      is not lookahead: a momentum feature <em>is</em> the previous return, and
      correlating 1.000 with it is the definition of momentum.</p>
      <p>The first version of this module tested the wrong direction. It flagged
      momentum as contaminated and passed a feature that was a copy of next period's
      return — the exact inversion of what it was for.</p>
    </div>
    <div class="note warn" style="background:var(--warn-bg);border-color:transparent">
      <h3>One case it misses, left in the table</h3>
      <p>The centred rolling mean straddles time t, so it genuinely is contaminated. It
      scores {[c for c in la["cases"] if c["feature"].startswith("centred")][0]["max_forward_corr"]:.3f}
      — just under the 0.50 threshold — and is <strong>not flagged</strong>.</p>
      <p>Lowering the bound would catch it and would start flagging strong-but-real
      signals on short samples. The threshold is a plausibility bound on forward
      predictability, not a significance test, and this row is here so the bound's cost
      is visible rather than tuned away.</p>
    </div>
  </div>
</section>

<section>
  <h2>2 · Survivorship</h2>
  <div class="stack-lg">
    {sv_tbl}
    <p>Dropping the {sv['n_delisted']} names that died — {1 - sv['survivor_share']:.0%}
    of the universe — raises the mean period return from
    {sv['mean_return_all']:.6f} to {sv['mean_return_survivors']:.6f}, a bias of
    <strong>{sv['bias_bps']:.1f} basis points per period</strong>. Compounded over a
    long sample that is not a small distortion; it can invert the sign of a result.</p>
    <p>The function takes the full universe including the dead, which is exactly the
    data most survivorship-biased studies do not have. When it is unavailable the honest
    output is a warning, and this library does not attempt to correct a bias it cannot
    measure.</p>
  </div>
</section>

<section>
  <h2>3 · Label leakage in cross-validation</h2>
  <div class="stack-lg">
    {va_tbl}
    <p>With labels spanning {va['label_span']} periods, naive k-fold leaves
    <strong>{va['naive_overlapping_train_points']}</strong> training observations whose
    label windows reach into the test block. Each one shares its answer with a test
    point. Purging removes them; the embargo additionally drops the periods immediately
    after each test block, where serial correlation survives purging.</p>
    <p>With span 1 and no embargo the splitter reduces to ordinary contiguous k-fold,
    which is the check that it is not doing something exotic.</p>
  </div>
</section>

<section>
  <h2>4 · How many strategies did you try?</h2>
  <div class="stack-lg">
    {sel_chart}
    {sel_tbl}
    <div class="note">
      <h3>Read the first row against the last</h3>
      <p>{sel['n_trials_run']} strategies were generated from <strong>pure noise</strong>.
      Their true Sharpe is exactly zero. The best of them shows an observed Sharpe of
      <strong>{sel['best_observed_sharpe']:.3f}</strong>, and the probabilistic Sharpe
      ratio against zero is <strong>{sel['psr_vs_zero']:.4f}</strong> — that is a result
      that looks decisively significant and is entirely selection.</p>
      <p>Deflating for the number of trials is what exposes it. Assuming a single
      pre-registered strategy, it survives. Told the truth —
      {sel['n_trials_run']} trials — the probability falls to
      {sel['by_assumed_trials'][-1]['deflated_sharpe_prob']:.3f} and it does not.</p>
      <p>The minimum track record length for this series is
      {sel['min_track_record_length']:.0f} periods, against the
      750 it actually has. Reporting a Sharpe without the trial count is not a
      rounding issue; it is the difference between a finding and an artefact.</p>
    </div>
  </div>
</section>

<section>
  <h2>Install and use</h2>
  <div class="stack">
    <pre>pip install -e .

qkit lookahead features.csv --target fwd_return --features mom_5 vol_20 rsi
qkit sharpe backtest.csv --column returns --trials 200</pre>
    <p>Both subcommands exit non-zero on a finding, so they work as a pre-commit hook or
    a CI gate on a research repository.</p>
  </div>
</section>

<section>
  <h2>What this does not establish</h2>
  <div class="stack">
    <ul class="tight">
      <li><strong>Not published.</strong> No PyPI release, no downloads, no users.</li>
      <li>Every demonstration uses synthetic series with contamination inserted
      deliberately. That shows the detectors find what was planted, not that they
      find what a real research process produces.</li>
      <li>The lookahead detector is correlational and univariate. A feature that
      leaks only in combination with another will pass, and the centred-window case
      above shows it also misses a genuine leak that sits under the threshold.</li>
      <li>Deflated Sharpe assumes independent trials. Two hundred variants of one
      idea are not independent, and the correction is then too weak.</li>
      <li>Purged k-fold assumes a fixed label span. Variable-horizon labels need
      per-observation windows, which are not implemented.</li>
    </ul>
  </div>
</section>
"""
    return sk.build(ROOT, META, body, results)
