import json, sys, glob, os
R = sys.argv[1]
def load(p):
    d = {}
    for l in open(p):
        if l.strip():
            o = json.loads(l); d.setdefault(o["packet"], o)
    return d
def one(pat): return load(glob.glob(R + "/" + pat + "/state/tiers.jsonl")[0])
def tier(o): return "U" if o.get("unplaceable") else ("A" if o["q2"]=="yes" else "B" if o["q1"]=="yes" else "C")
q = lambda o: tier(o) in "AB" and o["q3"]=="no" and o["q4"]=="no"
key = json.load(open(R + "/rehearsal-key.json"))["packets"]
syn = {n for n, v in key.items() if not v["expected"]}
n120 = set(os.listdir(R + "/export-120/packets")) & syn
runs = {"run-120 (prereg2 prompt)": one("run-120-*"), "run-486 (prereg2 prompt)": one("run-486-*"), "run-486m (prereg3 prompt)": one("run-486m-*")}
for lab, t in runs.items():
    c = sorted(n120 & set(t))
    print(f"{lab}: on the {len(c)} non-plant packets of export-120: qualify-shaped {sum(q(t[n]) for n in c)}, q3=no {sum(t[n]['q3']=='no' for n in c)}, q4=no {sum(t[n]['q4']=='no' for n in c)}")
