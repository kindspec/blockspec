import json, sys, glob, collections
R = sys.argv[1]
def load(p):
    d = {}
    for l in open(p):
        if l.strip():
            o = json.loads(l); d.setdefault(o["packet"], o)
    return d
a = load(glob.glob(R + "/run-486-*/state/tiers.jsonl")[0])
b = load(glob.glob(R + "/run-486m-*/state/tiers.jsonl")[0])
def tier(o):
    return "U" if o.get("unplaceable") else ("A" if o["q2"] == "yes" else "B" if o["q1"] == "yes" else "C")
common = sorted(set(a) & set(b))
print("common", len(common))
for q in ("q1", "q2", "q3", "q4"):
    ca = collections.Counter(a[n][q] for n in common); cb = collections.Counter(b[n][q] for n in common)
    agree = sum(a[n][q] == b[n][q] for n in common)
    print(q, "prereg2-prompt", dict(ca), "prereg3-prompt", dict(cb), "agree", agree)
ta = collections.Counter(tier(a[n]) for n in common); tb = collections.Counter(tier(b[n]) for n in common)
print("tier p2", dict(ta), "p3", dict(tb), "agree", sum(tier(a[n]) == tier(b[n]) for n in common))
qual = lambda o: tier(o) in "AB" and o["q3"] == "no" and o["q4"] == "no"
print("would-qualify (A/B, q3 no, q4 no): p2", sum(qual(a[n]) for n in common), "p3", sum(qual(b[n]) for n in common), "agree", sum(qual(a[n]) == qual(b[n]) for n in common))
