#!/usr/bin/env -S python3 -I -S -B
# SPDX-License-Identifier: MIT
"""PRE-REGISTRATION-3.md, the harness. blockspec#2. Run it isolated:

    python3 -I -S -B harness3/prereg3.py seal      --manifest PATH   (before validation 3, once)
    python3 -I -S -B harness3/prereg3.py export    --d8-dir D8 --manifest PATH        (step 3, once)
    python3 -I -S -B harness3/prereg3.py validate-export DIR
    python3 -I -S -B harness3/prereg3.py tier-run  [--late-reason TEXT] [--credentials FILE]  (step 6)
    python3 -I -S -B harness3/prereg3.py repro     --d8-dir D8 --arm ARM --id RECORD --work-dir W (step 7)
    python3 -I -S -B harness3/prereg3.py aggregate --d8-dir D8 --manifest PATH --manifest2 PATH2 (step 9)

It imports prereg 2's harness (spike/harness/) unmodified, and refuses every
bound command unless that harness, PRE-REGISTRATION-2.md and ORACLE.md are
byte-identical to prereg 2's validation commit d79bf2e (§9 H1). Its own
binding is p2/binding.py's logic over the namespace prereg3: bound paths
harness3/ and PRE-REGISTRATION-3.md, results under results/prereg3/, and the
validation commit derived as the one commit that adds
results/prereg3/VALIDATION.

Every invocation writes a transcript under results/prereg3/transcripts/,
opened before its arguments are parsed. It refuses unless run with
`python3 -I -S`, loads every module from its tracked file, never reads
bytecode caches, and accepts no abbreviated or repeated option.

--unbound runs the commands that open no corpus without the binding, for the
V steps. Such a run names every output path, none of them under
results/prereg3/ or results/prereg2/, and its output carries no verdict.
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
sys.pycache_prefix = os.path.join(os.sep, "nonexistent", f"prereg3-nopyc-{os.getpid()}")
HERE = os.path.dirname(os.path.abspath(__file__))
SPIKE = os.path.dirname(HERE)
H2 = os.path.join(SPIKE, "harness")
sys.path.insert(0, H2)
sys.path.insert(0, HERE)

from p2 import mech as Mx  # noqa: E402
# Every module is imported at start, so check_modules can confirm each came
# from its tracked file.
from p2 import aggregate, arms, corpus, evaluate, export, gaps, oracle, tierrun, tiers  # noqa: E402,F401
import prose_merge  # noqa: E402,F401
import prereg2_plants  # noqa: E402,F401
import prereg3_plants  # noqa: E402,F401
from p3 import aggregate3, binding as BD, export3 as X3, gates as G, plants as PL  # noqa: E402,F401
from p3 import tierrun3 as T3, transcript as TR  # noqa: E402

NS = BD.PREREG3
RESULTS = os.path.join(SPIKE, NS.results_rel)
RESULTS2 = os.path.join(SPIKE, BD.PREREG2.results_rel)
SCORING_COMMIT = X3.SCORING_COMMIT
COMMANDS = ("seal", "export", "validate-export", "tier-run", "repro", "aggregate")
OUTPUTS = {"export": ("out", "score_dir"), "tier-run": ("state_dir", "export", "gate_repo"),
           "repro": ("repro_dir", "score_dir"),
           "aggregate": ("out", "arm0_dir", "score_dir", "state_dir", "repro_dir", "export")}
FIXED = {"out:export": os.path.join(RESULTS, "export"), "score_dir": os.path.join(RESULTS2, "score"),
         "arm0_dir": os.path.join(RESULTS2, "arm0"), "state_dir": RESULTS,
         "export": os.path.join(RESULTS, "export"), "gate_repo": SPIKE,
         "repro_dir": os.path.join(RESULTS, "repro"), "out:aggregate": os.path.join(RESULTS, "verdict.json")}
BOUND_DEFAULTS = {"out": None, "score_dir": None, "arm0_dir": None, "state_dir": None, "repro_dir": None,
                  "export": None, "gate_repo": None, "agent_cmd": None, "fixture_ok": False,
                  "fixture_repo": None, "fixture_pin": None, "fixture_pathspec": None, "manifest_sha": None,
                  "manifest2_sha": None, "spike_repo": None, "unbound": False}
BOUND_RUN = False


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


def inside(path, root):
    p, r = os.path.realpath(path), os.path.realpath(root)
    return p == r or p.startswith(r + os.sep)


def resolve_paths(a, bound):
    for opt in OUTPUTS.get(a.cmd, ()):
        if bound:
            setattr(a, opt, FIXED.get(f"{opt}:{a.cmd}", FIXED.get(opt)))
            continue
        v = getattr(a, opt, None)
        if not v:
            raise SystemExit(f"refusing: an unbound run must name --{opt.replace('_', '-')}")
        if opt in ("out", "state_dir", "repro_dir") and (inside(v, RESULTS) or inside(v, RESULTS2)):
            raise SystemExit(f"refusing: an unbound run may not write under results/ (--{opt} {v})")


def binding_of(tr):
    return {"bound": tr.state["bound"], "validation_commit": tr.state.get("validation_commit"),
            "head": tr.state.get("head")}


def check_modules():
    bad = []
    for name, mod in sorted(sys.modules.items()):
        if name == "p2" or name.startswith("p2."):
            want = os.path.join(H2, "p2", "__init__.py" if name == "p2" else name[3:] + ".py")
        elif name == "p3" or name.startswith("p3."):
            want = os.path.join(HERE, "p3", "__init__.py" if name == "p3" else name[3:] + ".py")
        elif name in ("d8_cheap_arm", "prose_merge", "prereg2_plants"):
            want = os.path.join(H2, name + ".py")
        elif name == "prereg3_plants":
            want = os.path.join(HERE, name + ".py")
        else:
            continue
        f = getattr(mod, "__file__", None)
        if not f or os.path.realpath(f) != os.path.realpath(want):
            bad.append(f"{name} was loaded from {f}, not {want}")
    return bad


def repeated_options(argv):
    seen, rep = set(), []
    for tok in argv:
        if tok.startswith("--"):
            name = tok.split("=", 1)[0]
            if name in seen and name not in rep:
                rep.append(name)
            seen.add(name)
    return rep


def check_pin_and_bundle(o, what):
    from p2 import corpus as K
    arm = o.get("arm")
    if arm not in K.ARMS:
        raise SystemExit(f"refusing: {what} names no §6.2 arm ({arm!r})")
    if "no_verdict" in o and "pin" not in o:
        return
    spec = K.ARMS[arm]
    if o.get("pin") != spec["pin"] or o.get("bundle_sha256") != K.bundles()[spec["bundle"]]["sha256"]:
        raise SystemExit(f"refusing: {what} was not run at {arm}'s pin from its committed bundle")


def input_ok(o, what, fixture_ok):
    """H6: prereg 2's inputs only if bound to d79bf2e."""
    if fixture_ok:
        return
    try:
        aggregate3.check_input(o, what)
    except aggregate3.InputRefused as e:
        raise SystemExit(f"refusing: {e}")
    check_pin_and_bundle(o, what)


