# SPDX-License-Identifier: MIT
"""PRE-REGISTRATION-2.md §5.2 Counting, §6.6 cell verdicts, §6.7 the overall
verdict and near misses, joined with the tiering of §7.

`aggregate()` is a pure function of its inputs. It raises Empty on an input
that holds nothing, so an empty run can never print a verdict, and it raises
MissingRepro when a record meets F1-F8 but has no reproduction result, so F9
can never be assumed.

Each exported packet has one representative record: the record with the
smallest id over every arm mode (review A5, LOG §16). F6 and F9 are judged
on that record, for every cell that exported the packet. F9 holds only for a
reproduction result that is bound and whose committed and regenerated
sha256s are equal (review B1).
"""
from collections import defaultdict

from . import corpus as K
from . import export as X
from . import tiers as T

MODES = ("E", "S5", "S25", "M")
MECHS = ("Q", "R")
FLOOR = 300
UNDECIDABLE_MAX = 0.10


class Empty(Exception):
    pass


class MissingRepro(Exception):
    pass


def in_cell(inst, rule=K.VERDICT_RULE, site_set="strict"):
    """The instances a cell counts: the verdict rule's selection, and for
    site-policy M the strict set (§6.2, F1). The other rules, and the 25-case
    set, are reported beside it and carry no verdict."""
    if rule not in inst.get("rules", []):
        return False
    if inst["arm"] == "site-policy" and inst["mode"] == "M":
        return bool(inst.get("strict" if site_set == "strict" else "set25"))
    return True


def reproduced(rp):
    """F9: a bound reproduction whose committed and regenerated records
    have equal sha256s."""
    return (isinstance(rp, dict) and rp.get("bound") is True and rp.get("ok") is True
            and isinstance(rp.get("committed_sha256"), str) and len(rp["committed_sha256"]) == 64
            and rp.get("committed_sha256") == rp.get("regenerated_sha256"))


def distinct_status(records):
    """§5.2 Counting, over distinct units (§6.1). Returns {unit key:
    'decided' | 'undecidable' | 'UNKNOWN'}."""
    st = defaultdict(set)
    for r in records:
        if "oracle" not in r:
            continue
        st[X.unit_key(r)].add("decided" if r["decided"] else r["oracle"])
    out = {}
    for k, s in st.items():
        if "decided" in s:
            out[k] = "decided"
        elif any(x.startswith("UNDECIDABLE-") for x in s):
            out[k] = "undecidable"
        else:
            out[k] = "UNKNOWN"
    return out


def floor_verdict(n_decided, n_undecidable, passed_arm0):
    """§6.6 NOT FOUND's three conditions, or the reason it is NO VERDICT."""
    if not passed_arm0:
        return "NO VERDICT", "the arm did not pass Arm 0"
    if n_decided < FLOOR:
        return "NO VERDICT", f"{n_decided} distinct decided natural-language units < {FLOOR}"
    if n_undecidable > UNDECIDABLE_MAX * (n_decided + n_undecidable):
        return "NO VERDICT", (f"undecidable {n_undecidable} > 10% of "
                              f"{n_decided + n_undecidable}")
    return "NOT FOUND", f"n={n_decided}, bound 3/n = {3 / n_decided:.5f} at 95%"


