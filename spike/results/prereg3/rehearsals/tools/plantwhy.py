"""Print each plant's answers and `why` for prereg-3 rehearsal runs.

usage: python3 -I -S -B plantwhy.py <rehearsal dir> <label>...
"""
import glob
import json
import os
import sys

root = sys.argv[1]
for label in sys.argv[2:]:
    key = json.load(open(os.path.join(root, f"export-{label}-key.json")))["packets"]
    for run in sorted(glob.glob(os.path.join(root, f"run-{label}-2*"))):
        t = os.path.join(run, "state", "tier-work-1", "tiers.jsonl")
        ans = {}
        for ln in open(t, encoding="utf-8") if os.path.exists(t) else []:
            if ln.strip():
                o = json.loads(ln)
                ans.setdefault(o["packet"], o)
        print("==", os.path.basename(run), len(ans), "answered")
        for n, v in sorted(key.items(), key=lambda x: str(x[1]["plant"])):
            if not v["plant"]:
                continue
            a, e = ans.get(n), v["expected"]
            if a is None:
                print(f"  {v['plant']}: UNTIERED")
                continue
            got = " ".join(a[q] for q in ("q1", "q2", "q3", "q4"))
            ok = all(a[q] == e[q] for q in ("q1", "q2", "q3", "q4")) and not a.get("unplaceable")
            print(f"  {v['plant']}: {got} {'OK' if ok else 'MISMATCH'} | {a.get('why')}")
