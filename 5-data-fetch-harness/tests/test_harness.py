"""What the harness promises before it touches the network.

The value of this script is that someone who is not its author can re-fetch the
portfolio's data and re-run every demo. That promise rests on which projects it
decides to visit, and that decision used to be invisible until a run was already
under way. These tests drive the real script in --list mode against fixture
trees, so the selection is checked rather than assumed.
"""
import json
import os
import pathlib
import subprocess

import pytest

HARNESS = pathlib.Path(__file__).resolve().parent.parent / "fetch-all.sh"


def run(*args, root=None, env=None):
    cmd = ["bash", str(HARNESS), *args]
    if root is not None:
        cmd += ["--root", str(root)]
    e = dict(os.environ)
    e.pop("DATAKIT_UA", None)
    e.update(env or {})
    return subprocess.run(cmd, capture_output=True, text=True, env=e)


def project(root, repo, name, *, fetcher=True):
    p = root / repo / name
    (p / "data").mkdir(parents=True)
    if fetcher:
        (p / "data" / "fetch.py").write_text("# stub\n", encoding="utf8")
    return p


def test_the_script_is_executable_and_answers_help():
    r = run("--help")
    assert r.returncode == 0
    assert "--list" in r.stdout


def test_listing_names_every_project_that_owns_a_fetcher(tmp_path):
    project(tmp_path, "1.0-Repo", "1-alpha")
    project(tmp_path, "2.0-Repo", "1-beta")
    r = run("--list", root=tmp_path)
    assert r.returncode == 0, r.stderr
    assert "1.0-Repo/1-alpha" in r.stdout
    assert "2.0-Repo/1-beta" in r.stdout
    assert "2 project(s)" in r.stdout


def test_a_project_without_a_fetcher_is_not_visited(tmp_path):
    project(tmp_path, "1.0-Repo", "1-alpha")
    project(tmp_path, "1.0-Repo", "2-no-fetcher", fetcher=False)
    r = run("--list", root=tmp_path)
    assert "1-alpha" in r.stdout
    assert "2-no-fetcher" not in r.stdout


def test_historical_archive_is_excluded_even_when_it_owns_a_fetcher(tmp_path):
    """The archive holds prior work that backs no claim. It is skipped by name.

    Skipping it by depth alone would be an accident of layout: put a fetcher at
    the archive folder's own root and a depth-based rule lets it through.
    """
    project(tmp_path, "1.0-Repo", "1-alpha")
    project(tmp_path, "1.0-Repo", "historical-archive")
    r = run("--list", root=tmp_path)
    assert "1-alpha" in r.stdout
    assert "historical-archive" not in r.stdout


def test_listing_makes_no_network_request_and_needs_no_user_agent(tmp_path):
    """--list must work with DATAKIT_UA unset, or it cannot be used to inspect
    the plan before committing to a run."""
    project(tmp_path, "1.0-Repo", "1-alpha")
    r = run("--list", root=tmp_path)
    assert r.returncode == 0
    assert "DATAKIT_UA" not in r.stdout
    assert "Nothing was fetched" in r.stdout


def test_a_run_without_a_user_agent_stops_before_fetching_anything(tmp_path):
    project(tmp_path, "1.0-Repo", "1-alpha")
    r = run(root=tmp_path)
    assert r.returncode == 1
    assert "DATAKIT_UA is not set" in r.stdout


def test_an_empty_portfolio_says_so_rather_than_reporting_success(tmp_path):
    (tmp_path / "1.0-Repo" / "1-alpha").mkdir(parents=True)
    r = run("--list", root=tmp_path)
    assert r.returncode == 1
    assert "No project with a data/fetch.py" in r.stdout


def test_an_unknown_option_is_rejected_rather_than_ignored(tmp_path):
    r = run("--fetch-everything-now", root=tmp_path)
    assert r.returncode == 64
    assert "unknown option" in r.stderr


def test_a_missing_root_is_reported(tmp_path):
    r = run("--list", root=tmp_path / "does-not-exist")
    assert r.returncode == 66
    assert "not a directory" in r.stderr


def test_the_run_record_is_not_a_filename_the_rollup_reads():
    """The roll-up treats results/latest.json, latest-real.json and
    latest-llm.json as evidence that a directory is a project with a result.
    This harness is tooling; naming its log one of those would add a
    twenty-third project to a portfolio that has twenty-two."""
    text = HARNESS.read_text(encoding="utf8")
    assert "runs/last-run.json" in text or 'RUNS="$HERE/runs"' in text
    for reserved in ("results/latest.json", "results/latest-real.json",
                     "results/latest-llm.json"):
        assert f'> "{reserved}"' not in text
