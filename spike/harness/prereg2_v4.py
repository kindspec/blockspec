#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""PRE-REGISTRATION-2.md §9 V4: a mutation sweep over the new gates, in the
style of armed_check.sh.

    python3 -I prereg2_v4.py --d8-dir <research>/experiments/D8-identity

Each mutation breaks one gate in a scratch copy of spike/harness,
PRE-REGISTRATION-2.md and ORACLE.md, then runs V3 (prereg2_v3.py) against the copy. V3
must go red. The mutated file is hashed before and after: a mutation whose
pattern does not occur exactly once leaves the file unchanged and is reported
BROKEN, never as killed or survived. A mutant that only crashes a V3
section, with no named check red, counts as surviving. V4 passes only if
every mutant is killed by a named check, with none surviving and none BROKEN.
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
     "                if not O.repeat_rule(h[\"Bc\"], h[\"Mc\"], h[\"target\"], k, t):",
     "                if False:"),
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
     "    if void and keys:", "    if False:"),
    ("aggregate: F9 not required", "p2/aggregate.py",
     '        if not reproduced(repro[rep["id"]]):\n            differs.append(rep["id"])\n            continue\n', ""),
    ("aggregate: a missing reproduction tolerated", "p2/aggregate.py",
     '        if rep["id"] not in repro:\n            raise MissingRepro',
     '        if False:\n            raise MissingRepro'),
    ("arm0: the bar never stops", "p2/arm0.py",
     "    return nl_twin <= BAR * nl_all", "    return True"),
    ("arm0: exactly 10% stops", "p2/arm0.py",
     "    return nl_twin <= BAR * nl_all", "    return nl_twin < BAR * nl_all"),
    ("arm0: an empty arm fails the bar (§6.5 stops only above 10%)", "p2/arm0.py",
     "    return nl_twin <= BAR * nl_all", "    return nl_all > 0 and nl_twin <= BAR * nl_all"),
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
     '        if QUALIFIES.get(t, False) != QUALIFIES[exp["tier"]]:', "        if False:"),
    ("void: A<->B confusion voids", "p2/tiers.py",
     '        if QUALIFIES.get(t, False) != QUALIFIES[exp["tier"]]:', '        if t != exp["tier"]:'),
    ("void: q3 and q4 not checked", "p2/tiers.py",
     '        for q in ("q3", "q4"):\n            if ans[q]', '        for q in ():\n            if ans[q]'),
    ("void: an untiered plant passes", "p2/tiers.py",
     '            out.append(f"{plant}: untiered")\n', "            pass\n"),
    ("tier: q1 before q2", "p2/tiers.py",
     '    if ans["q2"] == "yes":\n        return "A"\n    if ans["q1"] == "yes":\n        return "B"',
     '    if ans["q1"] == "yes":\n        return "B"\n    if ans["q2"] == "yes":\n        return "A"'),
    ("tier-run: the first run does not bind", "p2/tierrun.py",
     "        if lines > 0:\n            raise TierRefused", "        if False:\n            raise TierRefused"),
    ("tier-run: no window", "p2/tierrun.py",
     "        if not late_reason:", "        if False:"),
    ("tier-run: runs before the start day", "p2/tierrun.py",
     "    if today < start:", "    if False:"),
    ("tier-run: an invalid export is sent", "p2/tierrun.py",
     '    if bad:\n        raise TierRefused("the export fails its validator: "',
     '    if False:\n        raise TierRefused("the export fails its validator: "'),
    ("undecodable: an M case with a non-UTF-8 input is merged anyway", "p2/arms.py",
     '    if any(has_surrogate(case[k]) for k in ("base", "a", "c")):\n        return UNDECODABLE, None\n', ""),
    ("undecodable: E/S read non-UTF-8 with replacement", "p2/arms.py",
     '        t = raw.decode("utf-8")', '        t = raw.decode("utf-8", errors="replace")'),
    ("undecodable: find_merge_cases keeps its strict reader", "p2/arms.py",
     "    P.g = g_tolerant", "    P.g = strict_g"),
    ("undecodable: not counted", "prereg2.py",
     "                    undecodable += 1\n", ""),
    ("arm0: the adjacent-run label dropped", "p2/arm0.py",
     'ADJACENT_RUN_LABEL = "provisional reading (LOG §15)"', 'ADJACENT_RUN_LABEL = "provisional reading"'),
    ("sandbox: the host home bound in", "p2/tierrun.py",
     '          "--chdir", "/work", "--"]',
     '          "--ro-bind", os.path.expanduser("~"), os.path.expanduser("~"), "--chdir", "/work", "--"]'),
    ("sandbox: the agent run outside it", "p2/tierrun.py",
     "        p = subprocess.Popen(argv, stdout",
     '        p = subprocess.Popen(argv[argv.index("--") + 1:], cwd=work, stdout'),
    ("sandbox: the credential file not bound", "p2/tierrun.py",
     '          "--ro-bind", credentials, SANDBOX_HOME + "/.claude/.credentials.json",\n', ""),
    # review A1, A4, A5, A3
    ("A4: a preamble R unit", "p2/oracle.py",
     "    starts = sorted({i for i, _, _ in Mx.headings(text, bl)})\n    return",
     "    starts = sorted({i for i, _, _ in Mx.headings(text, bl)} | ({0} if bl else set()))\n    return"),
    ("A4: an unplaceable plant always voids", "p2/tiers.py",
     "QUALIFIES.get(t, False) != QUALIFIES", "QUALIFIES.get(t, None) != QUALIFIES"),
    ("A5: each cell picks its own representative", "p2/aggregate.py",
     "        rep = reps[key]", "        rep = X.select_packets(recs, inst)[key]"),
    ("A3: WRONG_on_deleted not reported", "p2/aggregate.py",
     '            if rep.get("oracle") == "DELETED":', "            if False:"),
    ("A3: the selection rule ignored in a cell", "p2/aggregate.py",
     '    if rule not in inst.get("rules", []):\n        return False', '    if False:\n        return False'),
    ("A3: the 25-case set reported as the strict set", "p2/aggregate.py",
     'return bool(inst.get("strict" if site_set == "strict" else "set25"))', 'return bool(inst.get("strict"))'),
    ("A3: the strict-set difference not logged", "p2/corpus.py",
     '        counts["strict_difference"] = counts["strict"] - SITE_POLICY_EXPECTED_STRICT',
     '        counts["strict_difference"] = 0'),
    ("B1: an unbound reproduction accepted", "p2/aggregate.py",
     '    return (isinstance(rp, dict) and rp.get("bound") is True and rp.get("ok") is True',
     '    return (isinstance(rp, dict) and rp.get("ok") is True'),
    ("B1: differing reproduction hashes accepted", "p2/aggregate.py",
     '            and rp.get("committed_sha256") == rp.get("regenerated_sha256"))', "            )"),
    ("B8: a failed reproduction vanishes from the reason", "p2/aggregate.py",
     '    note = (f"; F9: {len(differs)} record(s) do not reproduce', '    note = "" and (f"; F9: {len(differs)} record(s) do not reproduce'),
    # review B2, C4
    ("B2: an empty expected manifest sha skips the check", "p2/export.py",
     "    if not want_sha or len(want_sha) != 64:\n        raise ExportError(\"the manifest's expected sha256 is required\")\n"
     "    raw = open(path, \"rb\").read()\n    got = hashlib.sha256(raw).hexdigest()\n    if got != want_sha:",
     "    raw = open(path, \"rb\").read()\n    got = hashlib.sha256(raw).hexdigest()\n    if want_sha and got != want_sha:"),
    ("C4: the manifest's plants not checked", "p2/export.py",
     '    if m.get("plants") != want:', "    if False:"),
    ("C4: void reads the manifest's expectations", "p2/tiers.py",
     "        exp = PLANT_EXPECT[plant]", '        exp = manifest["plants"][plant]["expected"]'),
    ("B7: a symlink followed", "p2/tierrun.py",
     "    if not stat.S_ISREG(st.st_mode):", "    if False:"),
    ("C2: the run not recorded before it starts", "p2/tierrun.py",
     '    append_ledger(state_dir, {"event": "started", "n": n,', '    (lambda *x: None)(state_dir, {"event": "started", "n": n,'),
    ("C2: two runs allowed whatever the first wrote", "p2/tierrun.py",
     "    if len(started) >= 2:", "    if len(started) >= 3:"),
    ("C6: any number of scoring commits", "p2/tierrun.py",
     "    if len(commits) != 1:", "    if not commits:"),
    ("C6: a listing from any day", "p2/tierrun.py",
     "    if listing_day != start:", "    if False:"),
    ("C6: the model chosen again", "p2/tierrun.py",
     "    if os.path.exists(mpath):\n        raise TierRefused(f\"{mpath} exists; the model is chosen once\")",
     "    if False:\n        raise TierRefused(f\"{mpath} exists; the model is chosen once\")"),
    # review C1, B6, C3, B3, B10
    ("B6: hash-object not compared", "p2/binding.py",
     "        if h.strip() != blob:", "        if False:"),
    ("C1: files outside the validation commit not walked", "p2/binding.py",
     "                    if rel not in want:", "                    if False:"),
    ("C1: ignored files not listed", "p2/binding.py",
     '    rc, st, _ = _git(spike, "status", "--porcelain", "--ignored", "--untracked-files=all",\n                     "--", *BOUND_PATHS)',
     '    rc, st, _ = _git(spike, "status", "--porcelain", "--untracked-files=all",\n                     "--", *BOUND_PATHS)'),
    ("C3: uncommitted results ignored", "p2/binding.py",
     '        reasons.append(f"uncommitted under {RESULTS_REL}: {line}")', "        pass"),
    ("C3: overrides accepted on a bound run", "prereg2.py",
     "            if given:\n                raise SystemExit", "            if False:\n                raise SystemExit"),
    ("B10: an unbound run writes under results/prereg2", "prereg2.py",
     "        if inside(v, RESULTS):", "        if False:"),
    ("B3: sample sizes not checked", "prereg2.py",
     "        if sizes and not fixture_ok and (", "        if False and ("),
    ("B5-13/14: unbound inputs accepted", "prereg2.py",
     '    if not o.get("bound") or (tr.state["bound"]', '    if False and (tr.state["bound"]'),
    ("C3: preflight passes several arm0 transcripts", "prereg2.py",
     '        one(f"arm0-{arm}", "arm0", arm)', "        pass"),
    ("C3: preflight passes two runs after a first with lines", "prereg2.py",
     "    if len(runs) == 2 and TRN.count_lines_bytes", "    if False and TRN.count_lines_bytes"),
    # the independent review's surviving mutants (B5), adapted to this code
    ("B5/1: a cell counts every selection rule", "p2/aggregate.py",
     "    recs = [r for r in mine if in_cell(inst[(arm, r[\"instance\"])])]", "    recs = mine"),
    ("B5/2: the floor counts non-NL units", "p2/aggregate.py",
     '    nl = [r for r in recs if r.get("nl")]', "    nl = recs"),
    ("B5/3: F6 not required", "p2/aggregate.py",
     '        f6 = ans["q4"] == "no"', "        f6 = True"),
    ("B5/4: F7 not required", "p2/aggregate.py",
     '        f7 = ans["q3"] == "no"', "        f7 = True"),
    ("B5/6: §6.7's Q condition accepts M", "p2/aggregate.py",
     '    q = nf("k8s-en", "Q", ("E", "S5", "S25")) and nf("cncf-toc", "Q", ("E", "S5", "S25"))',
     '    q = nf("k8s-en", "Q", MODES) and nf("cncf-toc", "Q", MODES)'),
    ("B5/9: the bar over prose only", "p2/arm0.py",
     "    nl_twin = sum(len(d_twin[ty]) for ty in Mx.NL_TYPES)", '    nl_twin = len(d_twin["prose"])'),
    ("B5/10: the last tiers line binds", "p2/tiers.py",
     '        if o["packet"] in tiers:', "        if False:"),
    ("B5/11: unplaceable need not be a boolean", "p2/tiers.py",
     '            assert isinstance(o["unplaceable"], bool)\n', ""),
    ("B5/15: UNKNOWN counts as decided", "p2/evaluate.py",
     '        decided = verdict in ("SURVIVED", "DELETED")\n        r = dict(common, mech="Q"',
     '        decided = verdict in ("SURVIVED", "DELETED", "UNKNOWN")\n        r = dict(common, mech="Q"'),
    ("B5/20: a tiers.jsonl that predates every run accepted", "p2/tierrun.py",
     '    elif os.path.lexists(os.path.join(state_dir, "tiers.jsonl")):', "    elif False:"),
    ("B5/21: the bar read off the `none` rule", "prereg2.py",
     '    out["passes_bar"] = out["rules"][K.VERDICT_RULE]["passes_bar"]',
     '    out["passes_bar"] = out["rules"]["none"]["passes_bar"]'),
    ("B5/24: a cell ignores the Arm 0 bar", "p2/aggregate.py",
     '                if not a0.get("passes_bar"):', "                if False:"),
    ("B5/25: an unplaceable real packet treated as tiered", "p2/aggregate.py",
     '        if tier == "UNPLACEABLE":\n            continue\n', ""),
    # the re-review's mutants (scripts/mutants.py), adapted where the code moved
    ("R1: R-slug t is k's index, not p's unit", "p2/evaluate.py",
     '                t = h["m_b2u"].get(p)', "                t = k"),
    ("H4: p in no unit is always decided", "p2/oracle.py",
     "        return not any(Mc[c] == Bc[k] for c in range(len(Mc)))", "        return True"),
    ("H4: p in no unit is always UNDECIDABLE-REPEAT", "p2/oracle.py",
     "        return not any(Mc[c] == Bc[k] for c in range(len(Mc)))", "        return False"),
    ("R3: any surviving neighbour counts as context", "p2/oracle.py",
     "            if target(kk) == cc:", "            if target(kk) is not None:"),
    ("R4: only the preceding neighbour is scored", "p2/oracle.py",
     "        for d in (-1, 1):", "        for d in (-1,):"),
    ("R5: the after-side twin condition dropped", "p2/oracle.py",
     "            if nb[Bc[kk]] > 1 or nm[Mc[cc]] > 1:", "            if nb[Bc[kk]] > 1:"),
    ("R6: twins of t left out of T", "p2/oracle.py",
     "if c != t and (Mc[c] == Mc[t] or Mc[c] == Bc[k])]", "if c != t and (Mc[c] == Bc[k])]"),
    ("P1: R grading excludes the section's last block", "p2/evaluate.py",
     '("correct" if hit[0] <= p <= hit[1] else "WRONG")', '("correct" if hit[0] <= p < hit[1] else "WRONG")'),
    ("P2: the section form votes over the heading block only", "p2/oracle.py",
     "[pseudo_block(base, bb, first, last)], bm)[0]", "[pseudo_block(base, bb, first, first)], bm)[0]"),
    ("D1: DELETED not counted decided", "p2/aggregate.py",
     'st[X.unit_key(r)].add("decided" if r["decided"] else r["oracle"])',
     'st[X.unit_key(r)].add("decided" if r["oracle"] == "SURVIVED" else r["oracle"])'),
    ("D2: R DELETED is not decided", "p2/evaluate.py",
     'decided = verdict in ("SURVIVED", "DELETED")\n        res = Mx.resolve_r',
     'decided = verdict == "SURVIVED"\n        res = Mx.resolve_r'),
    ("D3: a Q resolution onto a DELETED target is correct", "p2/evaluate.py",
     '    return "correct" if hit is None else "WRONG"', '    return "correct"'),
    ("D4: WRONG_on_deleted labels SURVIVED finds", "p2/aggregate.py",
     'if rep.get("oracle") == "DELETED":', 'if rep.get("oracle") != "DELETED":'),
    ("D5: §6.7's R condition needs both arms", "p2/aggregate.py",
     'r = nf("k8s-en", "R", MODES) or nf("cncf-toc", "R", MODES)',
     'r = nf("k8s-en", "R", MODES) and nf("cncf-toc", "R", MODES)'),
    ("F9a: F9 reads only ok", "p2/aggregate.py",
     'if not reproduced(repro[rep["id"]]):', 'if not repro[rep["id"]].get("ok"):'),
    ("F9b: the representative is the largest id", "p2/export.py",
     'if k not in out or r["id"] < out[k]["id"]:', 'if k not in out or r["id"] > out[k]["id"]:'),
    ("V1: void does not check q4", "p2/tiers.py",
     '        for q in ("q3", "q4"):', '        for q in ("q3",):'),
    ("V2: PLANT_EXPECT P-C q1 flipped", "p2/export.py", '"P-C": {"q1": "no",', '"P-C": {"q1": "yes",'),
    ("V3: PLANT_EXPECT P-B q2 flipped", "p2/export.py",
     '"P-B": {"q1": "yes", "q2": "no",', '"P-B": {"q1": "yes", "q2": "yes",'),
    ("V4: PLANT_EXPECT P-C q3 flipped", "p2/export.py",
     '"P-C": {"q1": "no", "q2": "no", "q3": "no",', '"P-C": {"q1": "no", "q2": "no", "q3": "yes",'),
    ("T1: a third tiering run allowed", "p2/tierrun.py",
     "    if len(started) >= 2:", "    if len(started) >= 4:"),
    ("C3a: a started run without a transcript passes", "prereg2.py",
     "    if len(tier_tr) < len(runs):", "    if False:"),
    ("C3b: the export count not checked", "prereg2.py",
     '    one("export", "export", None)', "    pass"),
    ("C3c: score transcripts not checked", "prereg2.py",
     '        one(f"score-{arm}", "score", arm)', "        pass"),
    ("C6a: the committer day in its own offset", "p2/tierrun.py",
     "    return datetime.datetime.fromisoformat(iso).astimezone(datetime.timezone.utc).date()",
     "    return datetime.datetime.fromisoformat(iso).date()"),
    ("C6b: the window boundary moved by a day", "p2/tierrun.py",
     "    return (today - cday).days > WINDOW_DAYS", "    return (today - cday).days >= WINDOW_DAYS"),
    ("C6c: the most recent opus by id", "p2/tierrun.py",
     'return (max(opus, key=lambda m: m["created_at"])["id"],', 'return (max(opus, key=lambda m: m["id"])["id"],'),
    # the re-review's findings H1-H3, M1-M3
    ("H1: abbreviations allowed", "prereg2.py",
     'ap = argparse.ArgumentParser(description=__doc__.split("\\n\\n")[0], allow_abbrev=False)',
     'ap = argparse.ArgumentParser(description=__doc__.split("\\n\\n")[0])'),
    ("H1: subcommand abbreviations allowed", "prereg2.py",
     "_add(name, allow_abbrev=False, **kw)", "_add(name, **kw)"),
    ("H1: repeated options accepted", "prereg2.py",
     "        rep = repeated_options(argv)\n        if rep:", "        rep = repeated_options(argv)\n        if False:"),
    ("H1: an input's pin not checked", "prereg2.py",
     '    if o.get("pin") != spec["pin"] or', '    if False and o.get("pin") != spec["pin"] or'),
    ("H2: a later commit to the harness accepted", "p2/binding.py",
     "            if later.strip():", "            if False:"),
    ("H2: VALIDATION added more than once accepted", "p2/binding.py",
     "    if len(added) != 1:", "    if not added:"),
    ("H2: a changed VALIDATION accepted", "p2/binding.py",
     "    if touched.split() != [vc]:", "    if False:"),
    ("H2: a malformed manifest sha accepted", "p2/binding.py",
     '        assert isinstance(sha, str) and HEX64.match(sha) and set(v) == {"manifest_sha256"}',
     '        assert isinstance(sha, str)'),
    ("H3/C3: a second execution accepted", "p2/binding.py",
     '    if cmd in ("arm0", "score", "export") and executed(spike, cmd, arm):', "    if False:"),
    ("B4: export may execute twice", "p2/binding.py",
     '    if cmd in ("arm0", "score", "export") and executed(spike, cmd, arm):',
     '    if cmd in ("arm0", "score") and executed(spike, cmd, arm):'),
    ("C4: seal ignores VALIDATION's history", "prereg2.py",
     "    if os.path.lexists(vp) or hist.strip():", "    if os.path.lexists(vp):"),
    ("M1: bytecode caches read", "prereg2.py",
     'sys.pycache_prefix = os.path.join(os.sep, "nonexistent", f"prereg2-nopyc-{os.getpid()}")', "pass"),
    ("M2: an unbound run opens a real bundle", "prereg2.py",
     "    if not BOUND_RUN:\n        raise SystemExit(\"refusing: an unbound run never opens",
     "    if False:\n        raise SystemExit(\"refusing: an unbound run never opens"),
    # round 5: the reviewer's mutants_r5.py (N1-N34), adapted where the code moved
    ("N1: VALIDATION added twice accepted", "p2/binding.py", "    if len(added) != 1:\n", "    if len(added) < 1:\n"),
    ("N3: VALIDATION may carry extra fields", "p2/binding.py", ' and set(v) == {"manifest_sha256"}', ""),
    ("N5: the later-commit range reversed", "p2/binding.py", 'f"{vc}..HEAD"', 'f"HEAD..{vc}"'),
    ("N6: ORACLE.md not a bound path", "p2/binding.py",
     'BOUND_PATHS = ("harness", "PRE-REGISTRATION-2.md", "ORACLE.md")', 'BOUND_PATHS = ("harness", "PRE-REGISTRATION-2.md")'),
    ("N7: a symlinked harness file accepted", "p2/binding.py",
     "        if os.path.islink(p) or not os.path.isfile(p):", "        if not os.path.isfile(p):"),
    ("N9: only HEAD's history searched for a marker", "p2/binding.py",
     '_git(spike, "log", "--all", "--reflog", "--full-history", "--format=%H",',
     '_git(spike, "log", "--full-history", "--format=%H",'),
    ("N10: the work-tree marker ignored", "p2/binding.py",
     "    if os.path.lexists(os.path.join(spike, rel)):\n        return True\n", ""),
    ("N11: score not guarded by its marker", "p2/binding.py",
     '    if cmd in ("arm0", "score", "export") and executed(spike, cmd, arm):',
     '    if cmd in ("arm0", "export") and executed(spike, cmd, arm):'),
    ("N12: every uncommitted transcript exempt", "p2/binding.py",
     "        if own and path == own:", "        if os.sep + 'transcripts' + os.sep in path:"),
    ("N13: a .n transcript suffix not stripped", "p2/binding.py",
     "    if head and tail.isdigit():\n        stem = head\n", ""),
    ("N14: the arm0 marker written before the corpus opens", "prereg2.py",
     '    try:\n        repo, pin, pathspec, bsha = corpus_for(a, K, a.work_dir)\n    except K.NoVerdict as e:\n        executed(tr, "arm0", a.arm)',
     '    executed(tr, "arm0", a.arm)\n    try:\n        repo, pin, pathspec, bsha = corpus_for(a, K, a.work_dir)\n    except K.NoVerdict as e:\n        pass'),
    ("N15: export writes no marker", "prereg2.py", '    executed(tr, "export", None)\n', ""),
    ("N16: --opt=value forms not compared", "prereg2.py", '            name = tok.split("=", 1)[0]', "            name = tok"),
    ("N17: a prescan/parse disagreement accepted", "prereg2.py", "        if unbound != prescan_unbound:", "        if False:"),
    ("N18: a bound run may pass --agent-cmd", "prereg2.py", '"agent_cmd": None, ', ""),
    ("N19: a bound run may pass --fixture-pin", "prereg2.py", '"fixture_pin": None,\n', "\n"),
    ("N21: a no-verdict input skips the pin check", "prereg2.py",
     '    if "no_verdict" in o and "pin" not in o:', '    if "no_verdict" in o:'),
    ("N22: an input's validation commit not compared", "prereg2.py",
     '    if not o.get("bound") or (tr.state["bound"] and o.get("binding", {}).get("validation_commit")\n                              != tr.state.get("validation_commit")):',
     '    if not o.get("bound"):'),
    ("N23: a reproduction from another validation commit accepted", "prereg2.py",
     '        if not fixture_ok and o.get("binding", {}).get("validation_commit") != tr.state.get(\n                "validation_commit"):',
     "        if False:"),
    ("N24: score accepts an Arm 0 result of another validation commit", "prereg2.py",
     '    return not tr.state["bound"] or (a0.get("bound") is True and a0.get("binding", {}).get(\n        "validation_commit") == tr.state.get("validation_commit"))',
     '    return not tr.state["bound"] or a0.get("bound") is True'),
    ("N25: modes_requested not checked", "prereg2.py",
     '\n                                          or s.get("modes_requested") != ["E", "S5", "S25", "M"]):', "):"),
    ("N26: an unbound executed transcript counts as bound", "prereg2.py",
     '.append("# harness bound: True" in text)', ".append(True)"),
    ("N27: H4 misses a twin of k in M's first unit", "p2/oracle.py",
     "        return not any(Mc[c] == Bc[k] for c in range(len(Mc)))",
     "        return not any(Mc[c] == Bc[k] for c in range(1, len(Mc)))"),
    ("N28: p in no unit falls to the first unit", "p2/evaluate.py",
     '                t = h["m_b2u"].get(p)', '                t = h["m_b2u"].get(p, 0)'),
    ("N33: tier-model.json of another scoring commit accepted", "p2/tierrun.py",
     '    if choice.get("scoring_commit") != commit:', "    if False:"),
    # round 5: H-1, M-a, M-c, M-d, M-e
    ("H-1: score's directory made before the corpus opens", "prereg2.py",
     '    try:\n        repo, pin, pathspec, bsha = corpus_for(a, K, a.work_dir)\n    except K.NoVerdict as e:\n        executed(tr, "score", a.arm)',
     '    os.makedirs(out_dir, exist_ok=True)\n    try:\n        repo, pin, pathspec, bsha = corpus_for(a, K, a.work_dir)\n    except K.NoVerdict as e:\n        executed(tr, "score", a.arm)'),
    ("M-a: no marker copy in the common git directory", "p2/binding.py",
     "    if cd:\n        paths.append(", "    if False:\n        paths.append("),
    ("M-a: the common-dir marker not checked", "p2/binding.py",
     '    if cd and os.path.lexists(os.path.join(cd, "prereg2", os.path.basename(rel))):', "    if False:"),
    ("M-a: the reflog not searched", "p2/binding.py",
     '"log", "--all", "--reflog", "--full-history"', '"log", "--all", "--full-history"'),
    ("M-c: no --full-history when counting VALIDATION's adds", "p2/binding.py",
     '_git(spike, "log", "--full-history", "--format=%H", "--diff-filter=A", "--", VALIDATION_REL)',
     '_git(spike, "log", "--format=%H", "--diff-filter=A", "--", VALIDATION_REL)'),
    ("M-c: a shallow repository accepted", "p2/binding.py",
     '    if sh.strip() == "true":', "    if False:"),
    ("M-c: replace refs accepted", "p2/binding.py", "    if rep.strip():", "    if False:"),
    ("M-c: grafts accepted", "p2/binding.py",
     '    if cd and os.path.exists(os.path.join(cd, "info", "grafts")):', "    if False:"),
    ("M-c: the caller's GIT_* variables kept", "p2/binding.py",
     '    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}', "    e = dict(os.environ)"),
    ("M-d: --d8-dir left on sys.path", "p2/mech.py",
     '            sys.path[:] = [x for x in sys.path if os.path.realpath(x or ".") != os.path.realpath(d8_dir)]',
     "            sys.path.insert(0, d8_dir)"),
    ("M-d: module origins not checked", "prereg2.py",
     "        shadowed = check_modules()\n        if shadowed:\n            tr.record_binding",
     "        shadowed = []\n        if shadowed:\n            tr.record_binding"),
    ("M-d: -S not required", "prereg2.py",
     "        if not (sys.flags.isolated and sys.flags.no_site):", "        if not sys.flags.isolated:"),
    ("M1: no isolation required", "prereg2.py",
     "        if not (sys.flags.isolated and sys.flags.no_site):", "        if False:"),
    ("M3: a removed marker re-enables the arm", "p2/binding.py",
     '    _, out, _ = _git(spike, "log", "--all", "--reflog", "--full-history", "--format=%H",\n                     "--diff-filter=A", "--", rel)\n    return bool(out.strip())',
     "    return False"),
    ("M-e: a gap does not override its cell", "p2/aggregate.py",
     "    for cid, why in (gaps or {}).items():\n        if cid in cells:", "    for cid, why in (gaps or {}).items():\n        if False:"),
    ("M-e: a gap before Arm 0 accepted", "p2/gaps.py",
     '        if len(arm0) != 1 or c == arm0[0] or not _is_ancestor(spike, arm0[0], c):', "        if False:"),
    ("M-e: a gap after the scoring commit applied", "p2/gaps.py",
     '        if c == scoring_commit or _is_ancestor(spike, scoring_commit, c):', "        if False:"),
    ("M-e: a gap may be edited", "p2/gaps.py",
     '            if e["id"] in body and body[e["id"]] != e:', "            if False:"),
    ("M-e: a gap's LOG entry not checked", "p2/gaps.py",
     '        if not re.search(r"— " + re.escape(e["log"]) + r"\\.", logtxt):', "        if False:"),
    ("M-e: a gap's red test not checked", "p2/gaps.py",
     "        if _git(spike, \"cat-file\", \"-e\", f\"{c}:{_rel_top(spike, e['red_test'])}\")[0] != 0:", "        if False:"),
    ("M-e: a gap's red test may lie anywhere", "p2/gaps.py",
     '    if not (isinstance(rt, str) and rt.startswith(GAP_TESTS_REL) and ".." not in rt.split(os.sep)):',
     "    if not isinstance(rt, str):"),
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
        return subprocess.run([sys.executable, "-I", "-S", "-B", os.path.join(root, "harness", "prereg2_v3.py"),
                               "--d8-dir", a.d8_dir], capture_output=True, text=True, env=env)

    tmp = tempfile.mkdtemp(prefix="prereg2-v4.")
    try:
        def fresh():
            root = os.path.join(tmp, "spike")
            shutil.rmtree(root, ignore_errors=True)
            os.makedirs(root)
            shutil.copytree(os.path.join(SPIKE, "harness"), os.path.join(root, "harness"),
                            ignore=shutil.ignore_patterns("__pycache__"))
            for f in ("PRE-REGISTRATION-2.md", "ORACLE.md"):
                shutil.copy(os.path.join(SPIKE, f), root)
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
            named = [f for f in fails if not f.startswith("section raised")]
            if r.returncode != 0 and not named:
                # A mutant that only crashes a section is not shown red by a
                # check that names the gate; it counts as surviving.
                survived += 1
                print(f"MUTATION {n:2} {name}: *** KILLED ONLY BY A CRASH [{before} -> {after}] "
                      f"({(fails or ['(no output)'])[0][:110]}) ***")
            elif r.returncode != 0:
                killed += 1
                fails = named
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
