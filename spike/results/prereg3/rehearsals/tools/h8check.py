"""V3 cases and V4 mutant for H8, on the prototype aggregate3, built on the
reviewer's h8demo2 fixture: one record that is FOUND when every plant is
right. The plants' "right" answers are written out here, independently of
aggregate3's PLANT_EXPECT3, so that a changed expectation in aggregate3 makes
the all-right case fail instead of following along.

Cases: all right -> FOUND; P-D q3 "no" -> void; P-E q4 "no" -> void;
P-C answered as tier B (q1 "yes", q3 and q4 still right) -> void by the B/C
line alone; propagation mutant; four-plant manifest refused.

usage: python3 -I -S -B h8check.py <p2 harness dir> <harness3 dir>
"""
import sys

sys.path.insert(0, sys.argv[1])
sys.path.insert(0, sys.argv[2])
from p2 import corpus as K  # noqa: E402
from p2 import export as X  # noqa: E402
from p3 import aggregate3 as A3  # noqa: E402

RIGHT = {  # Appendix B's expected answers, written out independently
    "P-A": ("yes", "yes", "no", "no"),
    "P-B": ("yes", "no", "no", "no"),
    "P-C": ("no", "no", "no", "no"),
    "P-D": ("yes", "yes", "yes", "no"),
    "P-E": ("yes", "yes", "yes", "yes"),
}
EXPECT = {p: {"q1": a[0], "q2": a[1], "q3": a[2], "q4": a[3],
              "tier": "A" if a[1] == "yes" else ("B" if a[0] == "yes" else "C")} for p, a in RIGHT.items()}
nonce = "00" * 32
man = {"nonce": nonce, "plants": {n: {"key": f"plant:{n}", "expected": EXPECT[n]} for n in EXPECT}}
inst = {("k8s-en", "i1"): {"arm": "k8s-en", "mode": "E", "rules": [K.VERDICT_RULE, "none", "anywhere"]}}
recs = [{"id": "i1|0", "arm": "k8s-en", "mode": "E", "mech": "Q", "instance": "i1", "unit": "u" * 64,
         "hard": {"cls": "WRONG", "mechanism_target_text": "m"}, "oracle_target_text": "o",
         "oracle": "SURVIVED", "decided": True, "f2": True, "wf": True, "nl": True}]
for i in range(400):
    recs.append({"id": f"i1|{i+1}", "arm": "k8s-en", "mode": "E", "mech": "Q", "instance": "i1",
                 "unit": f"{i:064d}", "hard": {"cls": "RIGHT", "mechanism_target_text": "x"},
                 "oracle": "SURVIVED", "decided": True, "f2": True, "wf": True, "nl": True})
name = X.packet_name(nonce, X.packet_key(recs[0]))
tiers = {name: {"packet": name, "q1": "yes", "q2": "yes", "q3": "no", "q4": "no", "unplaceable": False}}
for p, a in RIGHT.items():
    n = X.packet_name(nonce, f"plant:{p}")
    tiers[n] = dict(packet=n, unplaceable=False, q1=a[0], q2=a[1], q3=a[2], q4=a[3])
arm0 = {"k8s-en": {"passes_bar": True}}
scores = {"k8s-en": {"modes": ["E"], "instances": inst, "records": recs}}
repro = {"i1|0": {"id": "i1|0", "ok": True, "bound": True, "committed_sha256": "a" * 64,
                  "regenerated_sha256": "a" * 64}}
cid = ("k8s-en", "E", "Q")
ok = True


def with_answer(plant, **kw):
    t = dict(tiers)
    n = X.packet_name(nonce, f"plant:{plant}")
    t[n] = dict(t[n], **kw)
    return t


def voided(label, t, **kw):
    r = A3.aggregate3(arm0, scores, man, t, repro, **kw)
    good = r["cells"][cid]["verdict"] == "NO VERDICT" and r["overall"] == "INCONCLUSIVE"
    print(f"{label}: {r['cells'][cid]['verdict']} | {r['cells'][cid].get('reason', '')[:70]} | overall "
          f"{r['overall']}")
    return good


r = A3.aggregate3(arm0, scores, man, tiers, repro)
print("all plants right:", r["cells"][cid]["verdict"], "| overall", r["overall"], "| void", r["void"])
ok &= r["cells"][cid]["verdict"] == "FOUND" and r["overall"] == "FOUND" and not r["void"]
ok &= voided("P-D q3=no", with_answer("P-D", q3="no"))
ok &= voided("P-E q4=no", with_answer("P-E", q4="no"))
ok &= voided("P-C answered tier B (q1=yes; q3, q4 right)", with_answer("P-C", q1="yes"))

killed = not voided("V4 mutant (void not passed to cell), P-D q3=no",
                    with_answer("P-D", q3="no"), propagate=False)
print("  ->", "KILLED by the P-D case" if killed else "SURVIVED")
ok &= killed

try:
    A3.aggregate3(arm0, scores, dict(man, plants={k: v for k, v in man["plants"].items() if k != "P-E"}),
                  tiers, repro)
    print("four-plant manifest: accepted (BAD)")
    ok = False
except ValueError as e:
    print("four-plant manifest: refused:", e)
print("H8 CHECK:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
