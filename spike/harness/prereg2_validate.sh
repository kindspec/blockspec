#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
#
# PRE-REGISTRATION-2.md §9: the V steps. Each stage writes its transcript to
# results/prereg2/validation/ and exits non-zero on failure. A V step fails
# when its transcript shows a non-zero exit, a cmp or sha256 mismatch, or a
# surviving or BROKEN mutant (§9).
#
#   prereg2_validate.sh V1|V2|V3|V4|V5|bundles|all   (all: every stage, in turn)
#
# Environment:
#   D8_DIR         kindspec/research experiments/D8-identity at d51ce09 (a git
#                  checkout, unmodified; V2 prints its HEAD)
#   CONTROL_D8_DIR the D8 directory the committed control-arm.txt names on its
#                  second line. control-arm.txt embeds that path and the
#                  research HEAD, so V1/V2's byte-identical regeneration needs
#                  research at f088cd76 at that exact path. Defaults to D8_DIR.
#   CORPORA_V1     rust-book obsidian-help cmspec at harness/corpora.json's pins
#   CORPORA        rust-book obsidian-help cmspec at D8 §3's pins, and
#                  k8s-website cncf-toc site-policy at §6.2's pins (the layout
#                  run_cheap_arm.sh reads)
#
# V1 and V2 exercise only committed harness code that predates this
# pre-registration. V3-V5 exercise the new code and need no corpus.
set -uo pipefail
set -f
export PYTHONDONTWRITEBYTECODE=1
HERE=$(cd "$(dirname "$0")" && pwd)
RES=$(cd "$HERE/../results" && pwd)
OUTDIR="${OUTDIR:-$RES/prereg2/validation}"
mkdir -p "$OUTDIR"
SCR=$(mktemp -d); trap 'rm -rf "$SCR"' EXIT

stamp() {
  echo "# harness HEAD $(git -C "$HERE" rev-parse HEAD 2>/dev/null)  uncommitted or ignored files under spike/harness, PRE-REGISTRATION-2.md, ORACLE.md: $(git -C "$HERE/.." status --porcelain --ignored --untracked-files=all -- harness PRE-REGISTRATION-2.md ORACLE.md | wc -l)"
  echo "# python $(python3 -c 'import sys;print(sys.version.split()[0])')  git $(git --version | cut -d' ' -f3)"
}

cmp_report() {  # cmp_report <label> <regenerated> <committed>
  local a b
  a=$(sha256sum < "$2" | cut -c1-64); b=$(sha256sum < "$3" | cut -c1-64)
  echo "$a  regenerated  $1"
  echo "$b  committed    $1"
  if cmp "$2" "$3" && [ "$a" = "$b" ]; then echo "BYTE-IDENTICAL: $1"; return 0; fi
  echo "MISMATCH: $1"; return 1
}

v1v2_control() {
  local d8=${CONTROL_D8_DIR:-${D8_DIR:?}}
  : "${CORPORA_V1:?set CORPORA_V1}"
  stamp
  echo "# V1 + V2(control-arm.txt): harness/run_control.sh at harness/corpora.json's pins"
  echo "# D8 dir: $d8 @ $(git -C "$d8" rev-parse HEAD)"
  CORPORA="$CORPORA_V1" D8_DIR="$d8" "$HERE/run_control.sh" > "$SCR/control.txt" 2> "$SCR/control.err"
  local rc=$?
  echo "run_control.sh exit=$rc"
  sed 's/^/  stderr| /' "$SCR/control.err" | head -5
  grep -E "^CONTROL GATE:" "$SCR/control.txt"
  local ok=0
  [ $rc -eq 0 ] || ok=1
  grep -q "^CONTROL GATE: PASS" "$SCR/control.txt" || ok=1
  cmp_report results/control-arm.txt "$SCR/control.txt" "$RES/control-arm.txt" || ok=1
  echo "V1+V2-control: $([ $ok -eq 0 ] && echo PASS || echo FAIL)"
  return $ok
}

