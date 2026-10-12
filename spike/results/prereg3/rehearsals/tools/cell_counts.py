"""Per-cell exported-packet counts from prereg 2's committed scores.
Aggregates only: prints a count per (arm, mode, mech) cell and totals, and
never prints a record, a reference, a target or a packet name.

The per-cell count is the same set p2/aggregate.py's cell() calls `keys`:
packet keys of in-cell records that p2/export.py's eligible() exports.

usage: python3 -I -S -B cell_counts.py <harness dir> <score dir>
"""
import glob
import gzip
import json
import os
import sys

harness, score_dir = sys.argv[1:3]
sys.path.insert(0, harness)
from p2 import aggregate as AG  # noqa: E402
from p2 import export as X  # noqa: E402

allkeys = set()
rows = []
for st in sorted(glob.glob(os.path.join(score_dir, "*", "status.json"))):
    d = os.path.dirname(st)
    s = json.load(open(st))
    arm = s["arm"]
    if "no_verdict" in s:
        rows.append((arm, "-", "-", "NO VERDICT at scoring"))
        continue
    inst = {}
    for line in open(os.path.join(d, "instances.jsonl"), encoding="utf-8"):
        o = json.loads(line)
        o.pop("texts", None)
        inst[(o["arm"], o["id"])] = o
    per = {(m, q): set() for m in AG.MODES for q in AG.MECHS}
    for line in gzip.open(os.path.join(d, "units.jsonl.gz"), "rt", encoding="utf-8"):
        r = json.loads(line)
        i = inst[(r["arm"], r["instance"])]
        if r["mode"] not in AG.MODES or not AG.in_cell(i):
            continue
        if X.eligible(r, i):
            k = X.packet_key(r)
            per[(r["mode"], r["mech"])].add(k)
            allkeys.add(k)
    for (m, q), ks in sorted(per.items()):
        rows.append((arm, m, q, len(ks) if m in s["modes"] else f"{len(ks)} (mode not run)"))
    del inst
for r in rows:
    print(f"{r[0]:<14}{r[1]:<5}{r[2]:<3}{r[3]}")
print("distinct exported packet keys over all cells:", len(allkeys))