def load_scores(score_dir, fixture_ok):
    scores = {}
    for st in sorted(glob.glob(os.path.join(score_dir, "*", "status.json"))):
        d = os.path.dirname(st)
        s = json.load(open(st))
        arm = s["arm"]
        input_ok(s, f"score/{arm}", fixture_ok)
        if "no_verdict" in s:
            scores[arm] = {"no_verdict": s["no_verdict"]}
            continue
        if not fixture_ok and (s.get("sample_e") != 1000 or s.get("sample_s") != 500
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
    return tr.state.get("manifest_sha256") if tr.state["bound"] else a.manifest_sha


# ---------------------------------------------------------------- commands

def cmd_seal(a, tr):
    vp = os.path.join(SPIKE, NS.validation_rel)
    _, hist, _ = BD._git(SPIKE, "log", "--all", "--format=%H", "--diff-filter=A", "--", NS.validation_rel)
    if os.path.lexists(vp) or hist.strip():
        print(f"refusing: {NS.validation_rel} exists; the manifest is sealed once", file=sys.stderr)
        return 2
    if inside(a.manifest, BD.toplevel(SPIKE) or SPIKE):
        print("refusing: the sealed manifest is kept outside the repository until step 8", file=sys.stderr)
        return 2
    sha = PL.seal(a.manifest)
    os.makedirs(os.path.dirname(vp), exist_ok=True)
    jdump({"manifest_sha256": sha}, vp)
    print(f"sealed manifest written: {a.manifest}")
    print(f"sha256: {sha}, written to {NS.validation_rel}")
    return 0


def cmd_export(a, tr):
    repo = a.spike_repo or SPIKE
    if BOUND_RUN or a.spike_repo:
        try:
            G.order_guard(repo)
        except G.GateError as e:
            print(f"refusing: {e}", file=sys.stderr)
            return 2
        print("order guard: prereg 2's tiering has not started (work trees, refs and reflogs)")
    try:
        m = PL.load_manifest(a.manifest, manifest_sha(a, tr))
    except PL.PlantError as e:
        print(f"refusing: {e}", file=sys.stderr)
        return 2
    scores = load_scores(a.score_dir, a.fixture_ok)
    recs, inst = [], {}
    for s in scores.values():
        recs += s.get("records", [])
        inst.update(s.get("instances", {}))
    if not recs:
        print("no scored records: nothing to export", file=sys.stderr)
        return 2
    tr.mark_executed()
    if BOUND_RUN:
        BD.mark_executed(SPIKE, NS, "export", None, tr.path)
    names = X3.export3(a.out, m, recs, inst)
    print(f"exported {len(names)} packets to {a.out}")
    lines = []
    for root, _, files in os.walk(a.out):
        for fn in files:
            p = os.path.join(root, fn)
            lines.append(f"{hashlib.sha256(open(p, 'rb').read()).hexdigest()}  {os.path.relpath(p, a.out)}")
    man = os.path.join(os.path.dirname(os.path.abspath(a.out)), "export-manifest.txt")
    with open(man, "w") as f:
        f.write("\n".join(sorted(lines, key=lambda x: x.split("  ", 1)[1])) + "\n")
    print(f"export manifest (sha256 of each file): {man}")
    pn = PL.plant_names(m)
    ok1, l1 = X3.same_records(repo, a.out, pn)
    ok2, l2 = X3.same_plants(a.out, pn)
    for ln in l1 + l2:
        print(ln)
    print(f"packet count: {len(names)}")
    return 0 if ok1 and ok2 else 1


def cmd_validate_export(a, tr):
    bad = X3.validate3(a.dir)
    for b in bad:
        print("INVALID:", b)
    print("export:", "clean" if not bad else f"{len(bad)} violation(s)")
    return 0 if not bad else 1


def cmd_tier_run(a, tr):
    try:
        rc, n, init_failed = T3.run(a.export, a.state_dir, a.gate_repo, a.late_reason,
                                    a.agent_cmd or "claude", credentials=a.credentials)
    except T3.TierRefused as e:
        print(f"refusing: {e}", file=sys.stderr)
        return 2
    return 0 if rc == 0 and not init_failed else 1


def cmd_repro(a, tr):
    """prereg2.py repro, under prereg 3's binding, writing results/prereg3/repro/."""
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
    if a.fixture_repo:
        repo, pin, pathspec = a.fixture_repo, a.fixture_pin, a.fixture_pathspec
    else:
        if not BOUND_RUN:
            raise SystemExit("refusing: an unbound run never opens a real bundle; use --fixture-repo")
        spec = K.ARMS[a.arm]
        os.makedirs(a.work_dir, exist_ok=True)
        repo, pin, pathspec = K.open_corpus(a.arm, a.bundle_dir or K.DEFAULT_BUNDLE_DIR, a.work_dir), \
            spec["pin"], spec["pathspec"]
    tr.mark_executed()
    K.check_pin(a.arm, repo, pin)
    inst = AR.rebuild(a.arm, repo, inst_id, K.selection(a.arm, repo, pathspec))
    regen = None
    if inst is not None:
        for r in E.evaluate(inst)[0]:
            if r["id"] == a.id:
                regen = E.dumps(r)
    ok = regen == committed
    h = lambda s: hashlib.sha256(s.encode()).hexdigest() if s is not None else None  # noqa: E731
    print(f"committed   {h(committed)}\nregenerated {h(regen)}")
    print(f"F9 REPRODUCTION: {'BYTE-IDENTICAL' if ok else 'DIFFERS'}  {a.id}")
    os.makedirs(a.repro_dir, exist_ok=True)
    out = os.path.join(a.repro_dir, hashlib.sha256(a.id.encode()).hexdigest()[:16] + ".json")
    if os.path.exists(out):
        print(f"refusing to overwrite {out}", file=sys.stderr)
        return 2
    jdump({"id": a.id, "ok": ok, "bound": tr.state["bound"], "binding": binding_of(tr),
           "committed_sha256": h(committed), "regenerated_sha256": h(regen)}, out)
    return 0 if ok else 1


def cmd_aggregate(a, tr):
    from p2 import corpus as K
    from p2 import gaps as GP
    from p2 import tiers as T
    repo = a.spike_repo or SPIKE
    if BOUND_RUN:
        try:
            for ln in G.committed_order(SPIKE):
                print("order:", ln)
        except G.GateError as e:
            print(f"refusing: {e}", file=sys.stderr)
            return 2
    arm0 = {}
    for p in sorted(glob.glob(os.path.join(a.arm0_dir, "*.json"))):
        o = json.load(open(p))
        input_ok(o, p, a.fixture_ok)
        arm0[o["arm"]] = {"no_verdict": o["no_verdict"]} if "no_verdict" in o and not o.get(
            "passes_bar") else {"passes_bar": bool(o.get("passes_bar"))}
    scores = load_scores(a.score_dir, a.fixture_ok)
    try:
        m = PL.load_manifest(a.manifest, manifest_sha(a, tr))
    except PL.PlantError as e:
        print(f"refusing: {e}", file=sys.stderr)
        return 2
    n, tpath = T3.binding_run(a.state_dir)
    print(f"tiers: run {n}'s tiers.jsonl binds" if n else "tiers: no binding tiering run")
    tiers_, problems = T.read_tiers(tpath) if tpath else ({}, ["no binding tiering run"])
    for p in problems:
        print("tiers.jsonl:", p)
    vc3 = tr.state.get("validation_commit") if tr.state["bound"] else a.validation_commit3
    load = lambda d: [json.load(open(p)) for p in sorted(glob.glob(os.path.join(d, "*.json")))] if d else []  # noqa: E731
    results3 = load(a.repro_dir)
    results2 = load(os.path.join(RESULTS2, "repro") if BOUND_RUN else a.repro_dir2)
    try:
        repro = aggregate3.accept_repros(results2, results3, vc3) if not a.fixture_ok else \
            {o["id"]: o for o in results2 + results3}
    except aggregate3.InputRefused as e:
        print(f"refusing: {e}", file=sys.stderr)
        return 2
    gaps_ = {}
    if BOUND_RUN:
        try:
            gaps_, notes = GP.load_gaps(SPIKE, SCORING_COMMIT, K.ARMS)
        except GP.GapError as e:
            print(f"refusing: {e}", file=sys.stderr)
            return 2
        for n_ in notes:
            print(n_)
    try:
        res = aggregate3.aggregate3(arm0, scores, m, tiers_, repro, gaps_)
    except aggregate.Empty as e:
        print(f"NO VERDICT: {e}", file=sys.stderr)
        return 2
    except aggregate.MissingRepro as e:
        print(f"refusing: {e}", file=sys.stderr)
        return 2
    # §5's per-name check comes first: nothing is printed or written unless
    # every real key's packet is the same under both names.
    try:
        from p2 import export as X2
        m2 = X2.load_manifest(a.manifest2, a.manifest2_sha or BD.derive_validation(repo, BD.PREREG2)[1])
    except Exception as e:  # noqa: BLE001
        print(f"refusing: prereg 2's manifest: {e}", file=sys.stderr)
        return 2
    ok, lines = X3.same_per_name(repo, m2["nonce"], a.export, m["nonce"], res["packet_keys"])
    for ln in lines:
        print(ln)
    if not ok:
        print("refusing: the per-name check failed; no verdict is written", file=sys.stderr)
        return 1
    for (arm, mode, mech), c in sorted(res["cells"].items()):
        print(f"  {arm:<14}{mode:<5}{mech}  {c['verdict']:<11} {c.get('reason', '')}")
    if res["void"]:
        print("TIERING VOID: " + "; ".join(res["void"]))
    print(f"near misses (distinct units): {res['near_misses']}")
    print(f"OVERALL: {res['overall']}")
    out = dict(res, bound=bool(tr.state["bound"] and not a.fixture_ok), binding=binding_of(tr))
    out["cells"] = {"|".join(k): v for k, v in res["cells"].items()}
    jdump(out, a.out)
    return 0


def build_parser():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], allow_abbrev=False)
    sub = ap.add_subparsers(dest="cmd", required=True)
    _add = sub.add_parser
    sub.add_parser = lambda name, **kw: _add(name, allow_abbrev=False, **kw)

    def base(p):
        p.add_argument("--transcript-dir")
        p.add_argument("--unbound", action="store_true")

    p = sub.add_parser("seal")
    base(p)
    p.add_argument("--manifest", required=True)
    p = sub.add_parser("export")
    base(p)
    p.add_argument("--d8-dir", required=True)
    p.add_argument("--manifest", required=True)
    p.add_argument("--manifest-sha")
    p.add_argument("--score-dir")
    p.add_argument("--out")
    p.add_argument("--spike-repo", help="unbound only: the repository whose e46e320 tree holds prereg 2's export")
    p.add_argument("--fixture-ok", action="store_true", help=argparse.SUPPRESS)
    p = sub.add_parser("validate-export")
    base(p)
    p.add_argument("dir")
    p = sub.add_parser("tier-run")
    base(p)
    p.add_argument("--state-dir")
    p.add_argument("--export")
    p.add_argument("--gate-repo", help="unbound only: the repository the gate reads")
    p.add_argument("--late-reason")
    p.add_argument("--agent-cmd", help="unbound only: a stub agent")
    p.add_argument("--credentials", default=None)
    p = sub.add_parser("repro")
    base(p)
    p.add_argument("--d8-dir", required=True)
    p.add_argument("--arm", required=True)
    p.add_argument("--id", required=True)
    p.add_argument("--work-dir")
    p.add_argument("--bundle-dir")
    p.add_argument("--score-dir")
    p.add_argument("--repro-dir")
    p.add_argument("--fixture-repo")
    p.add_argument("--fixture-pin")
    p.add_argument("--fixture-pathspec")
    p = sub.add_parser("aggregate")
    base(p)
    p.add_argument("--d8-dir", required=True)
    p.add_argument("--manifest", required=True)
    p.add_argument("--manifest-sha")
    p.add_argument("--manifest2", required=True, help="prereg 2's sealed manifest, for §5's per-name check")
    p.add_argument("--manifest2-sha")
    p.add_argument("--arm0-dir")
    p.add_argument("--score-dir")
    p.add_argument("--state-dir")
    p.add_argument("--repro-dir")
    p.add_argument("--repro-dir2", help="unbound only: prereg 2's reproductions")
    p.add_argument("--validation-commit3", help="unbound only")
    p.add_argument("--export", help="export 3, for the per-name check")
    p.add_argument("--out")
    p.add_argument("--spike-repo", help="unbound only")
    p.add_argument("--fixture-ok", action="store_true", help=argparse.SUPPRESS)
    return ap


