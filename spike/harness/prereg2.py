#!/usr/bin/env -S python3 -I -S -B
# SPDX-License-Identifier: MIT
"""PRE-REGISTRATION-2.md, the harness. blockspec#2. Run it isolated:

    python3 -I -S -B harness/prereg2.py seal       --manifest PATH   (before validation, once)
    python3 -I -S -B harness/prereg2.py arm0       --d8-dir D8 --arm ARM --work-dir W [--bundle-dir D]
    python3 -I -S -B harness/prereg2.py score      --d8-dir D8 --arm ARM --work-dir W [--bundle-dir D]
    python3 -I -S -B harness/prereg2.py export     --d8-dir D8 --manifest PATH
    python3 -I -S -B harness/prereg2.py tier-model                   (on the start day)
    python3 -I -S -B harness/prereg2.py tier-run   [--late-reason TEXT] [--credentials FILE]
    python3 -I -S -B harness/prereg2.py repro      --d8-dir D8 --arm ARM --id RECORD --work-dir W
    python3 -I -S -B harness/prereg2.py aggregate  --d8-dir D8 --manifest PATH
    python3 -I -S -B harness/prereg2.py validate-export DIR

§9's order of work binds: validation, then Arm 0, then the scoring arms and
the export, then tiers.jsonl, then the sealed manifest, the join and the
verdict. Each step lands on main as one squash commit (LOG.md §16, ruled
2026-10-08). The bundles are read from --bundle-dir, else $PREREG2_BUNDLE_DIR,
else the durable local copy recorded in p2/bundles.json (LOG.md §15).

THE BINDING IS CHECKED HERE (LOG.md §16, §18, §20). What it does not stop:
whoever runs the harness can run other code, and a forged history derives a
validation commit of its own; each §9 pull request's review re-derives the
validation commit in a fresh clone (spike/README.md). Every invocation writes a
transcript under results/prereg2/transcripts/, opened before its arguments
are parsed, so a usage error, a refusal and an abort are all recorded. It
refuses unless run with `python3 -I -S` (no PYTHONPATH, site or .pth
injection), loads every module from its tracked file, and never reads
bytecode caches. Options cannot be abbreviated or repeated.
A bound command (anything but seal and validate-export) runs only when
p2/binding.check passes: the validation commit -- derived, the one commit that
added results/prereg2/VALIDATION -- holds this harness byte for byte, no later
commit touches it, nothing under results/prereg2/ is uncommitted, and, for
arm0, score and export, that command has not executed for that arm before.
A bound run takes every path from its fixed place and accepts no override.

--fixture-repo/--fixture-pin/--fixture-pathspec, or --unbound for commands
that open no corpus, run without the binding, for the V3 tests. Such a run
must name every output path, none of them under results/prereg2/, never
opens a real bundle, and its output carries no verdict.
"""
import argparse
import glob
import gzip
import hashlib
import json
import os
import sys
import traceback

sys.dont_write_bytecode = True
# Never read a bytecode cache: a forged .pyc beside a verified source would
# otherwise be loaded in its place (re-review M1). The prefix names a
# directory that does not exist and, with bytecode writing off, never will.
sys.pycache_prefix = os.path.join(os.sep, "nonexistent", f"prereg2-nopyc-{os.getpid()}")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from p2 import binding as BD  # noqa: E402
from p2 import mech as Mx  # noqa: E402
from p2 import transcript as TR  # noqa: E402
# Every harness module is imported here, at start, so that check_modules can
# confirm each came from its tracked file (re-review M-d).
from p2 import aggregate, arm0, arms, corpus, evaluate, export, gaps, oracle, tierrun, tiers  # noqa: E402,F401
import prereg2_plants  # noqa: E402,F401

SPIKE = os.path.dirname(HERE)
RESULTS = os.path.join(SPIKE, "results", "prereg2")
COMMANDS = ("seal", "arm0", "score", "export", "tier-model", "tier-run", "repro",
            "aggregate", "validate-export")
# Each command's output options, which an unbound run must name, outside
# results/prereg2/ (review B10).
OUTPUTS = {"arm0": ("out_dir",), "score": ("out_dir", "arm0_dir"), "export": ("out", "score_dir"),
           "repro": ("repro_dir", "score_dir"), "tier-model": ("state_dir",),
           "tier-run": ("state_dir", "export"),
           "aggregate": ("out", "arm0_dir", "score_dir", "repro_dir", "state_dir")}
FIXED = {"out_dir:arm0": os.path.join(RESULTS, "arm0"), "out_dir:score": os.path.join(RESULTS, "score"),
         "arm0_dir": os.path.join(RESULTS, "arm0"), "score_dir": os.path.join(RESULTS, "score"),
         "repro_dir": os.path.join(RESULTS, "repro"), "state_dir": RESULTS,
         "out:export": os.path.join(RESULTS, "export"), "out:aggregate": os.path.join(RESULTS, "verdict.json"),
         "export": os.path.join(RESULTS, "export")}


def jdump(obj, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(obj, sort_keys=True, indent=1, ensure_ascii=False) + "\n")


