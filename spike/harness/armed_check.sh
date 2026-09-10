#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
#
# The org contract §2.2: "A check that cannot fail must never report a pass.
# Every check you add must be shown to fail. Break the thing it checks, watch it
# go red, put it back."
#
# `--plant` passing proves the harness reports two verdicts. It does NOT prove
# the verdicts are load-bearing: a harness that hard-coded them would also pass.
# So each mutation below breaks exactly one link in the chain and the gate must
# go red. A mutation that leaves the file byte-identical is reported BROKEN --
# never as a pass -- because a mutation that failed to apply is otherwise
# indistinguishable from one the check survived.
set -uo pipefail
cd "$(dirname "$0")"
D8="${D8_DIR:-$(cd ../../../../research/experiments/D8-identity 2>/dev/null && pwd)}"
[ -d "$D8" ] || { echo "set D8_DIR to kindspec/research/experiments/D8-identity"; exit 2; }

TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
cp -r prose_merge.py plant_cases "$TMP/"

run() { python3 "$TMP/prose_merge.py" --d8-dir "$D8" --plant 2>&1; }
h()   { sha256sum "$1" | cut -c1-16; }

fails=0
mutate() { # name file sed-expr expectation
  local name=$1 file=$2 expr=$3
  local before after out
  before=$(h "$TMP/$file")
  perl -pi -e "$expr" "$TMP/$file"
  after=$(h "$TMP/$file")
  if [ "$before" = "$after" ]; then
    echo "MUTATION $name: BROKEN -- pattern matched nothing, file unchanged ($before)"
    fails=$((fails+1)); return
  fi
  out=$(run)
  if grep -q "PLANTED-CASE GATE: FAIL" <<<"$out"; then
    echo "MUTATION $name: gate went RED as required   [$before -> $after]"
    grep -E "got  |GATE:" <<<"$out" | sed 's/^/      /'
  else
    echo "MUTATION $name: *** GATE STAYED GREEN -- the check is not armed ***"
    echo "$out" | sed 's/^/      /'
    fails=$((fails+1))
  fi
  cp -r prose_merge.py plant_cases "$TMP/"   # put it back
}

echo "=== 0. baseline: unmutated harness, both planted cases ==="
run
run | grep -q "PLANTED-CASE GATE: PASS" || { echo "baseline is not green; stop"; exit 1; }
echo
echo "=== mutations: each must turn the gate RED ==="

# 1. The verdict rule cannot report WRONG. This is the org contract's own named
#    failure -- a check that cannot fail.
mutate "verdict-always-correct" prose_merge.py \
  's/cls = "LOUD" if hit is None else \("correct" if hit == tgt else "WRONG"\)/cls = "correct"/'

# 2. The oracle abstains from everything. A harness that scores nothing must
#    report NOT-EVALUATED, not a pass.
mutate "oracle-never-confident" prose_merge.py \
  's/^ORACLE_CONFIDENCE = 0\.5/ORACLE_CONFIDENCE = 1.1/'

# 3. The oracle grades the mechanism by the mechanism's own algorithm --
#    ORACLE.md §1's explicit prohibition, and PRE-REGISTRATION §3.1's
#    "the mechanism under test grading itself".
mutate "oracle-self-grading" prose_merge.py \
  's/^            out\[n\] = \("SURVIVED", got\[0\]\)/            out[n] = ("SURVIVED", max(range(len(bm)), key=lambda i: difflib.SequenceMatcher(None, blk["content"], bm[i]["content"]).ratio()))/'

# 4. The FIXTURE, not the harness: remove leg C's verbatim re-quote from
#    wrong-01 and the silent-wrong must disappear. This proves the WRONG verdict
#    tracks the input rather than the fixture's name.
mutate "wrong-01-drop-leg-C-duplicate" plant_cases/wrong-01/c.md \
  's/^Before any release, confirm that the staging cluster has fully drained,$/REMOVED/ if $. == 19'

# 5. The other direction, on the minimal pair: clean-01 differs from wrong-01
#    only in WHICH paragraph leg A edits. Move leg A's edit onto the anchored
#    paragraph and the known-clean case must stop being silent.
mutate "clean-01-move-leg-A-edit-onto-the-anchor" plant_cases/clean-01/a.md \
  's/queued on the primary worker pool,/queued on either worker pool,/'

# 6. single-leg-01 is the case that refuted this spike's own both-legs claim
#    (LOG.md §9). Drop leg A's verbatim re-quote and the silent-wrong must
#    disappear, which is what proves the refutation tracks the input.
mutate "single-leg-01-drop-the-requote" plant_cases/single-leg-01/a.md \
  's/^Before any release, confirm that the staging cluster has fully drained,$/REMOVED/ if $. == 19'

echo
if [ "$fails" -eq 0 ]; then
  echo "ARMED-CHECK: PASS -- every mutation turned the gate red"
else
  echo "ARMED-CHECK: FAIL -- $fails mutation(s) did not"
fi
exit "$fails"
