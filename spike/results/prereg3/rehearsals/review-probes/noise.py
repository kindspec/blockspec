import json, sys, glob, collections, os
R = sys.argv[1]
def load(p):
    d = {}
    for l in open(p):
        if l.strip():
            o = json.loads(l); d.setdefault(o["packet"], o)
    return d
def one(pat): return load(glob.glob(R + "/" + pat + "/state/tiers.jsonl")[0])
r120, r486, r486m = one("run-120-*"), one("run-486-*"), one("run-486m-*")
n120 = set(os.listdir(R + "/export-120/packets")); n486 = set(os.listdir(R + "/export-486/packets"))
print("120 subset of 486:", n120 <= n486)
def cmp(a, b, label, names=None):
    c = sorted((set(a) & set(b)) if names is None else names)
    out = [label, "n=%d" % len(c)]
    for q in ("q1","q2","q3","q4"):
        out.append("%s agree %d; yes %d vs %d" % (q, sum(a[n][q]==b[n][q] for n in c), sum(a[n][q]=="yes" for n in c), sum(b[n][q]=="yes" for n in c)))
    print(" | ".join(out))
cmp(r120, r486, "old-prompt 120 vs old-prompt 486")
cmp(r120, r486m, "old-prompt 120 vs new-prompt 486m")
cmp(r486, r486m, "old 486 vs new 486m")
# fillers in p3 runs (new prompt, 30-packet)
fill = collections.defaultdict(list)
for kp in sorted(glob.glob(R + "/export-p3-*-key.json")):
    lab = os.path.basename(kp)[len("export-"):-len("-key.json")]
    runs = glob.glob(R + "/run-%s-*/state/tiers.jsonl" % lab)
    if not runs: continue
    t = load(runs[0]); k = json.load(open(kp))["packets"]
    for name, v in k.items():
        if v["plant"] is None and name in t:
            fill[v["source"]].append(t[name])
src = sorted(fill)
rows = [(s, x) for s in src for x in fill[s]]
print("p3 filler answers:", len(rows), "distinct sources", len(src))
for q in ("q3","q4"):
    print(q, "p3-runs yes", sum(x[q]=="yes" for s,x in rows), "of", len(rows),
          "| agree w/ old 486", sum(x[q]==r486[s][q] for s,x in rows), "| agree w/ new 486m", sum(x[q]==r486m[s][q] for s,x in rows))