def prescan(argv, flag):
    for i, x in enumerate(argv):
        if x == flag and i + 1 < len(argv):
            return argv[i + 1]
        if x.startswith(flag + "="):
            return x.split("=", 1)[1]
    return None


def unbound_mode(argv):
    return "--unbound" in argv or prescan(argv, "--fixture-repo") is not None


def inside(path, root):
    p, r = os.path.realpath(path), os.path.realpath(root)
    return p == r or p.startswith(r + os.sep)


def resolve_paths(a, bound):
    """Fill each output path: fixed on a bound run, named and outside
    results/prereg2/ on an unbound one."""
    for opt in OUTPUTS.get(a.cmd, ()):
        if bound:
            setattr(a, opt, FIXED.get(f"{opt}:{a.cmd}", FIXED.get(opt)))
            continue
        v = getattr(a, opt, None)
        if not v:
            raise SystemExit(f"refusing: an unbound run must name --{opt.replace('_', '-')}")
        if inside(v, RESULTS):
            raise SystemExit(f"refusing: an unbound run may not write under {RESULTS} "
                             f"(--{opt.replace('_', '-')} {v})")


def corpus_for(a, K, work_dir):
    """(repo, pin, pathspec, bundle sha256 or None). Raises NoVerdict."""
    if a.fixture_repo:
        return a.fixture_repo, a.fixture_pin, a.fixture_pathspec, None
    if not BOUND_RUN:
        raise SystemExit("refusing: an unbound run never opens a real bundle; use --fixture-repo (M2)")
    if a.arm not in K.ARMS:
        raise SystemExit(f"unknown arm {a.arm!r}; arms: {', '.join(K.ARMS)}")
    spec = K.ARMS[a.arm]
    os.makedirs(work_dir, exist_ok=True)
    repo = K.open_corpus(a.arm, a.bundle_dir, work_dir)
    return repo, spec["pin"], spec["pathspec"], K.bundles()[spec["bundle"]]["sha256"]


BOUND_RUN = False


def executed(tr, cmd, arm):
    """§9: the first EXECUTION binds. Marked once the corpus, or for export
    its input, is opened -- never by a refusal (re-review H3)."""
    tr.mark_executed()
    if BOUND_RUN:
        BD.mark_executed(SPIKE, cmd, arm, tr.path)


def binding_of(tr):
    return {"bound": tr.state["bound"], "validation_commit": tr.state.get("validation_commit"),
            "head": tr.state.get("head")}


# ---------------------------------------------------------------- commands

def cmd_seal(a, tr):
    """Seal the manifest outside the repository, and write VALIDATION, the
    manifest's sha256, to be committed in the validation commit (§7.3, §9).
    Refused once VALIDATION exists here or in any ref's history (C4)."""
    from p2 import export as X
    vp = os.path.join(SPIKE, BD.VALIDATION_REL)
    _, hist, _ = BD._git(SPIKE, "log", "--all", "--format=%H", "--diff-filter=A", "--", BD.VALIDATION_REL)
    if os.path.lexists(vp) or hist.strip():
        print(f"refusing: {BD.VALIDATION_REL} exists; the manifest is sealed once, before "
              "validation (review C4)", file=sys.stderr)
        return 2
    if inside(a.manifest, BD.toplevel(SPIKE) or SPIKE):
        print("refusing: the sealed manifest is kept outside the repository until after "
              "tiers.jsonl (§7.3)", file=sys.stderr)
        return 2
    sha = X.seal(a.manifest)
    os.makedirs(os.path.dirname(vp), exist_ok=True)
    jdump({"manifest_sha256": sha}, vp)
    print(f"sealed manifest written: {a.manifest}")
    print(f"sha256: {sha}, written to {BD.VALIDATION_REL}")
    print("commit VALIDATION in the validation commit; that commit is the one that adds it")
    return 0


