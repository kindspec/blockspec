import json, os, sys, hashlib
X, R = sys.argv[1], sys.argv[2]
def chash(d):
    h = hashlib.sha256()
    pj = json.load(open(os.path.join(d, "packet.json"))); pj.pop("packet")
    h.update(json.dumps(pj, sort_keys=True).encode())
    for f in sorted(os.listdir(d)):
        if f not in ("packet.json",):
            h.update(f.encode()); h.update(open(os.path.join(d, f), "rb").read())
    return h.hexdigest()[:12]
real = {n: chash(os.path.join(X, "packets", n)) for n in ("<P2-PLANT-A-NAME>", "<P2-PLANT-B-NAME>", "<P2-PLANT-C-NAME>")}
print("real plants", real)
k = json.load(open(os.path.join(R, "plants-p30-key.json")))
for name, v in sorted(k.items(), key=lambda x: (x[1]["run"], x[1]["plant"])):
    p = os.path.join(R, "export-p30-%d" % v["run"], "packets", name)
    print(v["run"], v["plant"], name, chash(p), chash(p) in real.values())
