#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
#
# The cheap arm: D8's single-edit anchor analysis (anchor_eval3) and its
# quote-uniqueness measurement (e4_uniqueness) on the three corpora
# PRE-REGISTRATION.md §5.1 names and pins. Input to a pre-registration not yet
# written; it decides nothing. See LOG.md §12.
#
#   CORPORA=/path/to/clones D8_DIR=/path/to/research/experiments/D8-identity \
#     spike/harness/run_cheap_arm.sh
#
# CORPORA holds full working-tree clones, each checked out at its pin:
#   rust-book obsidian-help cmspec          D8-identity.md §3's pins -- NOT
#                                           harness/corpora.json's, which pin an
#                                           earlier tree on purpose
#   k8s-website cncf-toc site-policy        PRE-REGISTRATION.md §5.1's pins
#
# Stages, each of which stops the run on failure:
#   1. validation  -- the adapted driver reproduces results-e4.txt and
#                     results-anchor3.txt byte for byte at D8 §3's pins
#   2. red states  -- the originals exit 0 on an empty run; the adapted
#                     driver exits non-zero on each way of reading nothing
#   3. the corpora -- selection census, uniqueness at 20/40/120, anchors at
#                     gaps 1/5/25; each with D8's classifier and again with
#                     frontmatter typed separately; and every silent-wrong
#                     printed (anchors-silent-wrongs.txt)
set -euo pipefail
set -f   # pathspecs are passed literally

HERE=$(cd "$(dirname "$0")" && pwd)
D8="${D8_DIR:?set D8_DIR to kindspec/research/experiments/D8-identity}"
CORPORA="${CORPORA:?set CORPORA to the directory holding the pinned clones}"
OUT="${OUT:-$HERE/../results/cheap-arm}"
mkdir -p "$OUT"
ARM=(python3 -I "$HERE/d8_cheap_arm.py")
export PYTHONDONTWRITEBYTECODE=1   # for the original scripts in stage 2

D8_CORPORA=(
  --corpus rust-book     "$CORPORA/rust-book"     1500248d8f230566e4ec9f27fcbb8fe9e2898ab1 'src/*.md'
  --corpus obsidian-help "$CORPORA/obsidian-help" 327a782e90481268361b5ccccdb0c224b2b13fe6 'en/*.md'
  --corpus cmspec        "$CORPORA/cmspec"        3da939428d80f146f270cd1765e4ba462e96bb1b '*.md'
)
# The prose-subset rule (LOG.md §12): the directory the published site renders
# from where there is one (kubernetes/website: content/), else the whole
# repository; minus forge metadata (.github/); minus, by --exclude-generated,
# files whose own text declares them generated. k8s-website-en is the English
# source alone, reported beside the all-languages arm, not instead of it.
NEW_CORPORA=(
  --corpus k8s-website    "$CORPORA/k8s-website" 6b27baef1e44275fd4368e14375296e1dfe5af11 'content/*.md'
  --corpus k8s-website-en "$CORPORA/k8s-website" 6b27baef1e44275fd4368e14375296e1dfe5af11 'content/en/*.md'
  --corpus cncf-toc       "$CORPORA/cncf-toc"    144c2e3215884e498e744cc51e6b7cef82d654f1 '*.md :(exclude).github/'
  --corpus site-policy    "$CORPORA/site-policy" b9578b546d2506febda1da2cd7431644d58e512c '*.md :(exclude).github/'
)

# ---- 1. validation -----------------------------------------------------------
v="$OUT/validation.txt"
{
  echo "research: $(git -C "$D8" rev-parse HEAD)  $(git -C "$D8" status --porcelain -- . | wc -l) modified paths under D8-identity"
  for n in 20 40 120; do "${ARM[@]}" uniqueness --d8-dir "$D8" "${D8_CORPORA[@]}" --minlen "$n"; done > "$OUT/.e4"
  "${ARM[@]}" anchors --d8-dir "$D8" "${D8_CORPORA[@]}" > "$OUT/.a3"
  for pair in ".e4 results-e4.txt" ".a3 results-anchor3.txt"; do
    set -- $pair
    echo "$(sha256sum < "$OUT/$1" | cut -c1-64)  adapted driver"
    echo "$(sha256sum < "$D8/$2" | cut -c1-64)  research $2"
    if cmp "$OUT/$1" "$D8/$2"; then echo "BYTE-IDENTICAL: $2"; else echo "DIFFERS: $2"; fi
  done
} > "$v"
rm -f "$OUT/.e4" "$OUT/.a3"
cat "$v"
grep -q DIFFERS "$v" && { echo "validation failed -- stop" >&2; exit 1; }

