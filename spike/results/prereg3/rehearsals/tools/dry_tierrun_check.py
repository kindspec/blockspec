"""Dry preflight of prereg 2's bound tier-run in a given checkout. It runs
only the checks prereg2.py's tier-run runs before it would start an agent,
and never starts one:
- p2.binding.check(spike, "tier-run"): the binding;
- p2.tierrun.scoring_commit(spike): the scoring-arm commit, derived;
- tier-model.json present, and its scoring_commit equal to that;
- p2.gaps.load_gaps(spike, scoring commit, arms): the §9 gap rule.
It also reports whether ef62c84 is an ancestor of HEAD, and whether prereg 3's
export-3 commit is, for prereg 3's committed order check.

usage: python3 -I -S -B dry_tierrun_check.py <spike dir>
"""
import json
import os
import subprocess
import sys

spike = os.path.abspath(sys.argv[1])
sys.path.insert(0, os.path.join(spike, "harness"))
from p2 import binding as BD  # noqa: E402
from p2 import corpus as K  # noqa: E402
from p2 import gaps as GP  # noqa: E402
from p2 import tierrun as TRN  # noqa: E402


def git(*a):
    return subprocess.run(["git", "-C", spike, *a], capture_output=True, text=True, env=BD.git_env())


print("checkout:", spike)
print("HEAD:", git("rev-parse", "HEAD").stdout.strip(), git("branch", "--show-current").stdout.strip())
st, reasons = BD.check(spike, "tier-run")
print("p2 binding for tier-run: bound =", st["bound"], "; validation commit", st.get("validation_commit"))
for r in reasons:
    print("  not bound:", r)
try:
    sc = TRN.scoring_commit(spike)
    print("scoring-arm commit (derived):", sc)
except TRN.TierRefused as e:
    sc = None
    print("scoring-arm commit: REFUSED:", e)
mp = os.path.join(spike, "results", "prereg2", "tier-model.json")
if os.path.exists(mp):
    m = json.load(open(mp))
    print("tier-model.json: model", m["model"], "; scoring_commit matches:", m.get("scoring_commit") == sc)
else:
    print("tier-model.json: MISSING")
if sc:
    try:
        gaps, notes = GP.load_gaps(spike, sc, K.ARMS)
        print("gap rule: ok;", len(gaps), "gap(s)")
    except GP.GapError as e:
        print("gap rule: REFUSED:", e)
for label, c in (("ef62c84", "ef62c84"), ("export 3 (adds results/prereg3/export)", None)):
    if c is None:
        out = git("log", "--full-history", "--format=%H", "--diff-filter=A", "--", "results/prereg3/export").stdout.split()
        c = out[0] if len(out) == 1 else None
        if c is None:
            print(f"{label}: not in HEAD's history")
            continue
    anc = git("merge-base", "--is-ancestor", c, "HEAD").returncode == 0
    print(f"{label} {c[:12]} is an ancestor of HEAD: {anc}")
