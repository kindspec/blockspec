#!/usr/bin/env bash
# shellcheck disable=SC2015  # ok() always succeeds, so A && ok || bad is if-then-else
# SPDX-License-Identifier: MIT
# The review step of each PRE-REGISTRATION-2.md §9 pull request, run in a
# fresh clone of the merged result (README.md, "What the harness checks";
# LOG.md §20, §22). It re-derives the validation commit, the Arm 0 commit
# and the scoring-arm commit from history alone, and checks what the harness
# cannot check about itself. Each check prints PASS or FAIL; the exit
# status is 1 if any failed.
#
#   harness/prereg2_reverify.sh [spike-dir]    (default: this script's ../)
set -u
spike=${1:-$(cd "$(dirname "$0")/.." && pwd)}
for v in $(env | sed -n 's/^\(GIT_[A-Za-z0-9_]*\)=.*/\1/p'); do unset "$v"; done
export GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null GIT_NO_REPLACE_OBJECTS=1
g() { git -C "$spike" "$@"; }
bound=(harness PRE-REGISTRATION-2.md ORACLE.md)
fails=0
ok() { echo "PASS  $*"; }
bad() { echo "FAIL  $*"; fails=$((fails + 1)); }
adders() { g log --full-history --format=%H --diff-filter=A -- "$1"; }

[ "$(g rev-parse --is-shallow-repository 2>/dev/null)" = false ] && ok "not shallow" || bad "shallow or not a repository"
[ -z "$(g replace -l 2>/dev/null)" ] && ok "no replace refs" || bad "replace refs present"
[ ! -e "$(g rev-parse --git-common-dir 2>/dev/null)/info/grafts" ] && ok "no grafts" || bad "info/grafts present"

mapfile -t vcs < <(adders results/prereg2/VALIDATION)
if [ "${#vcs[@]}" -ne 1 ]; then
  bad "${#vcs[@]} commits add results/prereg2/VALIDATION; exactly one must"
  echo "$fails failed"; exit 1
fi
V=${vcs[0]}
ok "validation commit $V"
if g rev-parse --verify -q "$V^" >/dev/null && g diff --quiet "$V^" "$V" -- "${bound[@]}"; then
  ok "the validation commit adds VALIDATION only"
else
  bad "the validation commit has no parent, or changes the harness, PRE-REGISTRATION-2.md or ORACLE.md"
fi
later=$(g log --full-history --format=%H "$V..HEAD" -- "${bound[@]}")
[ -z "$later" ] && ok "no later commit touches the harness or the frozen documents" \
  || bad "later commits touch the harness or the frozen documents: $later"
[ "$(g log --full-history --format=%H -- results/prereg2/VALIDATION | wc -l)" -eq 1 ] \
  && ok "VALIDATION never changed" || bad "VALIDATION changed after it was added"
others=$(grep -rhoE '"validation_commit": *"[0-9a-f]{40}"' "$spike/results/prereg2" 2>/dev/null \
  | grep -oE '[0-9a-f]{40}' | sort -u | grep -vx "$V")
[ -z "$others" ] && ok "every output that names a validation commit names $V" \
  || bad "outputs name another validation commit: $others"

mapfile -t a0 < <(adders results/prereg2/arm0)
case ${#a0[@]} in
  0) ok "no Arm 0 commit yet" ;;
  1) ok "Arm 0 commit ${a0[0]}" ;;
  *) bad "${#a0[@]} commits add results/prereg2/arm0" ;;
esac
mapfile -t sc < <(adders results/prereg2/score)
case ${#sc[@]} in
  0) ok "no scoring-arm commit yet" ;;
  1) ok "scoring-arm commit ${sc[0]}" ;;
  *) bad "${#sc[@]} commits add results/prereg2/score" ;;
esac
tm="$spike/results/prereg2/tier-model.json"
if [ -e "$tm" ]; then
  rec=$(python3 -I -S -c 'import json,sys; print(json.load(open(sys.argv[1]))["scoring_commit"])' "$tm" 2>/dev/null)
  if [ "${#sc[@]}" -eq 1 ] && [ "$rec" = "${sc[0]}" ]; then
    ok "tier-model recorded the scoring-arm commit"
  else
    bad "tier-model recorded ${rec:-nothing}, not the one scoring-arm commit"
  fi
else
  ok "no tier-model.json yet"
fi
echo "gaps.json versions (commit, committer date), to read against the commits above:"
g log --full-history --format='  %H %cI' -- results/prereg2/gaps.json
[ "$fails" -eq 0 ] && { echo "reverify: PASS"; exit 0; }
echo "reverify: $fails failed"; exit 1