def cmd_arm0(a, tr):
    from p2 import arm0 as A0
    from p2 import corpus as K
    out = {"arm": a.arm, "binding": binding_of(tr), "bound": tr.state["bound"]}
    path = os.path.join(a.out_dir, f"{a.arm}.json")
    if os.path.exists(path):
        print(f"refusing: {path} exists; the first execution binds", file=sys.stderr)
        return 2
    try:
        repo, pin, pathspec, bsha = corpus_for(a, K, a.work_dir)
    except K.NoVerdict as e:
        executed(tr, "arm0", a.arm)
        os.makedirs(a.out_dir, exist_ok=True)
        out["no_verdict"] = str(e)
        print(f"NO VERDICT: {e}")
        jdump(out, path)
        return 3
    executed(tr, "arm0", a.arm)
    os.makedirs(a.out_dir, exist_ok=True)
    K.check_pin(a.arm, repo, pin)
    out.update(pin=pin, pathspec=pathspec, bundle_sha256=bsha, rules={})
    sel = K.selection(a.arm, repo, pathspec)
    for rule in K.RULES:
        c = A0.census_repo(repo, sel[rule])
        out["rules"][rule] = c
        print(f"### {a.arm} rule={rule}{' (verdict rule)' if rule == K.VERDICT_RULE else ' (beside, no verdict)'}"
              f"  files={c['files_read']} unreadable={len(c['unreadable'])}")
        print(f"   {'type':<12}{'<20 skipped':>12}{'distinct>=20':>14}{'twin same file':>16}"
              f"{'single-line':>13}{'adjacent-run*':>15}")
        for ty, v in c["by_type"].items():
            print(f"   {ty:<12}{v['short_lt20']:>12}{v['distinct_ge20']:>14}{v['twin_same_file']:>16}"
                  f"{v['single_line_twin']:>13}{v['adjacent_run_twin']:>15}")
        share = c["nl_twin_same_file"] / c["nl_distinct_ge20"] if c["nl_distinct_ge20"] else None
        print(f"   natural-language distinct >=20: {c['nl_distinct_ge20']}, with a twin in the same "
              f"file: {c['nl_twin_same_file']}"
              + (f" ({100 * share:.2f}%)" if share is not None else "")
              + f"  bar 10%: {'PASS' if c['passes_bar'] else 'STOP'}")
    print(f"   * adjacent-run twin, {A0.ADJACENT_RUN_LABEL}, report only: {A0.ADJACENT_RUN_RULE}")
    out["adjacent_run_rule"] = A0.ADJACENT_RUN_LABEL + ": " + A0.ADJACENT_RUN_RULE
    out["passes_bar"] = out["rules"][K.VERDICT_RULE]["passes_bar"]
    if not out["passes_bar"]:
        out["no_verdict"] = "oracle reach"
    print(f"ARM 0 {a.arm}: {'passes the bar' if out['passes_bar'] else 'NO VERDICT (oracle reach)'}")
    jdump(out, path)
    return 0


def cmd_score(a, tr):
    from p2 import arms as AR
    from p2 import corpus as K
    bound = tr.state["bound"]
    out_dir = os.path.join(a.out_dir, a.arm)
    # The first execution binds, and it is the execution marker that says so
    # (binding.check). A status.json here means an execution wrote its
    # result; an empty directory means nothing (re-review H-1).
    if os.path.exists(os.path.join(out_dir, "status.json")):
        print(f"refusing: {out_dir}/status.json exists; the first execution binds", file=sys.stderr)
        return 2
    a0p = os.path.join(a.arm0_dir, f"{a.arm}.json")
    if not os.path.isfile(a0p):
        print(f"refusing: no Arm 0 result for {a.arm} at {a0p}; Arm 0 runs first", file=sys.stderr)
        return 2
    a0 = json.load(open(a0p))
    if not arm0_input_ok(a0, tr):
        print(f"refusing: {a0p} is not a bound result of this validation commit", file=sys.stderr)
        return 2
    if not a0.get("passes_bar"):
        print(f"{a.arm}: NO VERDICT ({a0.get('no_verdict', 'Arm 0')}); the arm does not run")
        return 3
    modes = a.modes.split(",")
    status = {"arm": a.arm, "binding": binding_of(tr), "bound": bound, "modes": [], "counts": {},
              "modes_requested": modes, "sample_e": a.sample_e, "sample_s": a.sample_s}
    try:
        repo, pin, pathspec, bsha = corpus_for(a, K, a.work_dir)
    except K.NoVerdict as e:
        executed(tr, "score", a.arm)
        os.makedirs(out_dir, exist_ok=True)
        status["no_verdict"] = str(e)
        jdump(status, os.path.join(out_dir, "status.json"))
        print(f"NO VERDICT: {e}")
        return 3
    executed(tr, "score", a.arm)
    os.makedirs(out_dir, exist_ok=True)
    K.check_pin(a.arm, repo, pin)
    status.update(pin=pin, pathspec=pathspec, bundle_sha256=bsha)
    sel = K.selection(a.arm, repo, pathspec)
    status["selected"] = {r: len(v) for r, v in sel.items()}
    w = AR.Writer(out_dir)
    s_cache = {}
    try:
        for mode in modes:
            n = skipped = undecodable = 0
            if mode == "E":
                gen, counts = AR.build_e(a.arm, repo, pin, sel, a.sample_e)
            elif mode in ("S5", "S25"):
                gen, counts = AR.build_s(a.arm, repo, sel, int(mode[1:]), a.sample_s, s_cache)
            elif mode == "M":
                kept, counts = AR.build_m(a.arm, repo, sel)
                merges = {"clean": 0, "not_clean": 0}

                def gen_m():
                    for c in kept:
                        inst, res = AR.inst_m(a.arm, c)
                        if res is not None:
                            merges["clean" if res["clean"] and res["merged"] is not None
                                   else "not_clean"] += 1
                        yield c["id"], inst
                gen = gen_m()
            else:
                raise SystemExit(f"unknown mode {mode!r}")
            for key, inst in gen:
                if inst is AR.UNDECODABLE:
                    # LOG §15: a case whose base, any leg, or after-state is
                    # not valid UTF-8 is excluded and counted.
                    undecodable += 1
                    continue
                if inst is None:
                    skipped += 1
                    continue
                w.add(inst)
                n += 1
            if mode == "M":
                counts["merges"] = merges
                fc = counts["filter"]
                if "strict" in fc:
                    print(f"   site-policy strict set: {fc['strict']} cases; the first registration's "
                          f"§5.1 expected {fc['strict_expected']}; difference {fc['strict_difference']:+d} "
                          f"(the rule's count stands, §6.2). 25-case set, beside, no verdict: {fc['set25']}")
            counts["evaluated_instances"] = n
            counts["not_evaluated"] = skipped
            counts["undecodable"] = undecodable
            status["counts"][mode] = counts
            status["modes"].append(mode)
            print(f"### {a.arm} {mode}: evaluated {n} instances, {skipped} not evaluated, "
                  f"undecodable {undecodable} (excluded, LOG §15)")
            print("   " + json.dumps(counts, sort_keys=True))
    finally:
        w.close()
        jdump(status, os.path.join(out_dir, "status.json"))
    return 0


