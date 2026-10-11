#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""PRE-REGISTRATION-3.md §9, V3: every new component goes red on a planted
case, and runs on a clean one. No corpus, no real packet, and no real
credential: tier-run cases use stub agents and a dummy credential file.

Run:  python3 -I -S -B harness3/prereg3_v3.py --d8-dir <research>/experiments/D8-identity

Prints one line per case, `PASS` or `FAIL`, and `V3: PASS` only if every
case passed. Exits 0 only then.
"""
import argparse
import copy
import datetime
import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
SPIKE = os.path.dirname(HERE)
H2 = os.path.join(SPIKE, "harness")
sys.path.insert(0, H2)
sys.path.insert(0, HERE)

from p2 import corpus as K  # noqa: E402
from p2 import evaluate as E  # noqa: E402
from p2 import export as X  # noqa: E402
from p2 import mech as Mx  # noqa: E402
from p3 import aggregate3 as A3  # noqa: E402
from p3 import binding as BD  # noqa: E402
from p3 import export3 as X3  # noqa: E402
from p3 import gates as G  # noqa: E402
from p3 import plants as PL  # noqa: E402
from p3 import tierrun3 as T3  # noqa: E402

RESULTS = []
D79 = BD.PREREG2_VALIDATION
TIER_MODEL_BYTES = None


def case(name, ok, detail=""):
    RESULTS.append(bool(ok))
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  -- {detail}" if detail else ""))


def raises(fn, exc=Exception):
    try:
        fn()
    except exc as e:
        return str(e) or type(e).__name__
    return None


def raises_exactly(fn, exc):
    """True only if fn raises exc; any other exception, or none, is False."""
    try:
        fn()
    except exc:
        return True
    except Exception:  # noqa: BLE001
        return False
    return False


def sh(*a, cwd=None, env=None, check=True):
    e = dict(BD.git_env(), **(env or {}))
    r = subprocess.run(list(a), cwd=cwd, capture_output=True, text=True, env=e)
    if check and r.returncode != 0:
        raise RuntimeError(f"{a}: {r.stderr}")
    return r.stdout


def git(repo, *a, env=None, check=True):
    return sh("git", "-C", repo, *a, env=env, check=check)


def new_repo(root, name):
    r = os.path.join(root, name)
    os.makedirs(os.path.join(r, "spike"))
    git(r, "init", "-q", "-b", "main")
    git(r, "config", "user.email", "v3@example.invalid")
    git(r, "config", "user.name", "v3")
    return r


def commit(repo, msg, date=None):
    env = {"GIT_COMMITTER_DATE": date, "GIT_AUTHOR_DATE": date} if date else None
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "--allow-empty", "-m", msg, env=env)
    return git(repo, "rev-parse", "HEAD").strip()


def write(path, text, mode="w"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, mode, encoding=None if "b" in mode else "utf-8") as f:
        f.write(text)


# ---------------------------------------------------------------- fixtures

def fixture_records():
    """Five 'real' records: prereg 3's Appendix B plants, run through the
    harness as k8s-en E records in the verdict selection. (Prereg 2's plants
    cannot serve: the content check matches them by text, so a 'real' copy
    would count twice.)"""
    import prereg3_plants as PP2
    recs, inst = [], {}
    for i, (n, (base, after, k, _, _)) in enumerate(sorted(PP2.PLANTS.items())):
        iid = f"fx{i}"
        ins = {"arm": "k8s-en", "mode": "E", "id": iid, "path": "doc.md", "before": base,
               "after": after, "legs": None, "f2": True}
        rs, _ = E.evaluate(ins)
        recs += [r for r in rs if r["mech"] == "Q" and r["index"] == k]
        assert X.eligible(recs[-1], dict(ins, rules=[K.VERDICT_RULE])), n
        inst[("k8s-en", iid)] = dict(ins, rules=[K.VERDICT_RULE], texts={"before": base, "after": after,
                                                                          "legs": None})
    return recs, inst


def manifest3(nonce=b"\x03" * 32):
    return {"nonce": nonce.hex(), "plants": PL.manifest_plants()}


def p2_export_repo(root, recs, inst, extra_plant=False, drop_plant=False):
    """A repository whose one commit holds a prereg 2 export of `recs` at
    spike/results/prereg2/export (p2.export.export, with prereg 2's plants)."""
    repo = new_repo(root, "p2x" + ("-extra" if extra_plant else "") + ("-drop" if drop_plant else ""))
    m2 = {"nonce": ("22" * 32), "plants": {n: {"key": f"plant:{n}", "expected": X.PLANT_EXPECT[n]}
                                           for n in X.PLANT_EXPECT}}
    out = os.path.join(repo, "spike", "results", "prereg2", "export")
    X.export(out, m2, recs, inst)
    if extra_plant:
        src = os.path.join(out, "packets", X.packet_name(m2["nonce"], "plant:P-A"))
        shutil.copytree(src, os.path.join(out, "packets", "ffffffffffffffff"))
    if drop_plant:
        shutil.rmtree(os.path.join(out, "packets", X.packet_name(m2["nonce"], "plant:P-C")))
    return repo, commit(repo, "prereg 2 export"), m2


def gate_repo(root, name, verdict=True, bound=True, vc=D79, tiers=True, started=1,
              change_after=False, days_ago=3, runs_text=None, tiers_after=False, runs_after=False):
    """A repository shaped like the history after prereg 2's step 5."""
    repo = new_repo(root, name)
    r2 = os.path.join(repo, "spike", "results", "prereg2")
    write(os.path.join(r2, "tier-model.json"), TIER_MODEL_BYTES.decode())
    d = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=days_ago)).strftime(
        "%Y-%m-%dT12:00:00Z")
    commit(repo, "tier model", d)
    if tiers and not tiers_after:
        write(os.path.join(r2, "tiers.jsonl"), '{"packet":"x"}\n')
    runs = "".join(json.dumps({"event": "started", "n": i + 1, "at": d}) + "\n" for i in range(started))
    if runs_text is not None:
        write(os.path.join(r2, "tier-runs.txt"), runs_text)
    elif started and not runs_after:
        write(os.path.join(r2, "tier-runs.txt"), runs)
    commit(repo, "prereg 2 tiers", d)
    if verdict:
        write(os.path.join(r2, "verdict.json"), json.dumps({"bound": bound, "binding": {"validation_commit": vc},
                                                            "overall": "INCONCLUSIVE"}))
        commit(repo, "prereg 2 verdict", d)
    if change_after:
        write(os.path.join(r2, "verdict.json"), json.dumps({"bound": True, "binding": {"validation_commit": vc},
                                                            "overall": "FOUND"}))
        commit(repo, "edit verdict", d)
    if tiers_after or runs_after:
        if tiers_after:
            write(os.path.join(r2, "tiers.jsonl"), '{"packet":"x"}\n')
        if runs_after:
            write(os.path.join(r2, "tier-runs.txt"), runs)
        commit(repo, "after the verdict", d)
    return os.path.join(repo, "spike")


