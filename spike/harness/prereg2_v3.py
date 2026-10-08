#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""PRE-REGISTRATION-2.md §9 V3: each new component goes red on a planted
case, and on an empty input.

    python3 -I prereg2_v3.py --d8-dir <research>/experiments/D8-identity

Prints one line per check and `V3: PASS` only if every check holds; exits 1
otherwise. Every repository it builds is a constructed fixture in a temporary
directory, with fixed author, committer and dates, so its commit ids -- and
so the records that name them -- are the same on every run. It reads no
corpus.

V4 (prereg2_v4.sh) breaks each gate this exercises and requires this script
to go red.
"""
import argparse
import contextlib
import gzip
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from p2 import mech as Mx  # noqa: E402

FIX = os.path.join(HERE, "p2", "fixtures")
RESULTS = []


def check(label, cond, detail=""):
    RESULTS.append((label, bool(cond)))
    print(f"  {'ok  ' if cond else 'FAIL'}  {label}" + (f"   [{detail}]" if detail else ""))
    return bool(cond)


def section(t):
    print(f"\n== {t}")


def d(*bl):
    return "\n\n".join(bl) + "\n"


GIT_ENV = {"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
           "GIT_AUTHOR_NAME": "fixture", "GIT_AUTHOR_EMAIL": "fixture@invalid",
           "GIT_COMMITTER_NAME": "fixture", "GIT_COMMITTER_EMAIL": "fixture@invalid",
           "GIT_AUTHOR_DATE": "2001-01-01T00:00:00Z", "GIT_COMMITTER_DATE": "2001-01-01T00:00:00Z",
           "LC_ALL": "C"}


def fixture_repo(root, commits, merges=()):
    """commits: [(message, {path: text or None})] on main, in order."""
    os.makedirs(root)
    env = dict(os.environ, **GIT_ENV)

    def g(*a):
        return subprocess.run(["git", "-C", root, *a], check=True, capture_output=True,
                              text=True, env=env).stdout.strip()
    g("init", "-q", "-b", "main")
    for msg, files in commits:
        for p, t in files.items():
            fp = os.path.join(root, p)
            if t is None:
                os.remove(fp)
                continue
            os.makedirs(os.path.dirname(fp) or root, exist_ok=True)
            with open(fp, "w", encoding="utf-8", newline="") as f:
                f.write(t)
        g("add", "-A")
        g("commit", "-q", "--allow-empty", "-m", msg)
    return g("rev-parse", "HEAD"), g


def cli(*args):
    """Run prereg2.py in-process; return (exit status, captured output)."""
    import prereg2
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        rc = prereg2.main([str(a) for a in args])
    return rc, buf.getvalue()


def recs_of(inst):
    from p2 import evaluate as E
    return E.evaluate(inst)[0]


def one(inst, mech, index=None, name=None):
    for r in recs_of(inst):
        if r["mech"] == mech and (index is None or r.get("index") == index) \
                and (name is None or r.get("name") == name):
            return r
    return None


def inst1(before, after, legs=None, f2=True, arm="fixture", mode="E", iid="x"):
    return {"arm": arm, "mode": mode, "id": iid, "path": "doc.md", "before": before,
            "after": after, "legs": legs, "f2": f2}


# ======================================================================

def t_d8_pin(a, tmp):
    section("D8 pin: the mechanism is kindspec/research d51ce09, or nothing runs")
    check("the --d8-dir in use matches d51ce09 file for file", not Mx.verify_d8(a.d8_dir))
    bad = os.path.join(tmp, "d8bad")
    shutil.copytree(a.d8_dir, bad)
    with open(os.path.join(bad, "anchor_eval3.py"), "a") as f:
        f.write("\n# edited\n")
    check("a D8 directory with one edited file is refused", Mx.verify_d8(bad))
    empty = os.path.join(tmp, "d8empty")
    os.makedirs(empty)
    check("an empty D8 directory is refused", len(Mx.verify_d8(empty)) == len(Mx.D8_SHA256))


def t_copied(a):
    section("R: the copied slugs() and regions() match d51ce09 byte for byte")
    src = open(os.path.join(HERE, "p2", "mech.py"), encoding="utf-8").read().split("\n")
    blocks, cur = [], None
    for line in src:
        if line.startswith("# ---- COPIED VERBATIM:"):
            cur = []
        elif line == "# ---- END COPIED ----":
            blocks.append("\n".join(cur))
            cur = None
        elif cur is not None:
            cur.append(line)
    check("three copied blocks are marked", len(blocks) == len(Mx.COPIED) == 3)
    for (f, lo, hi), got in zip(Mx.COPIED, blocks):
        want = "\n".join(open(os.path.join(a.d8_dir, f), encoding="utf-8").read().split("\n")[lo - 1:hi])
        check(f"{f} lines {lo}-{hi} == the copy in p2/mech.py", got == want,
              f"{len(got)} vs {len(want)} bytes")


def t_repeat(a):
    section("REPEAT (§5.2)")
    import oracle_limitation as OL
    P = Mx.P
    from p2 import oracle as O
    res = P.stock_merge(OL.BASE, OL.LEG_A, OL.LEG_C, "doc.md")
    bb, bm = Mx.D8.blocks(OL.BASE), Mx.D8.blocks(res["merged"])
    orc = P.tllc(OL.BASE, OL.LEG_A, OL.LEG_C, res["merged"], bb, bm)
    check("oracle_limitation.py's case: TLLC alone says SURVIVED, target 3",
          orc[2] == ("SURVIVED", 3), orc[2])
    tg = lambda i: orc[i][1] if orc[i][0] == "SURVIVED" else None  # noqa: E731
    check("oracle_limitation.py's case comes out UNDECIDABLE-REPEAT under the rule",
          O.repeat_rule([b["content"] for b in bb], [b["content"] for b in bm], tg, 2, 3) is False)
    # Its NOTE blocks are 16 characters, under the mechanism's 20-character
    # quote floor, so evaluate() skips them (skip:short_quote) and never
    # grades them. The same case with a 20+ character NOTE goes through the
    # whole evaluation path.
    note = "NOTE: see the paragraph above."
    b2, a2, c2 = (x.replace("NOTE: see above.", note) for x in (OL.BASE, OL.LEG_A, OL.LEG_C))
    res = P.stock_merge(b2, a2, c2, "doc.md")
    r = one(inst1(b2, res["merged"], legs=[a2, c2], f2=res["clean"], mode="M"), "Q", index=2)
    check("... and through evaluate(), with the NOTE lengthened past 20 characters",
          r and r.get("oracle") == "UNDECIDABLE-REPEAT" and r["decided"] is False,
          r and r.get("oracle", r.get("skip")))
    r = one(inst1(OL.BASE, res["merged"]), "Q", index=2)
    check("the original 16-character NOTE is skipped as short, never graded",
          r and r.get("skip") == "short_quote")
    para = "The deploy job waits for the canary to report healthy,\nthen promotes the build to every region."
    before = d("# Runbook", "## Staging", "Staging is refreshed from production nightly.", para,
               "Staging alerts page the on-call engineer.", "## Production",
               "Production changes need a second reviewer.", para,
               "Production alerts page the incident commander.")
    after = before.replace(
        "Staging is refreshed from production nightly.\n\n" + para,
        "Staging is refreshed from production nightly.\n\n"
        + para.replace("every region", "the staging region"))
    r = one(inst1(before, after), "Q", index=3)
    check("two identical multi-line paragraphs, one edited: decided",
          r and r["oracle"] == "SURVIVED" and r["decided"], r and r["oracle"])
    check("... and WRONG under the hardened policy",
          r and r["hard"]["cls"] == "WRONG", r and r["hard"])
    # The anchored block's neighbours are twins in B, so no context pair
    # counts and ctx(t) is 0; T is non-empty only because the base wording
    # of k survives verbatim at the end (a twin of k, not of t).
    note = "NOTE: this applies to every cluster in the fleet."
    P3 = "Drain the node before patching.\nWait for pods to reschedule.\nThen patch and reboot."
    before = d("# Patching", note, P3, note, "Done.")
    after = d("# Patching", note, P3.replace("Drain the node", "Cordon and drain the node"), note,
              "Done.", P3)
    r = one(inst1(before, after), "Q", index=2)
    check("an edited block whose old wording survives verbatim elsewhere, with twinned "
          "neighbours: UNDECIDABLE-REPEAT (T holds a twin of k, not of t)",
          r and r["target"] == 2 and r["oracle"] == "UNDECIDABLE-REPEAT", r and (r["target"], r["oracle"]))
    check("empty input: no record, nothing decided", recs_of(inst1("", "")) == [])


def t_known(a):
    section("REPEAT and SPLIT leave known cases alone")
    P = Mx.P
    for name in ("wrong-01", "single-leg-01", "clean-01"):
        case, exp = P.load_plant(os.path.join(P.PLANT_DIR, name))
        res = P.stock_merge(case["base"], case["a"], case["c"])
        r = one(inst1(case["base"], res["merged"], legs=[case["a"], case["c"]],
                      f2=res["clean"], mode="M"), "Q", index=exp["anchor_block"])
        got = (r["oracle"], r["naive"]["cls"], r["hard"]["cls"])
        check(f"{name} stays decided with its committed verdicts",
              r["decided"] and r["oracle"] == "SURVIVED"
              and got[1:] == (exp["expect_naive"], exp["expect_hard"]), got)


def t_wf(a):
    section("F3: every input state and the result are well-formed")
    good = d("# T", "First paragraph of the file.", "Second paragraph of the file.")
    bad = good + "```\nunclosed fence\n"
    r = one(inst1(good, good.replace("First", "1st")), "Q", index=1)
    check("well-formed before and after: wf", r["wf"] is True)
    r = one(inst1(bad, good), "Q", index=1)
    check("an ill-formed before-state: not wf", r["wf"] is False)
    r = one(inst1(good, bad), "Q", index=1)
    check("an ill-formed after-state: not wf", r["wf"] is False)
    r = one(inst1(good, good, legs=[bad, good], mode="M"), "Q", index=1)
    check("an ill-formed leg A: not wf", r["wf"] is False)
    r = one(inst1(good, good, legs=[good, bad], mode="M"), "Q", index=1)
    check("an ill-formed leg C: not wf", r["wf"] is False)
    r = one(inst1(good, "A single block after the edit, long enough.\n"), "Q", index=1)
    check("an after-state of one block: not wf (blocks() must find 2)", r["wf"] is False)


def t_split(a):
    section("SPLIT (§5.2)")
    before = d("# Guide", "Install the agent on every node.\nIt registers itself with the controller.\n"
               "Registration takes about a minute.\nThe node then appears in the dashboard.",
               "Uninstalling removes the agent and its state.")
    after = d("# Guide", "Install the agent on every node.\nIt registers itself with the controller.",
              "Registration takes about a minute.\nThe node then appears in the dashboard.",
              "Uninstalling removes the agent and its state.")
    r = one(inst1(before, after), "Q", index=1)
    check("a paragraph split in two comes out UNDECIDABLE-SPLIT",
          r and r["oracle"] == "UNDECIDABLE-SPLIT" and not r["decided"], r and r["oracle"])
    r2 = one(inst1(before, before.replace("every node", "each node")), "Q", index=1)
    check("the same paragraph edited in place stays decided",
          r2 and r2["oracle"] == "SURVIVED" and r2["decided"], r2 and r2["oracle"])


def t_r_units(a):
    section("R units: REPEAT and SPLIT over §5.2's R units")
    sec = "## Setup\n\nRun the installer, then reboot the host before continuing."
    before = d("# Manual", "Read this first, all of it.", sec, "## Usage", "Start the service with the CLI.")
    after = d("# Manual", "Read this first, all of it.", sec, sec, "## Usage", "Start the service with the CLI.")
    r = one(inst1(before, after), "R", name="setup")
    check("R slug REPEAT: a section copied directly after itself is UNDECIDABLE-REPEAT",
          r and r["oracle"] == "UNDECIDABLE-REPEAT", r and r["oracle"])
    check("... and its name, now duplicated, gives #REF!", r and r["hard"]["status"] == "#REF!")
    reg = "<!-- #retry-policy -->\n\nJobs are retried three times with backoff."
    before = d("# Jobs", "Jobs run on the shared pool.", reg, "Logs are kept for a week.")
    after = d("# Jobs", "Jobs run on the shared pool.", reg,
              "Jobs are retried three times with backoff.", "Logs are kept for a week.")
    r = one(inst1(before, after), "R", name="retry-policy")
    check("R region REPEAT: the region's block copied directly after itself is UNDECIDABLE-REPEAT",
          r and r["oracle"] == "UNDECIDABLE-REPEAT", r and r["oracle"])
    after = d("# Jobs", "Jobs are retried three times with backoff.", "Jobs run on the shared pool.",
              reg, "Logs are kept for a week.")
    r = one(inst1(before, after), "R", name="retry-policy")
    check("... and a copy elsewhere, where context tells them apart, stays decided",
          r and r["oracle"] == "SURVIVED" and r["decided"], r and r["oracle"])
    before = d("# Ops", "## Install", "Step one: fetch the package.\nStep two: verify its signature.",
               "## End", "That is all.")
    after = d("# Ops", "## Install", "Step one: fetch the package.", "## Verify",
              "Step two: verify its signature.", "## End", "That is all.")
    r = one(inst1(before, after), "R", name="install")
    check("R slug SPLIT: a section whose lines now fall under two headings is UNDECIDABLE-SPLIT",
          r and r["oracle"] == "UNDECIDABLE-SPLIT", r and r["oracle"])
    r2 = one(inst1(before, before.replace("fetch", "download")), "R", name="install")
    check("... and the same section edited in place stays decided",
          r2 and r2["decided"] and r2["hard"]["cls"] == "correct", r2 and (r2["oracle"], r2["hard"]))


def t_r(a):
    section("R: the resolver")
    # The Alpha body has three lines, so the vote over the section's lines
    # follows the body rather than the heading line. With a one-line body,
    # difflib aligns "## Alpha" onto the renamed heading and TLLC itself
    # follows the name, so the case would not be a mis-resolution at all.
    body = "Alpha owns the billing service.\nIt also runs the invoicing jobs.\nAnd it pages on payment failures."
    before = d("# Handbook", "## Alpha", body, "## Beta", "Beta owns the search service.")
    after = d("# Handbook", "## Overview", body, "## Alpha", "Beta owns the search service.")
    r = one(inst1(before, after), "R", name="alpha")
    check("a heading renamed onto another section's name: decided",
          r and r["decided"] and r["oracle"] == "SURVIVED", r and r["oracle"])
    check("... and WRONG", r and r["hard"]["cls"] == "WRONG", r and r["hard"])
    gone = before.replace("## Beta", "## Gamma")
    bm = Mx.D8.blocks(gone)
    check("a name that disappears gives #REF!", Mx.resolve_r(gone, bm, "beta") == Mx.REF)
    r = one(inst1(before, gone), "R", name="beta")
    check("... and is LOUD, not WRONG", r and r["hard"]["cls"] in ("LOUD", "correct"), r and r["hard"])
    dup = before + "\n## Beta\n\nA second Beta section.\n"
    check("a duplicated name gives #REF!", Mx.resolve_r(dup, Mx.D8.blocks(dup), "beta") == Mx.REF)
    fenced = d("# Notes", "```sh\n# install the tools\nmake tools\n```", "## Real heading", "Body.")
    names = Mx.r_names(fenced, Mx.D8.blocks(fenced))
    check("a `#` line inside a code fence is not a name",
          "install-the-tools" not in names and "real-heading" in names, names)
    nest = d("# Top", "## Alpha", "Alpha text here.", "### Detail", "Detail text here.", "## Beta", "Beta text.")
    nb = Mx.D8.blocks(nest)
    check("a section runs to the next heading of the same or a higher level, subsections included",
          Mx.resolve_r(nest, nb, "alpha") == ("slug", 1, 4) and Mx.resolve_r(nest, nb, "detail") == ("slug", 3, 4)
          and Mx.resolve_r(nest, nb, "top") == ("slug", 0, 6),
          [Mx.resolve_r(nest, nb, x) for x in ("top", "alpha", "detail")])
    regdup = d("<!-- #x -->", "one", "<!-- #x -->", "two")
    check("a region declared twice gives #REF!",
          Mx.resolve_r(regdup, Mx.D8.blocks(regdup), "x") == Mx.REF)
    both = d("<!-- #alpha -->", "Region text.", "## Alpha", "Slug text.")
    res = Mx.resolve_r(both, Mx.D8.blocks(both), "alpha")
    check("region markers are tried before slugs", res != Mx.REF and res[0] == "region", res)
    check("empty input: no name, #REF!", Mx.r_names("", []) == [] and Mx.resolve_r("", [], "a") == Mx.REF)


def t_plants(a, tmp):
    section("Plants: harness/prereg2_plants.py")
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run([sys.executable, "-I", "-B", os.path.join(HERE, "prereg2_plants.py"),
                        "--d8-dir", a.d8_dir], capture_output=True, text=True, env=env)
    check("prereg2_plants.py prints PLANTS: PASS and exits 0",
          r.returncode == 0 and "PLANTS: PASS" in r.stdout, r.stdout.strip().splitlines()[-1:])
    mdir = os.path.join(tmp, "plants-mut")
    os.makedirs(mdir)
    for f in ("prereg2_plants.py", "prose_merge.py"):
        shutil.copy(os.path.join(HERE, f), mdir)
    src = open(os.path.join(mdir, "prereg2_plants.py")).read()
    old = '"P-C": (d(H, N, W, E, N), d(H, E, N, W2, N), 4, 2, 4),'
    new = '"P-C": (d(H, N, W, E, N), d(H, N, W2, E, N), 4, 2, 4),'
    mutated = src.replace(old, new)
    check("the P-C mutation (§7.3: base with only the window sentence edited) applies",
          mutated != src)
    open(os.path.join(mdir, "prereg2_plants.py"), "w").write(mutated)
    r = subprocess.run([sys.executable, "-I", "-B", os.path.join(mdir, "prereg2_plants.py"),
                        "--d8-dir", a.d8_dir], capture_output=True, text=True, env=env)
    check("... and prereg2_plants.py goes red on it",
          r.returncode != 0 and "PLANTS: FAIL" in r.stdout, r.stdout.strip().splitlines()[-1:])
    from p2 import export as X
    import prereg2_plants as PP
    pr = X.plant_records()
    for n, (base, after, k, t, h) in PP.PLANTS.items():
        rr = pr[n][0]
        check(f"{n}: the harness's own records agree with Appendix B (TLLC {t}, hardened {h})",
              rr["target"] == t and rr["hard"]["hit"] == h and rr["decided"])


def single_leg_repo(root, s_form=False):
    P = Mx.P
    case, _ = P.load_plant(os.path.join(P.PLANT_DIR, "single-leg-01"))
    if not s_form:
        commits = [("base", {"doc.md": case["base"]}), ("edit", {"doc.md": case["a"]})]
    else:
        commits = [("base", {"doc.md": case["base"]})]
        for i in range(5):
            commits.append((f"c{i + 1}", {"doc.md": case["a"] if i % 2 == 0 else case["base"]}))
    return fixture_repo(root, commits)


def score(tmp, name, repo, pin, modes, arm="fixture", arm0=True, sample=None):
    out = os.path.join(tmp, name)
    tdir = os.path.join(tmp, name + "-transcripts")
    a0 = os.path.join(out, "arm0")
    args = ["--d8-dir", ARGS.d8_dir, "--arm", arm, "--fixture-repo", repo, "--fixture-pin", pin,
            "--fixture-pathspec", "*.md", "--transcript-dir", tdir]
    if arm0:
        rc0, o0 = cli("arm0", *args, "--out-dir", a0)
    extra = ["--sample-e", str(sample), "--sample-s", str(sample)] if sample else []
    rc, o = cli("score", *args, "--modes", modes, "--arm0-dir", a0, "--out-dir",
                os.path.join(out, "score"), *extra)
    return rc, o, os.path.join(out, "score", arm), tdir


def units(sdir):
    return [json.loads(x) for x in gzip.open(os.path.join(sdir, "units.jsonl.gz"), "rt", encoding="utf-8")]


STRIP = ("arm", "mode", "instance", "id")


def t_enumerators(a, tmp):
    section("E and S enumerators, and the scoring CLI")
    repo, pin = os.path.join(tmp, "sl-e"), None
    pin, _ = single_leg_repo(repo)
    rc, out, sdir, tdir = score(tmp, "e", repo, pin, "E")
    rs = [r for r in units(sdir) if r["mech"] == "Q" and r.get("index") == 1] if rc == 0 else []
    check("E: a repository holding single-leg-01 as one commit scores (exit 0)", rc == 0, f"exit {rc}")
    check("E: ... and yields that record: anchored block 1, decided, hardened WRONG",
          len(rs) == 1 and rs[0]["decided"] and rs[0]["hard"]["cls"] == "WRONG"
          and rs[0]["naive"]["cls"] == "WRONG", rs and rs[0].get("hard"))
    want = open(os.path.join(FIX, "single-leg-01.E.record.json"), encoding="utf-8").read().rstrip("\n")
    from p2 import evaluate as E
    check("E: ... byte-identical to the committed record p2/fixtures/single-leg-01.E.record.json",
          rs and E.dumps(rs[0]) == want)
    check("E: every invocation wrote a transcript", tdir and len(os.listdir(tdir)) == 2,
          tdir and sorted(os.listdir(tdir)))
    srepo = os.path.join(tmp, "sl-s")
    spin, _ = single_leg_repo(srepo, s_form=True)
    rc, out, sdir, _ = score(tmp, "s", srepo, spin, "S5")
    rs = [r for r in units(sdir) if r["mech"] == "Q" and r.get("index") == 1] if rc == 0 else []
    strip = lambda r: {k: v for k, v in r.items() if k not in STRIP}  # noqa: E731
    wantd = json.loads(want)
    check("S5: a history base, a, base, a, base, a yields the pair (cs[0], cs[5]) and that record",
          rc == 0 and len(rs) == 1 and strip(rs[0]) == strip(wantd),
          rs and rs[0]["instance"])
    # empty inputs
    empty = os.path.join(tmp, "empty-repo")
    os.makedirs(empty)
    subprocess.run(["git", "init", "-q", empty], check=True)
    rc, out = cli("score", "--d8-dir", a.d8_dir, "--arm", "fixture", "--fixture-repo", empty,
                  "--fixture-pin", "0" * 40, "--fixture-pathspec", "*.md", "--transcript-dir",
                  os.path.join(tmp, "empty-t"), "--arm0-dir", os.path.join(tmp, "nowhere"),
                  "--out-dir", os.path.join(tmp, "empty-out"))
    check("an empty repository exits non-zero (score)", rc != 0, f"exit {rc}")
    rc, out = cli("arm0", "--d8-dir", a.d8_dir, "--arm", "fixture", "--fixture-repo", empty,
                  "--fixture-pin", "0" * 40, "--fixture-pathspec", "*.md", "--transcript-dir",
                  os.path.join(tmp, "empty-t"), "--out-dir", os.path.join(tmp, "empty-a0"))
    check("an empty repository exits non-zero (arm0)", rc != 0, f"exit {rc}")
    check("... and the aborted runs still wrote transcripts with their exit status",
          all("exit status" in open(os.path.join(tmp, "empty-t", f)).read()
              for f in os.listdir(os.path.join(tmp, "empty-t"))) and len(os.listdir(os.path.join(tmp, "empty-t"))) == 2)
    nomd = os.path.join(tmp, "nomd")
    npin, _ = fixture_repo(nomd, [("t", {"a.txt": "x\n"})])
    rc, out, _, _ = score(tmp, "nomd", nomd, npin, "E")
    check("a repository with no selected .md exits non-zero", rc != 0, f"exit {rc}")
    from p2 import corpus as K
    pop, counts, _ = K.enumerate_e("fixture", repo, pin, ["doc.md"])
    check("E population: the edit is in it, the add is excluded and counted",
          len(pop) == 1 and counts["excluded:add"] == 1, counts)
    cyc = os.path.join(tmp, "cycle")
    texts = [d("# C", f"Version {i} of a paragraph that changes each time.") for i in range(5)]
    fixture_repo(cyc, [(f"c{i}", {"doc.md": texts[i % 5]}) for i in range(6)])
    pops, sc, _ = K.enumerate_s("fixture", cyc, ["doc.md"])
    check("S population: a pair whose two blobs are equal is excluded and counted",
          pops[5] == [] and sc["gap5:excluded:blobs_equal"] == 1 and sc["gap5:pairs"] == 1, sc)
    pops, sc, _ = K.enumerate_s("fixture", srepo, ["doc.md"])
    check("S population: the pair whose blobs differ is in it", len(pops[5]) == 1, sc)


def merge_repo(root, plant):
    """A real two-parent merge of a plant's legs: base on main, leg A on a
    branch, leg C on main, merged with stock git."""
    P = Mx.P
    case, exp = P.load_plant(os.path.join(P.PLANT_DIR, plant))
    head, g = fixture_repo(root, [("base", {"doc.md": case["base"]})])
    g("checkout", "-q", "-b", "leg-a")
    open(os.path.join(root, "doc.md"), "w").write(case["a"])
    g("commit", "-q", "-am", "leg a")
    g("checkout", "-q", "main")
    open(os.path.join(root, "doc.md"), "w").write(case["c"])
    g("commit", "-q", "-am", "leg c")
    g("merge", "-q", "--no-edit", "leg-a")
    return g("rev-parse", "HEAD"), exp


def t_m_arm(a, tmp):
    section("M: the scoring CLI on a real merge")
    repo = os.path.join(tmp, "m-w")
    pin, exp = merge_repo(repo, "wrong-01")
    rc, out, sdir, _ = score(tmp, "m", repo, pin, "M")
    rs = [r for r in units(sdir) if r["mech"] == "Q" and r.get("index") == 1] if rc == 0 else []
    check("M: a repository holding wrong-01 as a real merge scores (exit 0)", rc == 0, f"exit {rc}")
    check("M: ... and yields its record: decided, WRONG under both policies, F2 clean",
          len(rs) == 1 and rs[0]["decided"] and rs[0]["f2"]
          and (rs[0]["naive"]["cls"], rs[0]["hard"]["cls"]) == (exp["expect_naive"], exp["expect_hard"]),
          rs and (rs[0]["instance"], rs[0]["hard"]["cls"]))
    if rs:
        common = ["--d8-dir", a.d8_dir, "--arm", "fixture", "--fixture-repo", repo, "--fixture-pin", pin,
                  "--fixture-pathspec", "*.md", "--transcript-dir", os.path.join(tmp, "m-t")]
        rc, out = cli("repro", *common, "--id", rs[0]["id"], "--score-dir", os.path.dirname(sdir),
                      "--repro-dir", os.path.join(tmp, "m-r"))
        check("M: repro regenerates it byte for byte", rc == 0 and "BYTE-IDENTICAL" in out,
              out.strip().splitlines()[-1:])
    repo = os.path.join(tmp, "m-c")
    pin, exp = merge_repo(repo, "clean-01")
    rc, out, sdir, _ = score(tmp, "mc", repo, pin, "M")
    check("M: clean-01 as a real merge is stopped by Arm 0: its verbatim appendix twins "
          "the anchored paragraph", rc == 3, f"exit {rc}")
    section("Export CLI on scored fixtures")
    from p2 import export as X
    mp = os.path.join(tmp, "x-manifest.json")
    sha = X.seal(mp)
    sc = os.path.join(tmp, "x-scores")
    shutil.copytree(os.path.join(tmp, "m", "score"), sc)
    st = json.load(open(os.path.join(sc, "fixture", "status.json")))
    out_dir = os.path.join(tmp, "x-export")
    rc, out = cli("export", "--d8-dir", a.d8_dir, "--manifest", mp, "--manifest-sha", sha,
                  "--score-dir", sc, "--out", out_dir, "--transcript-dir", os.path.join(tmp, "x-t"),
                  "--fixture-ok", "--unbound")
    names = sorted(os.listdir(os.path.join(out_dir, "packets"))) if rc == 0 else []
    check("export: wrong-01's merge record plus the three plants make four packets",
          rc == 0 and len(names) == 4, f"exit {rc}, {len(names)} packets; status bound={st.get('bound')}")
    roles = [sorted(json.load(open(os.path.join(out_dir, "packets", n, "packet.json")))["files"])
             for n in names]
    check("export: the merge packet carries base, both legs and the after-file",
          ["after", "base", "leg_a", "leg_c"] in roles, roles)
    check("export: it passes its validator", X.validate(out_dir) == [])
    check("export: the invocation wrote a transcript", len(os.listdir(os.path.join(tmp, "x-t"))) == 1)
    rc, out = cli("export", "--d8-dir", a.d8_dir, "--manifest", mp, "--manifest-sha", sha,
                  "--score-dir", sc, "--out", out_dir, "--transcript-dir", os.path.join(tmp, "x-t"),
                  "--fixture-ok", "--unbound")
    check("export: a second export over the first is refused", rc != 0, f"exit {rc}")


def t_bundles(a, tmp):
    section("Corpora as bundles (§6.2)")
    from p2 import corpus as K
    b = K.bundles()
    check("every arm's bundle has a committed sha256, and its recorded head is the arm's pin",
          all(K.ARMS[x]["bundle"] in b and b[K.ARMS[x]["bundle"]]["head"] == K.ARMS[x]["pin"]
              and len(b[K.ARMS[x]["bundle"]]["sha256"]) == 64 for x in K.ARMS))
    check("the seven arms and their pins are §6.2's",
          [(x, K.ARMS[x]["pin"][:12], K.ARMS[x]["pathspec"]) for x in K.ARMS] == [
              ("rust-book", "1500248d8f23", "src/*.md"), ("obsidian-help", "327a782e9048", "en/*.md"),
              ("cmspec", "3da939428d80", "*.md"), ("k8s-en", "6b27baef1e44", "content/en/*.md"),
              ("k8s-l10n", "6b27baef1e44", "content/*.md :(exclude)content/en/"),
              ("cncf-toc", "144c2e321588", "*.md :(exclude).github/"),
              ("site-policy", "b9578b546d25", "*.md :(exclude).github/")])
    st = b["_storage"]
    check("bundle storage is recorded: the release tag and the durable local copy, which is "
          "the harness's default bundle directory",
          "prereg2-bundles-v1" in st["release"] and "internal" not in json.dumps(b)
          and (os.environ.get("PREREG2_BUNDLE_DIR") or K.DEFAULT_BUNDLE_DIR).rstrip("/")
          == (os.environ.get("PREREG2_BUNDLE_DIR") or st["local_copy"]).rstrip("/")
          and "scratch" not in K.DEFAULT_BUNDLE_DIR, K.DEFAULT_BUNDLE_DIR)
    src = os.path.join(tmp, "b-src")
    pin, g = fixture_repo(src, [("one", {"a.md": "# A\n\nText of the first commit.\n"}),
                                ("two", {"a.md": "# A\n\nText of the second commit.\n"})])
    bdir = os.path.join(tmp, "b-bundles")
    os.makedirs(bdir)
    g("bundle", "create", "-q", os.path.join(bdir, "fx.bundle"), "HEAD")
    bsha = K.sha256_file(os.path.join(bdir, "fx.bundle"))
    table = {"fx": {"bundle": "fx", "pin": pin, "pathspec": "*.md", "prefix": "",
                    "bundle_meta": {"sha256": bsha}}}
    repo = K.open_corpus("fx", bdir, os.path.join(tmp, "b-w1"), table)
    head = subprocess.run(["git", "-C", repo, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    check("a corpus is fetched fresh from its bundle and checked out at the pin", head == pin)
    first = g("rev-parse", "HEAD~1")
    t2 = {"fx": dict(table["fx"], pin=first)}
    repo = K.open_corpus("fx", bdir, os.path.join(tmp, "b-w2"), t2)
    check("an earlier pin in the bundle's history is reachable",
          subprocess.run(["git", "-C", repo, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip() == first)
    try:
        K.open_corpus("fx", bdir, os.path.join(tmp, "b-w3"), {"fx": dict(table["fx"], pin="1" * 40)})
        nv = None
    except K.NoVerdict as e:
        nv = str(e)
    check("a pin absent from its bundle is NO VERDICT", nv and "absent" in nv, nv)
    try:
        K.open_corpus("fx", bdir, os.path.join(tmp, "b-w4"),
                      {"fx": dict(table["fx"], bundle_meta={"sha256": "0" * 64})})
        refused = False
    except RuntimeError:
        refused = True
    check("a bundle whose sha256 is not the committed one is refused", refused)
    try:
        K.open_corpus("fx", bdir, os.path.join(tmp, "b-w1"), table)
        refused = False
    except RuntimeError:
        refused = True
    check("an existing work repository is never reused", refused)
    try:
        K.open_corpus("fx", os.path.join(tmp, "nowhere"), os.path.join(tmp, "b-w5"), table)
        refused = False
    except FileNotFoundError:
        refused = True
    check("a missing bundle is refused", refused)


def undecodable_repo(root):
    """doc.md: leg A writes a Latin-1 byte into it, leg C edits another
    paragraph, and stock git merges the two cleanly. ok.md: both legs edit
    valid UTF-8 on both sides."""
    para = ["# Doc", "Cafe opens at nine every weekday morning.", "The terrace closes in winter months.",
            "Orders over twenty units need a deposit."]
    ok = ["# Ok", "The first shared paragraph of the okay file.", "The second shared paragraph here.",
          "The third shared paragraph of the okay file."]
    env = dict(os.environ, **GIT_ENV)

    def g(*a):
        return subprocess.run(["git", "-C", root, *a], check=True, capture_output=True, env=env).stdout.decode().strip()

    def w(name, blocks, raw=None):
        with open(os.path.join(root, name), "wb") as f:
            f.write(raw if raw is not None else ("\n\n".join(blocks) + "\n").encode())
    os.makedirs(root)
    g("init", "-q", "-b", "main")
    w("doc.md", para)
    w("ok.md", ok)
    g("add", "-A")
    g("commit", "-q", "-m", "base")
    g("checkout", "-q", "-b", "leg-a")
    latin = ("\n\n".join(para) + "\n").replace("Cafe", "Caf\u00e9").encode("latin-1")
    w("doc.md", None, raw=latin)
    w("ok.md", [ok[0], ok[1].replace("first", "1st"), ok[2], ok[3]])
    g("commit", "-q", "-am", "leg a")
    g("checkout", "-q", "main")
    w("doc.md", [para[0], para[1], para[2], para[3].replace("twenty", "fifty")])
    w("ok.md", [ok[0], ok[1], ok[2], ok[3].replace("third", "3rd")])
    g("commit", "-q", "-am", "leg c")
    g("merge", "-q", "--no-edit", "leg-a")
    return g("rev-parse", "HEAD"), g("rev-parse", "leg-a")


def t_undecodable(a, tmp):
    section("Non-UTF-8 blobs: excluded and counted as undecodable (LOG §15)")
    P = Mx.P
    repo = os.path.join(tmp, "u-repo")
    pin, leg_a = undecodable_repo(repo)
    try:
        P.find_merge_cases(repo, "")
        crashed = False
    except UnicodeDecodeError:
        crashed = True
    check("the supplied find_merge_cases(), reading strictly, raises on such a merge "
          "(the defect the rule exists for)", crashed)
    for mode in ("M", "E"):
        rc, out, sdir, tdir = score(tmp, f"u-{mode}", repo, pin, mode)
        st = json.load(open(os.path.join(sdir, "status.json"))) if os.path.isdir(sdir) else {}
        c = st.get("counts", {}).get(mode, {})
        check(f"{mode}: the arm does not crash (exit 0)", rc == 0, f"exit {rc}")
        check(f"{mode}: the case with the non-UTF-8 blob is excluded and counted undecodable",
              c.get("undecodable") == 1, c.get("undecodable"))
        ev = [json.loads(x) for x in open(os.path.join(sdir, "instances.jsonl"))] if rc == 0 else []
        bad = (lambda i: i["path"] == "doc.md") if mode == "M" else \
            (lambda i: i["id"] == f"E:{leg_a}:doc.md")
        check(f"{mode}: valid cases are still evaluated, the undecodable one is not",
              any(i["path"] == "ok.md" for i in ev) and not any(bad(i) for i in ev),
              [i["id"] for i in ev])
        tr = "".join(open(os.path.join(tdir, f)).read() for f in os.listdir(tdir) if "score" in f)
        check(f"{mode}: the arm's output and transcript report it", "undecodable 1" in out and "undecodable 1" in tr)


def t_repro(a, tmp):
    section("Reproduction script (F9)")
    repo = os.path.join(tmp, "sl-r")
    pin, _ = single_leg_repo(repo)
    rc, out, sdir, _ = score(tmp, "r", repo, pin, "E")
    want = json.loads(open(os.path.join(FIX, "single-leg-01.E.record.json")).read())
    common = ["--d8-dir", a.d8_dir, "--arm", "fixture", "--fixture-repo", repo, "--fixture-pin", pin,
              "--fixture-pathspec", "*.md", "--transcript-dir", os.path.join(tmp, "r-t")]
    rc, out = cli("repro", *common, "--id", want["id"], "--score-dir", os.path.dirname(sdir),
                  "--repro-dir", os.path.join(tmp, "r-out"))
    check("repro regenerates single-leg-01's record byte for byte",
          rc == 0 and "BYTE-IDENTICAL" in out, out.strip().splitlines()[-1:])
    # red: the committed record altered by one byte
    p = os.path.join(sdir, "units.jsonl.gz")
    lines = gzip.open(p, "rt", encoding="utf-8").read().split("\n")
    lines = [ln.replace('"cls":"WRONG"', '"cls":"correct"', 1) if want["id"] in ln else ln for ln in lines]
    with gzip.open(p, "wt", encoding="utf-8") as f:
        f.write("\n".join(lines))
    rc, out = cli("repro", *common, "--id", want["id"], "--score-dir", os.path.dirname(sdir),
                  "--repro-dir", os.path.join(tmp, "r-out2"))
    check("... and reports DIFFERS, exit non-zero, against an altered record",
          rc != 0 and "DIFFERS" in out, out.strip().splitlines()[-1:])
    rc, out = cli("repro", *common, "--id", "E:" + "0" * 40 + ":doc.md|Q|1", "--score-dir",
                  os.path.dirname(sdir), "--repro-dir", os.path.join(tmp, "r-out3"))
    check("... and exits non-zero on a record id that is not committed", rc != 0, f"exit {rc}")


def t_mfilter(a, tmp):
    section("M filter and the §6.3 rule")
    from p2 import corpus as K
    C = Mx.C
    gen_fence = "---\ntitle: x\nauto_generated: true\n---\n\n# Gen\n\nGenerated body text here.\n"
    gen_comment = ("---\ntitle: y\n---\n<!--\nauto_generated: true\n-->\n\n# Translated\n\n"
                   "Translated body text here.\n")
    check("a generated key in the file's own fence excludes it (yaml-fence)",
          C.is_generated(gen_fence, "yaml-fence"))
    check("the same key inside an HTML comment does not (yaml-fence)",
          not C.is_generated(gen_comment, "yaml-fence"))
    check("... where the `anywhere` rule would exclude it", C.is_generated(gen_comment, "anywhere"))
    base = "# Doc\n\nFirst paragraph of the shared document.\n\nSecond paragraph.\n"
    repo = os.path.join(tmp, "mrepo")
    pin, g = fixture_repo(repo, [("base", {"gen.md": gen_fence, "tr.md": gen_comment, "doc.md": base,
                                           "skip/x.md": base})])
    sel = K.selection("fixture", repo, "*.md :(exclude)skip/")
    cases = [{"id": f"m:{p}", "path": p, "meta": {"merge": pin}} for p in ("gen.md", "tr.md", "doc.md", "skip/x.md")]
    kept, counts = K.m_filter("fixture", repo, cases, sel)
    rules = {c["path"]: c["rules"] for c in kept}
    check("M filter: the fence-generated file is not in the verdict selection",
          "yaml-fence" not in rules.get("gen.md", []), rules.get("gen.md"))
    check("M filter: the HTML-comment file is", "yaml-fence" in rules.get("tr.md", []), rules.get("tr.md"))
    check("M filter: a path outside the pathspec is dropped and counted",
          "skip/x.md" not in rules and counts["dropped:not_selected"] == 1, counts)
    check("empty input: no case in, none kept", K.m_filter("fixture", repo, [], sel)[0] == [])
    section("site-policy subject rule (§6.2)")
    for subj, want in (("Merge pull request #1 from x/automated-sync", (False, False)),
                       ("repo-sync: update", (False, True)),
                       ("Update the privacy statement", (True, True)),
                       ("Repo-Sync of policies", (True, True)),
                       ("AUTOMATED-SYNC", (True, True))):
        check(f"{subj!r}: strict={want[0]} 25-case={want[1]}", K.site_policy_sets(subj) == want)
    _, g2 = fixture_repo(os.path.join(tmp, "sprepo"), [("a", {"doc.md": base}),
                                                      ("Merge branch automated-sync", {"doc.md": base + "x\n"})])
    head = g2("rev-parse", "HEAD")
    kept, counts = K.m_filter("site-policy", os.path.join(tmp, "sprepo"),
                              [{"id": "m", "path": "doc.md", "meta": {"merge": head}}],
                              {r: ["doc.md"] for r in K.RULES})
    check("m_filter reads the subject with git log -1 --format=%s and drops it from the strict set",
          kept and kept[0]["strict"] is False and counts["strict"] == 0, counts)


def t_sampler(a):
    section("Sampler (§6.3)")
    from p2 import corpus as K
    keys = [f"{i:040x}:docs/p{i % 37}.md" for i in range(5000)]
    s = K.sample("k8s-en", keys, 1000)
    unselected = [k for k in keys if k not in set(s)]
    s2 = K.sample("k8s-en", [k for k in keys if k != unselected[0]], 1000)
    check("removing an item that was not selected leaves the sample byte-identical",
          json.dumps(s) == json.dumps(s2))
    many = set(unselected[:2000])
    s3 = K.sample("k8s-en", [k for k in keys if k not in many], 1000)
    check("... and removing 2,000 unselected items does too", json.dumps(s) == json.dumps(s3))
    s4 = K.sample("k8s-en", [k for k in keys if k != s[0]], 1000)
    check("removing a selected item does change it (the check can fail)", s4 != s)
    check("the rank is sha256('prereg2:' + arm + ':' + key)",
          K.rank("a", "b") == __import__("hashlib").sha256(b"prereg2:a:b").hexdigest())
    check("another arm ranks differently (the salt includes the arm)",
          K.sample("cncf-toc", keys, 1000) != s)
    check("empty input: an empty sample", K.sample("k8s-en", [], 1000) == [])


def syn(arm, mode, mech, unit, decided=True, oracle=None, nl=True, cls="correct", iid=None):
    return {"arm": arm, "mode": mode, "mech": mech, "unit": unit, "id": f"{iid or unit}|{mech}|0",
            "instance": iid or f"i-{unit}", "decided": decided,
            "oracle": oracle or ("SURVIVED" if decided else "UNDECIDABLE-REPEAT"),
            "nl": nl, "f2": True, "wf": True, "hard": {"cls": cls if decided else None},
            "naive": {"cls": cls if decided else None}, "type": "prose"}


def syn_scores(arm, recs, modes=("E",)):
    inst = {(arm, r["instance"]): {"arm": arm, "mode": r["mode"], "id": r["instance"],
                                   "rules": ["yaml-fence", "none", "anywhere"]} for r in recs}
    return {arm: {"modes": list(modes), "instances": inst, "records": recs}}


def manifest_for_test():
    from p2 import export as X
    return {"nonce": "11" * 32,
            "plants": {n: {"key": f"plant:{n}", "expected": X.PLANT_EXPECT[n]} for n in X.PLANT_EXPECT}}


def good_tiers(m):
    from p2 import export as X
    t = {}
    for p, v in m["plants"].items():
        e = v["expected"]
        t[X.packet_name(m["nonce"], v["key"])] = dict(q1=e["q1"], q2=e["q2"], q3=e["q3"], q4=e["q4"],
                                                      unplaceable=False)
    return t


def t_counting(a):
    section("Distinct count, decided rule, floor (§5.2, §6.6)")
    from p2 import aggregate as AG
    st = AG.distinct_status([syn("k8s-en", "E", "Q", "u1"), syn("k8s-en", "E", "Q", "u1", iid="other")])
    check("a duplicate is counted once", len(st) == 1, st)
    st = AG.distinct_status([syn("k8s-en", "E", "Q", "u2", decided=False, iid="a"),
                             syn("k8s-en", "E", "Q", "u2", decided=True, iid="b")])
    check("one decided instance plus one undecidable instance counts as decided",
          st == {("k8s-en", "Q", "", "u2"): "decided"}, st)
    st = AG.distinct_status([syn("k8s-en", "E", "Q", "u3", decided=False, iid="a"),
                             syn("k8s-en", "E", "Q", "u3", decided=False, oracle="UNKNOWN", iid="b")])
    check("undecidable plus UNKNOWN, none decided, is undecidable", list(st.values()) == ["undecidable"])
    st = AG.distinct_status([syn("k8s-en", "E", "Q", "u4", decided=False, oracle="UNKNOWN")])
    check("every instance UNKNOWN is UNKNOWN", list(st.values()) == ["UNKNOWN"])
    check("floor: 299 gives NO VERDICT", AG.floor_verdict(299, 0, True)[0] == "NO VERDICT")
    check("floor: 300 gives NOT FOUND", AG.floor_verdict(300, 0, True)[0] == "NOT FOUND")
    check("floor: undecidable over 10% gives NO VERDICT", AG.floor_verdict(300, 34, True)[0] == "NO VERDICT")
    check("floor: undecidable at 10% passes", AG.floor_verdict(300, 33, True)[0] == "NOT FOUND")
    m = manifest_for_test()
    arm0 = {arm: {"passes_bar": True} for arm in ("k8s-en",)}
    for n, want in ((299, "NO VERDICT"), (300, "NOT FOUND")):
        recs = [syn("k8s-en", "E", "Q", f"u{i}") for i in range(n)]
        res = AG.aggregate(arm0, syn_scores("k8s-en", recs), m, good_tiers(m), {})
        c = res["cells"][("k8s-en", "E", "Q")]
        check(f"aggregate: {n} distinct decided units gives {want}", c["verdict"] == want, c)
    recs = [syn("k8s-en", "E", "Q", f"u{i}") for i in range(300)] + \
           [syn("k8s-en", "E", "Q", "u0", iid=f"dup{i}") for i in range(50)]
    res = AG.aggregate(arm0, syn_scores("k8s-en", recs), m, good_tiers(m), {})
    check("aggregate: 300 units over 350 instances counts 300",
          res["cells"][("k8s-en", "E", "Q")]["distinct"]["decided"] == 300)
    c = res["cells"][("k8s-en", "E", "R")]
    check("an empty cell gives NO VERDICT, never zero", c["verdict"] == "NO VERDICT"
          and "0" not in c["verdict"], c)
    c = res["cells"][("cncf-toc", "E", "Q")]
    check("an arm with no Arm 0 result gives NO VERDICT", c["verdict"] == "NO VERDICT", c)


def t_arm0(a, tmp):
    section("Arm 0 bar (§6.5)")
    from p2 import arm0 as A0
    twin = "This shortcode note repeats in the file verbatim."
    texts = {"a.md": d("# A", twin, "Unique paragraph number one here.", twin,
                       "Unique paragraph number two here."),
             "b.md": d("# B", "Unique paragraph number three here.", "Unique paragraph number four here.")}
    c = A0.census_texts(texts)
    check("a planted corpus over 10% stops its arm", not c["passes_bar"],
          f"{c['nl_twin_same_file']}/{c['nl_distinct_ge20']}")
    many = {f"f{i}.md": d("# T", f"Paragraph {i} is about something entirely its own.",
                          f"Second paragraph {i}, also its own words.") for i in range(4)}
    many["z.md"] = d("# Z", twin, twin, "One more paragraph of its own words.")
    c = A0.census_texts(many)
    check("exactly 10% twinned passes", c["passes_bar"] and c["nl_twin_same_file"] * 10 == c["nl_distinct_ge20"],
          f"{c['nl_twin_same_file']}/{c['nl_distinct_ge20']}")
    check("blocks under 20 characters are counted as skipped",
          A0.census_texts({"x.md": d("# Hi", "Short one.", "A paragraph long enough to count.")})
          ["by_type"]["prose"]["short_lt20"] == 1)
    check("empty input does not pass", not A0.census_texts({})["passes_bar"])
    repo = os.path.join(tmp, "a0repo")
    pin, _ = fixture_repo(repo, [("t", texts)])
    rc, out, _, _ = score(tmp, "a0", repo, pin, "E", sample=10)
    check("the CLI: the arm reports NO VERDICT (oracle reach) and does not run",
          rc == 3 and "does not run" in out, f"exit {rc}")
    t = os.path.join(tmp, "a0-transcripts")
    a0out = "".join(open(os.path.join(t, f)).read() for f in sorted(os.listdir(t)) if "arm0" in f)
    check("Arm 0 prints the adjacent-run line labelled 'provisional reading (LOG §15)', with its rule",
          "adjacent-run twin, provisional reading (LOG §15), report only: " + A0.ADJACENT_RUN_RULE in a0out)
    j = json.load(open(os.path.join(tmp, "a0", "arm0", "fixture.json")))
    check("... and its JSON carries the label", j["adjacent_run_rule"].startswith("provisional reading (LOG §15): "))
    import ast
    leaks = []
    for f in ("p2/aggregate.py", "p2/tiers.py", "p2/export.py"):
        src = open(os.path.join(HERE, f), encoding="utf-8").read()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = [n.name for n in node.names] + [getattr(node, "module", None) or ""]
                if any("arm0" in (x or "") for x in names):
                    leaks.append(f"{f} imports arm0")
        if "adjacent" in src.lower():
            leaks.append(f"{f} mentions adjacent")
    agg = open(os.path.join(HERE, "prereg2.py"), encoding="utf-8").read()
    body = agg[agg.index("def cmd_aggregate"):agg.index("def main")]
    if "adjacent" in body.lower() or "arm0 as" in body:
        leaks.append("prereg2.py cmd_aggregate reads it")
    check("no aggregate or verdict path imports arm0 or reads the adjacent-run count", not leaks, leaks)


def t_export(a, tmp):
    section("Export, its validator, and the sealed manifest (§7.3)")
    from p2 import export as X
    mp = os.path.join(tmp, "manifest.json")
    sha = X.seal(mp)
    m = X.load_manifest(mp, sha)
    check("seal draws a 32-byte nonce", len(bytes.fromhex(m["nonce"])) == 32)
    try:
        X.seal(mp)
        refused = False
    except X.ExportError:
        refused = True
    check("seal refuses to overwrite a sealed manifest", refused)
    try:
        X.load_manifest(mp, "0" * 64)
        refused = False
    except X.ExportError:
        refused = True
    check("a manifest whose sha256 is not the committed one is refused", refused)
    out = os.path.join(tmp, "export")
    names, keys = X.export(out, m, [], {})
    check("an export of no real record holds the three plants", len(names) == 3, names)
    import hashlib
    check("packet names are sha256(nonce + ':' + key)[:16], computed independently here",
          all(hashlib.sha256(bytes.fromhex(m["nonce"]) + b":" + keys[n].encode()).hexdigest()[:16] == n
              for n in names) and sorted(keys.values()) == ["plant:P-A", "plant:P-B", "plant:P-C"])
    check("a clean export passes the validator", X.validate(out) == [], X.validate(out))
    pj = os.path.join(out, "packets", names[0], "packet.json")
    o = json.load(open(pj))
    json.dump(dict(o, count=3), open(pj, "w"))
    check("the validator rejects a packet that carries a count", X.validate(out) != [], X.validate(out)[:1])
    json.dump(dict(o, total="85 records over 7 arms"), open(pj, "w"))
    check("... and a string field outside the allow-list", any("allow-list" in b for b in X.validate(out)),
          X.validate(out)[:1])
    json.dump(dict(o, mechanism_target=7), open(pj, "w"))
    check("... and a number in an allowed field", any("number" in b for b in X.validate(out)))
    json.dump(o, open(pj, "w"))
    open(os.path.join(out, "packets", names[0], "totals.txt"), "w").write("85\n")
    check("... and a file outside the allow-list", X.validate(out) != [])
    os.remove(os.path.join(out, "packets", names[0], "totals.txt"))
    open(os.path.join(out, "LOG.md"), "w").write("x\n")
    check("... and LOG.md at the export root", X.validate(out) != [])
    os.remove(os.path.join(out, "LOG.md"))
    check("... and passes again once restored", X.validate(out) == [])
    nopk = os.path.join(tmp, "export-nopackets")
    os.makedirs(os.path.join(nopk, "packets"))
    open(os.path.join(nopk, "PROMPT.md"), "w").write(X.prompt_text())
    check("an export with PROMPT.md and no packet fails", X.validate(nopk) == ["no packets"], X.validate(nopk))
    empty = os.path.join(tmp, "export-empty")
    os.makedirs(empty)
    check("empty input: an empty export directory fails", X.validate(empty) != [])
    rc, outp = cli("validate-export", empty, "--transcript-dir", os.path.join(tmp, "ve-t"))
    check("validate-export exits non-zero on it", rc != 0, f"exit {rc}")


STUB = """#!/usr/bin/python3
import json, os, sys
mode = %r
probes = %r
print("stub agent, model", sys.argv[1], "cwd holds", sorted(os.listdir(".")))
for label, path in probes:
    try:
        if os.path.isdir(path):
            os.listdir(path)
        else:
            open(path, "rb").read(1)
        print("PROBE CAN-READ", label)
    except OSError:
        print("PROBE CANNOT-READ", label)