def check_input_binding(o, what, tr, fixture_ok):
    """An input to export or aggregate must be bound, by this run's
    validation commit, unless an unbound run passes --fixture-ok."""
    if fixture_ok:
        return
    if not o.get("bound") or (tr.state["bound"] and o.get("binding", {}).get("validation_commit")
                              != tr.state.get("validation_commit")):
        raise SystemExit(f"refusing: {what} is not a bound output of this validation commit")


def bound_gaps(spike, tr, final=False):
    """§9's gap rule on a bound run: ({cell: reason}, notes). final=True is
    aggregate, tier-model and tier-run, which come after the scoring-arm
    commit and need it. Otherwise it is the preflight of arm0, score and
    export, which run before that commit exists -- score on a branch with
    one commit per arm, squashed afterwards -- so every gaps.json version is
    held to the rule; a gap that breaks it is seen while it can still be
    dealt with (round 6, MEDIUM-1). Refuses (SystemExit) on any gap the rule
    does not allow."""
    from p2 import corpus as K
    from p2 import gaps as GP
    from p2 import tierrun as TRN
    if not tr.state["bound"]:
        return {}, []
    try:
        sc = TRN.scoring_commit(spike) if final else None
        return GP.load_gaps(spike, sc, K.ARMS)
    except (GP.GapError, TRN.TierRefused) as e:
        raise SystemExit(f"refusing: {e}")


def load_repro(repro_dir, tr, fixture_ok):
    """{record id: reproduction result}. A result from another validation
    commit is marked unbound, so it is not F9."""
    repro = {}
    for p in sorted(glob.glob(os.path.join(repro_dir, "*.json"))):
        o = json.load(open(p))
        if not fixture_ok and o.get("binding", {}).get("validation_commit") != tr.state.get(
                "validation_commit"):
            o = dict(o, bound=False)
        repro[o["id"]] = o
    return repro


def arm0_input_ok(a0, tr):
    """score's Arm 0 input: on a bound run, a bound result of this
    validation commit."""
    return not tr.state["bound"] or (a0.get("bound") is True and a0.get("binding", {}).get(
        "validation_commit") == tr.state.get("validation_commit"))


def check_pin_and_bundle(o, what):
    """An input names a §6.2 arm, its pin and its bundle's committed sha256
    (re-review H1)."""
    from p2 import corpus as K
    arm = o.get("arm")
    if arm not in K.ARMS:
        raise SystemExit(f"refusing: {what} names no §6.2 arm ({arm!r})")
    if "no_verdict" in o and "pin" not in o:
        return
    spec = K.ARMS[arm]
    if o.get("pin") != spec["pin"] or o.get("bundle_sha256") != K.bundles()[spec["bundle"]]["sha256"]:
        raise SystemExit(f"refusing: {what} was not run at {arm}'s pin from its committed bundle")


def load_scores(score_dir, tr, fixture_ok=False, sizes=True):
    """{arm: {...}} from score_dir/<arm>/. Each status must be bound by this
    validation commit, and must have run every mode at §6.5's sample sizes."""
    scores = {}
    for st in sorted(glob.glob(os.path.join(score_dir, "*", "status.json"))):
        d = os.path.dirname(st)
        s = json.load(open(st))
        arm = s["arm"]
        check_input_binding(s, f"score/{arm}", tr, fixture_ok)
        if not fixture_ok:
            check_pin_and_bundle(s, f"score/{arm}")
        if "no_verdict" in s:
            scores[arm] = {"no_verdict": s["no_verdict"]}
            continue
        if sizes and not fixture_ok and (s.get("sample_e") != 1000 or s.get("sample_s") != 500
                                          or s.get("modes_requested") != ["E", "S5", "S25", "M"]):
            raise SystemExit(f"refusing: score/{arm} did not run §6.5's arms at 1,000 and 500")
        inst = {}
        for line in open(os.path.join(d, "instances.jsonl"), encoding="utf-8"):
            o = json.loads(line)
            inst[(o["arm"], o["id"])] = o
        recs = [json.loads(line) for line in gzip.open(os.path.join(d, "units.jsonl.gz"), "rt",
                                                        encoding="utf-8")]
        scores[arm] = {"modes": s["modes"], "instances": inst, "records": recs}
    return scores


