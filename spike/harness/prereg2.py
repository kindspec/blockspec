#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""PRE-REGISTRATION-2.md, the harness. blockspec#2.

    prereg2.py seal       --manifest PATH
    prereg2.py arm0       --arm ARM --work-dir W [--bundle-dir D]
    prereg2.py score      --arm ARM --work-dir W [--bundle-dir D] [--modes E,S5,S25,M]
    prereg2.py export     --manifest PATH --manifest-sha SHA
    prereg2.py validate-export DIR
    prereg2.py repro      --arm ARM --id INSTANCE|MECH|UNIT --work-dir W [--bundle-dir D]

The bundles are read from --bundle-dir, else $PREREG2_BUNDLE_DIR, else the
durable local copy recorded in p2/bundles.json (LOG.md §15).
    prereg2.py tier-run   --scoring-commit SHA --models-listing FILE --listing-day DAY
    prereg2.py aggregate  --manifest PATH --manifest-sha SHA --tiers FILE

§9's order of work binds: validation, then Arm 0, then the scoring arms and
the export, then tiers.jsonl, then the sealed manifest, the join and the
verdict. The first execution of each arm binds. Every invocation of arm0,
score, export, tier-run, repro and aggregate writes a transcript under
results/prereg2/transcripts/ (§9), including one that aborts.

A run is BOUND only when the harness, PRE-REGISTRATION-2.md and ORACLE.md
are exactly the blockspec commit it runs from. An unbound run says so in its
transcript and its outputs, and `aggregate` refuses unbound inputs.

--fixture-repo/--fixture-pin/--fixture-pathspec run an arm on a constructed
repository instead of a pinned bundle. They exist for the V3 tests, and their
output is always unbound.
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
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from p2 import mech as Mx  # noqa: E402
from p2 import transcript as TR  # noqa: E402

SPIKE = os.path.dirname(HERE)
RESULTS = os.path.join(SPIKE, "results", "prereg2")


def jdump(obj, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(obj, sort_keys=True, indent=1, ensure_ascii=False) + "\n")


def corpus_for(a, K, work_dir):
    """(repo, pin, pathspec, bundle sha256 or None). Raises NoVerdict."""
    if a.fixture_repo:
        return a.fixture_repo, a.fixture_pin, a.fixture_pathspec, None
    if a.arm not in K.ARMS:
        raise SystemExit(f"unknown arm {a.arm!r}; arms: {', '.join(K.ARMS)}")
    spec = K.ARMS[a.arm]
    os.makedirs(work_dir, exist_ok=True)
    repo = K.open_corpus(a.arm, a.bundle_dir, work_dir)
    return repo, spec["pin"], spec["pathspec"], K.bundles()[spec["bundle"]]["sha256"]


def bound_or_refuse(a, tr):
    if a.fixture_repo:
        print("FIXTURE RUN: unbound; this output carries no verdict")
        return False
    if not tr.state["bound"]:
        if not a.unbound:
            print("refusing: the harness differs from the blockspec commit "
                  "(pass --unbound to run anyway, unbound)", file=sys.stderr)
            raise SystemExit(2)
        print("UNBOUND RUN: the harness differs from its commit; this output carries no verdict")
        return False
    return True


# ---------------------------------------------------------------- commands

def cmd_seal(a, tr):
    from p2 import export as X
    sha = X.seal(a.manifest)
    print(f"sealed manifest written: {a.manifest}")
    print(f"sha256: {sha}")
    print("commit this sha256 in the validation commit; commit the manifest itself only "
          "after tiers.jsonl (§7.3, §9)")
    return 0


def cmd_arm0(a, tr):
    from p2 import arm0 as A0
    from p2 import corpus as K
    bound = bound_or_refuse(a, tr)
    out = {"arm": a.arm, "harness": tr.state, "bound": bound}
    path = os.path.join(a.out_dir, f"{a.arm}.json")
    os.makedirs(a.out_dir, exist_ok=True)
    if os.path.exists(path) and not a.fixture_repo:
        print(f"refusing: {path} exists; the first execution binds", file=sys.stderr)
        return 2
    try:
        repo, pin, pathspec, bsha = corpus_for(a, K, a.work_dir)
    except K.NoVerdict as e:
        out["no_verdict"] = str(e)
        print(f"NO VERDICT: {e}")
        jdump(out, path)
        return 3
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
    bound = bound_or_refuse(a, tr)
    out_dir = os.path.join(a.out_dir, a.arm)
    if os.path.exists(out_dir):
        print(f"refusing: {out_dir} exists; the first execution binds", file=sys.stderr)
        return 2
    a0p = os.path.join(a.arm0_dir, f"{a.arm}.json")
    if not os.path.isfile(a0p):
        print(f"refusing: no Arm 0 result for {a.arm} at {a0p}; Arm 0 runs first", file=sys.stderr)
        return 2
    a0 = json.load(open(a0p))
    if not a0.get("passes_bar"):
        print(f"{a.arm}: NO VERDICT ({a0.get('no_verdict', 'Arm 0')}); the arm does not run")
        return 3
    modes = a.modes.split(",")
    status = {"arm": a.arm, "harness": tr.state, "bound": bound, "modes": [], "counts": {}}
    os.makedirs(out_dir)
    try:
        repo, pin, pathspec, bsha = corpus_for(a, K, a.work_dir)
    except K.NoVerdict as e:
        status["no_verdict"] = str(e)
        jdump(status, os.path.join(out_dir, "status.json"))
        print(f"NO VERDICT: {e}")
        return 3
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