def aggregate(arm0, scores, manifest, tiers, repro, gaps=None):
    """
    arm0:    {arm: {"passes_bar": bool} | {"no_verdict": reason}}
    scores:  {arm: {"no_verdict": reason} |
                   {"modes": [...], "instances": {(arm, id): inst}, "records": [unit records]}}
    manifest: the sealed manifest (nonce, plants)
    tiers:   {packet name: answers} from tiers.read_tiers
    repro:   {record id: reproduction result (id, ok, bound, committed_sha256,
              regenerated_sha256)}
    gaps:    {(arm, mode, mech): reason}, from p2.gaps.load_gaps: §9's gap rule
             makes each such cell NO VERDICT, whatever it would have been
    """
    if not arm0 or not scores or not any(s.get("records") for s in scores.values()):
        raise Empty("no Arm 0 result or no scored record: no verdict")
    nonce = manifest["nonce"]
    plant_names = {p: X.packet_name(nonce, v["key"]) for p, v in manifest["plants"].items()}
    void = T.void_reasons(manifest, plant_names, tiers)
    cells, near = {}, {"i": set(), "ii": set(), "iii": set()}
    # One representative per exported packet, over every arm and mode (A5).
    recs_all, inst_all = [], {}
    for sc in scores.values():
        recs_all += sc.get("records", [])
        inst_all.update(sc.get("instances", {}))
    reps = X.select_packets(recs_all, inst_all)
    for arm in K.ARM_ORDER:
        a0 = arm0.get(arm, {"no_verdict": "no Arm 0 result"})
        sc = scores.get(arm, {"no_verdict": "not run"})
        for mode in MODES:
            for mech in MECHS:
                cid = (arm, mode, mech)
                if "no_verdict" in a0:
                    cells[cid] = {"verdict": "NO VERDICT", "reason": a0["no_verdict"]}
                    continue
                if not a0.get("passes_bar"):
                    cells[cid] = {"verdict": "NO VERDICT", "reason": "oracle reach (Arm 0 bar)"}
                    continue
                if "no_verdict" in sc or mode not in sc.get("modes", []):
                    cells[cid] = {"verdict": "NO VERDICT",
                                  "reason": sc.get("no_verdict", f"{mode} not run")}
                    continue
                cells[cid] = cell(arm, mode, mech, sc, nonce, tiers, repro, void, near, reps)
    for cid, why in (gaps or {}).items():
        if cid in cells:
            was = cells[cid]
            cells[cid] = {"verdict": "NO VERDICT", "reason": f"§9 gap: {why}",
                          "without_the_gap": {k: v for k, v in was.items() if k in ("verdict", "reason")}}
    return {"cells": cells, "void": void, "overall": overall(cells, near),
            "near_misses": {k: len(v) for k, v in near.items()}}


def counts(recs):
    nl = [r for r in recs if r.get("nl")]
    status = distinct_status(nl)
    return {"distinct": {"decided": sum(1 for v in status.values() if v == "decided"),
                         "undecidable": sum(1 for v in status.values() if v == "undecidable"),
                         "UNKNOWN": sum(1 for v in status.values() if v == "UNKNOWN")},
            "instances": {"evaluated": sum(1 for r in nl if "oracle" in r),
                          "undecidable": sum(1 for r in nl if r.get("oracle", "").startswith("UNDECIDABLE-")),
                          "UNKNOWN": sum(1 for r in nl if r.get("oracle") == "UNKNOWN")}}


