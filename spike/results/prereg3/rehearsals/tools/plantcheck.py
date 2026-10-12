"""Run candidate plants through the prototype harness's own evaluate() path
(one-leg TLLC, §5.2 REPEAT and SPLIT, the hardened quote resolver), as
p2.export.plant_records does for a real plant.

usage: python3 -I -S -B plantcheck.py <harness dir> <d8 dir> <candidates.py>
candidates.py defines PLANTS = {name: (before, after, k)}.
"""
import json
import runpy
import sys

harness, d8, cand = sys.argv[1:4]
sys.path.insert(0, harness)
from p2 import mech as Mx  # noqa: E402
Mx.load(d8)
from p2 import evaluate as E  # noqa: E402

PLANTS = runpy.run_path(cand)["PLANTS"]
ok_all = True
for n, (base, after, k) in PLANTS.items():
    inst = {"arm": "plant", "mode": "E", "id": f"plant:{n}", "path": "doc.md",
            "before": base, "after": after, "legs": None, "f2": True}
    recs, _ = E.evaluate(inst)
    r = [x for x in recs if x["mech"] == "Q" and x["index"] == k][0]
    good = bool(r.get("decided") and r["hard"]["cls"] == "WRONG" and r["wf"] and r.get("nl"))
    ok_all &= good
    print(f"{n}: type={r.get('type')} oracle={r.get('oracle')} target={r.get('target')} "
          f"hard={r['hard']['status']},{r['hard']['hit']} cls={r['hard']['cls']} "
          f"naive={r['naive']['status']},{r['naive']['hit']} wf={r['wf']} -> {'OK' if good else 'FAIL'}")
    if good:
        print("   mechanism_target:", json.dumps(r["hard"]["mechanism_target_text"]))
        print("   oracle_target:   ", json.dumps(r["oracle_target_text"]))
print("PLANTS:", "PASS" if ok_all else "FAIL")
sys.exit(0 if ok_all else 1)