STUB_HEAD = "#!/usr/bin/python3\nimport json, sys, os\n"
INIT = {"type": "system", "subtype": "init", "tools": ["Edit", "Glob", "Grep", "Read", "Write"],
        "mcp_servers": []}


def stub(root, name, body):
    p = os.path.join(root, f"stub_{name}.py")
    write(p, STUB_HEAD + body)
    os.chmod(p, 0o755)
    return p


# ---------------------------------------------------------------- cases

def v_plants(d8, root):
    r = subprocess.run([sys.executable, "-I", "-B", os.path.join(HERE, "prereg3_plants.py"), "--d8-dir", d8],
                       capture_output=True, text=True)
    case("plants: prereg3_plants.py prints PLANTS: PASS", r.returncode == 0 and "PLANTS: PASS" in r.stdout)
    src = open(os.path.join(HERE, "prereg3_plants.py")).read()
    muts = [("P-A Defaults says four", 'd("## Defaults", L1 + "\\n" + L2,',
             'd("## Defaults", L1.replace("three", "four") + "\\n" + L2,'),
            ("P-B Beta status dated 03-05", '"Beta moves sandbox telemetry into the shared pipeline.", ST),',
             '"Beta moves sandbox telemetry into the shared pipeline.", ST.replace("03-04", "03-05")),'),
            ("P-C keeps old window time", 'd("## Sunday windows", NP, W2,', 'd("## Sunday windows", NP, W,'),
            ("P-D retention unchanged", 'S1.replace("seven", "thirty")', 'S1'),
            ("P-E stale duplicate removed", ',\n              "## Upload limits", U1 + "\\n" + U2), 1, 1, 5)',
             '), 1, 1, 5)')]
    work = os.path.join(root, "plantmut")
    os.makedirs(work)
    for f in ("prose_merge.py", "prereg2_plants.py"):
        shutil.copy(os.path.join(H2, f), work)
    for name, a, b in muts:
        if src.count(a) != 1:
            case(f"plants: mutant '{name}' goes red", False, "BROKEN: pattern does not match once")
            continue
        p = os.path.join(work, "prereg3_plants.py")
        write(p, src.replace(a, b, 1))
        r = subprocess.run([sys.executable, "-I", "-B", p, "--d8-dir", d8], capture_output=True, text=True)
        case(f"plants: mutant '{name}' goes red", r.returncode == 1 and "PLANTS: FAIL" in r.stdout)
    good = manifest3()
    case("loader: accepts P-A..P-E with §3's expectations", raises(lambda: PL.check_manifest(good)) is None)
    three = copy.deepcopy(good)
    for p in ("P-D", "P-E"):
        three["plants"].pop(p)
    case("loader: refuses three plants", raises(lambda: PL.check_manifest(three), PL.PlantError))
    six = copy.deepcopy(good)
    six["plants"]["P-F"] = six["plants"]["P-A"]
    case("loader: refuses six plants", raises(lambda: PL.check_manifest(six), PL.PlantError))
    chg = copy.deepcopy(good)
    chg["plants"]["P-D"]["expected"]["q3"] = "no"
    case("loader: refuses one changed expectation", raises(lambda: PL.check_manifest(chg), PL.PlantError))
    case("loader: refuses an empty manifest", raises(lambda: PL.check_manifest({}), PL.PlantError))


RIGHT = {"P-A": ("yes", "yes", "no", "no"), "P-B": ("yes", "no", "no", "no"), "P-C": ("no", "no", "no", "no"),
         "P-D": ("yes", "yes", "yes", "no"), "P-E": ("yes", "yes", "yes", "yes")}


def right_tiers(m):
    t = {}
    for p, a in RIGHT.items():
        n = X.packet_name(m["nonce"], f"plant:{p}")
        t[n] = dict(packet=n, unplaceable=False, q1=a[0], q2=a[1], q3=a[2], q4=a[3])
    return t


def v_void(root):
    m = manifest3()
    names = PL.plant_names(m)
    case("void: all plants right -> not void", PL.void_reasons(names, right_tiers(m)) == [])

    def with_(p, **kw):
        t = right_tiers(m)
        n = names[p]
        t[n] = dict(t[n], **kw)
        return PL.void_reasons(names, t)
    case("void: P-D q3 'no'", with_("P-D", q3="no"))
    case("void: P-E q4 'no'", with_("P-E", q4="no"))
    case("void: P-A q3 'yes'", with_("P-A", q3="yes"))
    case("void: P-C in tier B", with_("P-C", q1="yes"))
    for p in RIGHT:
        t = right_tiers(m)
        t.pop(names[p])
        case(f"void: {p} untiered", PL.void_reasons(names, t))
    case("void: A<->B confusion on P-B does not void", with_("P-B", q2="yes") == [])
    case("void: P-A unplaceable, with q1-q4 as expected, voids (UNPLACEABLE does not qualify)",
         with_("P-A", unplaceable=True))
    case("void: P-B unplaceable, with q1-q4 as expected, voids", with_("P-B", unplaceable=True))
    case("void: no tiers at all", PL.void_reasons(names, {}))


