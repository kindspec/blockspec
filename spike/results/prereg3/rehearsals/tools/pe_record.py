"""P-E's q3 record over every completed run with the final plants and the
final prompt (2779cd58...): the v2.1 rehearsals that completed (p3g, p3i;
p3h-1 was an environment abort and did not complete), the superseded V6 at
702bad3, and the V6 at 33f3a34. Prints the count and the exact one-sided 95%
Clopper-Pearson upper bound on the per-run q3 'no' rate.

usage: python3 -I -S -B pe_record.py <pdpe_q3.out> <v6 dir> [<v6 dir> ...]
"""
import glob
import os
import sys
from math import comb


def ub(k, n):
    lo, hi = 0.0, 1.0
    for _ in range(100):
        p = (lo + hi) / 2
        cdf = sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))
        lo, hi = (p, hi) if cdf > 0.05 else (lo, p)
    return hi


rows = []
for ln in open(sys.argv[1], encoding="utf-8"):
    run = ln.split()[0]
    if " P-E q3=" in ln and not run.startswith("run-p3h-"):
        rows.append((run, "yes" if " P-E q3=yes" in ln else "no"))
for d in sys.argv[2:]:
    for c in sorted(glob.glob(os.path.join(d, "v6*", "check.txt"))):
        for ln in open(c, encoding="utf-8"):
            if ln.strip().startswith("P-E:"):
                rows.append((os.path.basename(d) + "/" + os.path.basename(os.path.dirname(c)), ln.split()[3]))
n = len(rows)
no = sum(1 for _, q in rows if q == "no")
for r, q in rows:
    if q == "no":
        print("q3 'no':", r)
print(f"P-E q3: 'yes' in {n - no} of {n} completed runs, 'no' in {no}; one-sided 95% upper bound on the "
      f"per-run 'no' rate {ub(no, n):.1%}")