def manifest_sha(a, tr):
    """A bound run reads the sealed manifest's sha256 from VALIDATION; an
    unbound one must name it."""
    return tr.state.get("manifest_sha256") if tr.state["bound"] else a.manifest_sha


def cmd_export(a, tr):
    from p2 import export as X
    m = X.load_manifest(a.manifest, manifest_sha(a, tr))
    scores = load_scores(a.score_dir, tr, a.fixture_ok)
    recs, inst = [], {}
    for s in scores.values():
        recs += s.get("records", [])
        inst.update(s.get("instances", {}))
    if not recs:
        print("no scored records: nothing to export", file=sys.stderr)
        return 2
    executed(tr, "export", None)
    names, _ = X.export(a.out, m, recs, inst)
    print(f"exported {len(names)} packets to {a.out}")
    lines = []
    for root, _, files in os.walk(a.out):
        for fn in files:
            p = os.path.join(root, fn)
            lines.append(f"{hashlib.sha256(open(p, 'rb').read()).hexdigest()}  "
                         f"{os.path.relpath(p, a.out)}")
    man = os.path.join(os.path.dirname(os.path.abspath(a.out)), "export-manifest.txt")
    with open(man, "w") as f:
        f.write("\n".join(sorted(lines, key=lambda x: x.split("  ", 1)[1])) + "\n")
    print(f"export manifest (sha256 of each file): {man}")
    print(f"packet count: {len(names)}")
    return 0


def cmd_validate_export(a, tr):
    from p2 import export as X
    bad = X.validate(a.dir)
    for b in bad:
        print("REJECT:", b)
    print("EXPORT VALIDATOR:", "PASS" if not bad else "FAIL")
    return 0 if not bad else 1


def cmd_repro(a, tr):
    from p2 import arms as AR
    from p2 import corpus as K
    from p2 import evaluate as E
    inst_id, _ = a.id.split("|", 1)
    committed = None
    for line in gzip.open(os.path.join(a.score_dir, a.arm, "units.jsonl.gz"), "rt", encoding="utf-8"):
        if json.loads(line)["id"] == a.id:
            committed = line.rstrip("\n")
            break
    if committed is None:
        print(f"no committed record {a.id!r}", file=sys.stderr)
        return 2
    repo, pin, pathspec, _ = corpus_for(a, K, a.work_dir)
    K.check_pin(a.arm, repo, pin)
    sel = K.selection(a.arm, repo, pathspec)
    inst = AR.rebuild(a.arm, repo, inst_id, sel)
    regen = None
    if inst is not None:
        for r in E.evaluate(inst)[0]:
            if r["id"] == a.id:
                regen = E.dumps(r)
    ok = regen == committed
    h = lambda s: hashlib.sha256(s.encode()).hexdigest() if s is not None else None  # noqa: E731
    print(f"committed   {h(committed)}")
    print(f"regenerated {h(regen)}")
    print(f"F9 REPRODUCTION: {'BYTE-IDENTICAL' if ok else 'DIFFERS'}  {a.id}")
    os.makedirs(a.repro_dir, exist_ok=True)
    out = os.path.join(a.repro_dir, hashlib.sha256(a.id.encode()).hexdigest()[:16] + ".json")
    if os.path.exists(out):
        print(f"refusing to overwrite {out}", file=sys.stderr)
        return 2
    jdump({"id": a.id, "ok": ok, "bound": tr.state["bound"], "binding": binding_of(tr),
           "committed_sha256": h(committed), "regenerated_sha256": h(regen)}, out)
    return 0 if ok else 1


def transcript_preflight(spike, arms0, arms_scored):
    """Review C3, re-review H3: every transcript committed and clean (the
    binding check refuses any uncommitted file under results/prereg2/);
    exactly one bound, executed arm0 and score transcript per arm with a
    result, and its marker; one executed export; at most two tier-runs, the
    first having written zero lines if there are two. Refused runs leave
    transcripts that are not executions, and do not count."""
    from p2 import tierrun as TRN
    tdir = os.path.join(spike, BD.TRANSCRIPTS_REL)
    tags = {}
    for f in sorted(os.listdir(tdir)) if os.path.isdir(tdir) else []:
        text = open(os.path.join(tdir, f), encoding="utf-8").read()
        if "\n# executed: " in text:
            tags.setdefault(BD.transcript_tag(f), []).append("# harness bound: True" in text)
    bad = []

    def one(tag, cmd, arm):
        if tags.get(tag) != [True]:
            bad.append(f"{tag}: {len(tags.get(tag, []))} executed transcripts, want one bound")
        if not os.path.isfile(os.path.join(spike, BD.marker_rel(cmd, arm))):
            bad.append(f"{tag}: no execution marker")
    for arm in arms0:
        one(f"arm0-{arm}", "arm0", arm)
    for arm in arms_scored:
        one(f"score-{arm}", "score", arm)
    one("export", "export", None)
    runs = [e for e in TRN.read_ledger(os.path.join(spike, BD.RESULTS_REL)) if e.get("event") == "started"]
    if len(runs) > 2:
        bad.append(f"{len(runs)} tiering runs started")
    if len(runs) == 2 and TRN.count_lines_bytes(TRN.safe_read(TRN.work_tiers(
            os.path.join(spike, BD.RESULTS_REL), 1))) > 0:
        bad.append("two tiering runs, though the first wrote lines")
    tier_tr = [f for f in os.listdir(tdir) if BD.transcript_tag(f) == "tier-run"] if os.path.isdir(tdir) else []
    if len(tier_tr) < len(runs):
        bad.append("a started tiering run has no committed transcript")
    return bad


