#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""PRE-REGISTRATION-3.md §9, V4: a mutation sweep over harness3's gates.

Each mutation replaces one pattern, which must match exactly once, in one
file under harness3/p3/. The file's sha256 is taken before and after; a
mutation whose pattern does not match once, or that leaves the hash
unchanged, is BROKEN, never a pass. Each mutant then runs V3
(prereg3_v3.py), which must exit non-zero: the mutant is KILLED. The file is
restored from its original bytes after every mutant, and its hash is checked
again; a restore that does not give the original bytes stops the sweep.

V4 passes only if every mutant is KILLED: none SURVIVED and none BROKEN.

Run:  python3 -I -S -B harness3/prereg3_v4.py --d8-dir <research>/experiments/D8-identity
"""
import argparse
import hashlib
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
P3 = os.path.join(HERE, "p3")

# Mutants in prereg3.py, outside p3/, are listed with the path "../prereg3.py".
PERNAME = """    ok, lines = X3.same_per_name(repo, m2["nonce"], a.export, m["nonce"], res["packet_keys"])
    for ln in lines:
        print(ln)
    if not ok:
        print("refusing: the per-name check failed; no verdict is written", file=sys.stderr)
        return 1
"""
PRINTS = """    for (arm, mode, mech), c in sorted(res["cells"].items()):
        print(f"  {arm:<14}{mode:<5}{mech}  {c['verdict']:<11} {c.get('reason', '')}")
    if res["void"]:
        print("TIERING VOID: " + "; ".join(res["void"]))
    print(f"near misses (distinct units): {res['near_misses']}")
    print(f"OVERALL: {res['overall']}")