def main(argv=None):
    global BOUND_RUN
    argv = sys.argv[1:] if argv is None else list(argv)
    cmd = argv[0] if argv and argv[0] in COMMANDS else "invalid"
    unbound_pre = "--unbound" in argv
    tdir = prescan(argv, "--transcript-dir") if unbound_pre else None
    if unbound_pre and (not tdir or inside(tdir, RESULTS) or inside(tdir, RESULTS2)):
        tdir = None
    tr = TR.Transcript(cmd, prescan(argv, "--arm"), [os.path.basename(sys.argv[0])] + argv,
                       tdir or TR.DEFAULT_DIR)
    rc, how = 1, "exited"
    BOUND_RUN = False
    try:
        if not (sys.flags.isolated and sys.flags.no_site):
            tr.record_binding({"bound": False, "reasons": ["not run with python3 -I -S"]})
            raise SystemExit("refusing: run the harness as `python3 -I -S -B harness3/prereg3.py`")
        shadowed = check_modules()
        if shadowed:
            tr.record_binding({"bound": False, "reasons": shadowed})
            raise SystemExit("refusing: " + "; ".join(shadowed))
        rep = repeated_options(argv)
        if rep:
            tr.record_binding({"bound": False, "reasons": [f"repeated {', '.join(rep)}"]})
            raise SystemExit(f"refusing: {', '.join(rep)} given more than once")
        try:
            a = build_parser().parse_args(argv)
        except SystemExit:
            tr.record_binding({"bound": False, "reasons": ["usage error"]})
            raise
        if bool(a.unbound) != unbound_pre:
            raise SystemExit("refusing: the options parse differently from how they read")
        if a.unbound or a.cmd in ("seal", "validate-export"):
            state = {"bound": False, "reasons": ["unbound run" if a.unbound else f"{a.cmd} is not bound"],
                     "head": TR.head()}
        else:
            state, _ = BD.check(SPIKE, NS, a.cmd, None, tr.path)
        tr.record_binding(state)
        if a.unbound and not tdir:
            raise SystemExit("refusing: an unbound run must name --transcript-dir outside results/")
        if not a.unbound and a.cmd not in ("seal", "validate-export"):
            given = [k for k, v in BOUND_DEFAULTS.items() if hasattr(a, k) and getattr(a, k) != v]
            if given:
                raise SystemExit("refusing: a bound run takes no "
                                 + ", ".join("--" + g.replace("_", "-") for g in given))
            if not state["bound"]:
                for r in state["reasons"]:
                    print("not bound:", r, file=sys.stderr)
                raise SystemExit("refusing: this run would not be bound; use --unbound to test")
            BOUND_RUN = True
        resolve_paths(a, BOUND_RUN)
        if hasattr(a, "d8_dir"):
            Mx.load(a.d8_dir)
            shadowed = check_modules()
            if shadowed:
                raise SystemExit("refusing: " + "; ".join(shadowed))
        rc = {"seal": cmd_seal, "export": cmd_export, "validate-export": cmd_validate_export,
              "tier-run": cmd_tier_run, "repro": cmd_repro, "aggregate": cmd_aggregate}[a.cmd](a, tr)
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