def found_fixture():
    nonce = "00" * 32
    m = {"nonce": nonce, "plants": PL.manifest_plants()}
    inst = {("k8s-en", "i1"): {"arm": "k8s-en", "mode": "E", "rules": [K.VERDICT_RULE, "none", "anywhere"]}}
    recs = [{"id": "i1|0", "arm": "k8s-en", "mode": "E", "mech": "Q", "instance": "i1", "unit": "u" * 64,
             "hard": {"cls": "WRONG", "mechanism_target_text": "m"}, "oracle_target_text": "o",
             "oracle": "SURVIVED", "decided": True, "f2": True, "wf": True, "nl": True}]
    for i in range(400):
        recs.append({"id": f"i1|{i+1}", "arm": "k8s-en", "mode": "E", "mech": "Q", "instance": "i1",
                     "unit": f"{i:064d}", "hard": {"cls": "RIGHT", "mechanism_target_text": "x"},
                     "oracle": "SURVIVED", "decided": True, "f2": True, "wf": True, "nl": True})
    name = X.packet_name(nonce, X.packet_key(recs[0]))
    tiers = dict(right_tiers(m))
    tiers[name] = {"packet": name, "q1": "yes", "q2": "yes", "q3": "no", "q4": "no", "unplaceable": False}
    arm0 = {"k8s-en": {"passes_bar": True}}
    scores = {"k8s-en": {"modes": ["E"], "instances": inst, "records": recs}}
    repro = {"i1|0": {"id": "i1|0", "ok": True, "bound": True, "committed_sha256": "a" * 64,
                      "regenerated_sha256": "a" * 64}}
    return m, arm0, scores, tiers, repro, name


def v_aggregate(root):
    cid = ("k8s-en", "E", "Q")
    m, arm0, scores, tiers, repro, name = found_fixture()
    r = A3.aggregate3(arm0, scores, m, tiers, repro)
    case("H8: every plant right -> FOUND", r["cells"][cid]["verdict"] == "FOUND" and r["overall"] == "FOUND")
    for label, p, kw in (("P-D q3 'no'", "P-D", {"q3": "no"}), ("P-E q4 'no'", "P-E", {"q4": "no"}),
                         ("P-C in tier B", "P-C", {"q1": "yes"})):
        t = dict(tiers)
        n = X.packet_name(m["nonce"], f"plant:{p}")
        t[n] = dict(t[n], **kw)
        r = A3.aggregate3(arm0, scores, m, t, repro)
        case(f"H8: {label} alone -> every exporting cell NO VERDICT, overall INCONCLUSIVE",
             r["cells"][cid]["verdict"] == "NO VERDICT" and "void" in r["cells"][cid]["reason"]
             and r["overall"] == "INCONCLUSIVE")
    t = dict(tiers)
    t.pop(name)
    r = A3.aggregate3(arm0, scores, m, t, repro)
    case("coverage: an untiered real packet -> its cell NO VERDICT",
         r["cells"][cid]["verdict"] == "NO VERDICT" and "untiered" in r["cells"][cid]["reason"])
    t = dict(tiers)
    t.pop(X.packet_name(m["nonce"], "plant:P-B"))
    r = A3.aggregate3(arm0, scores, m, t, repro)
    case("coverage: a skipped plant voids the tiering", r["void"] and r["overall"] == "INCONCLUSIVE")
    r = A3.aggregate3(arm0, scores, m, tiers, repro, gaps={cid: "fixture gap"})
    case("inputs: a gap makes its cell NO VERDICT", r["cells"][cid]["verdict"] == "NO VERDICT"
         and "gap" in r["cells"][cid]["reason"])
    case("H8: aggregate3 refuses a three-plant manifest",
         raises(lambda: A3.aggregate3(arm0, scores, {"nonce": m["nonce"], "plants": {
             k: v for k, v in m["plants"].items() if k in ("P-A", "P-B", "P-C")}}, tiers, repro), PL.PlantError))
    nr = dict(repro)
    nr.pop("i1|0")
    from p2 import aggregate as AG
    case("repro: a record meeting F1-F6 with no repro stops aggregate (MissingRepro), never NOT FOUND",
         raises(lambda: A3.aggregate3(arm0, scores, m, tiers, nr), AG.MissingRepro))
    # inputs and repro acceptance
    ok = {"bound": True, "binding": {"validation_commit": D79}}
    case("inputs: bound to d79bf2e accepted", raises(lambda: A3.check_input(ok, "x")) is None)
    case("inputs: bound to another commit refused", raises(lambda: A3.check_input(
        {"bound": True, "binding": {"validation_commit": "0" * 40}}, "x"), A3.InputRefused))
    case("inputs: marked unbound refused", raises(lambda: A3.check_input(
        {"bound": False, "binding": {"validation_commit": D79}}, "x"), A3.InputRefused))
    vc3 = "3" * 40
    rp = lambda vc, b=True, okv=True: {"id": "i1|0", "ok": okv, "bound": b,  # noqa: E731
                                       "binding": {"validation_commit": vc},
                                       "committed_sha256": "a" * 64, "regenerated_sha256": "a" * 64}
    case("repro: prereg 2's, bound to d79bf2e, accepted", raises(lambda: A3.accept_repros([rp(D79)], [], vc3)) is None)
    case("repro: prereg 3's, bound to prereg 3's validation commit, accepted",
         raises(lambda: A3.accept_repros([], [rp(vc3)], vc3)) is None)
    case("repro: bound to another commit refused",
         raises_exactly(lambda: A3.accept_repros([rp("9" * 40)], [], vc3), A3.InputRefused))
    case("repro: bound:false refused",
         raises_exactly(lambda: A3.accept_repros([rp(D79, b=False)], [], vc3), A3.InputRefused))
    case("repro: two accepted results that disagree refused",
         raises_exactly(lambda: A3.accept_repros([rp(D79)], [rp(vc3, okv=False)], vc3), A3.InputRefused))
    case("repro: a prereg 3 result bound to d79bf2e is refused (source split)",
         raises_exactly(lambda: A3.accept_repros([], [rp(D79)], vc3), A3.InputRefused))
    case("repro: a prereg 2 result bound to prereg 3's validation commit is refused (source split)",
         raises_exactly(lambda: A3.accept_repros([rp(vc3)], [], vc3), A3.InputRefused))
    case("repro: with no prereg 3 validation commit, a prereg 3 result bound to None is refused",
         raises_exactly(lambda: A3.accept_repros([], [rp(None)], None), A3.InputRefused))
    case("repro: with no prereg 3 validation commit, prereg 2's d79bf2e results are still accepted",
         raises(lambda: A3.accept_repros([rp(D79)], [], None)) is None)
    acc = A3.accept_repros([rp(D79)], [], vc3)
    r = A3.aggregate3(arm0, scores, m, tiers, acc)
    case("repro: the reprodemo case gives FOUND with a d79bf2e-bound repro", r["overall"] == "FOUND")


