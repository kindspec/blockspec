#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Run the planted tiering packets of PRE-REGISTRATION-2.md Appendix B through
the pinned mechanism and the one-leg oracle, and check that each is realisable.

For each plant, it checks four things:

- TLLC (one-leg form) returns SURVIVED with the stated target;
- the hardened quote resolver lands on the stated mechanism target;
- the two targets differ;
- the §5.2 REPEAT rule leaves the verdict decided.

Run:  python3 -I prereg2_plants.py --d8-dir <research>/experiments/D8-identity

Exits 0 only if every plant meets its expectation, and 1 otherwise. This
module does not decide any tier.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prose_merge as P  # noqa: E402


def d(*bl):
    return "\n\n".join(bl) + "\n"


L1, L2 = "Failed jobs are retried three times", "before an alert is raised."
EXP = "Exports are written to the archive bucket nightly."
ST = "Status: this proposal was approved by TOC vote on 2026-03-04."
H = "## Maintenance windows"
N = "> **Note:** All times in this section are UTC."
W = "Windows open at 02:00 and close at 04:00 on Sundays."
W2 = "Windows open at 03:00 and close at 05:00 on Sundays."
E = "Emergency windows may open at any time with one hour's notice."

# name: (base, after, anchored block k, oracle target t, mechanism target)
PLANTS = {
    "P-A": (d("## Ingest service", L1 + "\n" + L2, "## Export service", EXP),
            d("## Ingest service", L1.replace("three", "five") + "\n" + L2,
              "## Export service", EXP, "## Audit trail",
              "Superseded Ingest wording, kept for audit:", L1 + "\n" + L2), 1, 1, 6),
    "P-B": (d("## Project Alpha", "Alpha moves sandbox telemetry into the shared pipeline.", ST,
              "## Project Beta", "Beta adds a conformance badge to the landscape.", ST),
            d("## Project Alpha", "Alpha was rescoped to cover only audit logs.", ST,
              "## Project Beta", "Beta moves sandbox telemetry into the shared pipeline.", ST),
            2, 2, 5),
    "P-C": (d(H, N, W, E, N), d(H, E, N, W2, N), 4, 2, 4),
}


def repeat_decided(bb, bm, orc, k):
    """PRE-REGISTRATION-2.md §5.2 UNDECIDABLE-REPEAT, for Q blocks."""
    t = orc[k][1]
    twin_b = lambda i: sum(b["content"] == bb[i]["content"] for b in bb) > 1  # noqa: E731
    twin_m = lambda i: sum(b["content"] == bm[i]["content"] for b in bm) > 1  # noqa: E731
    T = [c for c in range(len(bm))
         if c != t and bm[c]["content"] in (bm[t]["content"], bb[k]["content"])]
    if not T:
        return True

    def ctx(c):
        n = 0
        for dd in (-1, 1):
            kk, cc = k + dd, c + dd
            if not (0 <= kk < len(bb) and 0 <= cc < len(bm)):
                continue
            v, tt = orc[kk]
            if v == "SURVIVED" and tt == cc and not twin_b(kk) and not twin_m(cc):
                n += 1
        return n
    s = {c: ctx(c) for c in [t] + T}
    return s[t] >= 1 and all(s[t] > s[c] for c in T)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--d8-dir", required=True)
    a = ap.parse_args()
    P.D8, P.D83 = P.load_d8(a.d8_dir)
    ok = True
    for name, (base, after, k, t_exp, hit_exp) in PLANTS.items():
        bb, bm = P.D8.blocks(base), P.D8.blocks(after)
        orc = P.tllc(base, after, base, after, bb, bm)
        st, hit = P.D83.reanchor2(after, P.D8.anchor_of(base, bb[k]), bm, True)
        good = (orc[k] == ("SURVIVED", t_exp) and hit == hit_exp and hit != t_exp
                and repeat_decided(bb, bm, orc, k))
        ok &= good
        print(f"{name}: TLLC={orc[k]} hard={st},{hit} "
              f"repeat_decided={repeat_decided(bb, bm, orc, k) if orc[k][0] == 'SURVIVED' else None} "
              f"-> {'OK' if good else 'FAIL'}")
    print("PLANTS:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