v2_merge() {
  : "${CORPORA_V1:?set CORPORA_V1}" "${D8_DIR:?}"
  stamp
  echo "# V2: the merge arm, spike/README.md's command, at harness/corpora.json's pins"
  echo "# D8 dir @ $(git -C "$D8_DIR" rev-parse HEAD)"
  # The committed merge-arm.txt ends "wrote 85 candidate records ... ->
  # spike/results/merge-arm-candidates.jsonl": the run that produced it gave
  # --records relative to the repository root, where README's command, run
  # from spike/, spells it results/... . So this runs README's command from a
  # scratch directory laid out like the repository root, which prints the
  # committed path and writes the records into scratch.
  mkdir -p "$SCR/root/spike/results"
  echo "# cwd: a scratch directory standing in for the repository root"
  ( cd "$SCR/root" && python3 "$HERE/prose_merge.py" \
      --d8-dir "$D8_DIR" \
      --corpus "rust-book=$CORPORA_V1/rust-book:src/" \
      --corpus "obsidian-help=$CORPORA_V1/obsidian-help:en/" \
      --corpus "cmspec=$CORPORA_V1/cmspec:" \
      --records spike/results/merge-arm-candidates.jsonl ) > "$SCR/merge.txt" 2> "$SCR/merge.err"
  local rc=$? ok=0
  echo "prose_merge.py exit=$rc"
  sed 's/^/  stderr| /' "$SCR/merge.err" | head -5
  [ $rc -eq 0 ] || ok=1
  # The committed merge-arm.txt is the report; the trailing "wrote N" line
  # goes to the same stdout, so compare the whole stream.
  cmp_report results/merge-arm.txt "$SCR/merge.txt" "$RES/merge-arm.txt" || ok=1
  cmp_report results/merge-arm-candidates.jsonl "$SCR/root/spike/results/merge-arm-candidates.jsonl" "$RES/merge-arm-candidates.jsonl" || ok=1
  echo "V2-merge: $([ $ok -eq 0 ] && echo PASS || echo FAIL)"
  return $ok
}

v2_research() {
  : "${CORPORA:?}" "${D8_DIR:?}"
  stamp
  echo "# V2: research's results-e4.txt and results-anchor3.txt, D8's own scripts, at D8 §3's pins"
  echo "# D8 dir @ $(git -C "$D8_DIR" rev-parse HEAD), $(git -C "$D8_DIR" status --porcelain -- . | wc -l) modified paths"
  mkdir -p "$SCR/rd/corpora"
  for c in rust-book obsidian-help cmspec; do
    ln -s "$CORPORA/$c" "$SCR/rd/corpora/$c"
    echo "# pin $c $(git -C "$CORPORA/$c" rev-parse HEAD)"
  done
  local ok=0 rc
  ( cd "$SCR/rd" && for n in 20 40 120; do python3 "$D8_DIR/e4_uniqueness.py" "$n" || exit 1; done ) > "$SCR/e4.txt"
  rc=$?; echo "e4_uniqueness.py 20/40/120 exit=$rc"; [ $rc -eq 0 ] || ok=1
  ( cd "$SCR/rd" && python3 "$D8_DIR/anchor_eval3.py" ) > "$SCR/a3.txt"
  rc=$?; echo "anchor_eval3.py exit=$rc"; [ $rc -eq 0 ] || ok=1
  cmp_report research:results-e4.txt "$SCR/e4.txt" "$D8_DIR/results-e4.txt" || ok=1
  cmp_report research:results-anchor3.txt "$SCR/a3.txt" "$D8_DIR/results-anchor3.txt" || ok=1
  echo "V2-research: $([ $ok -eq 0 ] && echo PASS || echo FAIL)"
  return $ok
}

v2_cheap() {
  : "${CORPORA:?}" "${D8_DIR:?}"
  stamp
  echo "# V2: all of results/cheap-arm/, regenerated by harness/run_cheap_arm.sh"
  mkdir -p "$SCR/cheap"
  OUT="$SCR/cheap" CORPORA="$CORPORA" D8_DIR="$D8_DIR" "$HERE/run_cheap_arm.sh" > "$SCR/cheap.log" 2>&1
  local rc=$? ok=0
  echo "run_cheap_arm.sh exit=$rc"; [ $rc -eq 0 ] || ok=1
  local committed regenerated f
  committed=$(cd "$RES/cheap-arm" && ls -A | sort)
  regenerated=$(cd "$SCR/cheap" && ls -A | sort)
  if [ "$committed" != "$regenerated" ]; then
    echo "FILE SETS DIFFER"; diff <(echo "$committed") <(echo "$regenerated"); ok=1
  fi
  for f in $committed; do
    if [ -f "$SCR/cheap/$f" ]; then
      cmp_report "results/cheap-arm/$f" "$SCR/cheap/$f" "$RES/cheap-arm/$f" || ok=1
    else
      echo "MISSING: results/cheap-arm/$f"; ok=1
    fi
  done
  echo "V2-cheap-arm: $([ $ok -eq 0 ] && echo PASS || echo FAIL)"
  return $ok
}

v3() {
  stamp
  python3 -I -S -B "$HERE/prereg2_v3.py" --d8-dir "${D8_DIR:?}"
}

