"""Copy files into an evidence directory with local paths scrubbed.

<SCRATCH> replaces the session scratch directory, <REHEARSAL> the rehearsal
directory, and <HOME> any remaining home-directory prefix. Exits 1 if any
copied file still contains the home prefix.

usage: python3 -I -S -B scrub_copy.py <dest dir> <src> [<src> ...]
"""
import os
import sys

SCRATCH = "<SCRATCH>"
REHEARSAL = "<REHEARSAL>"
HOME = "<HOME>"
dest, srcs = sys.argv[1], sys.argv[2:]
os.makedirs(dest, exist_ok=True)
bad = 0
for s in srcs:
    t = open(s, encoding="utf-8").read()
    t = t.replace(SCRATCH, "<SCRATCH>").replace(REHEARSAL, "<REHEARSAL>").replace(HOME, "<HOME>")
    out = os.path.join(dest, os.path.basename(s))
    open(out, "w", encoding="utf-8").write(t)
    if "<HOME>" in t:
        bad += 1
        print("UNSCRUBBED", out)
print(len(srcs), "files copied to", dest.replace(HOME, "<HOME>"), "; unscrubbed:", bad)
sys.exit(1 if bad else 0)
