"""Mutate prereg3_plants.py one plant at a time and check that its
realisability check goes red. Each mutant is applied to a copy in a work
directory; a mutant whose pattern does not match once, or that leaves the
file's hash unchanged, is reported BROKEN, never as a pass.

usage: python3 -I -S -B plant_mutants.py <harness dir> <d8 dir> <work dir>
"""
import hashlib
import os
import shutil
import subprocess
import sys

harness, d8, work = sys.argv[1:4]
src = open(os.path.join(harness, "prereg3_plants.py")).read()
MUT = [
    ("P-A Defaults says four", 'd("## Defaults", L1 + "\\n" + L2,',
     'd("## Defaults", L1.replace("three", "four") + "\\n" + L2,'),
    ("P-A Ingest unchanged", 'L1.replace("three", "five")', 'L1'),
    ("P-B Beta status dated 03-05", '"Beta moves sandbox telemetry into the shared pipeline.", ST),',
     '"Beta moves sandbox telemetry into the shared pipeline.", ST.replace("03-04", "03-05")),'),
    ("P-C keeps old window time", 'd("## Sunday windows", NP, W2,', 'd("## Sunday windows", NP, W,'),
    ("P-D change-log copy edited", '"Superseded Backup wording, kept for the change log:", S1 + "\\n" + S2)',
     '"Superseded Backup wording, kept for the change log:", S1.replace("seven", "six") + "\\n" + S2)'),
    ("P-D retention unchanged", 'S1.replace("seven", "thirty")', 'S1'),
    ("P-E stale duplicate removed", ''',
              "## Upload limits", U1 + "\\n" + U2), 1, 1, 5)''', '), 1, 1, 5)'),
    ("P-E limit unchanged", 'U1.replace("50 GB", "80 GB, raised from 50 GB in May,")', 'U1'),
]
os.makedirs(work, exist_ok=True)
for f in ("prose_merge.py", "prereg2_plants.py"):
    shutil.copy(os.path.join(harness, f), work)
h0 = hashlib.sha256(src.encode()).hexdigest()
bad = 0
for name, a, b in MUT:
    m = src.replace(a, b, 1)
    h1 = hashlib.sha256(m.encode()).hexdigest()
    if src.count(a) != 1 or h1 == h0:
        print(f"{name}: BROKEN (pattern count {src.count(a)})")
        bad += 1
        continue
    p = os.path.join(work, "prereg3_plants.py")
    open(p, "w").write(m)
    r = subprocess.run([sys.executable, "-I", "-B", p, "--d8-dir", d8], capture_output=True, text=True)
    fails = [ln for ln in r.stdout.splitlines() if ln.endswith("FAIL") and not ln.startswith("PLANTS")]
    red = r.returncode == 1 and fails
    bad += not red
    print(f"{name}: {h0[:8]}->{h1[:8]} exit {r.returncode} {'RED' if red else 'SURVIVED'} | " + " | ".join(fails))
r = subprocess.run([sys.executable, "-I", "-B", os.path.join(harness, "prereg3_plants.py"), "--d8-dir", d8],
                   capture_output=True, text=True)
print("unmutated:", r.stdout.strip().splitlines()[-1], "exit", r.returncode)
print("MUTANTS:", "ALL RED" if not bad else f"{bad} NOT RED")