def load_scores(score_dir, need_bound=True):
    """{arm: {...}} from score_dir/<arm>/."""
    scores = {}
    for st in sorted(glob.glob(os.path.join(score_dir, "*", "status.json"))):
        d = os.path.dirname(st)
        s = json.load(open(st))
        arm = s["arm"]
        if need_bound and not s.get("bound"):
            raise SystemExit(f"{arm}: unbound score output; refusing")
        if "no_verdict" in s:
            scores[arm] = {"no_verdict": s["no_verdict"]}
            continue
        inst = {}
        for line in open(os.path.join(d, "instances.jsonl"), encoding="utf-8"):
            o = json.loads(line)
            inst[(o["arm"], o["id"])] = o
        recs = [json.loads(line) for line in gzip.open(os.path.join(d, "units.jsonl.gz"), "rt",
                                                        encoding="utf-8")]
        scores[arm] = {"modes": s["modes"], "instances": inst, "records": recs}
    return scores


def cmd_export(a, tr):
    from p2 import export as X
    bound_or_refuse(a, tr)
    m = X.load_manifest(a.manifest, a.manifest_sha)
    scores = load_scores(a.score_dir, need_bound=not a.fixture_ok)
    recs, inst = [], {}
    for s in scores.values():
        recs += s.get("records", [])
        inst.update(s.get("instances", {}))
    if not recs:
        print("no scored records: nothing to export", file=sys.stderr)
        return 2
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
    bound = bound_or_refuse(a, tr)
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
    h = lambda s: hashlib.sha256((s or "").encode()).hexdigest()  # noqa: E731
    print(f"committed   {h(committed)}")
    print(f"regenerated {h(regen)}")
    print(f"F9 REPRODUCTION: {'BYTE-IDENTICAL' if ok else 'DIFFERS'}  {a.id}")
    os.makedirs(a.repro_dir, exist_ok=True)
    jdump({"id": a.id, "ok": ok, "bound": bound, "committed_sha256": h(committed),
           "regenerated_sha256": h(regen)},
          os.path.join(a.repro_dir, hashlib.sha256(a.id.encode()).hexdigest()[:16] + ".json"))
    return 0 if ok else 1


def cmd_aggregate(a, tr):
    from p2 import aggregate as AG
    from p2 import export as X
    from p2 import tiers as T
    bound = bound_or_refuse(a, tr)
    arm0 = {}
    for p in sorted(glob.glob(os.path.join(a.arm0_dir, "*.json"))):
        o = json.load(open(p))
        if not o.get("bound") and not a.fixture_ok:
            raise SystemExit(f"{p}: unbound Arm 0 output; refusing")
        arm0[o["arm"]] = {"no_verdict": o["no_verdict"]} if "no_verdict" in o and not o.get(
            "passes_bar") else {"passes_bar": bool(o.get("passes_bar"))}
    scores = load_scores(a.score_dir, need_bound=not a.fixture_ok)
    m = X.load_manifest(a.manifest, a.manifest_sha)
    tiers, problems = T.read_tiers(a.tiers)
    for p in problems:
        print("tiers.jsonl:", p)
    repro = {}
    for p in glob.glob(os.path.join(a.repro_dir, "*.json")):
        o = json.load(open(p))
        repro[o["id"]] = bool(o["ok"])
    try:
        res = AG.aggregate(arm0, scores, m, tiers, repro)
    except AG.Empty as e:
        print(f"NO VERDICT: {e}", file=sys.stderr)
        return 2
    except AG.MissingRepro as e:
        print(f"refusing: {e}", file=sys.stderr)
        return 2
    for (arm, mode, mech), c in sorted(res["cells"].items()):
        print(f"  {arm:<14}{mode:<5}{mech}  {c['verdict']:<11} {c.get('reason', '')}"
              + (f"  distinct {c['distinct']}" if "distinct" in c else ""))
    if res["void"]:
        print("TIERING VOID: " + "; ".join(res["void"]))
    print(f"near misses (distinct units): {res['near_misses']}")
    print(f"OVERALL: {res['overall']}")
    res["bound"] = bound
    res["cells"] = {"|".join(k): v for k, v in res["cells"].items()}
    jdump(res, a.out)
    return 0