def v_export(d8, root):
    recs, inst = fixture_records()
    m3 = manifest3()
    out = os.path.join(root, "e3")
    names = X3.export3(out, m3, recs, inst)
    case("export3: 5 real + 5 plants written, validator clean", len(names) == 10 and X3.validate3(out) == [])
    case("export3: PROMPT.md is the registered prompt",
         __import__("hashlib").sha256(open(os.path.join(out, "PROMPT.md"), "rb").read()).hexdigest()
         == X3.PROMPT_SHA256)

    def broken(label, fn):
        d = os.path.join(root, "e3-" + label.replace(" ", "-"))
        shutil.copytree(out, d)
        fn(d)
        case(f"manifest: validate3 rejects {label}", X3.validate3(d) != [])
    broken("a missing PACKETS.txt", lambda d: os.remove(os.path.join(d, "PACKETS.txt")))
    broken("a PACKETS.txt symlink", lambda d: (os.rename(os.path.join(d, "PACKETS.txt"), os.path.join(root, "pk")),
                                               os.symlink(os.path.join(root, "pk"), os.path.join(d, "PACKETS.txt"))))
    broken("a list that omits a name", lambda d: write(os.path.join(d, "PACKETS.txt"),
                                                       "".join(open(os.path.join(d, "PACKETS.txt")).readlines()[1:])))
    broken("a list with an extra name", lambda d: write(os.path.join(d, "PACKETS.txt"), "0" * 16 + "\n", "a"))
    broken("an unsorted list", lambda d: write(os.path.join(d, "PACKETS.txt"),
                                               "".join(reversed(open(os.path.join(d, "PACKETS.txt")).readlines()))))
    broken("prereg 2's PROMPT.md", lambda d: write(os.path.join(d, "PROMPT.md"), X.prompt_text()))
    case("manifest: validate3 rejects an empty directory", X3.validate3(os.path.join(root, "nothing")) != [])
    # same records / same plants
    repo, c2, m2 = p2_export_repo(root, recs, inst)
    # the work tree is made to differ from the committed export: same_records
    # must read the commit, so it still passes (L5)
    wt_pk = os.path.join(repo, "spike", "results", "prereg2", "export", "packets")
    victim = sorted(os.listdir(wt_pk))[0]
    shutil.rmtree(os.path.join(wt_pk, victim))
    write(os.path.join(wt_pk, sorted(os.listdir(wt_pk))[0], "after.md"), "work-tree edit", "a")
    pn = PL.plant_names(m3)
    ok, lines = X3.same_records(os.path.join(repo, "spike"), out, pn, c2)
    case("same records: passes on a fixture built like the real exports, reading the commit while the work "
         "tree differs", ok and git(repo, "status", "--porcelain").strip() != "", lines[-2])
    case("same records: prints counts only, no packet name",
         not any(n in "\n".join(lines) for n in os.listdir(os.path.join(out, "packets"))))
    ok, lines = X3.same_plants(out, pn)
    case("same plants: passes on the fixture export", ok)

    def red(label, fn, check="records"):
        d = os.path.join(root, "e3r-" + label.replace(" ", "-"))
        shutil.copytree(out, d)
        fn(d)
        if check == "records":
            res = X3.same_records(os.path.join(repo, "spike"), d, pn, c2)[0]
        else:
            res = X3.same_plants(d, pn)[0]
        case(f"same {check}: red when {label}", not res)
    real = sorted(set(os.listdir(os.path.join(out, "packets"))) - set(pn.values()))
    red("one byte of one real packet changes", lambda d: write(
        os.path.join(d, "packets", real[0], "after.md"), "x", "a"))
    red("a real packet is missing", lambda d: shutil.rmtree(os.path.join(d, "packets", real[0])))
    red("one plant packet's text changes", lambda d: write(
        os.path.join(d, "packets", pn["P-C"], "after.md"), "x", "a"), check="plants")
    repo_d, c2d, _ = p2_export_repo(root, recs, inst, drop_plant=True)
    res = X3.same_records(os.path.join(repo_d, "spike"), out, pn, c2d)[0]
    case("same records: red when prereg 2's export lacks one of its plants", not res)
    repo_x, c2x, _ = p2_export_repo(root, recs, inst, extra_plant=True)
    res = X3.same_records(os.path.join(repo_x, "spike"), out, pn, c2x)[0]
    case("same records: red when a fourth prereg 2 plant is in excess", not res)
    keys = [X.packet_key(r) for r in recs]
    ok, lines = X3.same_per_name(os.path.join(repo, "spike"), m2["nonce"], out, m3["nonce"], keys, c2)
    case("per name: passes when every key's packets agree", ok and "5 keys" in lines[0], lines[0])
    d = os.path.join(root, "e3pn")
    shutil.copytree(out, d)
    write(os.path.join(d, "packets", X.packet_name(m3["nonce"], keys[0]), "after.md"), "x", "a")
    ok, lines = X3.same_per_name(os.path.join(repo, "spike"), m2["nonce"], d, m3["nonce"], keys, c2)
    case("per name: red when one key's packets differ", not ok, lines[0])
    ok, lines = X3.same_per_name(os.path.join(repo, "spike"), m2["nonce"], out, m3["nonce"], [], c2)
    case("per name: red when no key is checked", not ok, lines[0])
    return out


