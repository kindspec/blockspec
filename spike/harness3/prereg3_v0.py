#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""PRE-REGISTRATION-3.md §9, V0: harness3 agrees with the merged document,
and leaves prereg 2 alone.

- Appendix B's before- and after-texts are exactly prereg3_plants.PLANTS's;
- Appendix A, as PROMPT.md, hashes to the registered prompt;
- QUESTIONS.md is prereg 2's §7.1 table and §7.2 followed by Appendix A;
- p3/plants.py's expectations are §3's table;
- prereg 2's harness, PRE-REGISTRATION-2.md and ORACLE.md are byte-identical
  to d79bf2e, and prereg 2's own binding check still binds a prereg 2
  command in this work tree.

Run:  python3 -I -S -B harness3/prereg3_v0.py --d8-dir <research>/experiments/D8-identity
"""
import argparse
import hashlib
import os
import re
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
SPIKE = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(SPIKE, "harness"))
sys.path.insert(0, HERE)

from p2 import binding as B2  # noqa: E402
from p2 import export as X  # noqa: E402
from p2 import mech as Mx  # noqa: E402
from p3 import binding as BD  # noqa: E402
from p3 import export3 as X3  # noqa: E402
from p3 import plants as PL  # noqa: E402

OK = []


def check(name, ok, detail=""):
    OK.append(bool(ok))
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  -- {detail}" if detail else ""))


def appendix_b_blocks(doc):
    b = doc[doc.index("## Appendix B"):]
    blocks, cur = [], None
    for ln in b.splitlines():
        if ln.startswith("    ") or (cur is not None and ln == ""):
            cur = (cur or []) + [ln[4:]]
        elif cur is not None:
            blocks.append("\n".join(cur).strip("\n") + "\n")
            cur = None
    if cur:
        blocks.append("\n".join(cur).strip("\n") + "\n")
    return blocks


def table_expectations(doc):
    out = {}
    for m in re.finditer(r"^\| (P-[A-E]) \| [^|]+ \| (\w+) (\w+) (\w+) (\w+) \| ([ABC]) \|$", doc, re.M):
        p, q1, q2, q3, q4, t = m.groups()
        out[p] = {"q1": q1, "q2": q2, "q3": q3, "q4": q4, "tier": t}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--d8-dir", required=True)
    ap.add_argument("--red", action="store_true",
                    help="plant one fault in each check's input, in memory; every check must FAIL")
    a = ap.parse_args()
    Mx.load(a.d8_dir)
    import prereg3_plants as PP
    doc = X3.prereg3_text()
    if a.red:
        PP.PLANTS["P-C"] = (PP.PLANTS["P-C"][0].replace("UTC", "GMT"),) + PP.PLANTS["P-C"][1:]
        PL.PLANT_EXPECT3["P-D"] = dict(PL.PLANT_EXPECT3["P-D"], q3="no")
        X3.PROMPT_SHA256 = "0" * 64
        doc = doc.replace("## Appendix A", "## Appendix A ", 1)
        BD.PREREG2_VALIDATION = "f59c109"  # the prereg 2 document's commit, before its harness
        B2.VALIDATION_REL = os.path.join("results", "prereg2", "VALIDATION-red")
        X.questions_text = lambda: "### 7.1 Tiers (table)\n"
    check("PRE-REGISTRATION-3.md is the merged document",
          hashlib.sha256(doc.encode()).hexdigest() == X3.PREREG3_SHA256, X3.PREREG3_SHA256[:16])
    want = [x for p in ("P-A", "P-B", "P-C", "P-D", "P-E") for x in PP.PLANTS[p][:2]]
    got = appendix_b_blocks(doc)
    check("Appendix B's texts are prereg3_plants.PLANTS's", got == want, f"{len(got)} blocks")
    lines = [ln for ln in X3.appendix_a().splitlines() if ln.startswith(">")]
    p = "\n".join(ln[2:] if ln.startswith("> ") else ln[1:] for ln in lines) + "\n"
    check("Appendix A as PROMPT.md hashes to the registered prompt",
          hashlib.sha256(p.encode()).hexdigest() == X3.PROMPT_SHA256, X3.PROMPT_SHA256[:16])
    q = X3.questions_text3()
    check("QUESTIONS.md: prereg 2's §7.1 table and §7.2, then Appendix A",
          q.startswith("### 7.1 Tiers (table)") and q.endswith(X3.appendix_a()) and
          X.questions_text().split("## Appendix A")[0] == q.split("## Appendix A")[0])
    check("p3/plants.py's expectations are §3's table", table_expectations(doc) == PL.PLANT_EXPECT3)
    check("prereg 2's harness, PRE-REGISTRATION-2.md and ORACLE.md are d79bf2e's",
          BD.prereg2_untouched(SPIKE, BD.PREREG2_VALIDATION) == [],
          "; ".join(BD.prereg2_untouched(SPIKE, BD.PREREG2_VALIDATION))[:200])
    st, reasons = B2.check(SPIKE, "tier-run")
    check("prereg 2's binding check still binds a prereg 2 command here", st["bound"], "; ".join(reasons)[:200])
    n, ok = len(OK), sum(OK)
    print(f"{ok} of {n} checks passed")
    if a.red:
        print("V0 RED:", "PASS (every check failed on its planted fault)" if ok == 0 else "FAIL")
        return 0 if ok == 0 else 1
    print("V0:", "PASS" if ok == n else "FAIL")
    return 0 if ok == n else 1


if __name__ == "__main__":
    sys.exit(main())
