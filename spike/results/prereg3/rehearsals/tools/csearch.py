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
pool = [H1, NP, W2, EM, H2, NP, F]
seen = set()
hits = []
for perm in itertools.permutations(range(len(pool))):
    blocks = [pool[i] for i in perm]
    if blocks[0][0] != "#":
        continue
    # every heading is followed by the note: the convention holds
    if any(b.startswith("## ") and (j + 1 >= len(blocks) or blocks[j + 1] != NP)
           for j, b in enumerate(blocks)):
        continue
    after = d(*blocks)
    if after in seen:
        continue
    seen.add(after)
    inst = {"arm": "plant", "mode": "E", "id": "c", "path": "doc.md",
            "before": base, "after": after, "legs": None, "f2": True}
    recs, _ = E.evaluate(inst)
    for r in recs:
        if r["mech"] == "Q" and r["index"] in (1, 5) and r.get("decided") and r["hard"]["cls"] == "WRONG":
            hits.append((r["index"], r["target"], r["hard"]["hit"], [b[:14] for b in blocks]))
for h in hits:
    print(h)
print(len(seen), "afters,", len(hits), "hits")