def v_pins(root):
    import hashlib
    doc = open(X3.PREREG3, encoding="utf-8").read()
    case("pins: the merged document gives the registered prompt", raises(X3.prompt_text3) is None)
    old = "> `PACKETS.txt` names every packet, one per line. Work from that list, not"
    assert doc.count(old) == 1
    changed = doc.replace(old, old.replace("Work from", "Always work from"))
    p = os.path.join(root, "PRE-REGISTRATION-3.md")
    write(p, changed)
    saved = (X3.PREREG3, X3.PREREG3_SHA256)
    try:
        X3.PREREG3 = p
        case("pins: a changed document is refused", raises(X3.prompt_text3, X3.ExportError))
        outside = doc.replace("line. Work from that list, not from a directory listing, which can be cut",
                              "line. Work from that list, and not from a directory listing, which can be cut", 1)
        assert outside != doc and outside[outside.index("## Appendix A"):] == doc[doc.index("## Appendix A"):]
        write(p, outside)
        case("pins: a change outside Appendix A is refused by the document pin",
             raises(X3.prompt_text3, X3.ExportError))
        write(p, changed)
        X3.PREREG3_SHA256 = hashlib.sha256(changed.encode()).hexdigest()
        case("pins: a changed Appendix A is refused even if the document pin were updated",
             raises(X3.prompt_text3, X3.ExportError))
    finally:
        X3.PREREG3, X3.PREREG3_SHA256 = saved


def v_aggregate_cli(root, d8, recs, inst, m3, export3_dir):
    """prereg3.py aggregate, run in-process on fixtures with --unbound and
    --fixture-ok. prereg 2's export tree is read from a fixture repository:
    p3.export3.read_tree_packets is pointed at it, since the real e46e320
    tree is not a fixture."""
    import contextlib
    import gzip
    import io
    import hashlib
    import prereg3
    fx = os.path.join(root, "agg")
    os.makedirs(fx)
    repo, c2, m2 = p2_export_repo(fx, recs, inst)
    sd = os.path.join(fx, "score", "k8s-en")
    os.makedirs(sd)
    write(os.path.join(sd, "status.json"), json.dumps({"arm": "k8s-en", "modes": ["E"]}))
    write(os.path.join(sd, "instances.jsonl"), "".join(
        json.dumps(dict({k: v for k, v in i.items() if k != "texts"}, id=key[1])) + "\n" for key, i in inst.items()))
    with gzip.open(os.path.join(sd, "units.jsonl.gz"), "wt", encoding="utf-8") as g:
        g.write("".join(json.dumps(r) + "\n" for r in recs))
    write(os.path.join(fx, "arm0", "k8s-en.json"), json.dumps({"arm": "k8s-en", "passes_bar": True}))
    names3 = sorted(os.listdir(os.path.join(export3_dir, "packets")))
    pn = PL.plant_names(m3)
    lines = []
    for n in names3:
        p = [k for k, v in pn.items() if v == n]
        a = RIGHT[p[0]] if p else ("yes", "yes", "no", "no")
        lines.append(json.dumps({"packet": n, "q1": a[0], "q2": a[1], "q3": a[2], "q4": a[3],
                                 "unplaceable": False, "why": "fixture"}) + "\n")
    st = os.path.join(fx, "state")
    write(os.path.join(st, "tier-work-1", "tiers.jsonl"), "".join(lines))
    write(os.path.join(st, "tier-runs.txt"), json.dumps({"event": "started", "n": 1, "at": "x"}) + "\n"
          + json.dumps({"event": "completed", "n": 1, "lines": len(lines), "init_failed": False}) + "\n")
    for r in recs:
        write(os.path.join(fx, "repro2", hashlib.sha256(r["id"].encode()).hexdigest()[:16] + ".json"), json.dumps(
            {"id": r["id"], "ok": True, "bound": True, "binding": {"validation_commit": D79},
             "committed_sha256": "a" * 64, "regenerated_sha256": "a" * 64}))
    os.makedirs(os.path.join(fx, "repro3"))
    mf3, mf2 = os.path.join(fx, "m3.json"), os.path.join(fx, "m2.json")
    write(mf3, json.dumps(m3))
    write(mf2, json.dumps(m2))
    sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()  # noqa: E731
    tampered = os.path.join(fx, "export3-tampered")
    shutil.copytree(export3_dir, tampered)
    real = sorted(set(names3) - set(pn.values()))
    write(os.path.join(tampered, "packets", real[0], "after.md"), "x", "a")
    orig = X3.read_tree_packets
    X3.read_tree_packets = lambda spike, commit=None, rel=X3.EXPORT2_REL: orig(os.path.join(repo, "spike"), c2, rel)

    def run(export, out):
        argv = ["aggregate", "--unbound", "--fixture-ok", "--transcript-dir", os.path.join(fx, "tr"),
                "--d8-dir", d8, "--manifest", mf3, "--manifest-sha", sha(mf3), "--manifest2", mf2,
                "--manifest2-sha", sha(mf2), "--arm0-dir", os.path.join(fx, "arm0"),
                "--score-dir", os.path.join(fx, "score"), "--state-dir", st, "--repro-dir",
                os.path.join(fx, "repro3"), "--repro-dir2", os.path.join(fx, "repro2"),
                "--export", export, "--out", out, "--spike-repo", os.path.join(repo, "spike")]
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
            rc = prereg3.main(argv)
        return rc, buf.getvalue()
    try:
        out_bad = os.path.join(fx, "verdict-bad.json")
        rc, text = run(tampered, out_bad)
        verdictish = [ln for ln in text.splitlines()
                      if ln.startswith("OVERALL") or ln.startswith("TIERING VOID") or ln.startswith("  k8s-en")
                      or ln.startswith("near misses")]
        case("aggregate cli: a failed per-name check prints no cell, VOID or OVERALL line and writes no verdict",
             rc == 1 and "SAME PER NAME: FAIL" in text and not verdictish and not os.path.exists(out_bad),
             f"exit {rc}, {len(verdictish)} verdict line(s)")
        out_ok = os.path.join(fx, "verdict-ok.json")
        rc, text = run(export3_dir, out_ok)
        case("aggregate cli: with the per-name check passing, the same fixture prints OVERALL and writes a verdict",
             rc == 0 and "SAME PER NAME: PASS" in text and "OVERALL:" in text and os.path.exists(out_ok),
             f"exit {rc}")
    finally:
        X3.read_tree_packets = orig