"""
MUTATIONS = [
    ("../prereg3.py", "per-name check moved after the OVERALL print (delta Low)",
     PERNAME + PRINTS, PRINTS + PERNAME),
    ("../prereg3.py", "aggregate runs without --manifest2 (M1)",
     "    p.add_argument(\"--manifest2\", required=True,", "    p.add_argument(\"--manifest2\", required=False,"),
    # (file, label, pattern, replacement)
    ("tierrun3.py", "init check accepts any first event",
     "    return (isinstance(ev, dict) and ev.get(\"type\") == \"system\"",
     "    return True or (isinstance(ev, dict) and ev.get(\"type\") == \"system\""),
    ("tierrun3.py", "a stream with no init event passes",
     "        if not checked:\n            init_failed = True", "        if False:\n            init_failed = True"),
    ("tierrun3.py", "run cap allows a third run", "    if len(started) >= 2:", "    if len(started) >= 3:"),
    ("tierrun3.py", "an init_failed run can bind",
     "        if not init_failed and lines > 0:", "        if lines > 0:"),
    ("tierrun3.py", "auth label misses a 401",
     "ev.get(\"error_status\") in (401, 403)", "ev.get(\"error_status\") in (403,)"),
    ("tierrun3.py", "PACKETS.txt not bound into the sandbox",
     "    a[i:i] = [\"--ro-bind\", os.path.join(export_dir, X3.MANIFEST), \"/work/\" + X3.MANIFEST]",
     "    a[i:i] = []"),
    ("tierrun3.py", "credential not logged after the run",
     "        log(f\"credential after:", "        (lambda *x: None)(f\"credential after:"),
    ("gates.py", "start day is the verdict day itself", "    if today < start:", "    if today < cday:"),
    ("gates.py", "window one day longer", "    if (today - cday).days > WINDOW_DAYS:",
     "    if (today - cday).days > WINDOW_DAYS + 1:"),
    ("gates.py", "gate accepts an unbound verdict", "    if v.get(\"bound\") is not True or (",
     "    if False or ("),
    ("gates.py", "gate accepts a verdict bound elsewhere",
     ".get(\"validation_commit\") != BD.PREREG2_VALIDATION:", ".get(\"validation_commit\") == \"never\":"),
    ("gates.py", "gate accepts a changed verdict",
     "    if touched.split() != [vc]:\n        raise GateError(f\"{VERDICT2} has changed",
     "    if False:\n        raise GateError(f\"{VERDICT2} has changed"),
    ("gates.py", "gate needs no tiers.jsonl",
     "    if len(t2) != 1 or not _ancestor(spike, t2[0], vc):", "    if False:"),
    ("gates.py", "gate needs no started run",
     "    if not runs or not any(o.get(\"event\") == \"started\" for o in _ledger(runs, TIER_RUNS2)):",
     "    if not runs:"),
    ("gates.py", "gate needs tiers.jsonl but not before the verdict (O3)",
     "    if len(t2) != 1 or not _ancestor(spike, t2[0], vc):", "    if len(t2) != 1:"),
    ("gates.py", "gate reads tier-runs.txt at HEAD, not at the verdict commit (O4)",
     "    runs = _show(spike, vc, TIER_RUNS2)", "    runs = _show(spike, \"HEAD\", TIER_RUNS2)"),
    ("gates.py", "start day not converted to UTC (O5)",
     "datetime.datetime.fromisoformat(out.strip()).astimezone(datetime.timezone.utc).date()",
     "datetime.datetime.fromisoformat(out.strip()).date()"),
    ("gates.py", "a non-JSON ledger line is skipped (L3)",
     "            raise GateError(f\"{where}, line {i}, is not a JSON object\")", "            continue"),
    ("gates.py", "tier-model blob not pinned", "    if rc != 0 or blob.strip() != TIER_MODEL_BLOB:",
     "    if rc != 0:"),
    ("gates.py", "order guard ignores history and reflogs",
     "        if out.strip():\n            found.append(f\"{rel} is in the history",
     "        if False:\n            found.append(f\"{rel} is in the history"),
    ("gates.py", "order guard ignores other work trees", "    for wt in _worktrees(spike) or [top]:",
     "    for wt in [top]:"),
    ("gates.py", "order guard ignores tier-work directories",
     "                      if d.startswith(\"tier-work-\")]", "                      if d.startswith(\"never-\")]"),
    ("gates.py", "committed order ignores ancestry",
     "    if not _ancestor(spike, e3[0], t2[0]) or e3[0] == t2[0]:", "    if False:"),
    ("gates.py", "committed order ignores time", "    if not first > ex:", "    if False:"),
    ("aggregate3.py", "five-plant void not passed to cell()",
     "AG.cell(arm, mode, mech, sc, nonce, tiers, repro, void, near, reps)",
     "AG.cell(arm, mode, mech, sc, nonce, tiers, repro, [], near, reps)"),
    ("aggregate3.py", "inputs accepted when unbound", "    if o.get(\"bound\") is not True or (",
     "    if False and ("),
    ("aggregate3.py", "inputs accepted from any commit", "not in accepted:", "in ():"),
    ("aggregate3.py", "disagreeing repros accepted", "        if rid in out and (", "        if False and ("),
    ("aggregate3.py", "prereg 3 repros accepted when bound to d79bf2e (L4 source split)",
     "        tagged.append((o, (vc3,)))", "        tagged.append((o, (vc3, BD.PREREG2_VALIDATION)))"),
    ("aggregate3.py", "prereg 3 repros accepted with no prereg 3 validation commit (L4)",
     "        if not vc3:\n            raise InputRefused", "        if False:\n            raise InputRefused"),
    ("plants.py", "an UNPLACEABLE plant counts as qualifying (O2)",
     "        if QUALIFIES.get(t, False) != QUALIFIES[exp[\"tier\"]]:",
     "        if QUALIFIES.get(t, True) != QUALIFIES[exp[\"tier\"]]:"),
    ("plants.py", "void ignores the B/C line",
     "        if QUALIFIES.get(t, False) != QUALIFIES[exp[\"tier\"]]:", "        if False:"),
    ("plants.py", "void ignores q3", "        for q in (\"q3\", \"q4\"):\n            if ans[q] != exp[q]:",
     "        for q in (\"q4\",):\n            if ans[q] != exp[q]:"),
    ("plants.py", "void ignores q4", "        for q in (\"q3\", \"q4\"):\n            if ans[q] != exp[q]:",
     "        for q in (\"q3\",):\n            if ans[q] != exp[q]:"),
    ("plants.py", "void ignores an untiered plant",
     "        if ans is None:\n            out.append(f\"{plant}: untiered\")\n            continue",
     "        if ans is None:\n            continue"),
    ("plants.py", "P-D's q3 expectation flipped",
     "\"P-D\": {\"q1\": \"yes\", \"q2\": \"yes\", \"q3\": \"yes\"", "\"P-D\": {\"q1\": \"yes\", \"q2\": \"yes\", \"q3\": \"no\""),
    ("plants.py", "P-E's q4 expectation flipped",
     "\"P-E\": {\"q1\": \"yes\", \"q2\": \"yes\", \"q3\": \"yes\", \"q4\": \"yes\"",
     "\"P-E\": {\"q1\": \"yes\", \"q2\": \"yes\", \"q3\": \"yes\", \"q4\": \"no\""),
    ("plants.py", "manifest plants not checked",
     "    if not isinstance(m, dict) or m.get(\"plants\") != manifest_plants():",
     "    if not isinstance(m, dict):"),
    ("export3.py", "PACKETS.txt contents not checked",
     "            open(mp, encoding=\"utf-8\").read() != manifest_text(names):",
     "            open(mp, encoding=\"utf-8\").read() != manifest_text(names) and False:"),
    ("export3.py", "PACKETS.txt may be missing",
     "        if os.path.islink(p) or not os.path.isfile(p):\n            bad.append(f\"{f} missing",
     "        if False:\n            bad.append(f\"{f} missing"),
    ("export3.py", "same_records ignores missing and extra packets",
     "    ok &= not missing and not extra", "    ok &= True"),
    ("export3.py", "same_records ignores prereg 2's plant count", "        ok &= c == 1", "        ok &= True"),
    ("export3.py", "same_plants accepts any plant",
     "        same = content_hash(got) == content_hash(regen[p]) and", "        same = True or"),
    ("export3.py", "per-name check passes with zero keys checked (M1)",
     "    return differ == 0 and checked > 0, [", "    return differ == 0, ["),
    ("export3.py", "per-name check counts no difference",
     "        differ += content_hash(p2pk[n2]) != content_hash(got3)", "        differ += 0"),
    ("export3.py", "document pin not checked",
     "    if hashlib.sha256(raw).hexdigest() != PREREG3_SHA256:", "    if False:"),
    ("export3.py", "prompt pin not checked",
     "    if hashlib.sha256(p.encode()).hexdigest() != PROMPT_SHA256:", "    if False:"),
    ("binding.py", "prereg 2's harness not compared with d79bf2e",
     "    bad = files_differ(spike, commit, PREREG2.bound_paths)", "    bad = []"),
    ("binding.py", "prereg 3 markers looked for under prereg2/",
     "    if cd and os.path.lexists(os.path.join(cd, ns.name, os.path.basename(rel))):",
     "    if cd and os.path.lexists(os.path.join(cd, \"prereg2\", os.path.basename(rel))):"),
    ("binding.py", "prereg 3 markers written under prereg2/",
     "        paths.append(os.path.join(cd, ns.name, os.path.basename(marker_rel(ns, cmd, arm))))",
     "        paths.append(os.path.join(cd, \"prereg2\", os.path.basename(marker_rel(ns, cmd, arm))))"),
]


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--d8-dir", required=True)
    a = ap.parse_args()
    v3 = [sys.executable, "-I", "-S", "-B", os.path.join(HERE, "prereg3_v3.py"), "--d8-dir", a.d8_dir]
    r = subprocess.run(v3, capture_output=True, text=True)
    print(f"unmutated V3: exit {r.returncode}, {(r.stdout.strip().splitlines() or ['?'])[-1]}")
    if r.returncode != 0:
        print("V4: FAIL (V3 is not green unmutated)")
        return 1
    killed = survived = broken = 0
    for fname, label, pat, rep in MUTATIONS:
        p = os.path.join(P3, fname)
        orig = open(p, "rb").read()
        h0 = sha(p)
        src = orig.decode("utf-8")
        if src.count(pat) != 1:
            print(f"BROKEN    {fname}: {label} (pattern matches {src.count(pat)} times)")
            broken += 1
            continue
        try:
            with open(p, "w", encoding="utf-8") as f:
                f.write(src.replace(pat, rep, 1))
            h1 = sha(p)
            if h1 == h0:
                print(f"BROKEN    {fname}: {label} (hash unchanged)")
                broken += 1
                continue
            r = subprocess.run(v3, capture_output=True, text=True)
            fails = [ln for ln in r.stdout.splitlines() if ln.startswith("FAIL")]
            if r.returncode != 0:
                killed += 1
                why = fails[0][6:80] if fails else (r.stderr.strip().splitlines() or ["?"])[-1][:80]
                print(f"KILLED    {fname}: {label}  {h0[:8]}->{h1[:8]}  [{why}]")
            else:
                survived += 1
                print(f"SURVIVED  {fname}: {label}  {h0[:8]}->{h1[:8]}")
        finally:
            with open(p, "wb") as f:
                f.write(orig)
            if sha(p) != h0:
                print(f"RESTORE FAILED: {p}")
                return 2
    n = len(MUTATIONS)
    print(f"{n} mutants: {killed} killed, {survived} survived, {broken} broken")
    ok = killed == n
    print("V4:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
