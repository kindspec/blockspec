"""Report P-D's and P-E's q3 answer and full `why` for every run of the
given label prefixes, and flag a P-E "yes" whose why does not mention the
stale content (a 50 GB / 80 GB value, or the words stale/old/leftover/
outdated/raised). The flag is a pointer for reading, not the judgement.

usage: python3 -I -S -B pdpe_q3.py <rehearsal dir> <prefix>...
"""
import glob
import json
import os
import re
import sys

root = sys.argv[1]
CONTENT = re.compile(r"50 ?GB|80 ?GB|stale|old|leftover|outdated|raised|superseded", re.I)
for pfx in sys.argv[2:]:
    for kp in sorted(glob.glob(os.path.join(root, f"export-{pfx}-*-key.json")),
                     key=lambda p: int(p.rsplit("-", 2)[-2])):
        label = os.path.basename(kp)[len("export-"):-len("-key.json")]
        key = json.load(open(kp))["packets"]
        for run in sorted(glob.glob(os.path.join(root, f"run-{label}-2*"))):
            t = os.path.join(run, "state", "tier-work-1", "tiers.jsonl")
            ans = {}
            for ln in open(t, encoding="utf-8") if os.path.exists(t) else []:
                if ln.strip():
                    o = json.loads(ln)
                    ans.setdefault(o["packet"], o)
            for n, v in sorted(key.items(), key=lambda x: str(x[1]["plant"])):
                if v["plant"] not in ("P-D", "P-E"):
                    continue
                a = ans.get(n)
                if a is None:
                    print(f"{os.path.basename(run)} {v['plant']} UNTIERED")
                    continue
                flag = ""
                if v["plant"] == "P-E" and a["q3"] == "yes" and not CONTENT.search(a["why"]):
                    flag = "  [CHECK: no stale-content words]"
                print(f"{os.path.basename(run)} {v['plant']} q3={a['q3']}{flag} | {a['why']}")
