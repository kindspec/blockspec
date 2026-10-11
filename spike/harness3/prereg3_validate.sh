#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
#
# PRE-REGISTRATION-3.md §9: the V steps run before the validation commit.
# Each stage writes its transcript to results/prereg3/validation/ and exits
# non-zero on failure. A V step fails when its transcript shows a non-zero
# exit, a FAIL, or a surviving or BROKEN mutant (prereg 2 §9's V-failure
# rule). V1 and V2 are not rerun: nothing they cover changes. V6, the
# rehearsal of the bound tier-run, runs separately (prereg3_v6.py) because it
# needs a tierer.
#
#   prereg3_validate.sh V0|V3|V4|V5|all
#
# Environment:
#   D8_DIR   kindspec/research experiments/D8-identity at d51ce09
set -uo pipefail
set -f
export PYTHONDONTWRITEBYTECODE=1
HERE=$(cd "$(dirname "$0")" && pwd)
SPIKE=$(cd "$HERE/.." && pwd)
OUTDIR="${OUTDIR:-$SPIKE/results/prereg3/validation}"
mkdir -p "$OUTDIR"
SCR=$(mktemp -d); trap 'rm -rf "$SCR"' EXIT
: "${D8_DIR:?set D8_DIR to research experiments/D8-identity at d51ce09}"

stamp() {
  echo "# blockspec HEAD $(git -C "$HERE" rev-parse HEAD 2>/dev/null)  uncommitted or ignored files under spike/harness3, PRE-REGISTRATION-3.md: $(git -C "$SPIKE" status --porcelain --ignored --untracked-files=all -- harness3 PRE-REGISTRATION-3.md | wc -l)"
  echo "# python $(python3 -c 'import sys;print(sys.version.split()[0])')  git $(git --version | cut -d' ' -f3)  D8 HEAD $(git -C "$D8_DIR" rev-parse HEAD 2>/dev/null)"
}

v0() {
  stamp
  local ok=0
  python3 -I -S -B "$HERE/prereg3_v0.py" --d8-dir "$D8_DIR" || ok=1
  echo "== V0 red: one planted fault per check, in memory; every check must FAIL"
  python3 -I -S -B "$HERE/prereg3_v0.py" --d8-dir "$D8_DIR" --red || ok=1
  return $ok
}
v3() { stamp; python3 -I -S -B "$HERE/prereg3_v3.py" --d8-dir "$D8_DIR"; }
v4() { stamp; python3 -I -S -B "$HERE/prereg3_v4.py" --d8-dir "$D8_DIR"; }
v5() {
  stamp
  echo "# prereg 2's V5, run unchanged by harness/prereg2_validate.sh V5"
  OUTDIR="$SCR/v5" D8_DIR="$D8_DIR" "$SPIKE/harness/prereg2_validate.sh" V5 > "$SCR/v5.out" 2>&1
  local rc=$?
  cat "$SCR/v5/V5.txt" 2>/dev/null
  return $rc
}

run_stage() {  # run_stage <name> <fn>
  local out="$OUTDIR/$1.txt" rc
  "$2" > "$out" 2>&1; rc=$?
  echo "exit=$rc" >> "$out"
  local repo; repo=$(cd "$SPIKE/.." && pwd)
  sed -i -e "s|$SCR|\$SCRATCH|g" -e "s|$D8_DIR|\$D8_DIR|g" -e "s|$repo|\$REPO|g" \
      -e "s|${TMPDIR:-/tmp}/[^ ]*prereg3-v3-[A-Za-z0-9_]*|\$TMP|g" -e "s|/var/tmp/[^ ]*prereg3-v3-[A-Za-z0-9_]*|\$TMP|g" "$out"
  echo "$1: exit=$rc -> $out"
  return $rc
}

fails=0
case "${1:-}" in
  V0) run_stage V0 v0 || fails=1 ;;
  V3) run_stage V3 v3 || fails=1 ;;
  V4) run_stage V4 v4 || fails=1 ;;
  V5) run_stage V5 v5 || fails=1 ;;
  all) for s in "V0 v0" "V3 v3" "V4 v4" "V5 v5"; do set -- $s; run_stage "$1" "$2" || fails=1; done ;;
  *) echo "usage: $0 V0|V3|V4|V5|all" >&2; exit 64 ;;
esac
exit $fails
