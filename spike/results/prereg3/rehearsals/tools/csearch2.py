"""Search block permutations for a C-shaped plant the harness realises:
decided, hardened WRONG, with a page-wide note opening each section.

usage: python3 -I -S -B csearch.py <harness dir> <d8 dir>
"""
import itertools
import sys

harness, d8 = sys.argv[1:3]
sys.path.insert(0, harness)
from p2 import mech as Mx  # noqa: E402
Mx.load(d8)
from p2 import evaluate as E  # noqa: E402


def d(*bl):
    return "\n\n".join(bl) + "\n"


H1, H2, H3 = "## Maintenance windows", "## Release freezes", "## Sunday windows"
NP = "> **Note:** All times on this page are UTC."
W = "Windows open at 02:00 and close at 04:00 on Sundays."
W2 = "Windows open at 03:00 and close at 05:00 on Sundays."
EM = "Emergency windows may open at any time with one hour's notice."
F = "Freezes begin at 18:00 on the last Friday of each quarter."

base_blocks = [H1, NP, W, EM, H2, NP, F]
base = d(*base_blocks)
HE = "## Emergency windows"
seen = set()
hits = []
paras = [W, W2, EM, F]
import itertools as it
cands = []
for heads in it.permutations([H1, H2, HE, H3], 3):
    for assign in it.product(range(3), repeat=3):
        for wv in (W, W2):
            ps = [wv, EM, F]
            secs = [[h, NP] for h in heads]
            for pi, si in enumerate(assign):
                secs[si].append(ps[pi])
            if any(len(x) == 2 for x in secs):
                continue
            for order in it.permutations(range(3)):
                blocks = [b for i in order for b in secs[i]]
                cands.append(blocks)
for heads in it.permutations([H1, H2, HE, H3], 2):
    for assign in it.product(range(2), repeat=3):
        for wv in (W, W2):
            ps = [wv, EM, F]
            secs = [[h, NP] for h in heads]
            for pi, si in enumerate(assign):
                secs[si].append(ps[pi])
            if any(len(x) == 2 for x in secs):
                continue
            for perm in it.permutations(range(2)):
                cands.append([b for i in perm for b in secs[i]])
for blocks in cands:
    after = d(*blocks)
    if after in seen or after == base:
        continue
    seen.add(after)
    inst = {"arm": "plant", "mode": "E", "id": "c", "path": "doc.md",
            "before": base, "after": after, "legs": None, "f2": True}
    recs, _ = E.evaluate(inst)
    for r in recs:
        if r["mech"] == "Q" and r["index"] in (1, 5) and r.get("decided") and r["hard"]["cls"] == "WRONG":
            hits.append((r["index"], r["target"], r["hard"]["hit"], [b[3:12] if b[0]=="#" else b[:8] for b in blocks]))
for h in hits:
    print(h)
print(len(seen), "afters,", len(hits), "hits")