def v_binding(root):
    src = os.path.dirname(SPIKE)
    clone = os.path.join(root, "clone")
    sh("git", "clone", "-q", "--no-hardlinks", src, clone)
    cs = os.path.join(clone, "spike")
    case("prereg 2 untouched: a fresh clone passes", BD.prereg2_untouched(cs) == [])
    p = os.path.join(cs, "harness", "prose_merge.py")
    write(p, "#", "a")
    case("prereg 2 untouched: one byte changed under harness/ is refused", BD.prereg2_untouched(cs) != [])
    git(clone, "checkout", "-q", "--", "spike/harness/prose_merge.py")
    write(os.path.join(cs, "ORACLE.md"), "x", "a")
    case("prereg 2 untouched: a changed ORACLE.md is refused", BD.prereg2_untouched(cs) != [])
    git(clone, "checkout", "-q", "--", "spike/ORACLE.md")
    # namespaces
    fx = new_repo(root, "ns")
    fs = os.path.join(fx, "spike")
    commit(fx, "init")
    tp = os.path.join(root, "t.txt")
    write(tp, "t")
    BD.mark_executed(fs, BD.PREREG3, "export", None, tp)
    cd = BD.common_dir(fs)
    case("namespace: a prereg 3 export marker lands under <common>/prereg3/",
         os.path.isfile(os.path.join(cd, "prereg3", "export.json")))
    case("namespace: a prereg 3 marker does not stop a prereg 2 command",
         not BD.executed(fs, BD.PREREG2, "export"))
    fx2 = new_repo(root, "ns2")
    fs2 = os.path.join(fx2, "spike")
    commit(fx2, "init")
    BD.mark_executed(fs2, BD.PREREG2, "export", None, tp)
    case("namespace: a prereg 2 marker does not stop a prereg 3 command",
         not BD.executed(fs2, BD.PREREG3, "export"))
    case("namespace: a prereg 3 marker stops prereg 3's export", BD.executed(fs, BD.PREREG3, "export"))


def v_order(root):
    def fresh(name):
        r = new_repo(root, name)
        write(os.path.join(r, "spike", "README"), "x")
        commit(r, "init")
        return r
    r = fresh("og-clean")
    case("order guard: runs when prereg 2's tiering has not started",
         raises(lambda: G.order_guard(os.path.join(r, "spike"))) is None)
    rel = os.path.join("spike", "results", "prereg2", "tier-runs.txt")
    r = fresh("og-wt")
    write(os.path.join(r, rel), "{}\n")
    case("order guard: refuses tier-runs.txt in the work tree",
         raises(lambda: G.order_guard(os.path.join(r, "spike")), G.GateError))
    r = fresh("og-other")
    other = os.path.join(root, "og-other-wt")
    git(r, "worktree", "add", "-q", "-b", "side", other)
    write(os.path.join(other, rel), "{}\n")
    case("order guard: refuses tier-runs.txt only in another work tree",
         raises(lambda: G.order_guard(os.path.join(r, "spike")), G.GateError))
    r = fresh("og-hist")
    write(os.path.join(r, rel), "{}\n")
    commit(r, "add")
    os.remove(os.path.join(r, rel))
    commit(r, "remove")
    case("order guard: refuses tier-runs.txt committed then deleted",
         raises(lambda: G.order_guard(os.path.join(r, "spike")), G.GateError))
    r = fresh("og-reflog")
    git(r, "switch", "-q", "-c", "tmp")
    write(os.path.join(r, rel), "{}\n")
    commit(r, "add on tmp")
    git(r, "switch", "-q", "main")
    git(r, "branch", "-q", "-D", "tmp")
    case("order guard: refuses tier-runs.txt held only by a reflog",
         raises(lambda: G.order_guard(os.path.join(r, "spike")), G.GateError))
    r = fresh("og-work")
    os.makedirs(os.path.join(r, "spike", "results", "prereg2", "tier-work-1"))
    case("order guard: refuses a tier-work-1/ directory",
         raises(lambda: G.order_guard(os.path.join(r, "spike")), G.GateError))

    # committed order check
    def history(name, order_ok=True, started_late=True):
        r = new_repo(root, name)
        s = os.path.join(r, "spike")
        r3 = os.path.join(s, "results", "prereg3")
        r2 = os.path.join(s, "results", "prereg2")
        if order_ok:
            write(os.path.join(r3, "export", "PROMPT.md"), "p")
            write(os.path.join(r3, "transcripts", "t-export.txt"), "# executed: 2026-10-12T10:00:00Z\n")
            write(os.path.join(r3, "executed", "export.json"), json.dumps({"transcript": "t-export.txt"}))
            commit(r, "export 3")
        at = "2026-10-12T11:00:00+00:00" if started_late else "2026-10-12T09:00:00+00:00"
        write(os.path.join(r2, "tier-runs.txt"), json.dumps({"event": "started", "n": 1, "at": at}) + "\n")
        write(os.path.join(r2, "tiers.jsonl"), "{}\n")
        commit(r, "prereg 2 tiers")
        if not order_ok:
            write(os.path.join(r3, "export", "PROMPT.md"), "p")
            write(os.path.join(r3, "transcripts", "t-export.txt"), "# executed: 2026-10-12T10:00:00Z\n")
            write(os.path.join(r3, "executed", "export.json"), json.dumps({"transcript": "t-export.txt"}))
            commit(r, "export 3 after")
        return s
    case("committed order: passes in §7's order", raises(lambda: G.committed_order(history("co-ok"))) is None)
    bad = history("co-badjson")
    write(os.path.join(bad, "results", "prereg2", "tier-runs.txt"), "not json\n", "a")
    commit(os.path.dirname(bad), "garble the ledger")
    case("committed order: a non-JSON tier-runs.txt line is a GateError, not a traceback",
         raises_exactly(lambda: G.committed_order(bad), G.GateError))
    case("committed order: refuses tiers.jsonl not descending from export 3",
         raises(lambda: G.committed_order(history("co-bad", order_ok=False)), G.GateError))
    case("committed order: refuses a started run earlier than export 3's execution",
         raises(lambda: G.committed_order(history("co-early", started_late=False)), G.GateError))