def cell(arm, mode, mech, sc, nonce, tiers, repro, void, near, reps):
    inst = sc["instances"]
    mine = [r for r in sc["records"] if r["mode"] == mode and r["mech"] == mech and r["arm"] == arm]
    recs = [r for r in mine if in_cell(inst[(arm, r["instance"])])]
    out = counts(recs)
    n_dec, n_und = out["distinct"]["decided"], out["distinct"]["undecidable"]
    # Beside, with no verdict (§6.3, §6.2): the other selection rules, the
    # 25-case set for site-policy M, and their eligible mis-resolutions.
    beside = {}
    for rule in K.RULES:
        if rule == K.VERDICT_RULE:
            continue
        rr = [r for r in mine if in_cell(inst[(arm, r["instance"])], rule)]
        beside[rule] = dict(counts(rr), decided_hardened_misresolutions=len(
            {X.unit_key(r) for r in rr if r.get("decided") and r.get("hard", {}).get("cls") == "WRONG"
             and r["f2"] and r["wf"] and X.f5(r)}))
    if arm == "site-policy" and mode == "M":
        rr = [r for r in mine if in_cell(inst[(arm, r["instance"])], site_set="set25")]
        beside["set25"] = dict(counts(rr), decided_hardened_misresolutions=len(
            {X.unit_key(r) for r in rr if r.get("decided") and r.get("hard", {}).get("cls") == "WRONG"
             and r["f2"] and r["wf"] and X.f5(r)}))
    out["beside"] = beside
    keys = {X.packet_key(r) for r in recs if X.eligible(r, inst[(arm, r["instance"])])}
    untiered, qualifying, on_deleted, differs = [], set(), set(), []
    for key in sorted(keys):
        rep = reps[key]
        name = X.packet_name(nonce, key)
        ans = tiers.get(name)
        if ans is None:
            untiered.append(name)
            continue
        tier = T.tier_of(ans)
        if tier == "UNPLACEABLE":
            continue
        # F6 is "every input state is well-formed" and q4 "no". The first
        # half is a condition of export itself (§7.3, export.eligible), so
        # every representative here already meets it; only q4 is left.
        f6 = ans["q4"] == "no"
        f7 = ans["q3"] == "no"
        f8 = tier in ("A", "B")
        if not f6:
            continue
        # F9 is needed both for a find and for near miss (i), which is a
        # record meeting every condition except F7 or F8.
        if rep["id"] not in repro:
            raise MissingRepro(f"{rep['id']}: meets F1-F6 with no reproduction result")
        if not reproduced(repro[rep["id"]]):
            differs.append(rep["id"])
            continue
        if f7 and f8:
            qualifying.add(X.unit_key(rep))
            if rep.get("oracle") == "DELETED":
                on_deleted.add(X.unit_key(rep))
        else:
            near["i"].add(X.unit_key(rep))
    for r in recs:
        i = inst[(arm, r["instance"])]
        if r.get("decided") and r.get("hard", {}).get("cls") == "WRONG" \
                and X.f1(r, i) and r["f2"] and r["wf"] and not X.f5(r):
            near["ii"].add(X.unit_key(r))
        if r.get("decided") and r.get("naive", {}).get("cls") == "WRONG" \
                and r["hard"]["cls"] != "WRONG" and X.f1(r, i) and r["f2"] and r["wf"] and X.f5(r):
            near["iii"].add(X.unit_key(r))
    out["exported_packets"] = len(keys)
    out["qualifying_distinct"] = len(qualifying)
    out["wrong_on_deleted"] = len(on_deleted)
    note = (f"; F9: {len(differs)} record(s) do not reproduce: {', '.join(differs)}" if differs else "")
    if void and keys:
        out.update(verdict="NO VERDICT", reason="tiering void: " + "; ".join(void) + note)
    elif untiered:
        out.update(verdict="NO VERDICT", reason=f"{len(untiered)} exported packet(s) untiered" + note)
    elif qualifying:
        why = f"{len(qualifying)} qualifying distinct unit(s)"
        if on_deleted:
            why += (f", of which {len(on_deleted)} rest on an oracle DELETED target "
                    f"(WRONG_on_deleted): weaker, ORACLE.md §4")
        out.update(verdict="FOUND", reason=why + note)
    else:
        v, why = floor_verdict(n_dec, n_und, True)
        out.update(verdict=v, reason=why + note)
    return out


def overall(cells, near):
    if any(c["verdict"] == "FOUND" for c in cells.values()):
        return "FOUND"

    def nf(arm, mech, modes):
        return any(cells.get((arm, m, mech), {}).get("verdict") == "NOT FOUND" for m in modes)
    q = nf("k8s-en", "Q", ("E", "S5", "S25")) and nf("cncf-toc", "Q", ("E", "S5", "S25"))
    r = nf("k8s-en", "R", MODES) or nf("cncf-toc", "R", MODES)
    with_near = " with near misses" if any(near.values()) else ""
    if q and r:
        return "NOT FOUND" + with_near
    if q:
        return "NOT FOUND (Q only)" + with_near
    return "INCONCLUSIVE"
