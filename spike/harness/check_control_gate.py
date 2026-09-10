#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""The control-arm gate, as a check rather than as a sentence.

PRE-REGISTRATION §7: "The control arm is the gate. If the harness does not
reproduce D8's prose result on D8's corpora, stop and fix the harness."

WHAT THE GATE ACTUALLY IS.  §1 states the load-bearing fact as: "every
silent-wrong D8 recorded is typed `code`, `html` or `list`. Not one is typed
`prose`, in either strategy, in any arm."  So the gate is a claim about the
BY-TYPE breakdown, not about a rate.

It is asserted here on the HARDENED policy only, and that is a deliberate
narrowing of §1's "either strategy":

  * The `naive` claim is pin-dependent. At D8's own pin it holds. On a current
    clone of `obsidian-help` (7 commits later) it does not: one naive
    mis-anchor is YAML frontmatter, which `anchor_eval3.btype()` has no rule
    for and which therefore falls through to `prose`. Substantively that is
    structured data -- D8 §3.2's own category -- but the harness prints
    `prose`, so a gate asserting the naive claim goes red on corpus drift for
    a reason that has nothing to do with the harness.
  * The `hard` claim holds at both pins, in every arm.

A gate that fails for a reason unrelated to what it gates is not a gate, so the
narrow, stable form is the one asserted. The wide form is reported, not
asserted.

NOT asserted: "hardened silent-wrong is 0.00%". It is not, and D8 §3.2 does not
say it is -- rust-book hard is 0.12% (n=1, code) at gap=5 and 1.00% (n=2, code)
at gap=25. Zero applies to the PROSE-TYPED count, not the total.

Usage:  python3 anchor_eval3.py | python3 check_control_gate.py
        python3 check_control_gate.py --selftest
"""
import re
import sys

ARM = re.compile(r"^### (?P<name>\S+) (?P<glob>\S+) gap=(?P<gap>\d+)\s*"
                 r"(?:pairs=(?P<pairs>\d+)\s+)?"
                 r"(?:oracle-confident anchors=(?P<n>\d+)|:\s*too few \((?P<few>\d+)\))")
POL = re.compile(r"^\s+(?P<pol>naive|hard)\s+.*SILENT-WRONG\s+(?P<pct>[\d.]+)%\s+"
                 r"\(n=(?P<n>\d+)\)(?:\s+by type:\s+(?P<types>.*))?$")


def parse(text):
    arms, cur = [], None
    for line in text.splitlines():
        m = ARM.match(line)
        if m:
            cur = {"name": f"{m['name']} gap={m['gap']}",
                   "pairs": int(m["pairs"]) if m["pairs"] else None,
                   "anchors": int(m["n"]) if m["n"] else 0,
                   "measuring": m["few"] is None, "pol": {}}
            arms.append(cur)
            continue
        m = POL.match(line)
        if m and cur:
            types = {}
            if m["types"]:
                for tok in m["types"].split():
                    if "=" in tok:
                        k, v = tok.split("=", 1)
                        types[k] = int(v)
            cur["pol"][m["pol"]] = {"n": int(m["n"]), "pct": float(m["pct"]),
                                    "types": types}
    return arms


def gate(text, out=sys.stdout):
    arms = parse(text)
    fails, measuring = [], [a for a in arms if a["measuring"]]
    print("=== control-arm gate ===", file=out)
    if not arms:
        print("FAIL: no arms parsed at all -- did the run produce output?", file=out)
        return 1
    # A regex that silently stops matching is this project's most-repeated
    # defect. Every '###' line in the transcript must have become an arm.
    seen = sum(1 for l in text.splitlines() if l.startswith("### "))
    if seen != len(arms):
        print(f"FAIL: {seen} '###' arm headers in the transcript but {len(arms)} "
              f"parsed -- the parser is stale, not the corpus", file=out)
        return 1
    for a in arms:
        if not a["measuring"]:
            print(f"  {a['name']:<34} not measuring (too few) -- reported, not gated",
                  file=out)
            continue
        # The trap the parallel agent hit: a shell-expanded glob yields a
        # plausible-looking zero. A measuring arm with no version-pairs behind
        # it is not evidence of anything.
        if a["pairs"] == 0:
            fails.append(f"{a['name']}: pairs=0 -- arm measured nothing")
        hard = a["pol"].get("hard")
        if hard is None:
            fails.append(f"{a['name']}: no hard-policy line parsed")
            continue
        prose = hard["types"].get("prose", 0)
        status = "ok" if prose == 0 else f"*** {prose} PROSE-TYPED ***"
        print(f"  {a['name']:<34} pairs={a['pairs']} anchors={a['anchors']:<5} "
              f"hard n={hard['n']} ({hard['pct']}%) types={hard['types'] or '-'}  {status}",
              file=out)
        if prose:
            fails.append(f"{a['name']}: {prose} prose-typed silent-wrong under hard")
        naive = a["pol"].get("naive")
        if naive and naive["types"].get("prose", 0):
            print(f"      note: naive has {naive['types']['prose']} prose-typed "
                  f"(reported, not gated -- see module docstring)", file=out)
    if len(measuring) < 4:
        fails.append(f"only {len(measuring)} measuring arms; expected at least 4")
    print(f"  measuring arms: {len(measuring)}", file=out)
    if fails:
        print("CONTROL GATE: FAIL", file=out)
        for f in fails:
            print(f"    - {f}", file=out)
        return 1
    print("CONTROL GATE: PASS -- zero prose-typed silent-wrongs under the "
          "hardened policy in every measuring arm", file=out)
    return 0


SELFTEST_RED = """
### rust-book src/*.md gap=5  pairs=47  oracle-confident anchors=849
   block types: code=189 prose=460
   naive  correct  99.1%   LOUD-refusal   0.5%   SILENT-WRONG  0.47%  (n=4)  by type: code=3 html=1
   hard   correct  97.9%   LOUD-refusal   2.0%   SILENT-WRONG  0.24%  (n=2)  by type: code=1 prose=1
