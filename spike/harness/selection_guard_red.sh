#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
#
# Emit the selection guard's GREEN and RED states as one reproducible
# transcript, hashes included.
#
# WHY THIS IS A SCRIPT AND NOT A PASTED TRANSCRIPT. The red half was first
# recorded by hand, and the hash pair it carried named a working-tree state that
# no committed file matched -- the file was edited again before it was
# committed. A hash a reader cannot check against the artifact it names is worse
# than no hash, because it looks checkable. Generating it here means the hash is
# always of the file as it stands.
#
#   ./selection_guard_red.sh > ../results/selection-guard-selftest.txt
set -uo pipefail
export PYTHONDONTWRITEBYTECODE=1
cd "$(dirname "$0")"

h() { sha256sum "$1" | cut -c1-16; }
SRC=prose_merge.py

echo "# spike/harness/selection_guard_red.sh -- regenerate with that command."
echo "# $SRC as tested: sha256/16 = $(h $SRC)"
echo
echo "############ GREEN: the guard as committed ############"
python3 "$SRC" --selftest-selection
green=$?
echo
echo "############ RED: restore the guard's ORIGINAL tautological form ############"
echo "# LOG.md §5.3. The first version computed \`dropped\` from \`cand - acc\` and"
echo "# then asserted \`cand == acc + dropped\`, which is always true."

TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
cp "$SRC" "$TMP/"
before=$(h "$TMP/$SRC")
perl -0pi -e 's/        dropped = \(st\["drop:add_add"\] \+ st\["drop:delete_modify"\]\n                   \+ st\["drop:convergent"\] \+ st\["drop:unchanged_side"\]\)/        dropped = cand - acc/' "$TMP/$SRC"
after=$(h "$TMP/$SRC")

if [ "$before" = "$after" ]; then
  echo "MUTATION: BROKEN -- pattern matched nothing, file unchanged ($before)"
  echo "SELECTION-GUARD RED DEMONSTRATION: BROKEN"
  exit 2
fi
echo "# mutation applied [$before -> $after]"
python3 "$TMP/$SRC" --selftest-selection
red=$?

echo
if [ "$green" -eq 0 ] && [ "$red" -ne 0 ]; then
  echo "SELECTION-GUARD DEMONSTRATION: PASS -- green as committed (exit $green),"
  echo "red with the tautology restored (exit $red). Both states observed."
  exit 0
fi
echo "SELECTION-GUARD DEMONSTRATION: FAIL -- green exit $green, red exit $red;"
echo "the guard must pass as committed and fail with the tautology restored."
exit 1
