#!/usr/bin/env bash
# Fetch every project's real data, then re-run each demo against it.
#
# This is the script that makes the portfolio's "N of M projects run on real
# public data" claim checkable by someone who is not me. It walks all five
# repositories, runs each project's own data/fetch.py against the source that
# project names, re-runs that project's demo on what came back, and records
# which sources answered and which did not.
#
# Run it from a machine with ordinary internet access, in the folder that holds
# all five repositories side by side:
#
#   ~/niw/
#     1.0-Secure-Ai-Agent-Infrastructure/
#     2.0-Healthcare-Ai-Systems/
#     3.0-Financial-Ai-Systems/
#     4.0-Decision-Intelligence-Framework/
#     5.0-Ai-Engineering-Toolkit/
#
#   bash 5.0-Ai-Engineering-Toolkit/5-data-fetch-harness/fetch-all.sh --list
#   export DATAKIT_UA="Your Name your@email"      # the SEC requires this
#   bash 5.0-Ai-Engineering-Toolkit/5-data-fetch-harness/fetch-all.sh
#
# --list shows which projects would be visited and exits without touching the
# network, so the plan can be inspected before any request is made.
#
# A run never stops on a failure. Every project is attempted, and the summary
# says which sources answered, so one moved URL does not cost the whole run.

set -uo pipefail

MODE=run
ROOT=""

usage() {
  cat <<'USAGE'
usage: fetch-all.sh [--list] [--root DIR]

  --list, -n   List the projects that would be visited and exit. Makes no
               network request and does not need DATAKIT_UA.
  --root DIR   Treat DIR as the folder holding the five repositories.
               Defaults to two levels above this script.
  --help, -h   This message.
USAGE
}

while [ $# -gt 0 ]; do
  case "$1" in
    --list|-n) MODE=list; shift ;;
    --root)    ROOT="${2:-}"; shift 2 ;;
    --help|-h) usage; exit 0 ;;
    *) echo "unknown option: $1" >&2; usage >&2; exit 64 ;;
  esac
done

if [ -z "$ROOT" ]; then
  ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
fi
if [ ! -d "$ROOT" ]; then
  echo "not a directory: $ROOT" >&2
  exit 66
fi

# Which projects this harness is for.
#
# A project qualifies by owning a data/fetch.py -- that file is the project's
# own statement of where its data comes from, and running it is the only way
# this script knows how to fetch anything. historical-archive is excluded by
# name rather than by depth: those folders hold prior work that is kept for the
# record and is not part of any claim, and at least one of them does own a
# data/fetch.py. Relying on it sitting one level deeper than the glob reaches
# would make the exclusion an accident of layout instead of a decision.
projects() {
  local proj repo name
  for proj in "$ROOT"/*/*/; do
    [ -d "$proj" ] || continue
    name="$(basename "$proj")"
    [ "$name" = "historical-archive" ] && continue
    [ -f "$proj/data/fetch.py" ] || continue
    printf '%s\n' "$proj"
  done
}

mapfile -t PROJECTS < <(projects)

if [ "${#PROJECTS[@]}" -eq 0 ]; then
  echo "No project with a data/fetch.py under $ROOT."
  echo "Run this from the folder that holds the five repositories, or pass --root."
  exit 1
fi

label() { echo "$(basename "$(dirname "$1")")/$(basename "$1")"; }

if [ "$MODE" = list ]; then
  echo "portfolio root: $ROOT"
  echo "${#PROJECTS[@]} project(s) would be fetched and re-run:"
  for proj in "${PROJECTS[@]}"; do echo "  $(label "$proj")"; done
  echo ""
  echo "Nothing was fetched. Drop --list to run them."
  exit 0
fi

if [ -z "${DATAKIT_UA:-}" ]; then
  echo "DATAKIT_UA is not set."
  echo "The SEC refuses requests that do not name a contact, so several"
  echo "projects will fail with a 403 without it. Set it and re-run:"
  echo '  export DATAKIT_UA="Your Name your@email"'
  exit 1
fi

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG="$ROOT/fetch-all.log"
RUNS="$HERE/runs"
mkdir -p "$RUNS"
: > "$LOG"
STARTED="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