### cmspec *.md gap=5  pairs=0  oracle-confident anchors=73
   naive  correct 100.0%   LOUD-refusal   0.0%   SILENT-WRONG  0.00%  (n=0)
   hard   correct  94.5%   LOUD-refusal   5.5%   SILENT-WRONG  0.00%  (n=0)
"""

SELFTEST_GREEN = """
### rust-book src/*.md gap=5  pairs=47  oracle-confident anchors=849
   naive  correct  99.1%   LOUD-refusal   0.5%   SILENT-WRONG  0.47%  (n=4)  by type: code=3 html=1
   hard   correct  97.9%   LOUD-refusal   2.0%   SILENT-WRONG  0.12%  (n=1)  by type: code=1
### rust-book src/*.md gap=25  pairs=19  oracle-confident anchors=200
   naive  correct  97.5%   LOUD-refusal   0.5%   SILENT-WRONG  2.00%  (n=4)  by type: code=4
   hard   correct  94.0%   LOUD-refusal   5.0%   SILENT-WRONG  1.00%  (n=2)  by type: code=2
### obsidian-help en/*.md gap=5  pairs=31  oracle-confident anchors=384
   naive  correct  98.7%   LOUD-refusal   0.8%   SILENT-WRONG  0.52%  (n=2)  by type: list=2
   hard   correct  97.1%   LOUD-refusal   2.6%   SILENT-WRONG  0.26%  (n=1)  by type: list=1
### obsidian-help en/*.md gap=25: too few (22)
### cmspec *.md gap=5  pairs=6  oracle-confident anchors=73
   naive  correct 100.0%   LOUD-refusal   0.0%   SILENT-WRONG  0.00%  (n=0)
   hard   correct  94.5%   LOUD-refusal   5.5%   SILENT-WRONG  0.00%  (n=0)
### cmspec *.md gap=25  pairs=3  oracle-confident anchors=56
   naive  correct 100.0%   LOUD-refusal   0.0%   SILENT-WRONG  0.00%  (n=0)
   hard   correct  98.2%   LOUD-refusal   1.8%   SILENT-WRONG  0.00%  (n=0)
"""


def selftest():
    """The gate must be shown to fail. Org contract §2.2."""
    ok = True
    print("--- selftest: a known-GREEN transcript must pass ---")
    if gate(SELFTEST_GREEN) != 0:
        print("*** selftest FAIL: green transcript did not pass ***"); ok = False
    print("\n--- selftest: a transcript with a prose-typed hard silent-wrong,")
    print("    and an arm with pairs=0, must FAIL on both counts ---")
    if gate(SELFTEST_RED) == 0:
        print("*** selftest FAIL: red transcript passed -- the gate is not armed ***")
        ok = False
    print(f"\nSELFTEST: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv else gate(sys.stdin.read()))
