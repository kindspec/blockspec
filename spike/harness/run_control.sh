#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
#
# The control arm. PRE-REGISTRATION §7: "The control arm is the gate. If the
# harness does not reproduce D8's prose result on D8's corpora, stop and fix the
# harness."
#
# This runs D8's OWN scripts, unmodified, out of a kindspec/research checkout.
# Nothing here is reimplemented -- that is the point. The only thing this spike
# supplies is the pin (see corpora.json), because a clone at HEAD is not the
# clone D8 ran against.
#
#   CORPORA=/path/to/corpora D8_DIR=/path/to/research/experiments/D8-identity \
#     ./run_control.sh
#
# CORPORA must contain rust-book/ obsidian-help/ cmspec/, each checked out at
# its pin. anchor_eval3.py hard-codes those relative paths, so this script runs
# from a directory holding them.
set -euo pipefail
set -f   # never let the shell expand a corpus glob; the callee wants it literal

HERE=$(cd "$(dirname "$0")" && pwd)
D8="${D8_DIR:?set D8_DIR to kindspec/research/experiments/D8-identity}"
CORPORA="${CORPORA:?set CORPORA to the directory holding the pinned clones}"

work=$(mktemp -d); trap 'rm -rf "$work"' EXIT
mkdir -p "$work/corpora"
for c in rust-book obsidian-help cmspec; do
  ln -s "$CORPORA/$c" "$work/corpora/$c"
done

echo "# control arm -- D8's own scripts, unmodified"
echo "# D8_DIR  $D8  (kindspec/research @ $(git -C "$D8" rev-parse HEAD 2>/dev/null || echo unknown))"
for c in rust-book obsidian-help cmspec; do
  printf '# pin     %-14s %s  (%s commits)\n' "$c" \
    "$(git -C "$CORPORA/$c" rev-parse HEAD)" \
    "$(git -C "$CORPORA/$c" rev-list --count HEAD)"
done
cd "$work"
echo
echo "############ anchor_eval2.py -- D8 §3.1 (stored id vs computed anchor) ############"
for gap in 1 5 25; do
  python3 "$D8/anchor_eval2.py" corpora/rust-book 'src/*.md' "$gap"
done

echo
echo "############ anchor_eval3.py -- D8 §3.2 (block-type breakdown) ############"
python3 "$D8/anchor_eval3.py" | tee "$work/ae3.txt"

echo
echo "############ GATE ############"
python3 "$HERE/check_control_gate.py" < "$work/ae3.txt"