def cmd_aggregate(a, tr):
    from p2 import aggregate as AG
    from p2 import export as X
    from p2 import tierrun as TRN
    from p2 import tiers as T
    arm0 = {}
    for p in sorted(glob.glob(os.path.join(a.arm0_dir, "*.json"))):
        o = json.load(open(p))
        check_input_binding(o, p, tr, a.fixture_ok)
        if not a.fixture_ok:
            check_pin_and_bundle(o, p)
        arm0[o["arm"]] = {"no_verdict": o["no_verdict"]} if "no_verdict" in o and not o.get(
            "passes_bar") else {"passes_bar": bool(o.get("passes_bar"))}
    scores = load_scores(a.score_dir, tr, a.fixture_ok)
    m = X.load_manifest(a.manifest, manifest_sha(a, tr))
    if tr.state["bound"]:
        bad = transcript_preflight(SPIKE, list(arm0), list(scores))
        if bad:
            for b in bad:
                print("refusing:", b, file=sys.stderr)
            return 2
    n, tpath = TRN.binding_run(a.state_dir)
    print(f"tiers: run {n}'s tiers.jsonl binds" if n else "tiers: no tiering run")
    tiers, problems = T.read_tiers(tpath) if tpath else ({}, ["no tiering run"])
    for p in problems:
        print("tiers.jsonl:", p)
    repro = load_repro(a.repro_dir, tr, a.fixture_ok)
    try:
        gaps, gap_notes = bound_gaps(SPIKE, tr, final=True)
    except SystemExit:
        raise
    for n_ in gap_notes:
        print(n_)
    try:
        res = AG.aggregate(arm0, scores, m, tiers, repro, gaps)
    except AG.Empty as e:
        print(f"NO VERDICT: {e}", file=sys.stderr)
        return 2
    except AG.MissingRepro as e:
        print(f"refusing: {e}", file=sys.stderr)
        return 2
    for (arm, mode, mech), c in sorted(res["cells"].items()):
        print(f"  {arm:<14}{mode:<5}{mech}  {c['verdict']:<11} {c.get('reason', '')}"
              + (f"  distinct {c['distinct']}" if "distinct" in c else ""))
        for rule, b in sorted(c.get("beside", {}).items()):
            print(f"      beside, no verdict, {rule}: distinct {b['distinct']}, decided hardened "
                  f"mis-resolutions {b['decided_hardened_misresolutions']}")
    if res["void"]:
        print("TIERING VOID: " + "; ".join(res["void"]))
    print(f"near misses (distinct units): {res['near_misses']}")
    print(f"OVERALL: {res['overall']}")
    # Bound only if this run is bound and every input was checked bound above.
    res["bound"] = bool(tr.state["bound"] and not a.fixture_ok)
    res["binding"] = binding_of(tr)
    res["cells"] = {"|".join(k): v for k, v in res["cells"].items()}
    jdump(res, a.out)
    return 0


def derived_scoring_commit(a, tr):
    from p2 import tierrun as TRN
    if tr.state["bound"]:
        return SPIKE, TRN.scoring_commit(SPIKE)
    if not (a.repo and a.scoring_commit):
        raise SystemExit("refusing: an unbound run must name --repo and --scoring-commit")
    return a.repo, a.scoring_commit


def cmd_tier_model(a, tr):
    from p2 import tierrun as TRN
    repo, commit = derived_scoring_commit(a, tr)
    url = TRN.MODELS_URL if tr.state["bound"] else (a.models_url or TRN.MODELS_URL)
    try:
        TRN.tier_model(a.state_dir, repo, commit, url, os.environ.get("ANTHROPIC_API_KEY"))
    except TRN.TierRefused as e:
        print(f"refusing: {e}", file=sys.stderr)
        return 2
    return 0


def cmd_tier_run(a, tr):
    from p2 import tierrun as TRN
    repo, commit = derived_scoring_commit(a, tr)
    try:
        rc, n = TRN.run(a.export, a.state_dir, repo, commit, a.late_reason,
                        a.agent_cmd or "claude", credentials=a.credentials)
    except TRN.TierRefused as e:
        print(f"refusing: {e}", file=sys.stderr)
        return 2
    return 0 if rc == 0 else 1


