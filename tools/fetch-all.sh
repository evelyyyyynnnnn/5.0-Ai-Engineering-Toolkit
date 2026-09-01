#!/usr/bin/env bash
# Fetch every project's real data, then re-run each demo against it.
#
# Run this from a machine with ordinary internet access, in the folder that
# holds all five repositories side by side:
#
#   ~/niw/
#     1.0-Secure-Ai-Agent-Infrastructure/
#     2.0-Healthcare-Ai-Systems/
#     3.0-Financial-Ai-Systems/
#     4.0-Decision-Intelligence-Framework/
#     5.0-Ai-Engineering-Toolkit/
#
#   export DATAKIT_UA="Your Name your@email"      # the SEC requires this
#   bash 5.0-Ai-Engineering-Toolkit/tools/fetch-all.sh
#
# It never stops on a failure. Every project is attempted, and the summary at
# the end says which sources answered and which did not, so one moved URL does
# not cost you the whole run.

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LOG="$ROOT/fetch-all.log"
: > "$LOG"

if [ -z "${DATAKIT_UA:-}" ]; then
  echo "DATAKIT_UA is not set."
  echo "The SEC refuses requests that do not name a contact, so several"
  echo "projects will fail with a 403 without it. Set it and re-run:"
  echo '  export DATAKIT_UA="Your Name your@email"'
  exit 1
fi

ok=(); blocked=(); failed=(); demo_ok=(); demo_bad=()

for proj in "$ROOT"/*/*/; do
  name="$(basename "$(dirname "$proj")")/$(basename "$proj")"
  [ -f "$proj/data/fetch.py" ] || continue

  echo ""
  echo "=============================================================="
  echo "  $name"
  echo "=============================================================="
  {
    echo ""
    echo "########## $name ##########"
  } >> "$LOG"

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
printf '  fetched            %2d\n' "${#ok[@]}"
printf '  network blocked    %2d\n' "${#blocked[@]}"
printf '  fetch failed       %2d\n' "${#failed[@]}"
printf '  demo produced real results %2d\n' "${#demo_ok[@]}"
printf '  demo errored       %2d\n' "${#demo_bad[@]}"

show() { [ ${#2} -eq 0 ] && return; echo ""; echo "$1"; shift; printf '  %s\n' "$@"; }
[ ${#blocked[@]} -gt 0 ] && { echo ""; echo "BLOCKED (this machine cannot reach the host):"; printf '  %s\n' "${blocked[@]}"; }
[ ${#failed[@]}  -gt 0 ] && { echo ""; echo "FAILED (a URL moved, or a source refused the request):"; printf '  %s\n' "${failed[@]}"; }
[ ${#demo_bad[@]} -gt 0 ] && { echo ""; echo "FETCHED BUT THE DEMO ERRORED:"; printf '  %s\n' "${demo_bad[@]}"; }

echo ""
echo "Full output: $LOG"
if [ ${#failed[@]} -gt 0 ] || [ ${#demo_bad[@]} -gt 0 ] || [ ${#blocked[@]} -gt 0 ]; then
  echo "Send that log back and the failures can be fixed."
fi
echo ""
echo "Nothing was committed. To keep the real results:"
echo "  for r in \"$ROOT\"/*/; do (cd \"\$r\" && git add -A && git commit -m 'Add results from real data' && git push); done"
