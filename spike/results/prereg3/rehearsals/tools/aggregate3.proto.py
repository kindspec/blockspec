# SPDX-License-Identifier: MIT
"""PROTOTYPE of H8: prereg 3's aggregate. It reimplements only the top-level
loop of p2.aggregate.aggregate, so that the five-plant void reaches every
cell through p2.aggregate.cell(), which is reused unchanged, as is overall().
"""
from p2 import aggregate as AG
from p2 import export as X

PLANT_EXPECT3 = {
    "P-A": {"q1": "yes", "q2": "yes", "q3": "no", "q4": "no", "tier": "A"},
    "P-B": {"q1": "yes", "q2": "no", "q3": "no", "q4": "no", "tier": "B"},
    "P-C": {"q1": "no", "q2": "no", "q3": "no", "q4": "no", "tier": "C"},
    "P-D": {"q1": "yes", "q2": "yes", "q3": "yes", "q4": "no", "tier": "A"},
    "P-E": {"q1": "yes", "q2": "yes", "q3": "yes", "q4": "yes", "tier": "A"},
}
QUALIFIES = {"A": True, "B": True, "C": False}


def tier_of(ans):
    if ans.get("unplaceable"):
        return "UNPLACEABLE"
    return "A" if ans["q2"] == "yes" else ("B" if ans["q1"] == "yes" else "C")


def void_reasons5(plant_names, tiers):
    out = []
    for plant, name in sorted(plant_names.items()):
        exp = PLANT_EXPECT3[plant]
        ans = tiers.get(name)
        if ans is None:
            out.append(f"{plant}: untiered")
            continue
        t = tier_of(ans)
        if QUALIFIES.get(t, False) != QUALIFIES[exp["tier"]]:
            out.append(f"{plant}: tier {t} is on the wrong side of the B/C line (expected {exp['tier']})")
        for q in ("q3", "q4"):
            if ans[q] != exp[q]:
                out.append(f"{plant}: {q}={ans[q]}, expected {exp[q]}")
    return out


def load_manifest3(m):
    want = {n: {"key": f"plant:{n}", "expected": PLANT_EXPECT3[n]} for n in PLANT_EXPECT3}
    if m.get("plants") != want:
        raise ValueError("the manifest's plants are not prereg 3's Appendix B")
    return m


def aggregate3(arm0, scores, manifest, tiers, repro, gaps=None, propagate=True):
    """propagate=False is the V4 mutant: prereg 2's behaviour of not passing
    the five-plant void into cell()."""
    manifest = load_manifest3(manifest)
    if not arm0 or not scores or not any(s.get("records") for s in scores.values()):
        raise AG.Empty("no Arm 0 result or no scored record: no verdict")
    nonce = manifest["nonce"]
    plant_names = {p: X.packet_name(nonce, v["key"]) for p, v in manifest["plants"].items()}
    void = void_reasons5(plant_names, tiers)
    cells, near = {}, {"i": set(), "ii": set(), "iii": set()}
    recs_all, inst_all = [], {}
    for sc in scores.values():
        recs_all += sc.get("records", [])
        inst_all.update(sc.get("instances", {}))
    reps = X.select_packets(recs_all, inst_all)
    for arm in AG.K.ARM_ORDER:
        a0 = arm0.get(arm, {"no_verdict": "no Arm 0 result"})
        sc = scores.get(arm, {"no_verdict": "not run"})
        for mode in AG.MODES:
            for mech in AG.MECHS:
                cid = (arm, mode, mech)
                if "no_verdict" in a0:
                    cells[cid] = {"verdict": "NO VERDICT", "reason": a0["no_verdict"]}
                elif not a0.get("passes_bar"):
                    cells[cid] = {"verdict": "NO VERDICT", "reason": "oracle reach (Arm 0 bar)"}
                elif "no_verdict" in sc or mode not in sc.get("modes", []):
                    cells[cid] = {"verdict": "NO VERDICT", "reason": sc.get("no_verdict", f"{mode} not run")}
                else:
                    cells[cid] = AG.cell(arm, mode, mech, sc, nonce, tiers, repro,
                                         void if propagate else [], near, reps)
    for cid, why in (gaps or {}).items():
        if cid in cells:
            was = cells[cid]
            cells[cid] = {"verdict": "NO VERDICT", "reason": f"§9 gap: {why}",
                          "without_the_gap": {k: v for k, v in was.items() if k in ("verdict", "reason")}}
    return {"cells": cells, "void": void, "overall": AG.overall(cells, near),
            "near_misses": {k: len(v) for k, v in near.items()}}