# ---- 2. red states -----------------------------------------------------------
r="$OUT/red-states.txt"
scratch=$(mktemp -d); trap 'rm -rf "$scratch"' EXIT
mkdir "$scratch/empty"
git init -q "$scratch/shallow"
printf '# t\n\nOne paragraph of prose that is long enough to count.\n' > "$scratch/shallow/a.md"
git -C "$scratch/shallow" -c user.name=t -c user.email=t@t add a.md
git -C "$scratch/shallow" -c user.name=t -c user.email=t@t commit -qm t
SH=$(git -C "$scratch/shallow" rev-parse HEAD)
git init -q "$scratch/blank"
: > "$scratch/blank/a.md"
git -C "$scratch/blank" -c user.name=t -c user.email=t@t add a.md
git -C "$scratch/blank" -c user.name=t -c user.email=t@t commit -qm t
BL=$(git -C "$scratch/blank" rev-parse HEAD)
RB=1500248d8f230566e4ec9f27fcbb8fe9e2898ab1
fails=0
run() {  # run <expect: zero|nonzero> <label> <cmd...>
  local want=$1 label=$2; shift 2
  set +e; "$@" > "$scratch/out" 2> "$scratch/err"; local rc=$?; set -e
  local ok=no
  { [ "$want" = zero ] && [ $rc -eq 0 ]; } && ok=yes
  { [ "$want" = nonzero ] && [ $rc -ne 0 ]; } && ok=yes
  [ $ok = yes ] || fails=$((fails+1))
  echo "== $label"
  echo "   exit=$rc (expected $want) -> $([ $ok = yes ] && echo as-expected || echo UNEXPECTED)"
  sed 's/^/   stdout| /' "$scratch/out" | head -4
  sed 's/^/   stderr| /' "$scratch/err" | head -2
}
{
  echo "-- the originals, run from a directory with no corpora/ (kindspec/research#6)"
  run zero "original e4_uniqueness.py 40, wrong cwd" \
    bash -c 'cd "$1" && python3 "$2/e4_uniqueness.py" 40' _ "$scratch/empty" "$D8"
  run zero "original anchor_eval3.py, wrong cwd" \
    bash -c 'cd "$1" && python3 "$2/anchor_eval3.py"' _ "$scratch/empty" "$D8"
  echo
  echo "-- the adapted driver, each way of reading nothing"
  run nonzero "uniqueness: corpus path does not exist" \
    "${ARM[@]}" uniqueness --d8-dir "$D8" --corpus rust-book "$scratch/empty/rust-book" $RB 'src/*.md'
  run nonzero "uniqueness: path exists, is not a git work tree" \
    "${ARM[@]}" uniqueness --d8-dir "$D8" --corpus rust-book "$scratch/empty" $RB 'src/*.md'
  run nonzero "uniqueness: HEAD is not the stated pin" \
    "${ARM[@]}" uniqueness --d8-dir "$D8" --corpus rust-book "$CORPORA/rust-book" 917544888a55e4da7109bdba8c88c893c0da70f4 'src/*.md'
  run nonzero "uniqueness: pathspec selects nothing" \
    "${ARM[@]}" uniqueness --d8-dir "$D8" --corpus rust-book "$CORPORA/rust-book" $RB 'en/*.md'
  run nonzero "uniqueness: files read, zero blocks" \
    "${ARM[@]}" uniqueness --d8-dir "$D8" --corpus blank "$scratch/blank" "$BL" '*.md'
  run nonzero "anchors: pathspec selects nothing" \
    "${ARM[@]}" anchors --d8-dir "$D8" --corpus rust-book "$CORPORA/rust-book" $RB 'en/*.md'
  run nonzero "anchors: files selected, no version pair at any gap" \
    "${ARM[@]}" anchors --d8-dir "$D8" --corpus shallow "$scratch/shallow" "$SH" '*.md'
  run nonzero "--d8-dir without the D8 scripts" \
    "${ARM[@]}" anchors --d8-dir "$scratch/empty" --corpus rust-book "$CORPORA/rust-book" $RB 'src/*.md'
  echo
  echo "-- the validation gate itself: frontmatter typing relabels D8's YAML"
  echo "   silent-wrong (D8 §3.2), so stage 1's cmp must now report a difference"
  run nonzero "cmp of results-anchor3.txt against a --frontmatter-type run" \
    bash -c 'o=$0 d=$1; shift; "$@" > "$o" && cmp "$o" "$d/results-anchor3.txt"' "$scratch/a3fm" "$D8" \
    "${ARM[@]}" anchors --d8-dir "$D8" "${D8_CORPORA[@]}" --frontmatter-type
  echo
  echo "unexpected exits: $fails"
} > "$scratch/red"
# local paths are not committed: name them by the variable that set them
sed -e "s|$scratch|\$SCRATCH|g" -e "s|$CORPORA|\$CORPORA|g" -e "s|$D8|\$D8_DIR|g" "$scratch/red" > "$r"
cat "$r"
[ "$fails" -eq 0 ] || { echo "red-state check failed -- stop" >&2; exit 1; }

# ---- 3. the corpora ----------------------------------------------------------
"${ARM[@]}" select --d8-dir "$D8" "${NEW_CORPORA[@]}" --exclude-generated > "$OUT/selection.txt"
"${ARM[@]}" select --d8-dir "$D8" "${NEW_CORPORA[@]}" > "$OUT/selection-before-generated-rule.txt"
for fm in "" --frontmatter-type; do
  sfx=${fm:+-frontmatter}
  for n in 20 40 120; do
    "${ARM[@]}" uniqueness --d8-dir "$D8" "${NEW_CORPORA[@]}" --exclude-generated $fm --minlen "$n"
  done > "$OUT/uniqueness$sfx.txt"
  "${ARM[@]}" anchors --d8-dir "$D8" "${NEW_CORPORA[@]}" --exclude-generated $fm --gaps 1,5,25 \
    > "$OUT/anchors$sfx.txt"
done
"${ARM[@]}" anchors --d8-dir "$D8" "${NEW_CORPORA[@]}" --exclude-generated --frontmatter-type \
  --gaps 1,5,25 --show-wrong > "$OUT/anchors-silent-wrongs.txt"
ls -l "$OUT"
