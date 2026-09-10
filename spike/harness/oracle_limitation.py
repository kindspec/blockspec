#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Demonstrate TLLC's third limitation, the one found by USING it.

`ORACLE.md` §4 and §5 name two limitations in advance. This is a third, found
after the fact. `ORACLE.md` is frozen -- it says nothing in it may be adjusted in
light of a result -- so the limitation is demonstrated and logged
(`LOG.md` §6.2), not fixed. Fixing it means a second oracle statement.

THE LIMITATION. For a block of a SINGLE LINE whose text repeats in the file,
`frac_L` is either 0.0 or 1.0, so the `>= 0.5` confidence threshold has no
discriminating power, and the plurality vote is taken over one element. TLLC
therefore returns SURVIVED with full confidence on a question that is genuinely
undecidable from the bytes, and emits no signal that it guessed. It should
return UNKNOWN.

Run:  python3 oracle_limitation.py [--d8-dir PATH]

This is a demonstration, not a gate. It exits 0 when the limitation reproduces,
and 1 if it does not -- because a demonstration that silently stopped
demonstrating is the failure this project keeps finding in itself.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prose_merge as P  # noqa: E402

BASE = "# Doc\n\nAlpha one.\n\nNOTE: see above.\n\nBeta two.\n\nNOTE: see above.\n\nGamma three.\n\nNOTE: see above.\n"
# Leg A inserts one MORE byte-identical copy directly after the first.
LEG_A = "# Doc\n\nAlpha one.\n\nNOTE: see above.\n\nNOTE: see above.\n\nBeta two.\n\nNOTE: see above.\n\nGamma three.\n\nNOTE: see above.\n"
# Leg C edits something far away, so this is a real two-branch clean merge.
LEG_C = "# Doc\n\nAlpha one.\n\nNOTE: see above.\n\nBeta two.\n\nNOTE: see above.\n\nGamma three revised.\n\nNOTE: see above.\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--d8-dir", default=P.DEFAULT_D8)
    a = ap.parse_args()
    P.D8, P.D83 = P.load_d8(a.d8_dir)

    res = P.stock_merge(BASE, LEG_A, LEG_C, "doc.md")
    if not res["clean"]:
        print("FAIL: the merge did not come out clean; the demonstration needs it to")
        return 1
    bb, bm = P.D8.blocks(BASE), P.D8.blocks(res["merged"])
    print("stock git merge: clean\n")
    print("base blocks  :", [b["content"][:20] for b in bb])
    print("merged blocks:", [b["content"][:20] for b in bm])
    print()

    orc = P.tllc(BASE, LEG_A, LEG_C, res["merged"], bb, bm)
    notes = [k for k, b in enumerate(bb) if b["content"].startswith("NOTE")]
    for k in notes:
        truth, tgt = orc[k]
        print(f"  base block {k}  ->  oracle {truth}, target = merged block {tgt}")

    truth, tgt = orc[notes[0]]
    print()
    print("THE POINT. Leg A inserted a byte-identical copy of base block "
          f"{notes[0]} directly")
    print("after it. Which of the two adjacent, identical merged blocks is the")
    print(f"'descendant' is undecidable from the bytes -- yet TLLC answers "
          f"{truth},")
    print(f"target {tgt}, with no margin, no corroboration and no signal that it")
    print("guessed. A single-line block's frac is 0.0 or 1.0, so ORACLE.md §2's")
    print("`>= 0.5` threshold cannot discriminate, and the plurality vote in")
    print("`tllc()` runs over exactly one element. The honest answer is UNKNOWN.")
    print()
    print("WHY IT MATTERS AND WHY IT IS NOT FIXED HERE. Nothing this spike")
    print("currently reports depends on it: LOG.md §6.1's candidates are excluded")
    print("by PRE-REGISTRATION §3(5) on their own. But the duplicate-heavy corpora")
    print("PRE-REGISTRATION §5 calls for are exactly this shape -- short, highly")
    print("repeated blocks -- so that arm needs a stronger oracle before its prose")
    print("numbers mean anything. ORACLE.md is frozen; this needs a second oracle")
    print("statement, not an edit to the first.")

    ok = truth == "SURVIVED" and tgt == notes[0] + 1
    print(f"\nDEMONSTRATION: {'reproduces' if ok else 'DID NOT REPRODUCE'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
