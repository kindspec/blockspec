# SPDX-License-Identifier: MIT
"""PRE-REGISTRATION-3.md §9 H6-H8: prereg 3's aggregate.

It reimplements only the top-level loop of p2.aggregate.aggregate, so that
the five-plant void (plants.void_reasons) reaches every cell through
p2.aggregate.cell(), which is reused unchanged, as is overall(). Replacing
p2's returned `void` afterwards would leave a cell FOUND: cell() has already
used prereg 2's three-plant void by then.

Inputs (H6): prereg 2's Arm 0 results and scores are accepted only if bound
to d79bf2e, at their pin and bundle. Reproductions (H7): only `bound: true`
results bound to d79bf2e or to prereg 3's validation commit; conflicting
duplicates are refused.
"""
from p2 import aggregate as AG
from p2 import export as X

from . import binding as BD
from . import plants as PL


class InputRefused(Exception):
    pass


def check_input(o, what, accepted=(BD.PREREG2_VALIDATION,)):
    if o.get("bound") is not True or (o.get("binding") or {}).get("validation_commit") not in accepted:
        raise InputRefused(f"{what} is not a bound output of {', '.join(c[:12] for c in accepted)}")


def accept_repros(results2, results3, vc3):
    """{record id: result}: H7's acceptance rule, with its source split.
    results2, from results/prereg2/repro/, must be bound to d79bf2e;
    results3, from results/prereg3/repro/, must be bound to prereg 3's
    validation commit vc3. With no vc3, no prereg 3 result is accepted."""
    out = {}
    tagged = [(o, (BD.PREREG2_VALIDATION,)) for o in results2]
    for o in results3:
        if not vc3:
            raise InputRefused(f"reproduction {o.get('id')!r} is prereg 3's, and no prereg 3 validation "
                               "commit is known")
        tagged.append((o, (vc3,)))
    for o, accepted in tagged:
        check_input(o, f"reproduction {o.get('id')!r}", accepted)
        rid = o.get("id")
        if rid in out and (out[rid].get("ok"), out[rid].get("committed_sha256"),
                           out[rid].get("regenerated_sha256")) != (o.get("ok"), o.get("committed_sha256"),
                                                                    o.get("regenerated_sha256")):
            raise InputRefused(f"two accepted reproductions of {rid!r} disagree")
        out[rid] = o
    return out


def aggregate3(arm0, scores, manifest, tiers, repro, gaps=None):
    """As p2.aggregate.aggregate, with prereg 3's manifest and the five-plant
    void passed into every cell."""
    PL.check_manifest(manifest)
    if not arm0 or not scores or not any(s.get("records") for s in scores.values()):
        raise AG.Empty("no Arm 0 result or no scored record: no verdict")
    nonce = manifest["nonce"]
    void = PL.void_reasons(PL.plant_names(manifest), tiers)
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
                    cells[cid] = AG.cell(arm, mode, mech, sc, nonce, tiers, repro, void, near, reps)
    for cid, why in (gaps or {}).items():
        if cid in cells:
            was = cells[cid]
            cells[cid] = {"verdict": "NO VERDICT", "reason": f"§9 gap: {why}",
                          "without_the_gap": {k: v for k, v in was.items() if k in ("verdict", "reason")}}
    return {"cells": cells, "void": void, "overall": AG.overall(cells, near),
            "near_misses": {k: len(v) for k, v in near.items()}, "packet_keys": sorted(reps)}
