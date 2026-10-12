import json, os, sys, hashlib, glob
R = sys.argv[1]
def chash(d):
    h = hashlib.sha256()
    pj = json.load(open(os.path.join(d, "packet.json"))); pj.pop("packet")
    h.update(json.dumps(pj, sort_keys=True).encode())
    for f in sorted(os.listdir(d)):
        if f not in ("packet.json", "QUESTIONS.md"):
            h.update(f.encode()); h.update(open(os.path.join(d, f), "rb").read())
    return h.hexdigest()
syn = {chash(os.path.join(R, "export-486/packets", n)) for n in os.listdir(R + "/export-486/packets")}
p30k = json.load(open(R + "/plants-p30-key.json"))
for ex in sorted(glob.glob(R + "/export-p30-*")) + sorted(glob.glob(R + "/export-p3-*[0-9]")):
    lab = os.path.basename(ex)
    kp = ex + "-key.json"
    plants = set(json.load(open(kp))["packets"]) if os.path.exists(kp) else set()
    if os.path.exists(kp):
        plants = {n for n, v in json.load(open(kp))["packets"].items() if v["plant"]}
    else:
        plants = set(p30k)
    names = os.listdir(ex + "/packets")
    nonplant = [n for n in names if n not in plants]
    out = [n for n in nonplant if chash(os.path.join(ex, "packets", n)) not in syn]
    print(lab, len(names), "nonplant", len(nonplant), "not-in-synthetic", len(out))