v4() {
  stamp
  python3 -I -S -B "$HERE/prereg2_v4.py" --d8-dir "${D8_DIR:?}"
}

v5() {
  stamp
  local ok=0 rc
  echo "== armed_check.sh"
  D8_DIR="$D8_DIR" "$HERE/armed_check.sh" > "$SCR/armed.txt" 2>&1; rc=$?
  tail -2 "$SCR/armed.txt"; echo "exit=$rc"; [ $rc -eq 0 ] || ok=1
  grep -q "^ARMED-CHECK: PASS" "$SCR/armed.txt" || ok=1
  echo "== prose_merge.py --selftest-selection"
  python3 "$HERE/prose_merge.py" --selftest-selection > "$SCR/sel.txt" 2>&1; rc=$?
  tail -1 "$SCR/sel.txt"; echo "exit=$rc"; [ $rc -eq 0 ] || ok=1
  echo "== selection_guard_red.sh"
  "$HERE/selection_guard_red.sh" > "$SCR/sgr.txt" 2>&1; rc=$?
  grep "DEMONSTRATION" "$SCR/sgr.txt"; echo "exit=$rc"; [ $rc -eq 0 ] || ok=1
  echo "== oracle_limitation.py"
  python3 "$HERE/oracle_limitation.py" --d8-dir "$D8_DIR" > "$SCR/ol.txt" 2>&1; rc=$?
  tail -1 "$SCR/ol.txt"; echo "exit=$rc"; [ $rc -eq 0 ] || ok=1
  echo "V5: $([ $ok -eq 0 ] && echo PASS || echo FAIL)"
  return $ok
}

bundles() {
  BUNDLE_DIR="${BUNDLE_DIR:-${PREREG2_BUNDLE_DIR:-/home/cam/kindspec-data/prereg2-bundles}}"
  stamp
  echo "# corpus bundles (§6.2): sha256 against harness/p2/bundles.json, and the head each holds"
  echo "# bundle dir: $BUNDLE_DIR"
  python3 -I - "$HERE/p2/bundles.json" "$BUNDLE_DIR" <<'PY'
import hashlib, json, os, subprocess, sys
meta, d = json.load(open(sys.argv[1])), sys.argv[2]
ok = True
for name, m in meta.items():
    if name.startswith("_"):
        continue
    p = os.path.join(d, name + ".bundle")
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    heads = subprocess.run(["git", "bundle", "list-heads", p], capture_output=True, text=True).stdout.split()
    good = h.hexdigest() == m["sha256"] and os.path.getsize(p) == m["bytes"] and heads == [m["head"], "HEAD"]
    ok &= good
    print(f"{h.hexdigest()}  {os.path.getsize(p):>10}  {name}.bundle  head {heads[:1]}  {'ok' if good else 'MISMATCH'}")
print("BUNDLES:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
PY
}

run_stage() {  # run_stage <name> <fn>
  local out="$OUTDIR/$1.txt" rc
  "$2" > "$out" 2>&1; rc=$?
  echo "exit=$rc" >> "$out"
  local h; h=$(cd "$HERE/../.." && pwd)
  sed -i -e "s|$SCR|\$SCRATCH|g" -e "s|$h|\$REPO|g" "$out"
  echo "$1: exit=$rc -> $out"
  return $rc
}

fails=0
case "${1:-}" in
  V1|V2-control) run_stage V1-V2-control v1v2_control || fails=1 ;;
  V2-merge)      run_stage V2-merge v2_merge || fails=1 ;;
  V2-research)   run_stage V2-research v2_research || fails=1 ;;
  V2-cheap)      run_stage V2-cheap-arm v2_cheap || fails=1 ;;
  V2)            for s in "V2-merge v2_merge" "V2-research v2_research" "V2-cheap-arm v2_cheap"; do
                   set -- $s; run_stage "$1" "$2" || fails=1; done ;;
  V3)            run_stage V3 v3 || fails=1 ;;
  V4)            run_stage V4 v4 || fails=1 ;;
  V5)            run_stage V5 v5 || fails=1 ;;
  bundles)       run_stage bundles bundles || fails=1 ;;
  all)           for s in "V1-V2-control v1v2_control" "V2-merge v2_merge" "V2-research v2_research" \
                          "V2-cheap-arm v2_cheap" "V3 v3" "V4 v4" "V5 v5" "bundles bundles"; do
                   set -- $s; run_stage "$1" "$2" || fails=1; done ;;
  *) echo "usage: $0 V1|V2|V2-control|V2-merge|V2-research|V2-cheap|V3|V4|V5|bundles|all" >&2; exit 64 ;;
esac
exit $fails