def build_parser():
    # No abbreviated option is accepted: `--fixture-r` must not reach
    # --fixture-repo past the checks (re-review H1).
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], allow_abbrev=False)
    sub = ap.add_subparsers(dest="cmd", required=True)
    _add = sub.add_parser
    sub.add_parser = lambda name, **kw: _add(name, allow_abbrev=False, **kw)

    def common(p, corpus=True):
        p.add_argument("--d8-dir", required=True)
        p.add_argument("--transcript-dir")
        p.add_argument("--unbound", action="store_true")
        if corpus:
            p.add_argument("--arm", required=True)
            p.add_argument("--bundle-dir", default=None,
                           help="default: $PREREG2_BUNDLE_DIR, else the local copy bundles.json records")
            p.add_argument("--work-dir")
            p.add_argument("--fixture-repo")
            p.add_argument("--fixture-pin")
            p.add_argument("--fixture-pathspec")
        else:
            p.add_argument("--fixture-repo", default=None)

    def plain(p):
        p.add_argument("--transcript-dir")
        p.add_argument("--unbound", action="store_true")
        p.add_argument("--fixture-repo", default=None, help=argparse.SUPPRESS)

    p = sub.add_parser("seal")
    plain(p)
    p.add_argument("--manifest", required=True)
    p = sub.add_parser("arm0")
    common(p)
    p.add_argument("--out-dir")
    p = sub.add_parser("score")
    common(p)
    p.add_argument("--modes", default="E,S5,S25,M")
    p.add_argument("--arm0-dir")
    p.add_argument("--out-dir")
    p.add_argument("--sample-e", type=int, default=1000, help=argparse.SUPPRESS)
    p.add_argument("--sample-s", type=int, default=500, help=argparse.SUPPRESS)
    p = sub.add_parser("export")
    common(p, corpus=False)
    p.add_argument("--manifest", required=True)
    p.add_argument("--manifest-sha")
    p.add_argument("--score-dir")
    p.add_argument("--out")
    p.add_argument("--fixture-ok", action="store_true", help=argparse.SUPPRESS)
    p = sub.add_parser("validate-export")
    p.add_argument("dir")
    p.add_argument("--transcript-dir")
    p.add_argument("--unbound", action="store_true")
    p = sub.add_parser("repro")
    common(p)
    p.add_argument("--id", required=True)
    p.add_argument("--score-dir")
    p.add_argument("--repro-dir")
    for name in ("tier-model", "tier-run"):
        p = sub.add_parser(name)
        plain(p)
        p.add_argument("--state-dir")
        p.add_argument("--repo", help="unbound only: where the scoring-arm commit is read")
        p.add_argument("--scoring-commit", help="unbound only")
        if name == "tier-model":
            p.add_argument("--models-url", help="unbound only")
        else:
            p.add_argument("--export")
            p.add_argument("--late-reason")
            p.add_argument("--agent-cmd", help="unbound only: a stub agent")
            p.add_argument("--credentials", default=None,
                           help="the one credential file bound into the sandbox "
                                "(default ~/.claude/.credentials.json)")
    p = sub.add_parser("aggregate")
    common(p, corpus=False)
    p.add_argument("--arm0-dir")
    p.add_argument("--score-dir")
    p.add_argument("--manifest", required=True)
    p.add_argument("--manifest-sha")
    p.add_argument("--state-dir")
    p.add_argument("--repro-dir")
    p.add_argument("--out")
    p.add_argument("--fixture-ok", action="store_true", help=argparse.SUPPRESS)
    return ap


# The option values a bound run must leave at their defaults (review C3, B3).
BOUND_DEFAULTS = {"transcript_dir": None, "out_dir": None, "out": None, "state_dir": None,
                  "arm0_dir": None, "score_dir": None, "repro_dir": None, "export": None,
                  "modes": "E,S5,S25,M", "sample_e": 1000, "sample_s": 500, "fixture_ok": False,
                  "scoring_commit": None, "repo": None, "models_url": None, "manifest_sha": None,
                  "agent_cmd": None, "fixture_repo": None, "fixture_pin": None,
                  "fixture_pathspec": None, "unbound": False}


def check_modules():
    """Each harness module must be the tracked file it names: an untracked
    p2/binding/ package, say, would otherwise shadow p2/binding.py."""
    bad = []
    for name, mod in sorted(sys.modules.items()):
        if name == "p2" or name.startswith("p2."):
            rel = os.path.join("p2", "__init__.py") if name == "p2" else os.path.join("p2", name[3:] + ".py")
        elif name in ("d8_cheap_arm", "prose_merge", "prereg2_plants"):
            rel = name + ".py"
        else:
            continue
        f = getattr(mod, "__file__", None)
        if not f or os.path.realpath(f) != os.path.realpath(os.path.join(HERE, rel)):
            bad.append(f"{name} was loaded from {f}, not {rel}")
    return bad


def repeated_options(argv):
    """Options given more than once. argparse keeps the last, so a repeated
    --arm could aim a run's checks at one arm and its work at another."""
    seen, rep = set(), []
    for tok in argv:
        if tok == "--":
            break
        if tok.startswith("--"):
            name = tok.split("=", 1)[0]
            if name in seen and name not in rep:
                rep.append(name)
            seen.add(name)
    return rep