def v_gate(root):
    ok = gate_repo(root, "g-ok")
    case("gate: passes on a committed, bound, unchanged verdict with tiers and a started run",
         raises(lambda: G.verdict_gate(ok)) is None)
    for name, kw in (("no verdict.json", {"verdict": False}), ("a verdict marked bound:false", {"bound": False}),
                     ("a verdict bound to another commit", {"vc": "0" * 40}),
                     ("a verdict changed after it was added", {"change_after": True}),
                     ("no committed tiers.jsonl", {"tiers": False}),
                     ("no tier-runs.txt", {"started": 0})):
        case(f"gate: refuses {name}", raises(lambda: G.verdict_gate(gate_repo(root, "g-" + name.replace(" ", "-"),
                                                                              **kw)), G.GateError))
    case("gate: refuses a tier-runs.txt with zero started runs",
         raises(lambda: G.verdict_gate(gate_repo(root, "g-zero", runs_text='{"event": "completed", "n": 1}\n')),
                G.GateError))
    case("gate: refuses a tiers.jsonl committed only after the verdict",
         raises_exactly(lambda: G.verdict_gate(gate_repo(root, "g-tiers-after", tiers_after=True)), G.GateError))
    case("gate: refuses a tier-runs.txt committed only after the verdict (read at the verdict commit, not HEAD)",
         raises_exactly(lambda: G.verdict_gate(gate_repo(root, "g-runs-after", runs_after=True)), G.GateError))
    case("gate: a non-JSON tier-runs.txt line is a GateError, not a traceback",
         raises_exactly(lambda: G.verdict_gate(gate_repo(root, "g-badjson", runs_text="not json\n")),
                        G.GateError))
    utc = new_repo(root, "g-utc")
    write(os.path.join(utc, "spike", "x"), "x")
    commit(utc, "late evening, New York", "2026-10-10T22:30:00-04:00")
    case("start day: the committer date is converted to UTC (22:30 -04:00 on 10-10 is UTC day 10-11)",
         G.commit_day(os.path.join(utc, "spike"), "HEAD") == datetime.date(2026, 10, 11))
    case("model pin: the pinned tier-model.json gives the model", G.tier_model(ok) == "claude-opus-5-5")
    bad = gate_repo(root, "g-model")
    write(os.path.join(bad, "results", "prereg2", "tier-model.json"), " ", "a")
    commit(os.path.dirname(bad), "edit model")
    case("model pin: refuses a tier-model.json with another blob", raises(lambda: G.tier_model(bad), G.GateError))
    write(os.path.join(bad, "results", "prereg2", "tier-model.json"), TIER_MODEL_BYTES.decode())
    case("model pin: refuses another committed blob even when the work tree holds the pinned bytes",
         raises(lambda: G.tier_model(bad), G.GateError))
    wt = gate_repo(root, "g-model-wt")
    write(os.path.join(wt, "results", "prereg2", "tier-model.json"), " ", "a")
    case("model pin: refuses a work tree that differs from the pinned, committed blob",
         raises(lambda: G.tier_model(wt), G.GateError))
    d = datetime.date(2026, 10, 20)
    case("window: refuses on the verdict commit's own day", raises(lambda: G.window(d, d), G.GateError))
    case("window: runs on day D+1", raises(lambda: G.window(d, d + datetime.timedelta(days=1))) is None)
    case("window: runs on day D+14", raises(lambda: G.window(d, d + datetime.timedelta(days=14))) is None)
    case("window: day D+15 needs --late-reason",
         raises(lambda: G.window(d, d + datetime.timedelta(days=15)), G.GateError))
    case("window: day D+15 with a reason is a logged late run",
         "LATE RUN" in G.window(d, d + datetime.timedelta(days=15), "fixture reason"))
    return ok


