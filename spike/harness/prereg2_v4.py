#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""PRE-REGISTRATION-2.md §9 V4: a mutation sweep over the new gates, in the
style of armed_check.sh.

    python3 -I prereg2_v4.py --d8-dir <research>/experiments/D8-identity

Each mutation breaks one gate in a scratch copy of spike/harness and
PRE-REGISTRATION-2.md, then runs V3 (prereg2_v3.py) against the copy. V3
must go red. The mutated file is hashed before and after: a mutation whose
pattern does not occur exactly once leaves the file unchanged and is reported
BROKEN, never as killed or survived. V4 passes only if every mutant is
killed, with none surviving and none BROKEN.
"""
import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SPIKE = os.path.dirname(HERE)

# (name, file relative to spike/harness, old text, new text)
MUTATIONS = [
    ("repeat: T always empty", "p2/oracle.py",
     "    T = [c for c in range(len(Mc)) if c != t and (Mc[c] == Mc[t] or Mc[c] == Bc[k])]",
     "    T = []"),
    ("repeat: twins of k left out of T", "p2/oracle.py",
     "if c != t and (Mc[c] == Mc[t] or Mc[c] == Bc[k])]", "if c != t and (Mc[c] == Mc[t])]"),
    ("repeat: a tie decides", "p2/oracle.py",
     "return s[t] >= 1 and all(s[t] > s[c] for c in T)",
     "return s[t] >= 1 and all(s[t] >= s[c] for c in T)"),
    ("repeat: ctx(t) of 0 decides", "p2/oracle.py",
     "return s[t] >= 1 and all(s[t] > s[c] for c in T)",
     "return all(s[t] >= s[c] for c in T)"),
    ("repeat: twinned neighbours count as context", "p2/oracle.py",
     "            if nb[Bc[kk]] > 1 or nm[Mc[cc]] > 1:\n                continue\n", ""),
    ("split: never fires", "p2/oracle.py",
     "    return len(units) >= 2", "    return len(units) >= 3"),
    ("split: only legs that did not propose", "p2/oracle.py",
     "        if len(mapped) / len(mine) >= P.ORACLE_CONFIDENCE:",
     "        if len(mapped) / len(mine) < P.ORACLE_CONFIDENCE:"),
    ("evaluate: REPEAT not applied to Q", "p2/evaluate.py",
     "            if not O.repeat_rule(Bc, Mc, btarget, k, tgt):",
     "            if False:"),
    ("evaluate: SPLIT not applied to Q", "p2/evaluate.py",
     "            elif O.split_rule(base, after, legs, O.base_lines_of(base, bb, k, k), m_line_block):",
     "            elif False:"),
    ("evaluate: R slug REPEAT not applied", "p2/evaluate.py",
     "                elif not O.repeat_rule(h[\"Bc\"], h[\"Mc\"], h[\"target\"], k, t):",
     "                elif False:"),
    ("evaluate: R slug SPLIT not applied", "p2/evaluate.py",
     "                elif O.split_rule(base, after, legs, O.base_lines_of(base, bb, *h[\"B\"][k]),",
     "                elif False and O.split_rule(base, after, legs, O.base_lines_of(base, bb, *h[\"B\"][k]),"),
    ("evaluate: R region REPEAT not applied", "p2/evaluate.py",
     "                if not O.repeat_rule(Bc, Mc, btarget, first, p):",
     "                if False:"),
    ("evaluate: R graded by any resolution", "p2/evaluate.py",
     '("correct" if hit[0] <= p <= hit[1] else "WRONG")', '"correct"'),
    ("evaluate: the 20-character floor dropped", "p2/evaluate.py",
     '        if len(anc["quote"]) < 20:', '        if len(anc["quote"]) < 0:'),
    ("evaluate: F3 ignores the legs", "p2/evaluate.py",
     '    states = [base] + list(legs or []) + [after]', '    states = [after]'),
    ("R: slugs before region markers", "p2/mech.py",
     "    if reg:\n        return", "    if False:\n        return"),
    ("R: a duplicated slug resolves to the first", "p2/mech.py",
     "    if len(hit) == 1:\n        return (\"slug\"", "    if len(hit) >= 1:\n        return (\"slug\""),
    ("R: names from blocks of any type", "p2/mech.py",
     '        if D83.btype(b["content"]) != "heading":\n            continue\n', ""),
    ("R: section ends at a deeper heading", "p2/mech.py",
     "        if i > h and l <= lv:", "        if i > h:"),
    ("D8 pin: any directory accepted", "p2/mech.py",
     "        if got != want:\n            bad.append", "        if False:\n            bad.append"),
    ("bundle: an absent pin is not NO VERDICT", "p2/corpus.py",
     '    if git(repo, "cat-file", "-e", spec["pin"] + "^{commit}", check=False).returncode != 0:',
     "    if False:"),
    ("bundle: the sha256 not checked", "p2/corpus.py",
     '    if got != want["sha256"]:', "    if False:"),
    ("bundle: a work repository reused", "p2/corpus.py",
     "    if os.path.exists(repo):\n        raise RuntimeError",
     "    if False:\n        raise RuntimeError"),
    ("sampler: the arm left out of the salt", "p2/corpus.py",
     'f"prereg2:{arm}:{key}"', 'f"prereg2:{key}"'),
    ("sampler: D8's Random(7) shuffle", "p2/corpus.py",
     "    return sorted(keys, key=lambda x: (rank(arm, x), x))[:k]",
     "    import random\n    ks = list(keys)\n    random.Random(7).shuffle(ks)\n    return ks[:k]"),
    ("E: adds enter the population", "p2/corpus.py",
     '        if st == "M":\n            pop.append', '        if st in ("M", "A"):\n            pop.append'),
    ("S: equal blobs enter the population", "p2/corpus.py",
     "                elif a == b:\n                    same += 1", "                elif False:\n                    same += 1"),
    ("M filter: every case kept under every rule", "p2/corpus.py",
     '        rules = [r for r in RULES if c["path"] in sel[r]]', "        rules = list(RULES)"),
    ("site-policy: repo-sync stays in the strict set", "p2/corpus.py",
     'SITE_POLICY_STRICT = ("automated-sync", "repo-sync")', 'SITE_POLICY_STRICT = ("automated-sync",)'),
    ("site-policy: matched case-insensitively", "p2/corpus.py",
     "    return (not any(s in subject for s in SITE_POLICY_STRICT),",
     "    return (not any(s in subject.lower() for s in SITE_POLICY_STRICT),"),
    ("§6.3: yaml-fence reads the whole file", "d8_cheap_arm.py",
     "    return end >= 0 and bool(GENERATED_KEY.search(text[:end]))",
     "    return bool(GENERATED_KEY.search(text))"),
    ("distinct: a unit keyed by its instance", "p2/export.py",
     '    return (r["arm"], r["mech"], r.get("name", ""), r["unit"])',
     '    return (r["arm"], r["mech"], r.get("name", ""), r["unit"], r["id"])'),
    ("decided rule: every instance must be decided", "p2/aggregate.py",
     '        if "decided" in s:', '        if s == {"decided"}:'),
    ("floor: 299 is enough", "p2/aggregate.py", "FLOOR = 300", "FLOOR = 299"),
    ("floor: 300 is not enough", "p2/aggregate.py",
     "    if n_decided < FLOOR:", "    if n_decided <= FLOOR:"),
    ("floor: the undecidable share ignored", "p2/aggregate.py",
     "    if n_undecidable > UNDECIDABLE_MAX * (n_decided + n_undecidable):",
     "    if False:"),
    ("aggregate: empty input gets a verdict", "p2/aggregate.py",
     "    if not arm0 or not scores or not any(s.get(\"records\") for s in scores.values()):",
     "    if False:"),
    ("aggregate: untiered packets ignored", "p2/aggregate.py",
     "    elif untiered:", "    elif False:"),
    ("aggregate: void tiering ignored", "p2/aggregate.py",
     "    if void and packets:", "    if False:"),
    ("aggregate: F9 not required", "p2/aggregate.py",
     '        if repro[rep["id"]] is not True:\n            continue\n', ""),
    ("aggregate: a missing reproduction tolerated", "p2/aggregate.py",
     '        if rep["id"] not in repro:\n            raise MissingRepro',
     '        if False:\n            raise MissingRepro'),
    ("arm0: the bar never stops", "p2/arm0.py",
     "    return nl_twin <= BAR * nl_all", "    return True"),
    ("arm0: exactly 10% stops", "p2/arm0.py",
     "    return nl_twin <= BAR * nl_all", "    return nl_twin < BAR * nl_all"),
    ("arm0: an empty arm passes", "p2/arm0.py",
     "    if nl_all == 0:\n        return False", "    if nl_all == 0:\n        return True"),
    ("score: Arm 0 not consulted", "prereg2.py",
     '    if not a0.get("passes_bar"):', '    if False:'),
    ("export: F1 ignored", "p2/export.py",
     '    if "yaml-fence" not in inst.get("rules", []):\n        return False',
     '    if False:\n        return False'),
    ("export: the strict set ignored", "p2/export.py",
     '        return bool(inst.get("strict"))', "        return True"),
    ("export: F5 ignored", "p2/export.py",
     '    return r["mech"] == "R" or r.get("nl") is True', "    return True"),
    ("validator: fields outside the allow-list accepted", "p2/export.py",
     "        if set(pj) - PACKET_FIELDS:", "        if False:"),
    ("validator: numbers accepted", "p2/export.py",
     "    if isinstance(v, bool) or isinstance(v, (int, float)):", "    if False:"),
    ("validator: extra files accepted", "p2/export.py",
     "        if files != want:", "        if not want <= files:"),
    ("validator: extra root files accepted", "p2/export.py",
     "    if extra:\n        bad.append", "    if False:\n        bad.append"),
    ("validator: an empty export accepted", "p2/export.py",
     "    if not names:\n        bad.append", "    if False:\n        bad.append"),
    ("names: the nonce left out", "p2/export.py",
     'hashlib.sha256(bytes.fromhex(nonce_hex) + b":" + key.encode("utf-8"))',
     'hashlib.sha256(key.encode("utf-8"))'),
    ("seal: overwrites a sealed manifest", "p2/export.py",
     "    if os.path.exists(path):\n        raise ExportError(f\"{path} exists; a manifest is sealed once\")",
     "    if False:\n        raise ExportError(f\"{path} exists; a manifest is sealed once\")"),
    ("void: the B/C line not checked", "p2/tiers.py",
     '        if QUALIFIES[t] != QUALIFIES[exp["tier"]]:', "        if False:"),
    ("void: A<->B confusion voids", "p2/tiers.py",
     '        if QUALIFIES[t] != QUALIFIES[exp["tier"]]:', '        if t != exp["tier"]:'),
    ("void: q3 and q4 not checked", "p2/tiers.py",
     '        for q in ("q3", "q4"):\n            if ans[q]', '        for q in ():\n            if ans[q]'),
    ("void: an untiered plant passes", "p2/tiers.py",
     '            out.append(f"{plant}: untiered")\n', "            pass\n"),
    ("tier: q1 before q2", "p2/tiers.py",
     '    if ans["q2"] == "yes":\n        return "A"\n    if ans["q1"] == "yes":\n        return "B"',
     '    if ans["q1"] == "yes":\n        return "B"\n    if ans["q2"] == "yes":\n        return "A"'),
    ("tier-run: the first run does not bind", "p2/tierrun.py",
     "        if existing is None or existing > 0:", "        if False:"),
    ("tier-run: no window", "p2/tierrun.py",
     "        if not late_reason:", "        if False:"),
    ("tier-run: runs before the start day", "p2/tierrun.py",
     "    if today < start:", "    if False:"),
    ("tier-run: an invalid export is sent", "p2/tierrun.py",
     "    if bad:\n        raise TierRefused", "    if False:\n        raise TierRefused"),
    ("transcript: no exit status written", "p2/transcript.py",
     '        self.f.write(f"\\n# end: {now()}\\n# {how}: exit status {rc}\\n")',
     '        self.f.write("")'),
    ("repro: any regeneration accepted", "prereg2.py",
     "    ok = regen == committed", "    ok = regen is not None"),
]


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--d8-dir", required=True)
    a = ap.parse_args()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")

    def v3(root):
        return subprocess.run([sys.executable, "-I", "-B", os.path.join(root, "harness", "prereg2_v3.py"),
                               "--d8-dir", a.d8_dir], capture_output=True, text=True, env=env)

    tmp = tempfile.mkdtemp(prefix="prereg2-v4.")
    try:
        def fresh():
            root = os.path.join(tmp, "spike")
            shutil.rmtree(root, ignore_errors=True)
            os.makedirs(root)
            shutil.copytree(os.path.join(SPIKE, "harness"), os.path.join(root, "harness"),
                            ignore=shutil.ignore_patterns("__pycache__"))
            shutil.copy(os.path.join(SPIKE, "PRE-REGISTRATION-2.md"), root)
            return root

        print("=== 0. baseline: unmutated harness, V3")
        r = v3(fresh())
        print("   " + "\n   ".join(r.stdout.strip().splitlines()[-2:]))
        if r.returncode != 0:
            print("baseline is not green; stop")
            return 1
        print(f"\n=== {len(MUTATIONS)} mutations: each must turn V3 red")
        killed = survived = broken = 0
        for n, (name, rel, old, new) in enumerate(MUTATIONS, 1):
            root = fresh()
            p = os.path.join(root, "harness", rel)
            before = sha(p)
            src = open(p, encoding="utf-8").read()
            if src.count(old) == 1:
                open(p, "w", encoding="utf-8").write(src.replace(old, new))
            after = sha(p)
            if before == after:
                broken += 1
                print(f"MUTATION {n:2} {name}: BROKEN -- pattern found {src.count(old)} times, "
                      f"file unchanged ({before})")
                continue
            r = v3(root)
            fails = [ln.strip()[6:] for ln in r.stdout.splitlines() if ln.startswith("  FAIL")]
            if r.returncode != 0:
                killed += 1
                why = fails[0] if fails else (r.stdout.strip().splitlines() or ["(no output)"])[-1]
                print(f"MUTATION {n:2} {name}: KILLED [{before} -> {after}] "
                      f"({len(fails)} check(s) red; first: {why[:110]})")
            else:
                survived += 1
                print(f"MUTATION {n:2} {name}: *** SURVIVED [{before} -> {after}] -- V3 stayed green ***")
        print(f"\n{len(MUTATIONS)} mutants: {killed} killed, {survived} survived, {broken} BROKEN")
        ok = killed == len(MUTATIONS)
        print("V4:", "PASS" if ok else "FAIL")
        return 0 if ok else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