def main(argv=None):
    global BOUND_RUN
    argv = sys.argv[1:] if argv is None else list(argv)
    cmd = argv[0] if argv and argv[0] in COMMANDS else "invalid"
    prescan_unbound = unbound_mode(argv)
    tdir = prescan(argv, "--transcript-dir") if prescan_unbound else None
    # The transcript opens before the arguments are parsed (review A7). An
    # unbound run's transcript goes where it names, never under results/.
    if prescan_unbound and (not tdir or inside(tdir, RESULTS)):
        tdir = None
    tr = TR.Transcript(cmd, prescan(argv, "--arm"), [os.path.basename(sys.argv[0])] + argv,
                       tdir or TR.DEFAULT_DIR)
    rc, how = 1, "exited"
    BOUND_RUN = False
    try:
        if not (sys.flags.isolated and sys.flags.no_site):
            tr.record_binding({"bound": False, "reasons": ["not run with python3 -I -S"]})
            raise SystemExit("refusing: run the harness as `python3 -I -S -B harness/prereg2.py`: "
                             "without -I and -S, PYTHONPATH, site packages and .pth files can "
                             "replace its code (M1, M-d)")
        shadowed = check_modules()
        if shadowed:
            tr.record_binding({"bound": False, "reasons": shadowed})
            raise SystemExit("refusing: " + "; ".join(shadowed) + " (M-d)")
        rep = repeated_options(argv)
        if rep:
            tr.record_binding({"bound": False, "reasons": [f"repeated {', '.join(rep)}"]})
            raise SystemExit(f"refusing: {', '.join(rep)} given more than once (re-review H1)")
        try:
            a = build_parser().parse_args(argv)
        except SystemExit:
            tr.record_binding({"bound": False, "reasons": ["usage error"]})
            raise
        unbound = bool(a.unbound or getattr(a, "fixture_repo", None))
        if unbound != prescan_unbound:
            tr.record_binding({"bound": False, "reasons": ["the parsed options disagree with the prescan"]})
            raise SystemExit("refusing: the options parse differently from how they read (H1)")
        if unbound or a.cmd in ("seal", "validate-export"):
            state = {"bound": False, "reasons": ["unbound run" if unbound else f"{a.cmd} is not bound"],
                     "head": TR.head()}
        else:
            state, _ = BD.check(SPIKE, a.cmd, getattr(a, "arm", None), tr.path)
        tr.record_binding(state)
        if unbound and not tdir:
            raise SystemExit("refusing: an unbound run must name --transcript-dir outside results/prereg2/")
        if not unbound and a.cmd not in ("seal", "validate-export"):
            given = [k for k, v in BOUND_DEFAULTS.items() if hasattr(a, k) and getattr(a, k) != v]
            if given:
                raise SystemExit("refusing: a bound run takes no "
                                 + ", ".join("--" + g.replace("_", "-") for g in given)
                                 + " (§9, review C3)")
            if not state["bound"]:
                for r in state["reasons"]:
                    print("not bound:", r, file=sys.stderr)
                raise SystemExit("refusing: this run would not be bound; use --fixture-repo or "
                                 "--unbound to run it for testing, with no verdict")
            BOUND_RUN = True
        if getattr(a, "fixture_repo", None) and a.cmd in ("arm0", "score", "repro") and not (
                a.fixture_pin and a.fixture_pathspec):
            raise SystemExit("refusing: --fixture-repo needs --fixture-pin and --fixture-pathspec")
        if a.cmd in ("arm0", "score", "repro") and not a.fixture_repo:
            if not a.work_dir or inside(a.work_dir, SPIKE):
                raise SystemExit("refusing: --work-dir is required, outside the repository")
            if not a.bundle_dir:
                from p2 import corpus as K
                a.bundle_dir = K.DEFAULT_BUNDLE_DIR
        if BOUND_RUN and a.cmd in ("arm0", "score", "export", "tier-model", "tier-run"):
            for n_ in bound_gaps(SPIKE, tr, final=a.cmd in ("tier-model", "tier-run"))[1]:
                print(n_)
        resolve_paths(a, BOUND_RUN)
        if hasattr(a, "d8_dir"):
            Mx.load(a.d8_dir)
            shadowed = check_modules()
            if shadowed:
                raise SystemExit("refusing: " + "; ".join(shadowed) + " (M-d)")
        rc = {"seal": cmd_seal, "arm0": cmd_arm0, "score": cmd_score,
              "export": cmd_export, "validate-export": cmd_validate_export, "repro": cmd_repro,
              "aggregate": cmd_aggregate, "tier-model": cmd_tier_model,
              "tier-run": cmd_tier_run}[a.cmd](a, tr)
    except SystemExit as e:
        rc = e.code if isinstance(e.code, int) else (0 if e.code is None else 2)
        if isinstance(e.code, str):
            print(e.code, file=sys.stderr)
        how = "aborted" if rc else "exited"
    except BaseException:
        traceback.print_exc()
        rc, how = 1, "aborted by an exception"
    finally:
        BOUND_RUN = False
        tr.close(rc, how)
    return rc


if __name__ == "__main__":
    sys.exit(main())
