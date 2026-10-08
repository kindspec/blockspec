# SPDX-License-Identifier: MIT
"""Evaluate one instance -- one before-state, its legs if a merge, and one
after-state for one path -- under Q and R, graded by TLLC with §5.2's rules.

ONE code path for every arm and for the plants. It writes no verdict, no tier
and no FOUND condition beyond F2, F3 and F5, which are properties of the
instance and the block; F1 is the enumerator's, F4 is read off `cls`, and
F6-F9 belong to tiering and reproduction.

Records are canonical JSON (`dumps`), so a record regenerates byte for byte
(F9) or not at all.
"""
import json

from . import mech as Mx
from . import oracle as O

P = Mx.P


def dumps(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def wellformed(text):
    """§4 F3: fences_balanced, and blocks() finds at least 2 blocks."""
    return P.fences_balanced(text) and len(Mx.D8.blocks(text)) >= 2


def q_class(truth, hit, tgt):
    """The verdict rule of ORACLE.md §3 / prose_merge.evaluate_case."""
    if truth == "SURVIVED":
        return "LOUD" if hit is None else ("correct" if hit == tgt else "WRONG")
    return "correct" if hit is None else "WRONG"


def evaluate(inst):
    """inst: dict(arm, mode, id, path, before, after, legs (None or [A, C]),
    f2 (bool)). Returns (unit records, keep_texts)."""
    base, after, legs = inst["before"], inst["after"], inst.get("legs")
    states = [base] + list(legs or []) + [after]
    wf = all(wellformed(t) for t in states)
    bb, bm = Mx.D8.blocks(base), Mx.D8.blocks(after)
    common = {"arm": inst["arm"], "mode": inst["mode"], "instance": inst["id"],
              "f2": bool(inst["f2"]), "wf": wf}
    recs = []
    if not bb or not bm:
        return recs, False
    orc = O.block_oracle(base, after, legs, bb, bm)
    Bc = [b["content"] for b in bb]
    Mc = [b["content"] for b in bm]

    def btarget(i):
        v, t = orc[i]
        return t if v == "SURVIVED" else None
    m_line_block = O.line_to_unit(after, bm, O.block_units(after, bm))

    # ---------------------------------------------------------------- Q
    for k, b in enumerate(bb):
        anc = Mx.D8.anchor_of(base, b)
        ty = Mx.typer(base, b)
        if len(anc["quote"]) < 20:
            recs.append(dict(common, mech="Q", id=f"{inst['id']}|Q|{k}", index=k,
                             type=ty, skip="short_quote",
                             unit=Mx.sha256_text(b["content"])))
            continue
        truth, tgt = orc[k]
        verdict = truth
        if truth == "SURVIVED":
            if not O.repeat_rule(Bc, Mc, btarget, k, tgt):
                verdict = "UNDECIDABLE-REPEAT"
            elif O.split_rule(base, after, legs, O.base_lines_of(base, bb, k, k), m_line_block):
                verdict = "UNDECIDABLE-SPLIT"
        decided = verdict in ("SURVIVED", "DELETED")
        r = dict(common, mech="Q", id=f"{inst['id']}|Q|{k}", index=k, type=ty,
                 nl=ty in Mx.NL_TYPES, unit=Mx.sha256_text(b["content"]),
                 oracle=verdict, decided=decided, target=tgt)
        wrong = False
        for lab, hard in P.POLICIES:
            st, hit = Mx.D83.reanchor2(after, anc, bm, hard)
            cls = q_class(truth, hit, tgt) if decided else None
            r[lab] = {"status": st, "hit": hit, "cls": cls}
            if cls == "WRONG":
                wrong = True
                r[lab]["mechanism_target_text"] = bm[hit]["content"] if hit is not None else None
        if wrong:
            r["reference"] = b["content"]
            r["oracle_target_text"] = bm[tgt]["content"] if tgt is not None else None
        recs.append(r)

    # ---------------------------------------------------------------- R
    hu_cache = {}

    def slug_ctx():
        if "B" not in hu_cache:
            Bu, Mu = O.heading_units(base, bb), O.heading_units(after, bm)
            m_b2u = O.unit_of_block(Mu)
            tg = {}

            def target(i):
                if i not in tg:
                    v, p = O.unit_oracle(base, after, legs, bb, bm, *Bu[i])
                    tg[i] = m_b2u[p] if v == "SURVIVED" and p is not None else None
                return tg[i]
            hu_cache.update(
                B=Bu, M=Mu, target=target, b2u=O.unit_of_block(Bu),
                Bc=[Mx.span_text(base, bb, a, z) for a, z in Bu],
                Mc=[Mx.span_text(after, bm, a, z) for a, z in Mu],
                lines=O.line_to_unit(after, bm, Mu))
        return hu_cache

    for name in Mx.r_names(base, bb):
        u = Mx.resolve_r(base, bb, name)
        if u == Mx.REF:
            continue                      # not unique at the before-state
        kind, first, last = u
        content = Mx.span_text(base, bb, first, last)
        truth, p = O.unit_oracle(base, after, legs, bb, bm, first, last)
        verdict, note = truth, None
        if truth == "SURVIVED":
            if kind == "region":
                # A region unit is one block, so the section form over it is
                # the block form, and p is TLLC's block target.
                if not O.repeat_rule(Bc, Mc, btarget, first, p):
                    verdict = "UNDECIDABLE-REPEAT"
                elif O.split_rule(base, after, legs, O.base_lines_of(base, bb, first, first),
                                  m_line_block):
                    verdict = "UNDECIDABLE-SPLIT"
            else:
                h = slug_ctx()
                k = h["b2u"][first]
                t = h["target"](k)
                if t is None:
                    verdict, note = "UNDECIDABLE-REPEAT", "heading-span has no TLLC target"
                elif not O.repeat_rule(h["Bc"], h["Mc"], h["target"], k, t):
                    verdict = "UNDECIDABLE-REPEAT"
                elif O.split_rule(base, after, legs, O.base_lines_of(base, bb, *h["B"][k]),
                                  h["lines"]):
                    verdict = "UNDECIDABLE-SPLIT"
        decided = verdict in ("SURVIVED", "DELETED")
        res = Mx.resolve_r(after, bm, name)
        hit = None if res == Mx.REF else [res[1], res[2]]
        cls = None
        if decided:
            if truth == "SURVIVED":
                cls = "LOUD" if hit is None else ("correct" if hit[0] <= p <= hit[1] else "WRONG")
            else:
                cls = "correct" if hit is None else "WRONG"
        r = dict(common, mech="R", id=f"{inst['id']}|R|{name}", name=name, kind=kind,
                 index=[first, last], type="R:" + kind, nl=True,
                 unit=Mx.sha256_text(content), oracle=verdict, decided=decided,
                 target=p, hard={"status": "#REF!" if hit is None else "RESOLVED",
                                 "hit": hit, "cls": cls})
        if note:
            r["note"] = note
        if cls == "WRONG":
            r["reference"] = name
            r["oracle_target_text"] = bm[p]["content"] if p is not None else None
            r["hard"]["mechanism_target_text"] = Mx.span_text(after, bm, hit[0], hit[1])
        recs.append(r)
    keep = any(r.get("hard", {}).get("cls") == "WRONG" or r.get("naive", {}).get("cls") == "WRONG"
               for r in recs)
    return recs, keep


def instance_line(inst, keep_texts):
    d = {k: v for k, v in inst.items() if k not in ("before", "after", "legs")}
    d["kind"] = "instance"
    d["wf"] = all(wellformed(t) for t in [inst["before"]] + list(inst.get("legs") or [])
                  + [inst["after"]])
    if keep_texts:
        d["texts"] = {"before": inst["before"], "after": inst["after"],
                      "legs": inst.get("legs")}
    return d
