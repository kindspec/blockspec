#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""PROTOTYPE. Run the planted tiering packets of PRE-REGISTRATION-3.md
Appendix B through the pinned mechanism and the one-leg oracle, and check that
each is realisable. Same checks as prereg2_plants.py, which it reuses:

- TLLC (one-leg form) returns SURVIVED with the stated target;
- the hardened quote resolver lands on the stated mechanism target;
- the two targets differ;
- the §5.2 REPEAT rule leaves the verdict decided.

Run:  python3 -I prereg3_plants.py --d8-dir <research>/experiments/D8-identity

Exits 0 only if every plant meets its expectation, and 1 otherwise.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prose_merge as P  # noqa: E402
from prereg2_plants import repeat_decided  # noqa: E402


def d(*bl):
    return "\n\n".join(bl) + "\n"


L1, L2 = "Failed jobs are retried three times", "before an alert is raised."
EXP = "Exports are written to the archive bucket nightly."
ST = "Status: this proposal was approved by TOC vote on 2026-03-04."
RV = "Status: this proposal is under review."
NP = "> **Note:** All times on this page, in every section, are UTC."
W = "Windows open at 02:00 and close at 04:00 on Sundays."
W2 = "Windows open at 03:00 and close at 05:00 on Sundays."
EM = "Emergency windows may open at any time with one hour's notice."
FR = "Freezes begin at 18:00 on the last Friday of each quarter."
S1, S2 = "Snapshots are kept for seven days", "before they are pruned."
RS = "Restores are verified against a checksum manifest."
U1, U2 = "Each project may store up to 50 GB", "of build artifacts at a time."
DL = "Downloads are rate-limited to 100 requests per minute."

# name: (base, after, anchored block k, oracle target t, mechanism target)
PLANTS = {
    "P-A": (d("## Ingest service", L1 + "\n" + L2, "## Export service", EXP),
            d("## Defaults", L1 + "\n" + L2,
              "## Ingest service", L1.replace("three", "five") + "\n" + L2,
              "## Export service", EXP), 1, 3, 1),
    "P-B": (d("## Project Alpha", "Alpha moves sandbox telemetry into the shared pipeline.", ST,
              "## Project Beta", "Beta adds a conformance badge to the landscape.", RV),
            d("## Project Alpha", "Alpha was rescoped to cover only audit logs.", ST,
              "## Project Beta", "Beta moves sandbox telemetry into the shared pipeline.", ST),
            2, 2, 5),
    "P-C": (d("## Maintenance windows", NP, W, EM, "## Release freezes", NP, FR),
            d("## Sunday windows", NP, W2, "## Maintenance windows", NP, EM,
              "## Release freezes", NP, FR), 1, 4, 1),
    # Positive control for q3: the misplaced copy is labelled as superseded.
    "P-D": (d("## Backup service", S1 + "\n" + S2, "## Restore service", RS),
            d("## Backup service", S1.replace("seven", "thirty") + "\n" + S2,
              "## Restore service", RS, "## Change log",
              "Superseded Backup wording, kept for the change log:", S1 + "\n" + S2), 1, 1, 6),
    # Positive control for q4: an edit leaves a stale duplicate of a section behind.
    "P-E": (d("## Upload limits", U1 + "\n" + U2, "## Download limits", DL),
            d("## Upload limits", U1.replace("50", "80") + "\n" + U2, "## Download limits", DL,
              "## Upload limits", U1 + "\n" + U2), 1, 1, 5),
}


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
