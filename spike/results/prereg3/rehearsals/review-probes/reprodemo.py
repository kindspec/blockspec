import sys
sys.path.insert(0, sys.argv[1])
from p2 import aggregate as AG, export as X, corpus as K
nonce = "00" * 32
man = {"nonce": nonce, "plants": {n: {"key": f"plant:{n}", "expected": X.PLANT_EXPECT[n]} for n in X.PLANT_EXPECT}}
inst = {("k8s-en", "i1"): {"arm": "k8s-en", "mode": "E", "rules": [K.VERDICT_RULE, "none", "anywhere"]}}
recs = [{"id": "i1|0", "arm": "k8s-en", "mode": "E", "mech": "Q", "instance": "i1", "unit": "u" * 64,
         "hard": {"cls": "WRONG", "mechanism_target_text": "m"}, "oracle_target_text": "o", "oracle": "SURVIVED",
         "decided": True, "f2": True, "wf": True, "nl": True}]
for i in range(400):  # enough decided units for the floor
    recs.append({"id": f"i1|{i+1}", "arm": "k8s-en", "mode": "E", "mech": "Q", "instance": "i1", "unit": f"{i:064d}",
                 "hard": {"cls": "RIGHT", "mechanism_target_text": "x"}, "oracle": "SURVIVED", "decided": True,
                 "f2": True, "wf": True, "nl": True})
key = X.packet_key(recs[0]); name = X.packet_name(nonce, key)
tiers = {name: {"packet": name, "q1": "yes", "q2": "yes", "q3": "no", "q4": "no", "unplaceable": False}}
for p, v in man["plants"].items():
    e = v["expected"]; n = X.packet_name(nonce, v["key"])
    tiers[n] = dict(packet=n, unplaceable=False, **{q: e[q] for q in ("q1", "q2", "q3", "q4")})
arm0 = {"k8s-en": {"passes_bar": True}}
scores = {"k8s-en": {"modes": ["E"], "instances": inst, "records": recs}}
good = {"id": "i1|0", "ok": True, "bound": True, "committed_sha256": "a" * 64, "regenerated_sha256": "a" * 64}
for lab, rp in (("repro bound to this validation commit", good),
                ("same repro, marked unbound (other validation commit)", dict(good, bound=False))):
    c = AG.aggregate(arm0, scores, man, tiers, {"i1|0": rp})["cells"][("k8s-en", "E", "Q")]
    print(lab, "->", c["verdict"], "|", c["reason"][:110])
