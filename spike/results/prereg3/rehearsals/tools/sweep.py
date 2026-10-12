import hashlib, subprocess, sys, shutil
M, H, CHK = sys.argv[1:4]
orig = open(M + "/orig.py").read(); tgt = M + "/h3/p3/aggregate3.py"
fh = lambda: hashlib.sha256(open(tgt, "rb").read()).hexdigest()
def run():
    shutil.rmtree(M + "/h3/p3/__pycache__", ignore_errors=True)
    r = subprocess.run([sys.executable, "-I", "-S", "-B", CHK, H, M + "/h3"], capture_output=True, text=True)
    return r.returncode, (r.stdout.strip().splitlines() or ["(no output) " + r.stderr[-200:]])[-1]
open(tgt, "w").write(orig); print("unmutated:", run())
MUT = [("void not passed to cell", "void if propagate else []", "[]"),
       ("P-D q3 expectation flipped", '"P-D": {"q1": "yes", "q2": "yes", "q3": "yes"', '"P-D": {"q1": "yes", "q2": "yes", "q3": "no"'),
       ("q3/q4 loop drops q3", 'for q in ("q3", "q4"):\n            if ans[q] != exp[q]', 'for q in ("q4",):\n            if ans[q] != exp[q]'),
       ("P-E q4 expectation flipped", '"P-E": {"q1": "yes", "q2": "yes", "q3": "yes", "q4": "yes"', '"P-E": {"q1": "yes", "q2": "yes", "q3": "yes", "q4": "no"'),
       ("B/C check removed", "if QUALIFIES.get(t, False) != QUALIFIES[exp[\"tier\"]]:", "if False:"),
       ("manifest check removed", '    if m.get("plants") != want:\n        raise', '    if False:\n        raise')]
for name, a, b in MUT:
    open(tgt, "w").write(orig); h0 = fh(); n = orig.count(a)
    open(tgt, "w").write(orig.replace(a, b, 1)); h1 = fh()
    if n != 1 or h0 == h1: print(name, "BROKEN", n); continue
    rc, last = run(); print(f"{name}: {h0[:8]}->{h1[:8]} exit {rc} {'RED' if rc else 'SURVIVED'} | {last}")
open(tgt, "w").write(orig)