def cmd_tier_run(a, tr):
    from p2 import tierrun as TRN
    bound_or_refuse(a, tr)
    try:
        rc, n = TRN.run(a.export, a.out, a.state_dir, a.repo, a.scoring_commit, a.models_listing,
                        a.listing_day, a.late_reason, a.agent_cmd, credentials=a.credentials)
    except TRN.TierRefused as e:
        print(f"refusing: {e}", file=sys.stderr)
        return 2
    return 0 if rc == 0 else 1


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p, corpus=True):
        p.add_argument("--d8-dir", required=True)
        p.add_argument("--transcript-dir", default=TR.DEFAULT_DIR)
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

    p = sub.add_parser("seal")
    p.add_argument("--manifest", required=True)
    p.add_argument("--transcript-dir", default=TR.DEFAULT_DIR)
    p = sub.add_parser("arm0")
    common(p)
    p.add_argument("--out-dir", default=os.path.join(RESULTS, "arm0"))
    p = sub.add_parser("score")
    common(p)
    p.add_argument("--modes", default="E,S5,S25,M")
    p.add_argument("--arm0-dir", default=os.path.join(RESULTS, "arm0"))
    p.add_argument("--out-dir", default=os.path.join(RESULTS, "score"))
    p.add_argument("--sample-e", type=int, default=1000, help=argparse.SUPPRESS)
    p.add_argument("--sample-s", type=int, default=500, help=argparse.SUPPRESS)
    p = sub.add_parser("export")
    common(p, corpus=False)
    p.add_argument("--manifest", required=True)
    p.add_argument("--manifest-sha", required=True)
    p.add_argument("--score-dir", default=os.path.join(RESULTS, "score"))
    p.add_argument("--out", default=os.path.join(RESULTS, "export"))
    p.add_argument("--fixture-ok", action="store_true", help=argparse.SUPPRESS)
    p = sub.add_parser("validate-export")
    p.add_argument("dir")
    p.add_argument("--transcript-dir", default=TR.DEFAULT_DIR)
    p = sub.add_parser("repro")
    common(p)
    p.add_argument("--id", required=True)
    p.add_argument("--score-dir", default=os.path.join(RESULTS, "score"))
    p.add_argument("--repro-dir", default=os.path.join(RESULTS, "repro"))
    p = sub.add_parser("tier-run")
    p.add_argument("--transcript-dir", default=TR.DEFAULT_DIR)
    p.add_argument("--unbound", action="store_true")
    p.add_argument("--fixture-repo", default=None, help=argparse.SUPPRESS)
    p.add_argument("--export", default=os.path.join(RESULTS, "export"))
    p.add_argument("--out", default=os.path.join(RESULTS, "tiers.jsonl"))
    p.add_argument("--state-dir", default=RESULTS)
    p.add_argument("--repo", default=SPIKE, help="where the scoring-arm commit is read")
    p.add_argument("--scoring-commit", required=True)
    p.add_argument("--models-listing", required=True,
                   help="the Models API listing, fetched on the start day, as JSON")
    p.add_argument("--listing-day", required=True, help="the UTC day the listing was fetched")
    p.add_argument("--late-reason")
    p.add_argument("--agent-cmd", default="claude")
    p.add_argument("--credentials", default=None,
                   help="the one credential file bound into the sandbox "
                        "(default ~/.claude/.credentials.json)")
    p = sub.add_parser("aggregate")
    common(p, corpus=False)
    p.add_argument("--arm0-dir", default=os.path.join(RESULTS, "arm0"))
    p.add_argument("--score-dir", default=os.path.join(RESULTS, "score"))
    p.add_argument("--manifest", required=True)
    p.add_argument("--manifest-sha", required=True)
    p.add_argument("--tiers", default=os.path.join(RESULTS, "tiers.jsonl"))
    p.add_argument("--repro-dir", default=os.path.join(RESULTS, "repro"))
    p.add_argument("--out", default=os.path.join(RESULTS, "verdict.json"))
    p.add_argument("--fixture-ok", action="store_true", help=argparse.SUPPRESS)
    a = ap.parse_args(argv)
    if getattr(a, "fixture_repo", None) and not (getattr(a, "fixture_pin", None)
                                                  and getattr(a, "fixture_pathspec", None)):
        ap.error("--fixture-repo needs --fixture-pin and --fixture-pathspec")
    if a.cmd in ("arm0", "score", "repro") and not a.fixture_repo:
        if not a.work_dir:
            ap.error("--work-dir is required")
        if not a.bundle_dir:
            from p2 import corpus as K
            a.bundle_dir = K.DEFAULT_BUNDLE_DIR

    tr = TR.Transcript(a.cmd, getattr(a, "arm", None), [os.path.basename(sys.argv[0])] + argv,
                       a.transcript_dir)
    rc, how = 1, "exited"
    try:
        if hasattr(a, "d8_dir"):
            Mx.load(a.d8_dir)
        elif a.cmd == "validate-export":
            pass
        rc = {"seal": cmd_seal, "arm0": cmd_arm0, "score": cmd_score, "export": cmd_export,
              "validate-export": cmd_validate_export, "repro": cmd_repro,
              "aggregate": cmd_aggregate, "tier-run": cmd_tier_run}[a.cmd](a, tr)
    except SystemExit as e:
        rc = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
        if isinstance(e.code, str):
            print(e.code, file=sys.stderr)
        how = "aborted" if rc else "exited"
    except BaseException:
        traceback.print_exc()
        rc, how = 1, "aborted by an exception"
    finally:
        tr.close(rc, how)
    return rc


if __name__ == "__main__":
    sys.exit(main())