if mode != "silent":
    with open("tiers.jsonl", "w") as f:
        for n in sorted(os.listdir("packets")):
            f.write(json.dumps({"packet": n, "q1": "yes", "q2": "no", "q3": "no", "q4": "no",
                                "unplaceable": False, "why": "stub"}) + "\\n")
"""
CANARY_DIR = os.environ.get("PREREG2_CANARY_DIR", "/home/cam/repos_kindspec")


def t_tier_run(a, tmp):
    section("Tiering-run wrapper (§7.3), with a stub agent")
    from p2 import export as X
    from p2 import tierrun as TRN
    canary = os.path.join(CANARY_DIR, f".prereg2-v3-canary-{os.getpid()}")
    open(canary, "w").write("a file outside the export\n")
    creds = os.path.join(tmp, "fake-credentials.json")
    open(creds, "w").write("{}\n")
    home_claude = os.path.expanduser("~/.claude")
    probes = [("canary under " + CANARY_DIR, canary),
              ("~/.claude/projects", os.path.join(home_claude, "projects")),
              ("~/.claude", home_claude),
              ("the export's PROMPT.md", "PROMPT.md"),
              ("the bound credential file", "/home/tierer/.claude/.credentials.json")]
    stubs = {}
    for mode in ("answers", "silent"):
        stubs[mode] = os.path.join(tmp, f"stub-{mode}.py")
        open(stubs[mode], "w").write(STUB % (mode, probes))
        os.chmod(stubs[mode], 0o755)
    try:
        _t_tier_run(a, tmp, X, TRN, stubs, creds, canary)
    finally:
        os.remove(canary)


def _t_tier_run(a, tmp, X, TRN, stubs, creds, canary):
    mp = os.path.join(tmp, "tr-manifest.json")
    X.seal(mp)
    exp = os.path.join(tmp, "tr-export")
    X.export(exp, X.load_manifest(mp), [], {})
    # red first: the same stub, run without the sandbox, sees the host
    plain = os.path.join(tmp, "tr-plain")
    shutil.copytree(exp, plain)
    r = subprocess.run([stubs["silent"], "m", "p"], cwd=plain, capture_output=True, text=True)
    check("without the sandbox, the stub CAN read the canary under " + CANARY_DIR
          + " and ~/.claude/projects (so the probes can fail)",
          "PROBE CAN-READ canary" in r.stdout and "PROBE CAN-READ ~/.claude/projects" in r.stdout,
          [ln for ln in r.stdout.splitlines() if "PROBE" in ln])
    old_repo = os.path.join(tmp, "tr-old")
    old, _ = fixture_repo(old_repo, [("scoring-arm commit", {"x.md": "x\n"})])
    listing = os.path.join(tmp, "models.json")
    json.dump({"data": [{"id": "claude-opus-5-5", "created_at": "2026-01-01T00:00:00Z"},
                        {"id": "claude-opus-6", "created_at": "2026-09-01T00:00:00Z"}]}, open(listing, "w"))

    def tr(state, *extra, stub="answers", commit=old, repo=old_repo, day="2001-01-02"):
        return cli("tier-run", "--export", exp, "--out", os.path.join(tmp, state, "tiers.jsonl"),
                   "--state-dir", os.path.join(tmp, state), "--repo", repo, "--scoring-commit", commit,
                   "--models-listing", listing, "--listing-day", day, "--agent-cmd", stubs[stub],
                   "--transcript-dir", os.path.join(tmp, state + "-t"), "--credentials", creds,
                   "--unbound", *extra)
    rc, out = tr("s1")
    check("a run more than 14 days after the scoring-arm commit needs a reason", rc == 2 and "late" in out, f"exit {rc}")
    rc, out = tr("s1", "--late-reason", "V3 fixture", day="2001-01-05")
    check("a listing not fetched on the start day is refused", rc == 2 and "start day" in out, f"exit {rc}")
    rc, out = tr("s1", "--late-reason", "V3 fixture")
    lines = open(os.path.join(tmp, "s1", "tiers.jsonl")).read().splitlines() if rc == 0 else []
    check("a run writes tiers.jsonl as the agent wrote it", rc == 0 and len(lines) == 3, f"exit {rc}")
    check("... the agent saw only PROMPT.md and packets/", "cwd holds ['PROMPT.md', 'packets']" in out)
    check("in the sandbox the stub cannot read the canary under " + CANARY_DIR,
          "PROBE CANNOT-READ canary" in out and "PROBE CAN-READ canary" not in out)
    check("... cannot read ~/.claude/projects, nor ~/.claude itself",
          "PROBE CANNOT-READ ~/.claude/projects" in out and "PROBE CANNOT-READ ~/.claude\n" in out + "\n")
    check("... can read the export and the one bound credential file",
          "PROBE CAN-READ the export's PROMPT.md" in out and "PROBE CAN-READ the bound credential file" in out)
    check("... and the transcript records the bwrap invocation", "sandboxed agent: bwrap " in out)
    check("... with the pinned model, since the start day's listing serves it",
          json.load(open(os.path.join(tmp, "s1", "tier-model.json")))["model"] == "claude-opus-5-5")
    check("... and the transcript logs the late reason and Appendix A as sent",
          "LATE RUN" in out and "You are answering questions about records" in out)
    rc, out = tr("s1", "--late-reason", "V3 fixture")
    check("a second run after a first that wrote lines is refused (the first binds)", rc == 2, f"exit {rc}")
    rc, _ = tr("s2", "--late-reason", "V3 fixture", stub="silent")
    rc2, out2 = tr("s2", "--late-reason", "V3 fixture", stub="silent")
    rc3, _ = tr("s2", "--late-reason", "V3 fixture")
    check("one rerun is allowed after a first run that wrote zero lines, and no third",
          rc == 0 and rc2 == 0 and "RERUN" in out2 and rc3 == 2, f"{rc} {rc2} {rc3}")
    fut_repo = os.path.join(tmp, "tr-fut")
    os.makedirs(fut_repo)
    env = dict(os.environ, **dict(GIT_ENV, GIT_COMMITTER_DATE="2099-01-01T00:00:00Z"))
    subprocess.run(["git", "init", "-q", fut_repo], check=True, env=env)
    subprocess.run(["git", "-C", fut_repo, "commit", "-q", "--allow-empty", "-m", "f"], check=True, env=env)
    fut = subprocess.run(["git", "-C", fut_repo, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    rc, out = tr("s3", commit=fut, repo=fut_repo, day="2099-01-02")
    check("a run before the start day is refused", rc == 2 and "tiering starts on" in out, f"exit {rc}")
    json.dump({"data": [{"id": "claude-opus-6", "created_at": "2026-09-01T00:00:00Z"},
                        {"id": "claude-opus-5-1", "created_at": "2026-02-01T00:00:00Z"},
                        {"id": "claude-sonnet-9", "created_at": "2026-10-01T00:00:00Z"}]}, open(listing, "w"))
    import datetime
    c = TRN.choose_model(listing, datetime.date(2001, 1, 2), datetime.date(2001, 1, 2))
    check("unlisted pinned model: the most recent claude-opus-* is chosen", c["model"] == "claude-opus-6", c)
    bad = os.path.join(tmp, "tr-bad-export")
    shutil.copytree(exp, bad)
    open(os.path.join(bad, "notes.txt"), "w").write("85 records\n")
    rc, out = cli("tier-run", "--export", bad, "--out", os.path.join(tmp, "s4", "tiers.jsonl"),
                  "--state-dir", os.path.join(tmp, "s4"), "--repo", old_repo, "--scoring-commit", old,
                  "--models-listing", listing, "--listing-day", "2001-01-02", "--late-reason", "x",
                  "--agent-cmd", stubs["answers"], "--transcript-dir", os.path.join(tmp, "s4-t"),
                  "--credentials", creds, "--unbound")
    check("an export that fails its validator is never sent", rc == 2 and "validator" in out, f"exit {rc}")


def t_void(a):
    section("Void rule (§7.3)")
    from p2 import aggregate as AG
    from p2 import export as X
    from p2 import tiers as T
    m = manifest_for_test()
    pn = {p: X.packet_name(m["nonce"], v["key"]) for p, v in m["plants"].items()}
    good = good_tiers(m)
    check("correct plant answers: not void", T.void_reasons(m, pn, good) == [])
    t = dict(good)
    t[pn["P-C"]] = dict(t[pn["P-C"]], q1="yes")
    check("a plant crossing the B/C line (P-C answered B) voids", T.void_reasons(m, pn, t) != [])
    t = dict(good)
    t[pn["P-B"]] = dict(t[pn["P-B"]], q1="no")
    check("a plant crossing the B/C line (P-B answered C) voids", T.void_reasons(m, pn, t) != [])
    for q in ("q3", "q4"):
        t = dict(good)
        t[pn["P-A"]] = dict(t[pn["P-A"]], **{q: "yes"})
        check(f"a plant whose {q} mismatches voids", T.void_reasons(m, pn, t) != [])
    t = dict(good)
    del t[pn["P-B"]]
    check("an untiered plant voids", T.void_reasons(m, pn, t) != [])
    t = dict(good)
    t[pn["P-A"]] = dict(t[pn["P-A"]], q2="no")
    check("A<->B confusion (P-A answered B) does not void", T.void_reasons(m, pn, t) == [])
    t = dict(good)
    t[pn["P-B"]] = dict(t[pn["P-B"]], q2="yes")
    check("A<->B confusion (P-B answered A) does not void", T.void_reasons(m, pn, t) == [])
    check("tier computation: q2 yes -> A, q1 yes -> B, else C, unplaceable -> UNPLACEABLE",
          [T.tier_of(dict(q1=x, q2=y, unplaceable=False))
           for x, y in (("no", "yes"), ("yes", "yes"), ("yes", "no"), ("no", "no"))]
          == ["A", "A", "B", "C"] and T.tier_of({"unplaceable": True}) == "UNPLACEABLE")
    wr = dict(syn("site-policy", "M", "Q", "w9", cls="WRONG"), reference="q", oracle_target_text="o")
    wr["hard"] = {"cls": "WRONG", "mechanism_target_text": "m", "hit": 3, "status": "EXACT"}
    ins = {"arm": "site-policy", "mode": "M", "id": wr["instance"], "rules": ["yaml-fence"], "strict": True}
    check("export eligibility: a decided hardened WRONG meeting F1-F5 is exported",
          len(X.select_packets([wr], {("site-policy", wr["instance"]): ins})) == 1)
    check("... not if selected only under `none` (F1, §6.3)",
          X.select_packets([wr], {("site-policy", wr["instance"]): dict(ins, rules=["none", "anywhere"])}) == {})
    check("... not a site-policy M case outside the strict set (F1)",
          X.select_packets([wr], {("site-policy", wr["instance"]): dict(ins, strict=False)}) == {})
    check("... not a block of type code (F5)",
          X.select_packets([dict(wr, nl=False, type="code")], {("site-policy", wr["instance"]): ins}) == {})
    check("... not one whose input states are ill-formed (F3)",
          X.select_packets([dict(wr, wf=False)], {("site-policy", wr["instance"]): ins}) == {})
    check("... not an undecidable one", X.select_packets([dict(wr, decided=False)],
                                                         {("site-policy", wr["instance"]): ins}) == {})
    # truncated tiers.jsonl: a real packet untiered makes its cell NO VERDICT
    rec = dict(syn("k8s-en", "E", "Q", "w1", cls="WRONG"), reference="q",
               oracle_target_text="o")
    rec["hard"] = {"cls": "WRONG", "mechanism_target_text": "m", "hit": 3, "status": "EXACT"}
    recs = [rec] + [syn("k8s-en", "E", "Q", f"u{i}") for i in range(400)]
    sc = syn_scores("k8s-en", recs)
    arm0 = {"k8s-en": {"passes_bar": True}}
    res = AG.aggregate(arm0, sc, m, good, {})
    c = res["cells"][("k8s-en", "E", "Q")]
    check("a truncated tiers.jsonl makes the cell of an untiered real packet NO VERDICT",
          c["verdict"] == "NO VERDICT" and "untiered" in c["reason"], c.get("reason"))
    key = X.packet_key(rec)
    t = dict(good)
    t[X.packet_name(m["nonce"], key)] = dict(q1="yes", q2="no", q3="no", q4="no", unplaceable=False)
    res = AG.aggregate(arm0, sc, m, t, {rec["id"]: True})
    check("... and with it tiered B and reproduced, the cell is FOUND",
          res["cells"][("k8s-en", "E", "Q")]["verdict"] == "FOUND" and res["overall"] == "FOUND")
    res = AG.aggregate(arm0, sc, m, t, {rec["id"]: False})
    check("... a record that does not reproduce (F9) is not FOUND",
          res["cells"][("k8s-en", "E", "Q")]["verdict"] != "FOUND")
    try:
        AG.aggregate(arm0, sc, m, t, {})
        refused = False
    except AG.MissingRepro:
        refused = True
    check("... and with no reproduction result the aggregator refuses", refused)
    t2 = dict(t)
    t2[pn["P-C"]] = dict(t2[pn["P-C"]], q2="yes")
    res = AG.aggregate(arm0, sc, m, t2, {rec["id"]: True})
    check("a void tiering makes a cell that exported a packet NO VERDICT",
          res["cells"][("k8s-en", "E", "Q")]["verdict"] == "NO VERDICT")
    check("... and leaves a cell that exported none alone",
          "void" not in res["cells"][("k8s-en", "E", "R")]["reason"], res["cells"][("k8s-en", "E", "R")])


def t_aggregator(a, tmp):
    section("Aggregator: empty input")
    from p2 import aggregate as AG
    from p2 import export as X
    try:
        AG.aggregate({}, {}, manifest_for_test(), {}, {})
        raised = False
    except AG.Empty:
        raised = True
    check("empty input raises, no verdict", raised)
    mp = os.path.join(tmp, "agg-manifest.json")
    sha = X.seal(mp)
    for dd in ("agg-a0", "agg-sc", "agg-rp"):
        os.makedirs(os.path.join(tmp, dd))
    rc, out = cli("aggregate", "--d8-dir", a.d8_dir, "--transcript-dir", os.path.join(tmp, "agg-t"),
                  "--arm0-dir", os.path.join(tmp, "agg-a0"), "--score-dir", os.path.join(tmp, "agg-sc"),
                  "--manifest", mp, "--manifest-sha", sha, "--tiers", os.path.join(tmp, "none.jsonl"),
                  "--repro-dir", os.path.join(tmp, "agg-rp"), "--out", os.path.join(tmp, "v.json"),
                  "--fixture-ok", "--unbound")
    check("the aggregate CLI on empty input exits non-zero with no verdict",
          rc != 0 and "OVERALL" not in out and not os.path.exists(os.path.join(tmp, "v.json")),
          f"exit {rc}")
    section("Overall verdict (§6.7)")
    cells = {}

    def setc(arm, mode, mech, v):
        cells[(arm, mode, mech)] = {"verdict": v}
    for arm in ("k8s-en", "cncf-toc"):
        setc(arm, "E", "Q", "NOT FOUND")
    setc("k8s-en", "S5", "R", "NOT FOUND")
    check("Q in both and R in one: NOT FOUND", AG.overall(cells, {"i": set()}) == "NOT FOUND")
    del cells[("k8s-en", "S5", "R")]
    check("Q in both, no R: NOT FOUND (Q only)", AG.overall(cells, {"i": set()}) == "NOT FOUND (Q only)")
    del cells[("cncf-toc", "E", "Q")]
    check("Q in one only: INCONCLUSIVE", AG.overall(cells, {"i": set()}) == "INCONCLUSIVE")
    setc("site-policy", "M", "Q", "FOUND")
    check("any FOUND cell: FOUND", AG.overall(cells, {"i": set()}) == "FOUND")


ARGS = None


def main():
    global ARGS
    ap = argparse.ArgumentParser()
    ap.add_argument("--d8-dir", required=True)
    ARGS = a = ap.parse_args()
    a.d8_dir = os.path.abspath(a.d8_dir)
    Mx.load(a.d8_dir)
    tmp = tempfile.mkdtemp(prefix="prereg2-v3.")
    try:
        t_d8_pin(a, tmp)
        t_copied(a)
        t_repeat(a)
        t_known(a)
        t_split(a)
        t_wf(a)
        t_r_units(a)
        t_r(a)
        t_plants(a, tmp)
        t_enumerators(a, tmp)
        t_repro(a, tmp)
        t_undecodable(a, tmp)
        t_bundles(a, tmp)
        t_m_arm(a, tmp)
        t_mfilter(a, tmp)
        t_sampler(a)
        t_counting(a)
        t_arm0(a, tmp)
        t_export(a, tmp)
        t_tier_run(a, tmp)
        t_void(a)
        t_aggregator(a, tmp)
    except Exception:
        import traceback
        traceback.print_exc()
        RESULTS.append(("no exception", False))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    fails = [lbl for lbl, ok in RESULTS if not ok]
    print(f"\n{len(RESULTS)} checks, {len(fails)} failed")
    print("V3:", "PASS" if not fails and RESULTS else "FAIL")
    return 0 if not fails and RESULTS else 1


if __name__ == "__main__":
    sys.exit(main())
