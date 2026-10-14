#!/usr/bin/env -S python3 -I -S -B
# SPDX-License-Identifier: MIT
"""PRE-REGISTRATION-3.md §8: name every qualifying packet's answers, for the
run-2 verdict. A packet qualifies when it is in the key set of a cell that
p2.aggregate.cell() computes (the verdict rule's selection, eligible
records) and its representative record passes the packet-level tests that
cell() applies: a tier line, not unplaceable, q4 "no" (F6), reproduced (F9),
q3 "no" (F7) and tier A or B (F8). The check against verdict.json: the
distinct units of each cell's qualifying packets must equal the cell's
`qualifying_distinct`.

Prints a Markdown table: packet name, tier, q1-q4, unplaceable, and the
cells it qualifies in. The tierer's free-text `why` is not printed.

usage: python3 -I -S -B ruling/qualifying_run2.py <spike dir> <sealed manifest> <out.md>

    e.g. ruling/qualifying_run2.py . results/prereg3/sealed-manifest.json results/prereg3/run2/qualifying.md
"""
import collections
import glob
import gzip
import json
import os
import sys

spike, manifest, out = sys.argv[1:4]
sys.path[:0] = [os.path.join(spike, "harness3"), os.path.join(spike, "harness")]
from p2 import aggregate as AG  # noqa: E402
from p2 import export as X  # noqa: E402
from p2 import tiers as T  # noqa: E402
from p3 import aggregate3 as A3  # noqa: E402
from p3 import binding as BD  # noqa: E402
from p3 import plants as PL  # noqa: E402

R2 = os.path.join(spike, "results", "prereg2")
R3 = os.path.join(spike, "results", "prereg3")
m = PL.load_manifest(manifest, json.load(open(os.path.join(R3, "VALIDATION")))["manifest_sha256"])
verdict = json.load(open(os.path.join(R3, "run2", "verdict.json")))
arm0 = {}
for p in sorted(glob.glob(os.path.join(R2, "arm0", "*.json"))):
    o = json.load(open(p))
    arm0[o["arm"]] = o
scores = {}
for st in sorted(glob.glob(os.path.join(R2, "score", "*", "status.json"))):
    d = os.path.dirname(st)
    s = json.load(open(st))
    if "no_verdict" in s:
        continue
    inst = {}
    for line in open(os.path.join(d, "instances.jsonl"), encoding="utf-8"):
        o = json.loads(line)
        inst[(o["arm"], o["id"])] = o
    recs = [json.loads(line) for line in gzip.open(os.path.join(d, "units.jsonl.gz"), "rt", encoding="utf-8")]
    scores[s["arm"]] = {"modes": s["modes"], "instances": inst, "records": recs}
tiers, problems = T.read_tiers(os.path.join(R3, "tier-work-2", "tiers.jsonl"))
assert not problems
load = lambda d: [json.load(open(p)) for p in sorted(glob.glob(os.path.join(d, "*.json")))]  # noqa: E731
repro = A3.accept_repros(load(os.path.join(R2, "repro")), load(os.path.join(R3, "repro")),
                         BD.derive_validation(spike, BD.PREREG3)[0])
recs_all, inst_all = [], {}
for sc in scores.values():
    recs_all += sc["records"]
    inst_all.update(sc["instances"])
reps = X.select_packets(recs_all, inst_all)

qual = collections.defaultdict(list)
mismatch = []
for arm in AG.K.ARM_ORDER:
    a0, sc = arm0.get(arm, {}), scores.get(arm)
    if not a0.get("passes_bar") or sc is None:
        continue
    inst = sc["instances"]
    for mode in AG.MODES:
        if mode not in sc["modes"]:
            continue
        for mech in AG.MECHS:
            mine = [r for r in sc["records"] if r["mode"] == mode and r["mech"] == mech and r["arm"] == arm]
            recs = [r for r in mine if AG.in_cell(inst[(arm, r["instance"])])]
            keys = {X.packet_key(r) for r in recs if X.eligible(r, inst[(arm, r["instance"])])}
            units = set()
            for key in keys:
                rep = reps[key]
                name = X.packet_name(m["nonce"], key)
                ans = tiers.get(name)
                if ans is None or T.tier_of(ans) == "UNPLACEABLE" or ans["q4"] != "no":
                    continue
                if not AG.reproduced(repro[rep["id"]]):
                    continue
                if ans["q3"] == "no" and T.tier_of(ans) in ("A", "B"):
                    qual[name].append(f"{arm} {mode} {mech}")
                    units.add(X.unit_key(rep))
            want = verdict["cells"][f"{arm}|{mode}|{mech}"].get("qualifying_distinct", 0)
            if len(units) != want:
                mismatch.append(f"{arm} {mode} {mech}: {len(units)} != {want}")

print("qualifying packets:", len(qual), "; cells checked against verdict.json, mismatches:", mismatch or 0)
pat = collections.Counter((T.tier_of(tiers[n]),) + tuple(tiers[n][q] for q in ("q1", "q2", "q3", "q4"))
                          for n in qual)
print("answer patterns (tier, q1, q2, q3, q4):", dict(pat))
with open(out, "w") as f:
    pairs = sum(len(c) for c in qual.values())
    units = sum(c.get("qualifying_distinct", 0) for c in verdict["cells"].values())
    f.write(f"Rows are packets, not units. Several packets can share a unit, so the per-cell row counts here "
            f"({pairs} packet-cell pairs) exceed the verdict's distinct-unit counts ({units} units).\n\n")
    f.write("| packet | tier | q1 | q2 | q3 | q4 | unplaceable | qualifies in |\n|---|---|---|---|---|---|---|---|\n")
    for n in sorted(qual):
        a = tiers[n]
        f.write(f"| `{n}` | {T.tier_of(a)} | {a['q1']} | {a['q2']} | {a['q3']} | {a['q4']} | "
                f"{str(bool(a['unplaceable'])).lower()} | {'; '.join(qual[n])} |\n")
print("wrote", out)