ok=(); blocked=(); failed=(); demo_ok=(); demo_bad=()

for proj in "${PROJECTS[@]}"; do
  name="$(label "$proj")"

  echo ""
  echo "=============================================================="
  echo "  $name"
  echo "=============================================================="
  { echo ""; echo "########## $name ##########"; } >> "$LOG"

  ( cd "$proj" && python3 -m data.fetch 2>&1 | tee -a "$LOG" )
  rc=${PIPESTATUS[0]}

  case $rc in
    0) ok+=("$name") ;;
    2) blocked+=("$name") ;;
    *) failed+=("$name") ;;
  esac

  if [ $rc -eq 0 ]; then
    echo "--- re-running the demo on the real data ---"
    ( cd "$proj" && python3 -m src.demo --real 2>&1 | tee -a "$LOG" )
    if [ ${PIPESTATUS[0]} -eq 0 ]; then demo_ok+=("$name"); else demo_bad+=("$name"); fi
  fi
done

echo ""
echo "=============================================================="
echo "  SUMMARY"
echo "=============================================================="
printf '  projects visited            %2d\n' "${#PROJECTS[@]}"
printf '  fetched                     %2d\n' "${#ok[@]}"
printf '  network blocked             %2d\n' "${#blocked[@]}"
printf '  fetch failed                %2d\n' "${#failed[@]}"
printf '  demo produced real results  %2d\n' "${#demo_ok[@]}"
printf '  demo errored                %2d\n' "${#demo_bad[@]}"

[ ${#blocked[@]}  -gt 0 ] && { echo ""; echo "BLOCKED (this machine cannot reach the host):"; printf '  %s\n' "${blocked[@]}"; }
[ ${#failed[@]}   -gt 0 ] && { echo ""; echo "FAILED (a URL moved, or a source refused the request):"; printf '  %s\n' "${failed[@]}"; }
[ ${#demo_bad[@]} -gt 0 ] && { echo ""; echo "FETCHED BUT THE DEMO ERRORED:"; printf '  %s\n' "${demo_bad[@]}"; }

# A run that leaves no record is a claim without evidence, which is the thing
# this portfolio exists not to do. The name avoids latest.json, latest-real.json
# and latest-llm.json on purpose: those are what the roll-up reads to decide
# what counts as a project, and this harness is tooling, not a result.
RECORD="$RUNS/last-run.json"
STATUS_JSON="$(
  python3 - "$STARTED" "${#PROJECTS[@]}" <<'PY' "${ok[@]+"${ok[@]}"}" -- "${blocked[@]+"${blocked[@]}"}" -- "${failed[@]+"${failed[@]}"}" -- "${demo_ok[@]+"${demo_ok[@]}"}" -- "${demo_bad[@]+"${demo_bad[@]}"}"
import json, sys
started, visited, rest = sys.argv[1], int(sys.argv[2]), sys.argv[3:]
groups, cur = [], []
for a in rest:
    if a == "--":
        groups.append(cur); cur = []
    else:
        cur.append(a)
groups.append(cur)
ok, blocked, failed, demo_ok, demo_bad = (groups + [[]] * 5)[:5]
print(json.dumps({
    "started_at": started,
    "projects_visited": visited,
    "fetched": ok,
    "network_blocked": blocked,
    "fetch_failed": failed,
    "demo_produced_real_results": demo_ok,
    "demo_errored": demo_bad,
}, indent=2))
PY
)"
printf '%s\n' "$STATUS_JSON" > "$RECORD"

echo ""
echo "Full output: $LOG"
echo "Run record:  $RECORD"
if [ ${#failed[@]} -gt 0 ] || [ ${#demo_bad[@]} -gt 0 ] || [ ${#blocked[@]} -gt 0 ]; then
  echo "Send that log back and the failures can be fixed."
fi
echo ""
echo "Nothing was committed. To keep the real results:"
echo "  for r in \"$ROOT\"/*/; do (cd \"\$r\" && git add -A && git commit -m 'Add results from real data' && git push); done"