def v_tierrun(root, export_dir, gate):
    cred = os.path.join(root, "dummy-credentials.json")
    write(cred, '{"dummy": true}\n')
    good_body = f"print(json.dumps({INIT!r}))\n" \
                "ok = os.path.isfile('/work/PACKETS.txt')\n" \
                "try:\n    open('/work/PACKETS.txt', 'a').write('x')\n    w = 'WROTE'\n" \
                "except OSError:\n    w = 'READONLY'\n" \
                "print('PACKETS', ok, w)\n" \
                "names = open('/work/PACKETS.txt').read().split()\n" \
                "with open('/work/tiers.jsonl', 'w') as f:\n" \
                "    [f.write(json.dumps({'packet': n, 'q1': 'no', 'q2': 'no', 'q3': 'no', 'q4': 'no', " \
                "'unplaceable': False, 'why': 'stub'}) + '\\n') for n in names]\n"
    logs = []

    def run(name, body, state=None):
        st = state or os.path.join(root, "state-" + name)
        logs.clear()
        try:
            rc = T3.run(export_dir, st, gate, None, stub(root, name, body), log=logs.append, credentials=cred)
        except T3.TierRefused as e:
            return st, ("refused", str(e))
        return st, rc
    st, rc = run("good", good_body)
    case("sandbox: a stub can read /work/PACKETS.txt and cannot write it",
         any("PACKETS True READONLY" in ln for ln in logs), [ln for ln in logs if "PACKETS True" in ln][:1])
    case("init check: a stub with the exact init event runs, and its run binds",
         rc[2] is False and T3.binding_run(st)[0] == 1)
    case("credential: logged before and after", any("credential before" in ln for ln in logs)
         and any("credential after" in ln for ln in logs))
    extra = dict(INIT, tools=INIT["tools"] + ["Bash"])
    for name, first in (("extra-tool", extra), ("mcp", dict(INIT, mcp_servers=[{"name": "x"}])),
                        ("not-init", {"type": "assistant"})):
        body = f"print(json.dumps({first!r}), flush=True)\nopen('/work/tiers.jsonl','w').write('{{}}\\n')\n" \
               "import time; time.sleep(5)\n"
        st, rc = run(name, body)
        led = T3.read_ledger(st)
        case(f"init check: stub '{name}' is stopped, recorded init_failed, and does not bind",
             rc[2] is True and led[-1].get("init_failed") and T3.binding_run(st) == (None, None))
    st, rc = run("no-init", "print('no json here')\n")
    case("init check: a stream with no init event is init_failed", rc[2] is True and T3.read_ledger(st)[-1]["init_failed"])
    auth = f"print(json.dumps({INIT!r}))\nopen('/work/tiers.jsonl','w').write('{{\"packet\":\"x\"}}\\n')\n" \
           "print(json.dumps({'type':'system','subtype':'api_retry','error_status':401}))\n"
    st, rc = run("auth", auth)
    led = T3.read_ledger(st)
    case("auth abort: labelled auth_aborted, with the credential's sha256 and mtime logged",
         led[-1].get("status") == "auth_aborted" and any("credential after" in ln for ln in logs))
    _, again = run("auth", good_body, state=st)
    case("auth abort: a run that wrote a line binds, and no rerun is allowed",
         T3.binding_run(st)[0] == 1 and again[0] == "refused")
    # run cap: zero-line run, then init_failed rerun, then a third is refused
    st = os.path.join(root, "state-cap1")
    run("zero", f"print(json.dumps({INIT!r}))\n", state=st)
    run("cap-init", "print('no json')\n", state=st)
    _, third = run("third", good_body, state=st)
    case("run cap: zero-line run, init_failed rerun, third run refused", third[0] == "refused")
    st = os.path.join(root, "state-cap2")
    run("cap-init2", "print('no json')\n", state=st)
    run("zero2", f"print(json.dumps({INIT!r}))\n", state=st)
    _, third = run("third2", good_body, state=st)
    case("run cap: init_failed run, zero-line rerun, third run refused", third[0] == "refused")
    case("run cap: a run with lines refuses any rerun", run("x", good_body, state=os.path.join(
        root, "state-good"))[1][0] == "refused")
    bad_export = os.path.join(root, "bad-export")
    shutil.copytree(export_dir, bad_export)
    os.remove(os.path.join(bad_export, "PACKETS.txt"))
    case("tier-run: refuses an export without PACKETS.txt",
         raises(lambda: T3.run(bad_export, os.path.join(root, "st-bad"), gate, None, "x", credentials=cred),
                T3.TierRefused))
    nog = gate_repo(root, "g-none", verdict=False)
    case("tier-run: refuses without prereg 2's verdict commit",
         raises(lambda: T3.run(export_dir, os.path.join(root, "st-nog"), nog, None, "x", credentials=cred),
                T3.TierRefused))


def v_cli(root, export_dir):
    cli = os.path.join(HERE, "prereg3.py")
    td = os.path.join(root, "cli-transcripts")

    def go(*argv, isolated=True):
        pre = [sys.executable, "-I", "-S", "-B"] if isolated else [sys.executable, "-B"]
        return subprocess.run(pre + [cli, *argv], capture_output=True, text=True, cwd=root)
    r = go("validate-export", "--unbound", "--transcript-dir", td, export_dir)
    case("cli: validate-export on a clean export exits 0", r.returncode == 0 and "export: clean" in r.stdout)
    r = go("validate-export", "--unbound", "--transcript-dir", td, export_dir, isolated=False)
    case("cli: refuses without python3 -I -S", r.returncode != 0 and "refusing" in r.stderr)
    r = go("validate-export", "--unbound", "--unbound", "--transcript-dir", td, export_dir)
    case("cli: refuses a repeated option", r.returncode != 0 and "more than once" in r.stderr)
    r = go("validate-ex", "--unbound", "--transcript-dir", td, export_dir)
    case("cli: refuses an abbreviated command", r.returncode != 0)
    r = go("aggregate", "--unbound", "--transcript-dir", td, "--d8-dir", "x", "--manifest", "x")
    case("cli: aggregate refuses without --manifest2", r.returncode != 0 and "--manifest2" in r.stderr)
    r = go("tier-run", "--unbound", "--transcript-dir", td, "--state-dir", os.path.join(SPIKE, "results",
           "prereg3", "x"), "--export", export_dir, "--gate-repo", os.path.join(root, "nowhere"))
    case("cli: an unbound run may not write under results/", r.returncode != 0 and "results" in r.stderr)
    trs = sorted(os.listdir(td)) if os.path.isdir(td) else []
    case("cli: every invocation, refusals included, wrote a transcript", len(trs) >= 4, f"{len(trs)} transcripts")


def main():
    global TIER_MODEL_BYTES
    ap = argparse.ArgumentParser()
    ap.add_argument("--d8-dir", required=True)
    a = ap.parse_args()
    Mx.load(a.d8_dir)
    TIER_MODEL_BYTES = subprocess.run(["git", "-C", SPIKE, "cat-file", "blob", G.TIER_MODEL_BLOB],
                                      capture_output=True).stdout
    if not TIER_MODEL_BYTES:
        print("V3: cannot read the pinned tier-model.json blob from this repository; fetch prereg2/tiers")
        return 2
    root = tempfile.mkdtemp(prefix="prereg3-v3-")
    try:
        v_plants(a.d8_dir, root)
        v_void(root)
        v_aggregate(root)
        v_pins(root)
        out = v_export(a.d8_dir, root)
        recs_f, inst_f = fixture_records()
        v_aggregate_cli(root, a.d8_dir, recs_f, inst_f, manifest3(), out)
        v_binding(root)
        v_order(root)
        gate = v_gate(root)
        v_tierrun(root, out, gate)
        v_cli(root, out)
    finally:
        shutil.rmtree(root, ignore_errors=True)
    n, ok = len(RESULTS), sum(RESULTS)
    print(f"{ok} of {n} cases passed")
    print("V3:", "PASS" if ok == n and n else "FAIL")
    return 0 if ok == n and n else 1


if __name__ == "__main__":
    sys.exit(main())
