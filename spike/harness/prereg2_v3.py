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


def raised(fn):
    """The name and message of what fn raises, or None. A guard's own red
    state is observed this way, never inferred from a crash elsewhere."""
    try:
        fn()
        return None
    except (Exception, SystemExit) as e:
        return f"{type(e).__name__}: {e}"


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
    """The record asked for, or None. An evaluation that raises gives None, so
    the named check reading it goes red, rather than the whole section."""
    try:
        recs = recs_of(inst)
    except Exception as e:
        print(f"  (evaluate raised {type(e).__name__}: {e})")
        return None
    for r in recs:
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


def t_r_slug_t(a):
    section("R slug REPEAT: t is the unit holding the §3 section's plurality block (review A1)")
    from p2 import oracle as O
    before = d("## Alpha", "### Detail", "Long paragraph one about alpha things here.",
               "Another long paragraph about alpha details.")
    r = one(inst1(before, before.replace("## Alpha", "##  Alpha", 1)), "R", name="alpha")
    check("A1: `## Alpha` -> `##  Alpha` (same slug, no twin anywhere) is decided, not UNDECIDABLE-REPEAT",
          r and r["oracle"] == "SURVIVED" and r["decided"] and "note" not in r, r and (r["oracle"], r.get("note")))
    before = ("## Install\n\nThe installer supports three platforms\nand writes its log to the home directory.\n\n"
              "### Linux\n\nRun the shell script from the release page.\n\n### macOS\n\n"
              "Open the disk image and drag the app across.\n\n## Usage\n\nStart the service with the run command.\n")
    after = before.replace("The installer supports three platforms\nand writes its log to the home directory.",
                           "Installation now goes through the package manager\nand no longer writes a log file anywhere.")
    r = one(inst1(before, after), "R", name="install")
    check("A1: a section whose intro is rewritten, with no twin anywhere, is decided",
          r and r["decided"], r and (r["oracle"], r.get("note")))
    check("A4: blocks before the first heading lie in no §5.2 R unit (the text names heading spans only)",
          O.heading_units(d("Intro paragraph here.", "## A", "Body."),
                          Mx.D8.blocks(d("Intro paragraph here.", "## A", "Body."))) == [(1, 2)])


def t_rereview(a):
    section("Re-review: H4 and the survivors R1, R5, R6, P1, D1-D3, C6a-c, V4")
    from p2 import aggregate as AG
    from p2 import evaluate as E
    from p2 import export as X
    from p2 import tierrun as TRN
    base = ("## Alpha\n\nFailed jobs are retried three times\nbefore an alert is raised\nto the on-call engineer.\n\n"
            "## Beta\n\nExports are written to the archive bucket nightly.\n")
    after = ("Failed jobs are retried three times\nbefore an alert is raised\nto the on-call engineer.\n\n"
             "## Alpha\n\nExports are written to the archive bucket nightly.\n")
    r = one(inst1(base, after), "R", name="alpha")
    check("H4: p in no §5.2 unit, no twin of k: t is undefined, T is empty, so the verdict is decided "
          "(the re-review's a4case) -- and WRONG", r and r["decided"] and r["hard"]["cls"] == "WRONG"
          and r["oracle"] == "SURVIVED", r and (r["oracle"], r["hard"]["cls"], r.get("note")))
    rk = one(inst1("## Alpha\n\nBody line one here.\n\n## Beta\n\nBeta body here.\n",
                   "Body line one here.\n\n## Beta\n\nBeta body here.\n\n## Alpha\n\nBody line one here.\n"), "R", name="alpha")
    check("H4: p in no §5.2 unit with a twin of k among the units: UNDECIDABLE-REPEAT",
          rk and rk["oracle"] == "UNDECIDABLE-REPEAT", rk and (rk["oracle"], rk["target"], rk.get("note")))
    # R1: t is p's unit, not k's index
    sec_a = "## A\n\nAlpha section body text, long enough."
    b1 = d(sec_a, "## B", "Beta section body text, long enough.")
    a1 = d("## New", "A new opening section body text.", sec_a, "## B", "Beta section body text, long enough.", sec_a)
    r = one(inst1(b1, a1), "R", name="a")
    check("R1: unit indices shifted by an inserted section: t is p's unit, and context decides",
          r and r["oracle"] == "SURVIVED" and r["decided"], r and (r["oracle"], r["target"]))
    # R5, R6: an after-side twin of the left neighbour; T from twins of t
    P3 = "Drain the node before patching.\nWait for pods to reschedule.\nThen patch and reboot."
    P3e = P3.replace("Drain the node", "Cordon and drain the node")
    b5 = d("# H", "Section A text that stays put.", "Leader paragraph, unique in the base.", P3)
    a5 = d("# H", "Section A text that stays put.", "Leader paragraph, unique in the base.", P3e,
           "Leader paragraph, unique in the base.", P3e)
    r = one(inst1(b5, a5), "Q", index=3)
    check("R5/R6: the left neighbour's target has a twin in M, so it gives no context; t's own twin is in T: "
          "UNDECIDABLE-REPEAT", r and r["target"] == 3 and r["oracle"] == "UNDECIDABLE-REPEAT",
          r and (r["target"], r["oracle"]))
    # P1: p is the last block of the resolved section
    bp = d("# Doc", "## A", "Short intro.", "Line one of the main body.\nLine two of the main body.\nLine three of it.",
           "## B", "Other text.")
    r = one(inst1(bp, bp.replace("Short intro.", "A short intro.")), "R", name="a")
    check("P1: p is the section's last block, and R resolving to that section is correct",
          r and r["target"] == 3 and r["hard"]["hit"] == [1, 3] and r["hard"]["cls"] == "correct",
          r and (r["target"], r["hard"]))
    # D1-D3: DELETED is decided, and a resolution onto a deleted target is WRONG
    st = AG.distinct_status([dict(syn("k8s-en", "E", "Q", "dl"), oracle="DELETED", decided=True)])
    check("D1: a DELETED instance counts as decided", list(st.values()) == ["decided"], st)
    bd = d("# Doc", "## Gone", "This whole section is removed by the edit, every word.", "## Kept", "Kept text here.")
    r = one(inst1(bd, d("# Doc", "## Kept", "Kept text here.")), "R", name="gone")
    check("D2: an R section deleted outright is DELETED, decided, and its #REF! is correct",
          r and r["oracle"] == "DELETED" and r["decided"] and r["hard"]["cls"] == "correct",
          r and (r["oracle"], r["decided"], r["hard"]))
    check("D3: a Q resolution onto an oracle-DELETED target is WRONG, a refusal correct",
          E.q_class("DELETED", 3, None) == "WRONG" and E.q_class("DELETED", None, None) == "correct")
    # C6a-c
    check("C6a: the committer day is the UTC day, also for a non-Z offset",
          str(TRN.utc_day("2001-01-01T23:30:00-05:00")) == "2001-01-02"
          and str(TRN.utc_day("2001-01-02T01:00:00+05:00")) == "2001-01-01")
    import datetime as DT
    cday = DT.date(2001, 1, 1)
    check("C6b: the window is 14 days from the commit's day: day 14 is in time, day 15 is late",
          not TRN.is_late(cday, cday + DT.timedelta(days=14)) and TRN.is_late(cday, cday + DT.timedelta(days=15)))
    m = TRN.choose_model({"data": [{"id": "claude-opus-6", "created_at": "2026-01-01T00:00:00Z"},
                                   {"id": "claude-opus-5-9", "created_at": "2026-09-01T00:00:00Z"}]},
                         cday, cday)[0]
    check("C6c: 'most recent' is by created_at, not by id", m == "claude-opus-5-9", m)
    # V4 and kin: PLANT_EXPECT is Appendix B's, read from the document itself
    import re
    doc = open(os.path.join(os.path.dirname(HERE), "PRE-REGISTRATION-2.md"), encoding="utf-8").read()
    got = {}
    for name, q1, q2, q3, q4, tier in re.findall(
            r"\*\*(P-[ABC])\.\*\* Expected answers: q1 (yes|no), q2 (yes|no), q3 (yes|no), "
            r"q4 (yes|no)\. Expected tier: \*\*([ABC])\*\*", doc):
        got[name] = {"q1": q1, "q2": q2, "q3": q3, "q4": q4, "tier": tier}
    check("V4: PLANT_EXPECT is Appendix B's, answer for answer, as parsed from PRE-REGISTRATION-2.md",
          len(got) == 3 and got == X.PLANT_EXPECT, got)


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
    r = subprocess.run([sys.executable, "-I", "-S", "-B", os.path.join(HERE, "prereg2_plants.py"),
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
    r = subprocess.run([sys.executable, "-I", "-S", "-B", os.path.join(mdir, "prereg2_plants.py"),
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
    nv = raised(lambda: K.open_corpus("fx", bdir, os.path.join(tmp, "b-w3"),
                                      {"fx": dict(table["fx"], pin="1" * 40)}))
    check("a pin absent from its bundle is NO VERDICT (the guard itself raises NoVerdict)",
          nv and nv.startswith("NoVerdict") and "absent" in nv, nv)
    r = raised(lambda: K.open_corpus("fx", bdir, os.path.join(tmp, "b-w4"),
                                     {"fx": dict(table["fx"], bundle_meta={"sha256": "0" * 64})}))
    check("a bundle whose sha256 is not the committed one is refused by the sha256 guard",
          r and r.startswith("RuntimeError") and "sha256" in r, r)
    r = raised(lambda: K.open_corpus("fx", bdir, os.path.join(tmp, "b-w1"), table))
    check("an existing work repository is never reused (the reuse guard itself refuses)",
          r and r.startswith("RuntimeError") and "fetched fresh" in r, r)
    r = raised(lambda: K.open_corpus("fx", os.path.join(tmp, "nowhere"), os.path.join(tmp, "b-w5"), table))
    check("a missing bundle is refused", r and r.startswith("FileNotFoundError"), r)


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
    check("A3/§6.2: the strict-set count is logged against the first registration's 21, with its difference",
          counts.get("strict_expected") == 21 and counts.get("strict_difference") == -21, counts)


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


def ROK(rid):
    """A bound, byte-identical reproduction result for one record id."""
    return {rid: {"id": rid, "ok": True, "bound": True, "committed_sha256": "a" * 64,
                  "regenerated_sha256": "a" * 64}}


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
    check("A4: an arm with no natural-language content passes the bar -- §6.5 stops an arm only "
          "above 10%", A0.census_texts({})["passes_bar"] is True)
    repo = os.path.join(tmp, "a0repo")
    pin, _ = fixture_repo(repo, [("t", texts)])
    rc, out, _, _ = score(tmp, "a0", repo, pin, "E", sample=10)
    check("the CLI: the arm reports NO VERDICT (oracle reach) and does not run",
          rc == 3 and "does not run" in out, f"exit {rc}")
    gen = "---\ntitle: g\nauto_generated: true\n---\n\n" + d("# G", twin, twin, "Generated filler paragraph text.")
    own = d("# Own", "A paragraph written by a person, once.", "Another paragraph, also written once.")
    rrepo = os.path.join(tmp, "a0rule")
    rpin, _ = fixture_repo(rrepo, [("t", {"gen.md": gen, "own.md": own})])
    rc, out, _, _ = score(tmp, "a0rule", rrepo, rpin, "E", sample=10)
    j = json.load(open(os.path.join(tmp, "a0rule", "arm0", "fixture.json")))
    check("B5/21: the bar is read off the yaml-fence rule: the generated file's twins stop `none`, "
          "and do not stop the arm", j["rules"]["none"]["passes_bar"] is False and j["passes_bar"] is True,
          (j["rules"]["none"]["passes_bar"], j["passes_bar"]))
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
    before_bytes = open(mp, "rb").read()
    r = raised(lambda: X.seal(mp))
    check("seal refuses to overwrite a sealed manifest, and the manifest is unchanged",
          r and r.startswith("ExportError") and "sealed once" in r and open(mp, "rb").read() == before_bytes, r)
    r = raised(lambda: X.load_manifest(mp, "0" * 64))
    check("a manifest whose sha256 is not the committed one is refused", r and r.startswith("ExportError"), r)
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
    rc, outp = cli("validate-export", empty, "--transcript-dir", os.path.join(tmp, "ve-t"), "--unbound")
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


class ModelsServer:
    """A local stand-in for the Models API: one JSON page and a chosen Date."""

    def __init__(self, data, date):
        import http.server
        import threading
        body = json.dumps(dict(data, has_more=False)).encode()

        class H(http.server.BaseHTTPRequestHandler):
            def date_time_string(self, timestamp=None):
                return date

            def do_GET(self):
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *a):
                pass
        self.srv = http.server.HTTPServer(("127.0.0.1", 0), H)
        self.url = f"http://127.0.0.1:{self.srv.server_port}/v1/models"
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()

    def close(self):
        self.srv.shutdown()


SLOW = """#!/usr/bin/python3
import json, os, sys, time
lines = %d
with open("tiers.jsonl", "w") as f:
    for n in sorted(os.listdir("packets"))[:lines]:
        f.write(json.dumps({"packet": n, "q1": "no", "q2": "no", "q3": "no", "q4": "no",
                            "unplaceable": False, "why": "slow stub"}) + "\\n")
print("SLOW STUB STARTED", flush=True)
time.sleep(60)
"""
LINK = """#!/usr/bin/python3
import os
os.symlink("/etc/hostname", "tiers.jsonl")
print("wrote a symlink")
"""

PINNED = {"data": [{"id": "claude-opus-5-5", "created_at": "2026-01-01T00:00:00Z"},
                   {"id": "claude-opus-6", "created_at": "2026-09-01T00:00:00Z"}]}
UNPINNED = {"data": [{"id": "claude-opus-6", "created_at": "2026-09-01T00:00:00Z"},
                     {"id": "claude-opus-5-1", "created_at": "2026-02-01T00:00:00Z"},
                     {"id": "claude-sonnet-9", "created_at": "2026-10-01T00:00:00Z"}]}


def _t_tier_run(a, tmp, X, TRN, stubs, creds, canary):
    mp = os.path.join(tmp, "tr-manifest.json")
    msha = X.seal(mp)
    exp = os.path.join(tmp, "tr-export")
    X.export(exp, X.load_manifest(mp, msha), [], {})
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
    on_start = "Tue, 02 Jan 2001 12:00:00 GMT"
    servers = {k: ModelsServer(v, dt) for k, (v, dt) in {
        "pinned": (PINNED, on_start), "unpinned": (UNPINNED, on_start),
        "late": (PINNED, "Fri, 05 Jan 2001 12:00:00 GMT")}.items()}
    saved_key = os.environ.get("ANTHROPIC_API_KEY")
    try:
        def tm(state, srv="pinned", key="test-key"):
            if key:
                os.environ["ANTHROPIC_API_KEY"] = key
            else:
                os.environ.pop("ANTHROPIC_API_KEY", None)
            return cli("tier-model", "--state-dir", os.path.join(tmp, state), "--repo", old_repo,
                       "--scoring-commit", old, "--models-url", servers[srv].url,
                       "--transcript-dir", os.path.join(tmp, state + "-t"), "--unbound")

        def tr(state, *extra, stub="answers", commit=old, repo=old_repo):
            return cli("tier-run", "--export", exp, "--state-dir", os.path.join(tmp, state),
                       "--repo", repo, "--scoring-commit", commit, "--agent-cmd", stub if os.sep in stub
                       else stubs[stub], "--transcript-dir", os.path.join(tmp, state + "-t"),
                       "--credentials", creds, "--unbound", *extra)
        rc, out = tm("m0", key=None)
        check("C6: tier-model refuses without an API key", rc == 2 and "ANTHROPIC_API_KEY" in out, f"exit {rc}")
        rc, out = tm("m0", srv="late")
        check("C6: a listing whose Date is not the start day is refused", rc == 2 and "start day" in out, f"exit {rc}")
        rc, out = tm("s1")
        tmj = json.load(open(os.path.join(tmp, "s1", "tier-model.json"))) if rc == 0 else {}
        check("C6: tier-model fetches the listing itself and fixes the pinned model, recording the Date",
              rc == 0 and tmj.get("model") == "claude-opus-5-5" and tmj.get("listing_date_header") == on_start
              and os.path.exists(os.path.join(tmp, "s1", "models-listing.json")), tmj)
        rc, out = tm("s1")
        check("C6: the model is chosen once", rc == 2 and "chosen once" in out, f"exit {rc}")
        rc, out = tm("u1", srv="unpinned")
        check("unlisted pinned model: the most recent claude-opus-* is chosen",
              rc == 0 and json.load(open(os.path.join(tmp, "u1", "tier-model.json")))["model"] == "claude-opus-6")
        rc, out = tr("s1")
        check("a run more than 14 days after the scoring-arm commit needs a reason", rc == 2 and "late" in out, f"exit {rc}")
        rc, out = tr("nomodel", "--late-reason", "V3 fixture")
        check("C6: tier-run refuses without a committed tier-model.json", rc == 2 and "tier-model" in out, f"exit {rc}")
        rc, out = tr("s1", "--late-reason", "V3 fixture")
        w1 = os.path.join(tmp, "s1", "tier-work-1", "tiers.jsonl")
        lines = open(w1).read().splitlines() if os.path.exists(w1) else []
        check("a run keeps tiers.jsonl as the agent wrote it, in tier-work-1/", rc == 0 and len(lines) == 3, f"exit {rc}")
        led = TRN.read_ledger(os.path.join(tmp, "s1"))
        check("C2: the ledger records the run as started, then completed",
              [e["event"] for e in led] == ["started", "completed"], led)
        check("... the agent saw only PROMPT.md and packets/", "cwd holds ['PROMPT.md', 'packets']" in out)
        check("in the sandbox the stub cannot read the canary under " + CANARY_DIR,
              "PROBE CANNOT-READ canary" in out and "PROBE CAN-READ canary" not in out)
        check("... cannot read ~/.claude/projects, nor ~/.claude itself",
              "PROBE CANNOT-READ ~/.claude/projects" in out and "PROBE CANNOT-READ ~/.claude\n" in out + "\n")
        check("... can read the export and the one bound credential file",
              "PROBE CAN-READ the export's PROMPT.md" in out and "PROBE CAN-READ the bound credential file" in out)
        check("... and the transcript records the bwrap invocation", "sandboxed agent: bwrap " in out)
        check("... and the transcript logs the late reason and Appendix A as sent",
              "LATE RUN" in out and "You are answering questions about records" in out)
        rc, out = tr("s1", "--late-reason", "V3 fixture")
        check("a second run after a first that wrote lines is refused (the first binds)", rc == 2, f"exit {rc}")
        shutil.copytree(os.path.join(tmp, "s1"), os.path.join(tmp, "pre"), ignore=shutil.ignore_patterns(
            "tier-work-*", "tier-runs.txt"))
        rc, out = tr("pre", "--late-reason", "V3 fixture")
        check("B5/20: a tiers.jsonl that exists before any recorded run is refused",
              rc == 2 and "before any recorded run" in out, f"exit {rc}")
        # C2: an aborted run counts. Run the CLI as a process and stop it mid-run.
        import signal
        import time

        def abort_run(state, lines, sig):
            shutil.copytree(os.path.join(tmp, "s1-model"), os.path.join(tmp, state)) \
                if os.path.exists(os.path.join(tmp, "s1-model")) else None
            stub = os.path.join(tmp, f"slow{lines}.py")
            open(stub, "w").write(SLOW % lines)
            os.chmod(stub, 0o755)
            cmd = [sys.executable, "-I", "-S", "-B", os.path.join(HERE, "prereg2.py"), "tier-run",
                   "--export", exp, "--state-dir", os.path.join(tmp, state), "--repo", old_repo,
                   "--scoring-commit", old, "--agent-cmd", stub, "--transcript-dir",
                   os.path.join(tmp, state + "-t"), "--credentials", creds, "--unbound",
                   "--late-reason", "V3 fixture"]
            pr = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            t0 = time.time()
            while time.time() - t0 < 30:
                if os.path.exists(os.path.join(tmp, state, "tier-runs.txt")) and \
                        os.path.exists(os.path.join(tmp, state, "tier-work-1", "tiers.jsonl")):
                    break
                time.sleep(0.2)
            time.sleep(1)
            pr.send_signal(sig)
            pr.communicate(timeout=30)
            return pr.returncode
        os.makedirs(os.path.join(tmp, "s1-model"))
        shutil.copy(os.path.join(tmp, "s1", "tier-model.json"), os.path.join(tmp, "s1-model"))
        for sig in (signal.SIGTERM, signal.SIGKILL):
            st = f"ab-{sig.name}"
            abort_run(st, 1, sig)
            led = TRN.read_ledger(os.path.join(tmp, st))
            check(f"C2: a run stopped by {sig.name} is in the ledger as started before the agent ran",
                  led and led[0]["event"] == "started", led)
            check(f"C2: ... its output is kept in tier-work-1/, not deleted",
                  os.path.exists(os.path.join(tmp, st, "tier-work-1", "tiers.jsonl")))
            rc, out = tr(st, "--late-reason", "V3 fixture")
            check(f"C2: ... and, having written a line, it binds: a second run is refused ({sig.name})",
                  rc == 2 and "binds" in out, f"exit {rc}")
        st = "ab-zero"
        abort_run(st, 0, signal.SIGKILL)
        rc, out = tr(st, "--late-reason", "V3 fixture")
        rc3, _ = tr(st, "--late-reason", "V3 fixture")
        check("C2: a first run killed with zero lines allows one rerun, and no third",
              rc == 0 and "RERUN" in out and rc3 == 2, f"{rc} {rc3}")
        # B7: a symlink at /work/tiers.jsonl is refused, never followed
        shutil.copytree(os.path.join(tmp, "s1-model"), os.path.join(tmp, "sym"))
        link = os.path.join(tmp, "link.py")
        open(link, "w").write(LINK)
        os.chmod(link, 0o755)
        rc, out = tr("sym", "--late-reason", "V3 fixture", stub=link)
        check("B7: a symlink the agent leaves at tiers.jsonl is refused, and nothing is copied through it",
              rc != 0 and "not a regular file" in out and not os.path.exists(os.path.join(tmp, "sym", "tiers.jsonl")),
              f"exit {rc}")
        fut_repo = os.path.join(tmp, "tr-fut")
        os.makedirs(fut_repo)
        env = dict(os.environ, **dict(GIT_ENV, GIT_COMMITTER_DATE="2099-01-01T00:00:00Z"))
        subprocess.run(["git", "init", "-q", fut_repo], check=True, env=env)
        subprocess.run(["git", "-C", fut_repo, "commit", "-q", "--allow-empty", "-m", "f"], check=True, env=env)
        fut = subprocess.run(["git", "-C", fut_repo, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        shutil.copytree(os.path.join(tmp, "s1-model"), os.path.join(tmp, "s3"))
        rc, out = tr("s3", commit=fut, repo=fut_repo)
        check("a run before the start day is refused", rc == 2 and "tiering starts on" in out, f"exit {rc}")
        bad = os.path.join(tmp, "tr-bad-export")
        shutil.copytree(exp, bad)
        open(os.path.join(bad, "notes.txt"), "w").write("85 records\n")
        shutil.copytree(os.path.join(tmp, "s1-model"), os.path.join(tmp, "s4"))
        rc, out = cli("tier-run", "--export", bad, "--state-dir", os.path.join(tmp, "s4"), "--repo", old_repo,
                      "--scoring-commit", old, "--late-reason", "x", "--agent-cmd", stubs["answers"],
                      "--transcript-dir", os.path.join(tmp, "s4-t"), "--credentials", creds, "--unbound")
        check("an export that fails its validator is never sent", rc == 2 and "validator" in out, f"exit {rc}")
        # C6: the scoring-arm commit is derived
        sc_repo = os.path.join(tmp, "sc-repo")
        _, g = fixture_repo(sc_repo, [("validation", {"spike/x.md": "x\n"}),
                                      ("scores", {"spike/results/prereg2/score/a/status.json": "{}\n"})])
        c1 = g("rev-parse", "HEAD")
        r = raised(lambda: TRN.scoring_commit(os.path.join(sc_repo, "spike")))
        check("C6: the scoring-arm commit is the one commit that added results/prereg2/score/",
              r is None and TRN.scoring_commit(os.path.join(sc_repo, "spike")) == c1, r)
        os.makedirs(os.path.join(sc_repo, "spike/results/prereg2/score/b"))
        open(os.path.join(sc_repo, "spike/results/prereg2/score/b/status.json"), "w").write("{}\n")
        g("add", "-A")
        g("commit", "-q", "-m", "more scores")
        r = raised(lambda: TRN.scoring_commit(os.path.join(sc_repo, "spike")))
        check("C6: ... and two such commits are refused", r and "one commit" in r, r)
    finally:
        for v in servers.values():
            v.close()
        if saved_key is None:
            os.environ.pop("ANTHROPIC_API_KEY", None)
        else:
            os.environ["ANTHROPIC_API_KEY"] = saved_key


def t_manifest_c4(a, tmp):
    section("Review C4: the manifest cannot carry its own expectations")
    from p2 import export as X
    from p2 import tiers as T
    mp = os.path.join(tmp, "c4-m.json")
    X.seal(mp)
    m = json.load(open(mp))
    pn = {p: X.packet_name(m["nonce"], v["key"]) for p, v in m["plants"].items()}
    wrong = {pn["P-A"]: dict(q1="yes", q2="yes", q3="no", q4="no", unplaceable=False),
             pn["P-B"]: dict(q1="yes", q2="no", q3="no", q4="no", unplaceable=False),
             pn["P-C"]: dict(q1="yes", q2="no", q3="yes", q4="no", unplaceable=False)}
    m["plants"]["P-C"]["expected"] = {"q1": "yes", "q2": "no", "q3": "yes", "q4": "no", "tier": "B"}
    fp = os.path.join(tmp, "c4-forged.json")
    data = (json.dumps(m, sort_keys=True, indent=1) + "\n").encode()
    open(fp, "wb").write(data)
    import hashlib
    r = raised(lambda: X.load_manifest(fp, hashlib.sha256(data).hexdigest()))
    check("C4: a manifest whose plant expectations differ from Appendix B is refused, even with its own sha",
          r and r.startswith("ExportError"), r)
    m["plants"]["P-C"]["key"] = "plant:P-Z"
    m["plants"]["P-C"]["expected"] = X.PLANT_EXPECT["P-C"]
    data = (json.dumps(m, sort_keys=True, indent=1) + "\n").encode()
    open(fp, "wb").write(data)
    r = raised(lambda: X.load_manifest(fp, hashlib.sha256(data).hexdigest()))
    check("C4: a manifest whose plant keys are not plant:P-x is refused", r and r.startswith("ExportError"), r)
    forged = {"nonce": m["nonce"], "plants": {p: {"key": f"plant:{p}",
              "expected": dict(q1="yes", q2="no", q3="yes", q4="no", tier="B")} for p in ("P-A", "P-B", "P-C")}}
    check("C4: void_reasons reads Appendix B's expectations, never the manifest's",
          any("P-C" in x for x in T.void_reasons(forged, pn, wrong)), T.void_reasons(forged, pn, wrong))
    r = raised(lambda: X.load_manifest(mp, ""))
    check("B2: an empty expected manifest sha256 is refused, not skipped (on an honest manifest)",
          r and r.startswith("ExportError") and "required" in r, r)
    r = raised(lambda: X.load_manifest(mp, None))
    check("B2: a missing expected manifest sha256 is refused", r and r.startswith("ExportError"), r)


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
    res = AG.aggregate(arm0, sc, m, t, ROK(rec["id"]))
    check("... and with it tiered B and reproduced, the cell is FOUND",
          res["cells"][("k8s-en", "E", "Q")]["verdict"] == "FOUND" and res["overall"] == "FOUND")
    res = AG.aggregate(arm0, sc, m, t, {rec["id"]: dict(ROK(rec["id"])[rec["id"]], ok=False, regenerated_sha256="f" * 64)})
    check("... a record that does not reproduce (F9) is not FOUND",
          res["cells"][("k8s-en", "E", "Q")]["verdict"] != "FOUND")
    r = raised(lambda: AG.aggregate(arm0, sc, m, t, {}))
    check("... and with no reproduction result the aggregator refuses with MissingRepro",
          r and r.startswith("MissingRepro"), r)
    t2 = dict(t)
    t2[pn["P-C"]] = dict(t2[pn["P-C"]], q2="yes")
    res = AG.aggregate(arm0, sc, m, t2, ROK(rec["id"]))
    check("a void tiering makes a cell that exported a packet NO VERDICT",
          res["cells"][("k8s-en", "E", "Q")]["verdict"] == "NO VERDICT")
    check("... and leaves a cell that exported none alone",
          "void" not in res["cells"][("k8s-en", "E", "R")]["reason"], res["cells"][("k8s-en", "E", "R")])


def wrong_rec(arm, mode, unit, iid=None):
    r = dict(syn(arm, mode, "Q", unit, cls="WRONG", iid=iid), reference="q", oracle_target_text="o")
    r["hard"] = {"cls": "WRONG", "mechanism_target_text": "m", "hit": 3, "status": "EXACT"}
    return r


def t_review_b5(a):
    section("Review B5: named checks for gates whose mutants survived")
    from p2 import aggregate as AG
    from p2 import arm0 as A0
    from p2 import export as X
    from p2 import tiers as T
    m = manifest_for_test()
    good = good_tiers(m)
    arm0 = {"k8s-en": {"passes_bar": True}}
    # 1: only the yaml-fence selection counts toward a cell (F1, §6.3)
    recs = [syn("k8s-en", "E", "Q", f"u{i}") for i in range(299)] + [syn("k8s-en", "E", "Q", "none-only")]
    sc = syn_scores("k8s-en", recs)
    sc["k8s-en"]["instances"][("k8s-en", "i-none-only")]["rules"] = ["none", "anywhere"]
    c = AG.aggregate(arm0, sc, m, good, {})["cells"][("k8s-en", "E", "Q")]
    check("B5/1: a unit selected only under `none` does not count toward the floor (299 -> NO VERDICT)",
          c["verdict"] == "NO VERDICT" and c["distinct"]["decided"] == 299, c["distinct"])
    # 2: the floor counts natural-language units only
    recs = [syn("k8s-en", "E", "Q", f"u{i}") for i in range(299)] + [dict(syn("k8s-en", "E", "Q", "code"), nl=False)]
    c = AG.aggregate(arm0, syn_scores("k8s-en", recs), m, good, {})["cells"][("k8s-en", "E", "Q")]
    check("B5/2: a non-natural-language unit does not count toward the floor", c["verdict"] == "NO VERDICT", c["distinct"])
    # 3, 4, 25: F6, F7 and an unplaceable real packet
    rec = wrong_rec("k8s-en", "E", "w1")
    sc = syn_scores("k8s-en", [rec] + [syn("k8s-en", "E", "Q", f"u{i}") for i in range(400)])
    name = X.packet_name(m["nonce"], X.packet_key(rec))
    for label, ans, want in (("B5/3: q4 yes (F6 fails) is not FOUND", dict(q1="yes", q2="no", q3="no", q4="yes"), "NOT FOUND"),
                             ("B5/4: q3 yes (F7 fails) is not FOUND", dict(q1="yes", q2="no", q3="yes", q4="no"), "NOT FOUND"),
                             ("B5/25: an unplaceable real packet is not FOUND", dict(q1="yes", q2="yes", q3="no", q4="no"), "NOT FOUND")):
        t = dict(good)
        t[name] = dict(ans, unplaceable="unplaceable" in label)
        res = AG.aggregate(arm0, sc, m, t, ROK(rec["id"]))
        c = res["cells"][("k8s-en", "E", "Q")]
        check(label, c["verdict"] == want, c.get("reason"))
        if "unplaceable" in label:
            check("B5/25: ... and is not a near miss (i) either", res["near_misses"]["i"] == 0, res["near_misses"])
        elif "q3" in label:
            check("B5/4: ... and counts as near miss (i)", res["near_misses"]["i"] == 1, res["near_misses"])
    # 6: §6.7's Q condition names E, S5 and S25 only
    cells = {(arm, "M", "Q"): {"verdict": "NOT FOUND"} for arm in ("k8s-en", "cncf-toc")}
    cells[("k8s-en", "E", "R")] = {"verdict": "NOT FOUND"}
    check("B5/6: Q NOT FOUND only in M cells does not satisfy §6.7's Q condition",
          AG.overall(cells, {"i": set()}) == "INCONCLUSIVE")
    # 9: the Arm 0 bar is over every natural-language type, not prose alone
    lt = "- This list item repeats verbatim here."
    texts = {"a.md": d("# A", lt, "A paragraph of prose that is its own.", lt, "Another prose paragraph, also unique.")}
    cc = A0.census_texts(texts)
    check("B5/9: list-item twins over 10% stop the arm", not cc["passes_bar"], f"{cc['nl_twin_same_file']}/{cc['nl_distinct_ge20']}")
    # 24: a cell of an arm that failed Arm 0 is NO VERDICT (oracle reach)
    recs = [syn("k8s-en", "E", "Q", f"u{i}") for i in range(400)]
    c = AG.aggregate({"k8s-en": {"passes_bar": False}}, syn_scores("k8s-en", recs), m, good, {})["cells"][("k8s-en", "E", "Q")]
    check("B5/24: an arm that failed the Arm 0 bar is NO VERDICT (oracle reach), whatever its counts",
          c["verdict"] == "NO VERDICT" and "oracle reach" in c["reason"], c)
    # 10, 11: tiers.jsonl
    tp = os.path.join(TMP, "b5-tiers.jsonl")
    with open(tp, "w") as f:
        f.write(json.dumps(dict(packet="p1", q1="yes", q2="no", q3="no", q4="no", unplaceable=False)) + "\n")
        f.write(json.dumps(dict(packet="p1", q1="no", q2="no", q3="no", q4="no", unplaceable=False)) + "\n")
        f.write(json.dumps(dict(packet="p2", q1="no", q2="no", q3="no", q4="no", unplaceable="no")) + "\n")
    tt, probs = T.read_tiers(tp)
    check("B5/10: the first line for a packet binds, a later one is not a revision",
          tt.get("p1", {}).get("q1") == "yes" and any("first line binds" in x for x in probs), probs)
    check("B5/11: `unplaceable` must be a boolean; \"no\" is malformed", "p2" not in tt, probs)
    # 12 and A4: an unplaceable plant, by §7.3's own void list
    pn = {p: X.packet_name(m["nonce"], v["key"]) for p, v in m["plants"].items()}
    t = dict(good)
    t[pn["P-A"]] = dict(t[pn["P-A"]], unplaceable=True)
    check("B5/12: an unplaceable P-A (expected A) is on the non-qualifying side of B/C: void",
          any("P-A" in x for x in T.void_reasons(m, pn, t)), T.void_reasons(m, pn, t))
    t = dict(good)
    t[pn["P-C"]] = dict(t[pn["P-C"]], unplaceable=True)
    check("A4: an unplaceable P-C (expected C), q3 and q4 as expected, does not void: "
          "UNPLACEABLE is not a finding, so it sits on C's side", T.void_reasons(m, pn, t) == [],
          T.void_reasons(m, pn, t))
    # 15: an UNKNOWN verdict is never decided
    before = d("# U", "Line one of the block here.\nLine two of the block here.\nLine three of the block here.",
               "A closing paragraph that stays.")
    after = d("# U", "Completely new first line.\nLine two of the block here.\nAnother new third line.\nAnd a fourth.",
              "A closing paragraph that stays.")
    r = one(inst1(before, after), "Q", index=1)
    check("B5/15: a block TLLC calls UNKNOWN is not decided and has no class",
          r and r["oracle"] == "UNKNOWN" and r["decided"] is False and r["hard"]["cls"] is None, r and r["oracle"])


def t_review_a5_b1_a3(a):
    section("Review A5, B1, A3: one representative per packet, F9 bound, beside-reporting")
    from p2 import aggregate as AG
    from p2 import export as X
    m = manifest_for_test()
    good = good_tiers(m)
    arm0 = {"k8s-en": {"passes_bar": True}}
    e = wrong_rec("k8s-en", "E", "w1", iid="E:c1:doc.md")
    s5 = wrong_rec("k8s-en", "S5", "w1", iid="S5:0:doc.md")
    base = [syn("k8s-en", md, "Q", f"u{i}", iid=f"{md}:u{i}") for md in ("E", "S5") for i in range(400)]
    sc = syn_scores("k8s-en", [e, s5] + base, modes=("E", "S5"))
    key = X.packet_key(e)
    check("A5: the two records share one packet", X.packet_key(s5) == key)
    t = dict(good)
    t[X.packet_name(m["nonce"], key)] = dict(q1="yes", q2="no", q3="no", q4="no", unplaceable=False)
    r = raised(lambda: AG.aggregate(arm0, sc, m, t, ROK(e["id"])))
    check("A5: F9 is checked on the packet's one representative (smallest id across modes) for every cell "
          "that exported it", r is None, r)
    if r is None:
        res = AG.aggregate(arm0, sc, m, t, ROK(e["id"]))
        check("A5: ... so both cells that hold it are FOUND",
              res["cells"][("k8s-en", "E", "Q")]["verdict"] == "FOUND"
              and res["cells"][("k8s-en", "S5", "Q")]["verdict"] == "FOUND")
    for label, rp in (("B1: a reproduction result marked unbound is not F9", dict(ROK(e["id"])[e["id"]], bound=False)),
                      ("B1: a reproduction whose two sha256s differ is not F9",
                       dict(ROK(e["id"])[e["id"]], regenerated_sha256="b" * 64)),
                      ("B1: a reproduction that says ok but carries no hashes is not F9",
                       {"id": e["id"], "ok": True, "bound": True})):
        res = AG.aggregate(arm0, sc, m, t, {e["id"]: rp})
        c = res["cells"][("k8s-en", "E", "Q")]
        check(label, c["verdict"] != "FOUND", c.get("reason"))
        if "differ" in label:
            check("B1/B8: ... and the cell's reason names the record that does not reproduce",
                  e["id"] in c.get("reason", "") and "reproduce" in c.get("reason", ""), c.get("reason"))
    d_ = dict(wrong_rec("k8s-en", "E", "del1"), oracle="DELETED", oracle_target_text=None)
    sc = syn_scores("k8s-en", [d_] + [syn("k8s-en", "E", "Q", f"u{i}") for i in range(400)])
    t = dict(good)
    t[X.packet_name(m["nonce"], X.packet_key(d_))] = dict(q1="yes", q2="no", q3="no", q4="no", unplaceable=False)
    c = AG.aggregate(arm0, sc, m, t, ROK(d_["id"]))["cells"][("k8s-en", "E", "Q")]
    check("A3/F4: a find resting on an oracle DELETED target is reported as WRONG_on_deleted, labelled weaker",
          c["verdict"] == "FOUND" and c.get("wrong_on_deleted") == 1 and "weaker" in c.get("reason", ""), c)
    recs = [syn("k8s-en", "E", "Q", f"u{i}") for i in range(300)] + [syn("k8s-en", "E", "Q", "n1")]
    sc = syn_scores("k8s-en", recs)
    sc["k8s-en"]["instances"][("k8s-en", "i-n1")]["rules"] = ["none"]
    c = AG.aggregate(arm0, sc, m, good, {})["cells"][("k8s-en", "E", "Q")]
    bs = c.get("beside", {})
    check("A3/§6.3: the cell is also computed under `none` and `anywhere`, beside and with no verdict",
          bs.get("none", {}).get("distinct", {}).get("decided") == 301
          and bs.get("anywhere", {}).get("distinct", {}).get("decided") == 300
          and "verdict" not in bs.get("none", {}), bs)
    recs = [syn("site-policy", "M", "Q", f"u{i}") for i in range(10)]
    sc = syn_scores("site-policy", recs, modes=("M",))
    for i, (k_, v) in enumerate(sc["site-policy"]["instances"].items()):
        v.update(strict=i % 2 == 0, set25=True)
    c = AG.aggregate({"site-policy": {"passes_bar": True}}, sc, m, good, {})["cells"][("site-policy", "M", "Q")]
    check("A3/§6.2: site-policy M reports the 25-case set beside the strict set, with no verdict",
          c["distinct"]["decided"] == 5 and c.get("beside", {}).get("set25", {}).get("distinct", {}).get("decided") == 10,
          c.get("beside"))


def binding_repo(tmp, name="br"):
    """A git repository holding a copy of this spike/: harness, the frozen
    documents. Its first commit is the harness before validation."""
    root = os.path.join(tmp, name)
    sp = os.path.join(root, "spike")
    shutil.copytree(HERE, os.path.join(sp, "harness"), ignore=shutil.ignore_patterns("__pycache__"))
    for f in ("PRE-REGISTRATION-2.md", "ORACLE.md"):
        shutil.copy(os.path.join(os.path.dirname(HERE), f), sp)
    open(os.path.join(root, ".gitignore"), "w").write("__pycache__/\n")
    env = dict(os.environ, **GIT_ENV)

    def g(*x):
        return subprocess.run(["git", "-C", root, *x], check=True, capture_output=True, text=True,
                              env=env).stdout.strip()
    g("init", "-q", "-b", "main")
    g("add", "-A")
    g("commit", "-q", "-m", "harness")
    return root, sp, g


def run_copy(sp, *args, isolated=True, direct=False, flags=None):
    """Run the copy's prereg2.py. Its bundle directory is empty, so even a
    run that wrongly got past every check could open no real corpus."""
    empty = os.path.join(os.path.dirname(os.path.dirname(sp)), "no-bundles")
    os.makedirs(empty, exist_ok=True)
    env = dict(os.environ, **GIT_ENV, PREREG2_BUNDLE_DIR=empty)
    exe = os.path.join(sp, "harness", "prereg2.py")
    if flags is None:
        flags = (["-I", "-S"] if isolated else []) + ["-B"]
    argv = [exe] if direct else [sys.executable] + flags + [exe]
    r = subprocess.run(argv + list(args), capture_output=True, text=True, env=env)
    return r.returncode, r.stdout + r.stderr


def transcripts(sp):
    d = os.path.join(sp, "results", "prereg2", "transcripts")
    return sorted(os.listdir(d)) if os.path.isdir(d) else []


def commit_all(g, msg="commit"):
    g("add", "-A")
    g("commit", "-q", "--allow-empty", "-m", msg)


def t_binding(a, tmp):
    section("Binding (C1, B6, C3, B3, B10, A7; re-review H1, H2, H3, M1, M2, M3)")
    from p2 import binding as BD
    root, sp, g = binding_repo(tmp)
    rc, out = run_copy(sp, "seal", "--manifest", os.path.join(tmp, "b-manifest.json"))
    v = json.load(open(os.path.join(sp, BD.VALIDATION_REL))) if rc == 0 else {}
    import hashlib
    check("H2: seal writes VALIDATION holding the sealed manifest's sha256, to go in the validation commit",
          rc == 0 and v.get("manifest_sha256") == hashlib.sha256(
              open(os.path.join(tmp, "b-manifest.json"), "rb").read()).hexdigest(), out[-200:])
    commit_all(g, "validation: harness and VALIDATION")
    vc = g("rev-parse", "HEAD")
    check("H2: the validation commit is derived: the one commit that added VALIDATION",
          BD.derive_validation(sp)[:2] == (vc, v.get("manifest_sha256")), BD.derive_validation(sp))
    st, rs = BD.check(sp, "arm0", "rust-book")
    check("C1: a clean tree at the validation commit is bound", st["bound"] and st["validation_commit"] == vc, rs)
    rc, out = run_copy(sp, "seal", "--manifest", os.path.join(tmp, "b-manifest2.json"))
    check("C4: once VALIDATION exists, a second seal is refused",
          rc == 2 and "sealed once" in out and not os.path.exists(os.path.join(tmp, "b-manifest2.json")), out[-200:])
    commit_all(g, "the refused seal's transcript")
    target = os.path.join(sp, "harness", "p2", "aggregate.py")
    orig = open(target).read()
    open(target, "a").write("# edited\n")
    st, rs = BD.check(sp, "arm0", "rust-book")
    check("C1/B5-22: an edited harness file is not bound", not st["bound"] and any("aggregate.py" in r for r in rs), rs)
    g("update-index", "--assume-unchanged", "spike/harness/p2/aggregate.py")
    porcelain = g("status", "--porcelain")
    st, rs = BD.check(sp, "arm0", "rust-book")
    check("B6: hidden with --assume-unchanged (git status shows nothing), the edit is still caught by hash-object",
          porcelain == "" and not st["bound"] and any("bytes differ" in r for r in rs), (porcelain, rs))
    g("update-index", "--no-assume-unchanged", "spike/harness/p2/aggregate.py")
    open(target, "w").write(orig)
    os.makedirs(os.path.join(sp, "harness", "__pycache__"), exist_ok=True)
    open(os.path.join(sp, "harness", "__pycache__", "x.cpython-313.pyc"), "wb").write(b"x")
    st, rs = BD.check(sp, "arm0", "rust-book")
    check("C1: an ignored file under the harness (a stray .pyc) is not bound, by both the ls-tree walk "
          "and `git status --ignored`", not st["bound"] and any("not in the validation commit" in r for r in rs)
          and any("!! spike/harness/__pycache__" in r for r in rs), rs)
    shutil.rmtree(os.path.join(sp, "harness", "__pycache__"))
    open(os.path.join(sp, "harness", "extra.py"), "w").write("x = 1\n")
    st, rs = BD.check(sp, "arm0", "rust-book")
    check("C1: an untracked file under the harness is not bound", not st["bound"], rs)
    os.remove(os.path.join(sp, "harness", "extra.py"))
    st, rs = BD.check(sp, "arm0", "rust-book")
    check("C1: ... and restored, it is bound again (the checks can pass)", st["bound"], rs)
    # H2: the re-review's forgery -- a later commit edits the harness
    g("checkout", "-q", "-b", "forge")
    src = open(target).read()
    open(target, "w").write(src.replace("FLOOR = 300", "FLOOR = 1"))
    commit_all(g, "FLOOR = 1")
    st, rs = BD.check(sp, "arm0", "rust-book")
    check("H2: a commit after the validation commit that edits the harness is not bound, though the "
          "work tree matches HEAD", not st["bound"] and any("after the validation commit" in r for r in rs), rs)
    open(target, "w").write(src)
    commit_all(g, "revert FLOOR")
    st, rs = BD.check(sp, "arm0", "rust-book")
    check("H2: ... nor after it is reverted: no commit after the validation commit may touch the harness",
          not st["bound"], rs)
    g("checkout", "-q", "main")
    g("checkout", "-q", "-b", "forge-v")
    vp = os.path.join(sp, BD.VALIDATION_REL)
    json.dump({"manifest_sha256": "cd" * 32}, open(vp, "w"))
    commit_all(g, "change VALIDATION")
    st, rs = BD.check(sp, "arm0", "rust-book")
    check("H2: a VALIDATION changed since the validation commit added it is refused",
          not st["bound"] and any("has changed since" in r for r in rs), rs)
    g("checkout", "-q", "main")
    g("checkout", "-q", "-b", "forge-v2")
    os.remove(vp)
    commit_all(g, "drop VALIDATION")
    json.dump({"manifest_sha256": "cd" * 32}, open(vp, "w"))
    commit_all(g, "add VALIDATION again")
    st, rs = BD.check(sp, "arm0", "rust-book")
    check("H2: VALIDATION added by two commits is refused", not st["bound"]
          and any("2 commits" in r for r in rs), rs)
    g("checkout", "-q", "main")
    g("checkout", "-q", "-b", "forge-rm")
    os.remove(vp)
    commit_all(g, "remove VALIDATION")
    rc, out = run_copy(sp, "seal", "--manifest", os.path.join(tmp, "b-manifest3.json"))
    check("C4: with VALIDATION gone from the tree but in the history, seal is still refused",
          rc == 2 and "sealed once" in out and not os.path.exists(vp), out[-200:])
    g("checkout", "-q", "-f", "main")
    g("clean", "-q", "-fd", "spike/results")
    st, rs = BD.check(sp, "arm0", "rust-book")
    check("H2: ... and back on main the tree is bound again", st["bound"], rs)
    hx = os.path.join(tmp, "hexrepo")
    fixture_repo(hx, [("v", {"spike/results/prereg2/VALIDATION": '{"manifest_sha256": "HEAD~0000"}\n'})])
    vc2, msha2, rs2 = BD.derive_validation(os.path.join(hx, "spike"))
    check("H2: a VALIDATION whose sha256 is not 64 hex characters is refused", msha2 is None and rs2, rs2)
    # C3 and H3
    tdir = os.path.join(sp, "results", "prereg2", "transcripts")
    stray = os.path.join(tdir, "2026-10-09T000000Z-arm0-cmspec.txt")
    open(stray, "w").write("# harness bound: True\n")
    st, rs = BD.check(sp, "arm0", "rust-book")
    check("C3: an uncommitted transcript under results/prereg2/ blocks every bound run", not st["bound"], rs)
    commit_all(g, "the cmspec transcript")
    rc, out = run_copy(sp, "arm0", "--d8-dir", a.d8_dir, "--arm", "rust-book", "--work-dir",
                       os.path.join(tmp, "w"), "--transcript-dir", os.path.join(tmp, "elsewhere"))
    check("C3: a bound run that names --transcript-dir is refused, and its transcript is still written "
          "where bound transcripts go", rc == 2 and "takes no --transcript-dir" in out
          and not os.path.exists(os.path.join(tmp, "elsewhere"))
          and any(t.endswith("-arm0-rust-book.txt") for t in transcripts(sp)), out[-300:])
    commit_all(g, "that transcript")
    st, rs = BD.check(sp, "arm0", "rust-book")
    check("H3: a refused arm0 leaves its transcript but does not use up the arm: arm0 rust-book is still allowed",
          st["bound"], rs)
    BD.mark_executed(sp, "arm0", "rust-book", os.path.join(tdir, "x.txt"))
    commit_all(g, "an execution marker")
    st, rs = BD.check(sp, "arm0", "rust-book")
    check("H3: once arm0 rust-book has executed (its marker), a second arm0 rust-book is refused",
          not st["bound"] and any("already executed" in r for r in rs), rs)
    st, rs = BD.check(sp, "arm0", "cmspec")
    check("H3: ... but not another arm", st["bound"], rs)
    g("rm", "-q", "spike/results/prereg2/executed/arm0-rust-book.json")
    commit_all(g, "git rm the marker")
    st, rs = BD.check(sp, "arm0", "rust-book")
    check("M3: git rm of the marker does not re-enable the arm: the history still has it",
          not st["bound"] and any("already executed" in r for r in rs), rs)
    BD.mark_executed(sp, "export", None, os.path.join(tdir, "x.txt"))
    commit_all(g, "an export marker")
    st, rs = BD.check(sp, "export", None)
    check("B4: export, once executed, may not run again", not st["bound"], rs)
    # H1: abbreviations and repeated flags
    rc, out = run_copy(sp, "arm0", "--d8-dir", a.d8_dir, "--arm", "x", "--fixture-r", root,
                       "--fixture-pi", vc, "--fixture-pa", "*.md", "--work-dir", os.path.join(tmp, "w"))
    check("H1: abbreviated --fixture-r/--fixture-pi/--fixture-pa are not accepted",
          rc == 2 and "unrecognized arguments" in out and not os.path.exists(
              os.path.join(sp, "results", "prereg2", "arm0", "x.json")), out[-300:])
    commit_all(g, "that transcript")
    rc, out = run_copy(sp, "arm0", "--d8-dir", a.d8_dir, "--arm", "zzz", "--arm", "cncf-toc",
                       "--work-dir", os.path.join(tmp, "w"))
    check("H1: a repeated --arm is refused", rc == 2 and "given more than once" in out, out[-200:])
    commit_all(g, "that transcript")
    rc, out = run_copy(sp, "--he")
    check("H1: no abbreviation at the top level either: --he is not --help", rc == 2 and "usage:" in out, out[-200:])
    commit_all(g, "that transcript")
    rc, out = run_copy(sp, "tier-run", "--agent-c", "/bin/true")
    check("H1: an abbreviated --agent-c does not reach --agent-cmd", rc == 2 and "unrecognized" in out, out[-200:])
    commit_all(g, "that transcript")
    for flag, val in (("--sample-e", "10"), ("--modes", "E"), ("--out-dir", os.path.join(tmp, "o"))):
        rc, out = run_copy(sp, "score", "--d8-dir", a.d8_dir, "--arm", "rust-book", "--work-dir",
                           os.path.join(tmp, "w"), flag, val)
        check(f"B3/C3: a bound score run that passes {flag} is refused", rc == 2 and f"takes no {flag}" in out,
              out[-200:])
        commit_all(g, "that transcript")
    rc, out = run_copy(sp, "aggregate", "--d8-dir", a.d8_dir, "--manifest", os.path.join(tmp, "m.json"),
                       "--fixture-ok")
    check("B3: a bound aggregate that passes --fixture-ok is refused", rc == 2 and "takes no --fixture-ok" in out,
          out[-200:])
    commit_all(g, "that transcript")
    # M1, M2
    rc, out = run_copy(sp, "validate-export", os.path.join(tmp, "nothing"), isolated=False)
    check("M1: run without python3 -I, the harness refuses", rc == 2 and "python3 -I" in out, out[-200:])
    rc, out = run_copy(sp, "validate-export", os.path.join(tmp, "nothing"), direct=True)
    check("M1: run through its shebang, it is isolated and runs", "python3 -I" not in out and "EXPORT VALIDATOR" in out,
          out[-200:])
    commit_all(g, "those transcripts")
    rc, out = run_copy(sp, "arm0", "--d8-dir", a.d8_dir, "--arm", "rust-book", "--unbound", "--work-dir",
                       os.path.join(tmp, "w"), "--out-dir", os.path.join(tmp, "o"), "--transcript-dir",
                       os.path.join(tmp, "m2t"))
    check("M2: --unbound without --fixture-repo never opens a real bundle", rc == 2 and "never opens" in out,
          out[-200:])
    forged = os.path.join(tmp, "d8-forged")
    shutil.copytree(a.d8_dir, forged, ignore=shutil.ignore_patterns("__pycache__"))
    forge = ("import importlib.util, importlib._bootstrap_external as be, os, sys\n"
             "src = os.path.join(sys.argv[1], 'anchor_eval.py'); st = os.stat(src)\n"
             "code = compile(open(src).read() + \"\\nimport sys as _s; _s.stderr.write('FORGED PYC LOADED\\\\n')\\n\", src, 'exec')\n"
             "out = importlib.util.cache_from_source(src); os.makedirs(os.path.dirname(out), exist_ok=True)\n"
             "open(out, 'wb').write(be._code_to_timestamp_pyc(code, int(st.st_mtime), st.st_size))\n")
    subprocess.run([sys.executable, "-I", "-c", forge, forged], check=True)
    probe = subprocess.run([sys.executable, "-I", "-c", "import sys; sys.path.insert(0, sys.argv[1]); import anchor_eval",
                            forged], capture_output=True, text=True)
    check("M1: the forged .pyc is loaded by a plain import (so the check can fail)",
          "FORGED PYC LOADED" in probe.stderr, probe.stderr[-100:])
    fx_repo = os.path.join(tmp, "m1fx")
    fpin, _ = fixture_repo(fx_repo, [("t", {"a.md": d("# A", "Some prose that is long enough.")})])
    rc, out = run_copy(sp, "arm0", "--d8-dir", forged, "--arm", "x", "--fixture-repo", fx_repo, "--fixture-pin",
                       fpin, "--fixture-pathspec", "*.md", "--transcript-dir", os.path.join(tmp, "m1t"),
                       "--out-dir", os.path.join(tmp, "m1o"))
    check("M1: the harness never reads it: its verified D8 sources are compiled afresh",
          rc == 0 and "FORGED PYC LOADED" not in out, out[-200:])
    # aggregate: unbound inputs, pins and bundles, sample sizes
    a0 = os.path.join(tmp, "ub-a0")
    os.makedirs(a0)
    json.dump({"arm": "k8s-en", "bound": False, "passes_bar": True}, open(os.path.join(a0, "k8s-en.json"), "w"))
    os.makedirs(os.path.join(tmp, "ub-sc", "k8s-en"))
    json.dump({"arm": "k8s-en", "bound": False, "modes": []}, open(os.path.join(tmp, "ub-sc", "k8s-en", "status.json"), "w"))
    mp = os.path.join(tmp, "ub-m.json")
    from p2 import corpus as K
    from p2 import export as X
    sha = X.seal(mp)
    common = ["--d8-dir", a.d8_dir, "--manifest", mp, "--manifest-sha", sha, "--state-dir",
              os.path.join(tmp, "ub-st"), "--repro-dir", os.path.join(tmp, "ub-rp"), "--out",
              os.path.join(tmp, "ub-v.json"), "--transcript-dir", os.path.join(tmp, "ub-t"), "--unbound",
              "--score-dir", os.path.join(tmp, "ub-sc")]
    rc, out = run_copy(sp, "aggregate", *common, "--arm0-dir", a0)
    check("B5-13: aggregate refuses an unbound Arm 0 result (without --fixture-ok)",
          rc == 2 and "is not a bound output" in out and "k8s-en.json" in out, out[-200:])
    a0b = os.path.join(tmp, "ub-a0b")
    os.makedirs(a0b)
    good_pin = {"pin": K.ARMS["k8s-en"]["pin"], "bundle_sha256": K.bundles()["kubernetes-website"]["sha256"]}
    json.dump(dict(arm="k8s-en", bound=True, passes_bar=True, pin="0" * 40, bundle_sha256=good_pin["bundle_sha256"]),
              open(os.path.join(a0b, "k8s-en.json"), "w"))
    rc, out = run_copy(sp, "aggregate", *common, "--arm0-dir", a0b)
    check("H1: aggregate refuses an Arm 0 result not run at its arm's pin", rc == 2 and "was not run at" in out,
          out[-200:])
    json.dump(dict(arm="k8s-en", bound=True, passes_bar=True, pin=good_pin["pin"], bundle_sha256="0" * 64),
              open(os.path.join(a0b, "k8s-en.json"), "w"))
    rc, out = run_copy(sp, "aggregate", *common, "--arm0-dir", a0b)
    check("H1: ... or not from its committed bundle", rc == 2 and "was not run at" in out, out[-200:])
    json.dump(dict(arm="k8s-en", bound=True, passes_bar=True, **good_pin), open(os.path.join(a0b, "k8s-en.json"), "w"))
    rc, out = run_copy(sp, "aggregate", *common, "--arm0-dir", a0b)
    check("B5-14: aggregate refuses an unbound score result (without --fixture-ok)",
          rc == 2 and "is not a bound output" in out, out[-200:])
    json.dump(dict(arm="k8s-en", bound=True, modes=["E"], sample_e=10, sample_s=500, modes_requested=["E"],
                   **good_pin), open(os.path.join(tmp, "ub-sc", "k8s-en", "status.json"), "w"))
    rc, out = run_copy(sp, "aggregate", *common, "--arm0-dir", a0b)
    check("B3: aggregate refuses a score run that was not §6.5's (1,000 and 500, all four modes)",
          rc == 2 and "1,000 and 500" in out, out[-200:])
    rc, out = run_copy(sp, "arm0", "--d8-dir", a.d8_dir, "--arm", "x", "--fixture-repo", root,
                       "--fixture-pin", vc, "--fixture-pathspec", "*.md", "--transcript-dir",
                       os.path.join(tmp, "ft"), "--out-dir", os.path.join(sp, "results", "prereg2", "arm0"))
    check("B10: a fixture run may not write under results/prereg2/ (a bound Arm 0 result cannot be "
          "overwritten)", rc == 2 and "may not write under" in out, out[-200:])
    rc, out = run_copy(sp, "export", "--d8-dir", a.d8_dir, "--unbound", "--manifest", mp, "--manifest-sha", sha,
                       "--out", os.path.join(tmp, "o2"), "--score-dir", os.path.join(tmp, "ub-sc"))
    check("B10/A7: an unbound run that names no --transcript-dir is refused, and its transcript is "
          "written where bound ones go, to be committed", rc == 2 and "must name --transcript-dir" in out
          and any(t.endswith("-export.txt") for t in transcripts(sp)), out[-200:])
    commit_all(g, "that transcript")
    st, rs = BD.check(sp, "arm0", "cmspec")
    check("the binding check over the copy is still clean at the end (the refusals above were committed)",
          st["bound"], rs)


def t_preflight(a, tmp):
    section("Review C3, re-review H3: aggregate's transcript preflight")
    import prereg2
    from p2 import binding as BD
    from p2 import tierrun as TRN
    sp = os.path.join(tmp, "pf", "spike")
    td = os.path.join(sp, "results", "prereg2", "transcripts")
    os.makedirs(td)

    def tw(name, bound=True, executed=True):
        open(os.path.join(td, name), "w").write(
            f"# prereg2\n# harness bound: {bound}\n" + ("\n# executed: now\n" if executed else ""))
        tag = BD.transcript_tag(name)
        if executed and bound:
            cmd, _, arm = tag.partition("-")
            mp = os.path.join(sp, BD.marker_rel(cmd, arm or None))
            os.makedirs(os.path.dirname(mp), exist_ok=True)
            open(mp, "w").write("{}\n")
    tw("2026-10-10T000000Z-arm0-k8s-en.txt")
    tw("2026-10-11T000000Z-score-k8s-en.txt")
    tw("2026-10-12T000000Z-export.txt")
    tw("2026-10-12T010000Z-arm0-k8s-en.txt", executed=False)
    check("C3/H3: one executed bound transcript per arm0, score and export passes, and a refused run "
          "beside it does not count", prereg2.transcript_preflight(sp, ["k8s-en"], ["k8s-en"]) == [],
          prereg2.transcript_preflight(sp, ["k8s-en"], ["k8s-en"]))
    os.rename(os.path.join(td, "2026-10-10T000000Z-arm0-k8s-en.txt"), os.path.join(tmp, "held.txt"))
    tw("2026-10-10T010000Z-arm0-k8s-en.txt", bound=False)
    bad = prereg2.transcript_preflight(sp, ["k8s-en"], ["k8s-en"])
    check("N26: an arm whose only executed arm0 transcript is unbound is refused",
          any("arm0-k8s-en" in b for b in bad), bad)
    os.rename(os.path.join(tmp, "held.txt"), os.path.join(td, "2026-10-10T000000Z-arm0-k8s-en.txt"))
    bad = prereg2.transcript_preflight(sp, ["k8s-en"], ["k8s-en"])
    check("C3: a second executed arm0 transcript for an arm, even unbound, is refused",
          any("arm0-k8s-en" in b for b in bad), bad)
    os.remove(os.path.join(td, "2026-10-10T010000Z-arm0-k8s-en.txt"))
    tw("2026-10-13T000000Z-export.txt")
    bad = prereg2.transcript_preflight(sp, ["k8s-en"], ["k8s-en"])
    check("C3b: a second executed export transcript is refused", any(b.startswith("export:") for b in bad), bad)
    os.remove(os.path.join(td, "2026-10-13T000000Z-export.txt"))
    check("C3: a scored arm with no score transcript is refused",
          any("score-cncf-toc" in b for b in prereg2.transcript_preflight(sp, ["k8s-en"], ["k8s-en", "cncf-toc"])))
    os.remove(os.path.join(sp, BD.marker_rel("score", "k8s-en")))
    check("H3: an executed transcript with no execution marker is refused",
          any("no execution marker" in b for b in prereg2.transcript_preflight(sp, ["k8s-en"], ["k8s-en"])))
    open(os.path.join(sp, BD.marker_rel("score", "k8s-en")), "w").write("{}\n")
    st = os.path.join(sp, "results", "prereg2")
    TRN.append_ledger(st, {"event": "started", "n": 1})
    check("C3: a started tiering run with no transcript is refused",
          any("no committed transcript" in b for b in prereg2.transcript_preflight(sp, ["k8s-en"], ["k8s-en"])))
    tw("2026-10-13T000000Z-tier-run.txt", executed=False)
    os.makedirs(os.path.join(st, "tier-work-1"))
    open(os.path.join(st, "tier-work-1", "tiers.jsonl"), "w").write('{"packet": "x"}\n')
    TRN.append_ledger(st, {"event": "started", "n": 2})
    tw("2026-10-14T000000Z-tier-run.txt", executed=False)
    bad = prereg2.transcript_preflight(sp, ["k8s-en"], ["k8s-en"])
    check("C3: two tiering runs where the first wrote lines are refused", any("first wrote lines" in b for b in bad), bad)
    open(os.path.join(st, "tier-work-1", "tiers.jsonl"), "w").write("")
    check("C3: two tiering runs where the first wrote none pass",
          prereg2.transcript_preflight(sp, ["k8s-en"], ["k8s-en"]) == [], prereg2.transcript_preflight(sp, ["k8s-en"], ["k8s-en"]))
    n, path = TRN.binding_run(st)
    check("C2: then the second run's tiers bind", n == 2 and path.endswith("tier-work-2/tiers.jsonl"), (n, path))


class FakeTr:
    def __init__(self, bound, vc):
        self.state = {"bound": bound, "validation_commit": vc}


def bound_fixture(tmp, name="bf"):
    """A copy of this harness whose rust-book arm points at a fixture corpus
    bundled here, sealed and committed as its own validation commit. Bound
    runs on it open only the fixture bundle; every other arm's bundle is
    absent."""
    import hashlib
    import re
    corp = os.path.join(tmp, name + "-corpus")
    commits = [(f"c{v}", {"a.md": d("# A", f"Paragraph one of the fixture, version {v}, long enough.",
                                    "Paragraph two stays the same across versions here.",
                                    f"Paragraph three, edition {v % 3}, also long enough.")})
               for v in range(8)]
    pin, cg = fixture_repo(corp, commits)
    bdir = os.path.join(tmp, name + "-bundles")
    os.makedirs(bdir)
    cg("bundle", "create", "-q", os.path.join(bdir, "rust-book.bundle"), "HEAD")
    bsha = hashlib.sha256(open(os.path.join(bdir, "rust-book.bundle"), "rb").read()).hexdigest()
    root, sp, g = binding_repo(tmp, name)
    cpath = os.path.join(sp, "harness", "p2", "corpus.py")
    src = open(cpath).read()
    src2 = re.sub(r'"rust-book": \{"bundle": "rust-book", "pin": "[0-9a-f]{40}",\n                  "pathspec": "src/\*\.md", "prefix": "src/"\}',
                  f'"rust-book": {{"bundle": "rust-book", "pin": "{pin}",\n                  "pathspec": "*.md", "prefix": ""}}', src)
    assert src2 != src
    open(cpath, "w").write(src2)
    bj = os.path.join(sp, "harness", "p2", "bundles.json")
    meta = json.load(open(bj))
    meta["rust-book"] = {"sha256": bsha, "bytes": os.path.getsize(os.path.join(bdir, "rust-book.bundle")),
                         "head": pin}
    open(bj, "w").write(json.dumps(meta, indent=1) + "\n")
    commit_all(g, "fixture arm")
    manifest = os.path.join(tmp, name + "-manifest.json")
    rc, out = run_copy(sp, "seal", "--manifest", manifest)
    assert rc == 0, out
    commit_all(g, "validation")
    return root, sp, g, bdir, manifest


def run_bound(sp, bdir, *args):
    env = dict(os.environ, **GIT_ENV, PREREG2_BUNDLE_DIR=bdir)
    r = subprocess.run([sys.executable, "-I", "-S", "-B", os.path.join(sp, "harness", "prereg2.py"), *args],
                       capture_output=True, text=True, env=env)
    return r.returncode, r.stdout + r.stderr


def t_round5(a, tmp):
    section("Round 5: bound runs end to end on a fixture arm (H-1, N11, N14, N15)")
    from p2 import binding as BD
    root, sp, g, bdir, manifest = bound_fixture(tmp)
    cd = BD.common_dir(sp)
    w = lambda n: os.path.join(tmp, "bfw-" + n)  # noqa: E731
    empty = os.path.join(tmp, "bf-nobundles")
    os.makedirs(empty)
    rc, out = run_bound(sp, empty, "arm0", "--d8-dir", a.d8_dir, "--arm", "rust-book", "--work-dir", w("1"))
    check("N14: an arm0 whose bundle cannot be opened writes no marker, in the work tree or the git dir",
          rc != 0 and not os.path.exists(os.path.join(sp, BD.marker_rel("arm0", "rust-book")))
          and not os.path.exists(os.path.join(cd, "prereg2", "arm0-rust-book.json")), out[-200:])
    commit_all(g, "the failed arm0's transcript")
    g("checkout", "-q", "-b", "gap-before-arm0")
    write_gap(sp, [gap_entry()])
    commit_all(g, "a gap before Arm 0")
    rc, out = run_bound(sp, bdir, "arm0", "--d8-dir", a.d8_dir, "--arm", "rust-book", "--work-dir", w("2b"))
    check("MEDIUM-1: a gap declared before Arm 0 stops arm0 too (§9: it stops the work)",
          rc == 2 and "stops the work" in out and not os.path.exists(os.path.join(sp, BD.marker_rel("arm0", "rust-book"))),
          out[-200:])
    g("checkout", "-q", "-f", "main")
    g("clean", "-q", "-fd", "spike")
    g("branch", "-q", "-D", "gap-before-arm0")
    rc, out = run_bound(sp, bdir, "arm0", "--d8-dir", a.d8_dir, "--arm", "rust-book", "--work-dir", w("2"))
    tx = [open(os.path.join(sp, "results", "prereg2", "transcripts", t)).read() for t in transcripts(sp)
          if t.endswith(("-arm0-rust-book.txt", "-arm0-rust-book.2.txt"))]
    check("H3: ... so the next arm0 runs, bound, and executes",
          rc == 0 and any("# harness bound: True" in t and "\n# executed: " in t for t in tx), out[-300:])
    check("M-a: its marker is in the work tree and in the common git directory",
          os.path.exists(os.path.join(sp, BD.marker_rel("arm0", "rust-book")))
          and os.path.exists(os.path.join(cd, "prereg2", "arm0-rust-book.json")))
    commit_all(g, "arm0 rust-book")
    rc, out = run_bound(sp, bdir, "arm0", "--d8-dir", a.d8_dir, "--arm", "rust-book", "--work-dir", w("3"))
    check("H3: a second arm0 rust-book is refused", rc == 2 and "already executed" in out, out[-200:])
    commit_all(g, "refused")
    write_gap(sp, [gap_entry(cells=(("rust-book", "E", "Q"),))])
    commit_all(g, "a gap between Arm 0 and scoring")
    rc, out = run_bound(sp, empty, "score", "--d8-dir", a.d8_dir, "--arm", "rust-book", "--work-dir", w("4"))
    check("H-1: a score whose bundle cannot be opened leaves no score/<arm>/ and no marker",
          rc != 0 and not os.path.exists(os.path.join(sp, "results", "prereg2", "score", "rust-book"))
          and not os.path.exists(os.path.join(sp, BD.marker_rel("score", "rust-book"))), out[-200:])
    commit_all(g, "the failed score's transcript")
    rc, out = run_bound(sp, bdir, "score", "--d8-dir", a.d8_dir, "--arm", "rust-book", "--work-dir", w("5"))
    check("H-1: ... so the next score runs and executes", rc == 0 and os.path.exists(
        os.path.join(sp, "results", "prereg2", "score", "rust-book", "status.json")), out[-300:])
    commit_all(g, "score rust-book")
    rc, out = run_bound(sp, bdir, "score", "--d8-dir", a.d8_dir, "--arm", "rust-book", "--work-dir", w("6"))
    check("N11: a second score rust-book is refused by its marker", rc == 2 and "already executed" in out, out[-200:])
    commit_all(g, "refused")
    g("checkout", "-q", "-b", "per-arm")
    os.makedirs(os.path.join(sp, "results", "prereg2", "score", "zz"))
    open(os.path.join(sp, "results", "prereg2", "score", "zz", "status.json"), "w").write("{}\n")
    commit_all(g, "a second arm's score, in its own commit, as the score PR does")
    rc, out = run_bound(sp, bdir, "score", "--d8-dir", a.d8_dir, "--arm", "cncf-toc", "--work-dir", w("6b"))
    check("MEDIUM-1: score's gap preflight does not take the score PR's per-arm commits for scoring-arm commits",
          "commits add" not in out and "no Arm 0 result for cncf-toc" in out, out[-200:])
    g("checkout", "-q", "-f", "main")
    g("clean", "-q", "-fd", "spike")
    g("branch", "-q", "-D", "per-arm")
    rc, out = run_bound(sp, bdir, "export", "--d8-dir", a.d8_dir, "--manifest", manifest)
    check("N15: export runs bound and writes its marker", rc == 0 and os.path.exists(
        os.path.join(sp, BD.marker_rel("export", None))), out[-300:])
    commit_all(g, "export")
    rc, out = run_bound(sp, bdir, "export", "--d8-dir", a.d8_dir, "--manifest", manifest)
    check("N15: a second export is refused", rc == 2 and "already executed" in out, out[-200:])
    commit_all(g, "refused")
    agg = ["aggregate", "--d8-dir", a.d8_dir, "--manifest", manifest]
    rc, out = run_bound(sp, bdir, *agg)
    v = json.load(open(os.path.join(sp, "results", "prereg2", "verdict.json"))) if rc == 0 else {}
    c = v.get("cells", {}).get("rust-book|E|Q", {})
    check("G11: the bound CLI aggregate reads gaps.json: a gap between Arm 0 and scoring makes its cell NO VERDICT",
          rc == 0 and v.get("bound") is True and c.get("verdict") == "NO VERDICT" and "§9 gap" in c.get("reason", ""),
          (rc, out[-200:], c))
    commit_all(g, "verdict")
    open(os.path.join(sp, "results", "prereg2", "gaps.json"), "w").write("{not json\n")
    commit_all(g, "a malformed gaps.json after scoring")
    rc, out = run_bound(sp, bdir, *agg)
    check("MEDIUM-1: a malformed gaps.json after the scoring-arm commit does not stop aggregate; it is listed",
          rc == 0 and "malformed" in out and "alters no cell" in out, out[-300:])
    commit_all(g, "verdict again")
    rc, out = run_bound(sp, bdir, "tier-run", "--agent-cmd", "/bin/true")
    check("N18: a bound tier-run that names --agent-cmd is refused", rc == 2 and "takes no --agent-cmd" in out,
          out[-200:])
    commit_all(g, "refused")
    rc, out = run_bound(sp, bdir, "arm0", "--d8-dir", a.d8_dir, "--arm", "cncf-toc", "--work-dir", w("7"),
                        "--fixture-pin", "0" * 40)
    check("N19: a bound run that names --fixture-pin is refused", rc == 2 and "takes no --fixture-pin" in out,
          out[-200:])
    commit_all(g, "refused")
    rc, out = run_bound(sp, bdir, "arm0", "--d8-dir", a.d8_dir, "--arm=zzz", "--arm=cncf-toc", "--work-dir", w("8"))
    check("N16: a repeated --opt=value is refused", rc == 2 and "given more than once" in out, out[-200:])
    commit_all(g, "refused")
    rc, out = run_bound(sp, bdir, "arm0", "--d8-dir", a.d8_dir, "--arm", "cncf-toc", "--work-dir", w("9"),
                        "--fixture-repo=")
    check("N17: an option that reads unbound but parses bound (--fixture-repo=) is refused",
          rc == 2 and "parse differently" in out, out[-200:])
    commit_all(g, "refused")

    section("Round 5: a marker survives every escape (M-a)")
    st, rs = BD.check(sp, "arm0", "cmspec")
    check("M-a: before any escape test, arm0 cmspec is allowed", st["bound"], rs)
    mk = os.path.join(sp, BD.marker_rel("arm0", "cmspec"))
    open(mk, "w").write("{}\n")
    st, rs = BD.check(sp, "arm0", "cmspec")
    check("N10: an uncommitted work-tree marker (with no git-dir copy) blocks the arm",
          not st["bound"] and any("already executed" in r for r in rs), rs)
    os.remove(mk)
    g("checkout", "-q", "-b", "abandoned")
    open(os.path.join(sp, BD.marker_rel("arm0", "cncf-toc")), "w").write("{}\n")
    commit_all(g, "a marker on a PR branch")
    g("checkout", "-q", "main")
    st, rs = BD.check(sp, "arm0", "cncf-toc")
    check("N9: a marker committed only on another branch blocks the arm (git log --all)",
          not st["bound"] and any("already executed" in r for r in rs), rs)
    g("branch", "-q", "-D", "abandoned")
    st, rs = BD.check(sp, "arm0", "cncf-toc")
    check("M-a: ... and still after that branch is deleted (git log --reflog)",
          not st["bound"] and any("already executed" in r for r in rs), rs)
    BD.mark_executed(sp, "arm0", "site-policy", os.path.join(tmp, "x.txt"))
    os.remove(os.path.join(sp, BD.marker_rel("arm0", "site-policy")))
    g("clean", "-q", "-fd", "spike/results")
    st, rs = BD.check(sp, "arm0", "site-policy")
    check("M-a: an uncommitted marker removed with rm and git clean still blocks the arm (git-dir copy)",
          not st["bound"] and any("already executed" in r for r in rs), rs)
    wt2 = os.path.join(tmp, "bf-wt2")
    g("worktree", "add", "-q", "--detach", wt2)
    st, rs = BD.check(os.path.join(wt2, "spike"), "arm0", "site-policy")
    check("M-a: a second git worktree cannot run the arm again", not st["bound"]
          and any("already executed" in r for r in rs), rs)
    st, rs = BD.check(os.path.join(wt2, "spike"), "arm0", "k8s-en")
    check("M-a: ... though it may run an arm that has not executed", st["bound"], rs)
    g("worktree", "remove", "--force", wt2)

    section("Round 5: the derivation's history (M-c)")
    hx = os.path.join(tmp, "dbl")
    _, hg = fixture_repo(hx, [("base", {"spike/x.md": "x\n"})])
    hg("checkout", "-q", "-b", "side")
    os.makedirs(os.path.join(hx, "spike", "results", "prereg2"), exist_ok=True)
    open(os.path.join(hx, "spike", BD.VALIDATION_REL), "w").write(json.dumps({"manifest_sha256": "ab" * 32}) + "\n")
    hg("add", "-A")
    hg("commit", "-q", "-m", "side adds VALIDATION")
    hg("checkout", "-q", "main")
    os.makedirs(os.path.join(hx, "spike", "results", "prereg2"), exist_ok=True)
    open(os.path.join(hx, "spike", BD.VALIDATION_REL), "w").write(json.dumps({"manifest_sha256": "ab" * 32}) + "\n")
    hg("add", "-A")
    hg("commit", "-q", "-m", "main adds the same VALIDATION")
    hg("merge", "-q", "--no-edit", "side")
    vc_, _, rs = BD.derive_validation(os.path.join(hx, "spike"))
    check("M-c: VALIDATION added on both sides of a merge counts twice (--full-history), and is refused",
          vc_ is None and any("2 commits" in r for r in rs), rs)
    sh = os.path.join(tmp, "shallow")
    subprocess.run(["git", "clone", "-q", "--depth", "1", "file://" + root, sh], check=True,
                   env=dict(os.environ, **GIT_ENV), capture_output=True)
    st, rs = BD.check(os.path.join(sh, "spike"), "arm0", "k8s-l10n")
    check("M-c: a shallow clone is refused", not st["bound"] and any("shallow" in r for r in rs), rs)
    rp = os.path.join(tmp, "replaced")
    subprocess.run(["git", "clone", "-q", root, rp], check=True, env=dict(os.environ, **GIT_ENV), capture_output=True)
    subprocess.run(["git", "-C", rp, "replace", "--graft", "HEAD"], check=True, env=dict(os.environ, **GIT_ENV),
                   capture_output=True)
    st, rs = BD.check(os.path.join(rp, "spike"), "arm0", "k8s-l10n")
    check("M-c: a history rewritten by git replace is refused", not st["bound"]
          and any("replace refs" in r for r in rs), rs)
    gr = os.path.join(tmp, "grafted")
    subprocess.run(["git", "clone", "-q", root, gr], check=True, env=dict(os.environ, **GIT_ENV), capture_output=True)
    head = subprocess.run(["git", "-C", gr, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    open(os.path.join(gr, ".git", "info", "grafts"), "w").write(head + "\n")
    st, rs = BD.check(os.path.join(gr, "spike"), "arm0", "k8s-l10n")
    check("M-c: a history rewritten by info/grafts is refused", not st["bound"]
          and any("grafts" in r for r in rs), rs)
    st0, _ = BD.check(sp, "arm0", "k8s-l10n")
    saved = {k: os.environ.get(k) for k in ("GIT_DIR", "GIT_WORK_TREE")}
    os.environ["GIT_DIR"] = os.path.join(hx, ".git")
    os.environ["GIT_WORK_TREE"] = hx
    try:
        st1, rs1 = BD.check(sp, "arm0", "k8s-l10n")
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    check("M-c: GIT_DIR and GIT_WORK_TREE in the environment do not redirect the binding check",
          st1["validation_commit"] == st0["validation_commit"] and st1["bound"] == st0["bound"], (st1, rs1))

    section("Round 5: smaller survivors (N3, N6, N7, N13, N21-N28, N33)")
    ex = os.path.join(tmp, "extra")
    fixture_repo(ex, [("v", {"spike/results/prereg2/VALIDATION": json.dumps(
        {"manifest_sha256": "ab" * 32, "note": "x"}) + "\n"})])
    vcx, msx, rsx = BD.derive_validation(os.path.join(ex, "spike"))
    check("N3: a VALIDATION with any field besides manifest_sha256 is refused", msx is None and rsx, rsx)
    orc = os.path.join(sp, "ORACLE.md")
    o0 = open(orc).read()
    open(orc, "a").write("\nedited\n")
    st, rs = BD.check(sp, "arm0", "k8s-l10n")
    check("N6: an edited ORACLE.md is not bound", not st["bound"] and any("ORACLE.md" in r for r in rs), rs)
    open(orc, "w").write(o0)
    tgt = os.path.join(sp, "harness", "p2", "tiers.py")
    real = os.path.join(tmp, "tiers-real.py")
    shutil.copy(tgt, real)
    g("update-index", "--assume-unchanged", "spike/harness/p2/tiers.py")
    os.remove(tgt)
    os.symlink(real, tgt)
    st, rs = BD.check(sp, "arm0", "k8s-l10n")
    check("N7: a harness file replaced by a symlink to identical bytes, hidden with --assume-unchanged, is not bound",
          not st["bound"] and any("not a regular file" in r for r in rs), rs)
    os.remove(tgt)
    shutil.copy(real, tgt)
    g("update-index", "--no-assume-unchanged", "spike/harness/p2/tiers.py")
    check("N13: a transcript's .<n> suffix is not part of its tag",
          BD.transcript_tag("2026-10-08T000000Z-arm0-cmspec.2.txt") == "arm0-cmspec"
          and BD.transcript_tag("2026-10-08T000000Z-export.txt") == "export")
    import prereg2
    vca, vcb = "a" * 40, "b" * 40
    r = raised(lambda: prereg2.check_input_binding({"bound": True, "binding": {"validation_commit": vcb}},
                                                   "x", FakeTr(True, vca), False))
    check("N22: a bound input from another validation commit is refused", r and "not a bound output" in r, r)
    rd = os.path.join(tmp, "rp")
    os.makedirs(rd)
    json.dump({"id": "r1", "ok": True, "bound": True, "binding": {"validation_commit": vcb},
               "committed_sha256": "c" * 64, "regenerated_sha256": "c" * 64}, open(os.path.join(rd, "r.json"), "w"))
    check("N23: a reproduction from another validation commit is not bound",
          prereg2.load_repro(rd, FakeTr(True, vca), False)["r1"]["bound"] is False)
    check("N24: score refuses an Arm 0 result of another validation commit",
          not prereg2.arm0_input_ok({"bound": True, "binding": {"validation_commit": vcb}}, FakeTr(True, vca))
          and prereg2.arm0_input_ok({"bound": True, "binding": {"validation_commit": vca}}, FakeTr(True, vca)))
    r = raised(lambda: prereg2.check_pin_and_bundle({"arm": "k8s-en", "no_verdict": "x", "pin": "0" * 40,
                                                      "bundle_sha256": "0" * 64}, "x"))
    check("N21: a no-verdict input that names a wrong pin is refused", r and "was not run at" in r, r)
    from p2 import oracle as O
    check("N27: with t undefined, a twin of k in M's first unit makes the verdict undecidable",
          O.repeat_rule(["X", "Y"], ["X", "Z"], lambda i: None, 0, None) is False)
    base = ("## Alpha\n\nFailed jobs are retried three times\nbefore an alert is raised\nto the on-call engineer.\n\n"
            "## Beta\n\nExports are written to the archive bucket nightly.\n")
    after = ("Failed jobs are retried three times\nbefore an alert is raised\nto the on-call engineer.\n\n"
             "## Alpha\n\nExports are written to the archive bucket nightly.\n\n"
             "## Alpha\n\nExports are written to the archive bucket nightly.\n")
    r = one(inst1(base, after), "R", name="alpha")
    check("N28: p in no unit is not taken as the first unit: with a twin of that unit elsewhere, still decided",
          r and r["oracle"] == "SURVIVED" and r["decided"], r and (r["oracle"], r["target"]))
    from p2 import tierrun as TRN
    st_dir = os.path.join(tmp, "n33")
    os.makedirs(st_dir)
    json.dump({"model": "claude-opus-5-5", "why": "x", "scoring_commit": "f" * 40}, open(os.path.join(st_dir, "tier-model.json"), "w"))
    mp = os.path.join(tmp, "n33-m.json")
    from p2 import export as X
    msha = X.seal(mp)
    exp = os.path.join(tmp, "n33-export")
    X.export(exp, X.load_manifest(mp, msha), [], {})
    oldr = os.path.join(tmp, "n33-repo")
    oc, _ = fixture_repo(oldr, [("s", {"x.md": "x\n"})])
    r = raised(lambda: TRN.run(exp, st_dir, oldr, oc, "late", "/bin/true", log=lambda *x: None))
    check("N33: tier-run refuses a tier-model.json chosen for another scoring-arm commit",
          r and "another scoring-arm commit" in r, r)
    sc = os.path.join(tmp, "n25", "k8s-en")
    os.makedirs(sc)
    from p2 import corpus as K
    json.dump(dict(arm="k8s-en", bound=True, binding={"validation_commit": vca}, modes=["E"], sample_e=1000,
                   sample_s=500, modes_requested=["E"], pin=K.ARMS["k8s-en"]["pin"],
                   bundle_sha256=K.bundles()["kubernetes-website"]["sha256"]), open(os.path.join(sc, "status.json"), "w"))
    r = raised(lambda: prereg2.load_scores(os.path.dirname(sc), FakeTr(True, vca)))
    check("N25: a score that did not request all four modes is refused", r and "1,000 and 500" in r, r)

    section("Round 5: module loading (M-d)")
    forged = os.path.join(tmp, "d8-planted")
    shutil.copytree(a.d8_dir, forged, ignore=shutil.ignore_patterns("__pycache__"))
    open(os.path.join(forged, "colorsys.py"), "w").write("import sys\nsys.stderr.write('PLANTED STDLIB MODULE\\n')\n")
    pr = subprocess.run([sys.executable, "-I", "-S", "-B", "-c",
                         "import sys; sys.path.insert(0, sys.argv[1]); from p2 import mech; mech.load(sys.argv[2]); "
                         "import colorsys; print(colorsys.__file__)", HERE, forged], capture_output=True, text=True)
    check("M-d: after loading --d8-dir, a module planted there does not shadow the standard library",
          pr.returncode == 0 and "PLANTED" not in pr.stderr and forged not in pr.stdout, (pr.stdout, pr.stderr[-200:]))
    r2, sp2, g2 = binding_repo(tmp, "shadow")
    pk = os.path.join(sp2, "harness", "p2", "binding")
    os.makedirs(pk)
    shutil.copy(os.path.join(sp2, "harness", "p2", "binding.py"), os.path.join(pk, "__init__.py"))
    rc, out = run_copy(sp2, "validate-export", os.path.join(tmp, "nothing"), "--unbound", "--transcript-dir",
                       os.path.join(tmp, "shadow-t"))
    check("M-d: an untracked p2/binding/ package that shadows binding.py is refused",
          rc == 2 and "p2.binding was loaded from" in out, out[-300:])
    rc, out = run_copy(sp, "validate-export", os.path.join(tmp, "nothing"), "--unbound", "--transcript-dir",
                       os.path.join(tmp, "nosite-t"), flags=["-I", "-B"])
    check("M-d: run without -S (so a .pth file could run), the harness refuses",
          rc == 2 and "-I -S" in out, out[-200:])


def t_gaps(a, tmp):
    section("§9's gap rule, implemented (M-e)")
    from p2 import aggregate as AG
    from p2 import gaps as GP
    from p2 import corpus as K
    m = manifest_for_test()
    recs = [wrong_rec("k8s-en", "E", "w1")] + [syn("k8s-en", "E", "Q", f"u{i}") for i in range(400)]
    res = AG.aggregate({"k8s-en": {"passes_bar": True}}, syn_scores("k8s-en", recs), m, good_tiers(m), {},
                       {("k8s-en", "E", "Q"): "gap G1 (LOG §21): the E enumerator cannot follow renames"})
    c = res["cells"][("k8s-en", "E", "Q")]
    check("M-e: a declared gap makes its cell NO VERDICT, whatever it would have been, and names the gap",
          c["verdict"] == "NO VERDICT" and "gap G1 (LOG §21)" in c["reason"] and "without_the_gap" in c, c)
    check("M-e: ... and leaves other cells alone",
          res["cells"][("k8s-en", "E", "R")]["reason"] != c["reason"])
    gr = os.path.join(tmp, "gaprepo")
    log = "# log\n\n## 2026-10-09 — §21. A gap\n\ntext\n"
    entry = {"id": "G1", "log": "§21", "red_test": "results/prereg2/gaps/G1/red.txt",
             "cells": [["k8s-en", "E", "Q"]], "why": "the enumerator cannot follow renames"}
    gj = json.dumps({"gaps": [entry]}) + "\n"
    files_gap = {"spike/results/prereg2/gaps.json": gj, "spike/results/prereg2/gaps/G1/red.txt": "red\n",
                 "spike/LOG.md": log}

    def repo(name, order):
        root = os.path.join(tmp, name)
        commits = []
        for step in order:
            if step == "arm0":
                commits.append(("arm0", {"spike/results/prereg2/arm0/k8s-en.json": "{}\n"}))
            elif step == "gap":
                commits.append(("gap", files_gap))
            elif step == "score":
                commits.append(("score", {"spike/results/prereg2/score/k8s-en/status.json": "{}\n"}))
            else:
                commits.append((step, {f"spike/{step}.md": step + "\n"}))
        _, g = fixture_repo(root, commits)
        sc = g("log", "--format=%H", "--diff-filter=A", "--", "spike/results/prereg2/score")
        return os.path.join(root, "spike"), sc, g
    sp, sc, g = repo("gap-between", ["base", "arm0", "gap", "score"])
    gaps, notes = GP.load_gaps(sp, sc, K.ARMS)
    check("M-e: a gap declared between the Arm 0 commit and the scoring-arm commit makes its cells NO VERDICT",
          gaps == {("k8s-en", "E", "Q"): "gap G1 (LOG §21): the enumerator cannot follow renames"}, gaps)
    sp, sc, g = repo("gap-before", ["base", "gap", "arm0", "score"])
    r = raised(lambda: GP.load_gaps(sp, sc, K.ARMS))
    check("M-e: a gap declared before the Arm 0 commit is refused: per §9 it stops the work",
          r and "stops the work" in r, r)
    sp, sc, g = repo("gap-after", ["base", "arm0", "score", "gap"])
    got = []
    r = raised(lambda: got.append(GP.load_gaps(sp, sc, K.ARMS)))
    gaps, notes = got[0] if got else (None, [])
    check("M-e: a gap declared after the scoring-arm commit alters no cell, and is listed",
          r is None and gaps == {} and notes and "alters no cell" in notes[0], (r, gaps, notes))
    sp, sc, g = repo("gap-edited", ["base", "arm0", "gap"])
    open(os.path.join(sp, "results", "prereg2", "gaps.json"), "w").write(
        json.dumps({"gaps": [dict(entry, cells=[["cncf-toc", "E", "Q"]])]}) + "\n")
    commit_all(g, "edit the gap")
    g("checkout", "-q", "-b", "x")
    open(os.path.join(sp, "score.md"), "w").write("x\n")
    os.makedirs(os.path.join(sp, "results", "prereg2", "score", "k8s-en"))
    open(os.path.join(sp, "results", "prereg2", "score", "k8s-en", "status.json"), "w").write("{}\n")
    commit_all(g, "score")
    sc = g("log", "--format=%H", "--diff-filter=A", "--", "spike/results/prereg2/score")
    r = raised(lambda: GP.load_gaps(sp, sc, K.ARMS))
    check("M-e: a declared gap may not be edited afterwards", r and "never edited" in r, r)
    for label, bad in (("with no LOG entry", dict(entry, log="§99")),
                       ("whose red test lies outside results/prereg2/gaps/", dict(entry, red_test="harness/x.py")),
                       ("that names no real cell", dict(entry, cells=[["k8s-en", "X", "Q"]])),
                       ("with an extra key", dict(entry, extra=1))):
        root = os.path.join(tmp, "gap-bad-" + str(abs(hash(label)) % 10000))
        fl = dict(files_gap, **{"spike/results/prereg2/gaps.json": json.dumps({"gaps": [bad]}) + "\n",
                                "spike/harness/x.py": "red\n"})
        _, gg = fixture_repo(root, [("base", {"spike/a.md": "a\n"}),
                                    ("arm0", {"spike/results/prereg2/arm0/k8s-en.json": "{}\n"}),
                                    ("gap", fl), ("score", {"spike/results/prereg2/score/k8s-en/status.json": "{}\n"})])
        sc2 = gg("log", "--format=%H", "--diff-filter=A", "--", "spike/results/prereg2/score")
        r = raised(lambda: GP.load_gaps(os.path.join(root, "spike"), sc2, K.ARMS))
        why = {"with no LOG entry": "has no entry", "whose red test lies outside results/prereg2/gaps/": "must lie under",
               "that names no real cell": "is not a cell", "with an extra key": "exactly the keys"}[label]
        check(f"M-e: a gap {label} is refused", r and r.startswith("GapError") and why in r, r)
    root = os.path.join(tmp, "gap-notest")
    fl = {k: v for k, v in files_gap.items() if not k.endswith("red.txt")}
    _, gg = fixture_repo(root, [("base", {"spike/a.md": "a\n"}),
                                ("arm0", {"spike/results/prereg2/arm0/k8s-en.json": "{}\n"}),
                                ("gap", fl), ("score", {"spike/results/prereg2/score/k8s-en/status.json": "{}\n"})])
    sc2 = gg("log", "--format=%H", "--diff-filter=A", "--", "spike/results/prereg2/score")
    r = raised(lambda: GP.load_gaps(os.path.join(root, "spike"), sc2, K.ARMS))
    check("M-e: a gap whose red test is not committed is refused", r and "red test" in r, r)
    root = os.path.join(tmp, "gap-none")
    _, gg = fixture_repo(root, [("base", {"spike/a.md": "a\n"})])
    check("M-e: no gaps.json, no gap", GP.load_gaps(os.path.join(root, "spike"), "0" * 40, K.ARMS) == ({}, []))


def gap_entry(gid="G1", log="§21", cells=(("k8s-en", "E", "Q"),), why="the enumerator cannot follow renames",
              red_test=None):
    return {"id": gid, "log": log, "red_test": red_test or f"results/prereg2/gaps/{gid}/red.txt",
            "cells": [list(c) for c in cells], "why": why}


def write_gap(sp, entries, logs=("§21",), tests=True):
    os.makedirs(os.path.join(sp, "results", "prereg2"), exist_ok=True)
    open(os.path.join(sp, "results", "prereg2", "gaps.json"), "w").write(json.dumps({"gaps": entries}) + "\n")
    with open(os.path.join(sp, "LOG.md"), "a") as f:
        for s_ in logs:
            f.write(f"\n## 2026-10-09 — {s_}. A gap\n\ntext\n")
    if tests:
        for e in entries:
            p = os.path.join(sp, e["red_test"])
            if ".." not in e["red_test"]:
                os.makedirs(os.path.dirname(p), exist_ok=True)
                open(p, "w").write("red\n")


class GapRepo:
    """A repository built step by step, one commit a minute apart, so that
    history order is unambiguous."""

    def __init__(self, tmp, name):
        self.root = os.path.join(tmp, name)
        self.sp = os.path.join(self.root, "spike")
        os.makedirs(self.sp)
        self.n = 0
        self.g("init", "-q", "-b", "main")
        self.commit("base", {"a.md": "a\n"})

    def g(self, *a):
        self.n += 1
        d = f"2001-01-01T{self.n // 60:02d}:{self.n % 60:02d}:00Z"
        env = dict(os.environ, **dict(GIT_ENV, GIT_AUTHOR_DATE=d, GIT_COMMITTER_DATE=d))
        return subprocess.run(["git", "-C", self.root, *a], check=True, capture_output=True, text=True,
                              env=env).stdout.strip()

    def commit(self, msg, files=None):
        for p, t in (files or {}).items():
            fp = os.path.join(self.sp, p)
            if t is None:
                os.remove(fp)
                continue
            os.makedirs(os.path.dirname(fp), exist_ok=True)
            open(fp, "w").write(t)
        self.g("add", "-A")
        self.g("commit", "-q", "--allow-empty", "-m", msg)
        return self.g("rev-parse", "HEAD")

    def arm0(self):
        return self.commit("arm0", {"results/prereg2/arm0/k8s-en.json": "{}\n"})

    def score(self):
        return self.commit("score", {"results/prereg2/score/k8s-en/status.json": "{}\n"})

    def gap(self, entries, msg="gap", **kw):
        write_gap(self.sp, entries, **kw)
        return self.commit(msg)

    def load(self, sc="auto"):
        from p2 import corpus as K
        from p2 import gaps as GP
        if sc == "auto":
            adds = self.g("log", "--full-history", "--format=%H", "--diff-filter=A", "--",
                          "spike/results/prereg2/score").split()
            sc = adds[0] if adds else None
        got = []
        r = raised(lambda: got.append(GP.load_gaps(self.sp, sc, K.ARMS)))
        return r, (got[0] if got else (None, None))


def t_round6(a, tmp):
    section("Round 6: §9's gap rule at its boundaries (G1-G12, MEDIUM-1)")
    import prereg2
    r2 = GapRepo(tmp, "g1b")
    write_gap(r2.sp, [gap_entry()])
    r2.arm0()
    r2.score()
    err, _ = r2.load()
    check("G1: a gap declared in the Arm 0 commit itself is before Arm 0, and stops the work",
          err and "stops the work" in err, err)
    r = GapRepo(tmp, "g2")
    r.arm0()
    write_gap(r.sp, [gap_entry()])
    r.score()
    err, (gaps, notes) = r.load()
    check("G2: a gap declared in the scoring-arm commit itself alters no cell, and is listed",
          err is None and gaps == {} and any("alters no cell" in n for n in notes), (err, gaps, notes))
    r = GapRepo(tmp, "g3")
    r.arm0()
    r.g("checkout", "-q", "-b", "side")
    r.gap([gap_entry()])
    r.g("checkout", "-q", "main")
    r.score()
    r.g("merge", "-q", "--no-ff", "--no-edit", "side")
    err, (gaps, notes) = r.load()
    check("G3: a gap on a side branch merged after the scoring-arm commit is outside its history: "
          "alters no cell, listed, never refused", err is None and gaps == {} and notes, (err, gaps, notes))
    r = GapRepo(tmp, "g4")
    r.arm0()
    r.gap([gap_entry()])
    r.commit("withdraw", {"results/prereg2/gaps.json": json.dumps({"gaps": []}) + "\n"})
    r.score()
    err, _ = r.load()
    check("G4: a gap withdrawn before scoring is refused", err and "never withdrawn" in err, err)
    r = GapRepo(tmp, "g10")
    r.arm0()
    r.gap([gap_entry()])
    r.commit("delete", {"results/prereg2/gaps.json": None})
    r.score()
    err, _ = r.load()
    check("G10: a gaps.json deleted before scoring is a withdrawal, and is refused", err and "never withdrawn" in err, err)
    r = GapRepo(tmp, "g5")
    r.arm0()
    r.gap([gap_entry(), gap_entry(why="again")])
    r.score()
    err, _ = r.load()
    check("G5: two gaps with one id are refused", err and "declared twice" in err, err)
    r = GapRepo(tmp, "g6")
    r.arm0()
    e = gap_entry()
    r.gap([e], tests=False)
    r.commit("red test later", {e["red_test"]: "red\n"})
    r.score()
    err, _ = r.load()
    check("G6: a red test committed only after the gap is refused: it is checked at the gap's commit",
          err and "red test" in err, err)
    r = GapRepo(tmp, "g7")
    r.arm0()
    r.gap([gap_entry()], logs=())
    r.commit("log later", {"LOG.md": "## 2026-10-09 — §21. A gap\n"})
    r.score()
    err, _ = r.load()
    check("G7: a LOG entry written only after the gap is refused: it is checked at the gap's commit",
          err and "no entry" in err, err)
    r = GapRepo(tmp, "g8")
    r.arm0()
    r.gap([gap_entry(red_test="results/prereg2/gaps/../../harness/x.py")])
    r.score()
    err, _ = r.load()
    check("G8: a red test path that climbs out with .. is refused", err and "must lie under" in err, err)
    r = GapRepo(tmp, "g12")
    r.arm0()
    r.gap([gap_entry()])
    r.gap([gap_entry(why="reworded before scoring")], logs=())
    r.score()
    err, _ = r.load()
    check("G12: a gap whose why changes before scoring is refused (every field is fixed)", err and "never edited" in err, err)
    r = GapRepo(tmp, "g9")
    r.g("checkout", "-q", "-b", "early")
    r.gap([gap_entry()])
    r.g("checkout", "-q", "main")
    r.arm0()
    r.gap([gap_entry()], logs=())
    r.g("merge", "-q", "--no-edit", "-X", "ours", "early")
    r.score()
    err, _ = r.load()
    check("G9: an identical gap first committed on a branch before Arm 0 is found (--full-history), and stops the work",
          err and "stops the work" in err, err)
    r = GapRepo(tmp, "post")
    r.arm0()
    r.gap([gap_entry()])
    sc = r.score()
    r.gap([gap_entry(why="reworded after scoring")], logs=())
    r.gap([gap_entry(), gap_entry("G2", log="§99")], logs=())
    r.commit("malformed", {"results/prereg2/gaps.json": "{not json\n"})
    err, (gaps, notes) = r.load()
    check("MEDIUM-1: after the scoring-arm commit, an edit, a missing LOG entry and malformed JSON are listed, "
          "never refused, and the gap declared before scoring still holds",
          err is None and gaps.get(("k8s-en", "E", "Q", )) and any("malformed" in n for n in notes)
          and any("G2" in n for n in notes) and any("G1" in n for n in notes),
          (err, gaps, notes))
    r = GapRepo(tmp, "pre")
    r.gap([gap_entry()])
    r1 = raised(lambda: prereg2.bound_gaps(r.sp, FakeTr(True, "a" * 40)))
    check("MEDIUM-1: the bound preflight (arm0, score, export, tier-run) refuses a gap declared before Arm 0",
          r1 and "stops the work" in r1, r1)
    r = GapRepo(tmp, "mid")
    r.arm0()
    r.gap([gap_entry()])
    r1 = raised(lambda: prereg2.bound_gaps(r.sp, FakeTr(True, "a" * 40)))
    check("MEDIUM-1: ... and passes one declared after Arm 0, before any scoring commit exists", r1 is None, r1)
    check("MEDIUM-1: an unbound run reads no gaps", prereg2.bound_gaps(r.sp, FakeTr(False, None)) == ({}, []))

    section("Round 6: the validation commit adds VALIDATION only (MEDIUM-3), and K4, H2, H3, D3")
    from p2 import binding as BD
    root, sp, g = binding_repo(tmp, "valharness")
    agg = os.path.join(sp, "harness", "p2", "aggregate.py")
    open(agg, "w").write(open(agg).read().replace("FLOOR = 300", "FLOOR = 1"))
    rc, out = run_copy(sp, "seal", "--manifest", os.path.join(tmp, "vh-manifest.json"))
    commit_all(g, "a validation PR that also sets FLOOR = 1")
    st, rs = BD.check(sp, "arm0", "rust-book")
    check("MEDIUM-3: a validation commit that also changes the harness is refused",
          not st["bound"] and any("itself changes the harness" in x for x in rs), rs)
    tdir = os.path.join(tmp, "k4")
    _, sp4, g4 = binding_repo(tmp, "k4repo")
    BD.mark_executed(sp4, "arm0", "cmspec", os.path.join(tdir, "first.txt"))
    mk = os.path.join(sp4, BD.marker_rel("arm0", "cmspec"))
    before = open(mk).read()
    r1 = raised(lambda: BD.mark_executed(sp4, "arm0", "cmspec", os.path.join(tdir, "second.txt")))
    check("K4: an existing marker is never overwritten", r1 and r1.startswith("FileExistsError")
          and open(mk).read() == before, r1)
    env = BD.git_env()
    check("H2/H3: binding git runs with no user or system config and no replace objects",
          env.get("GIT_CONFIG_GLOBAL") == os.devnull and env.get("GIT_CONFIG_SYSTEM") == os.devnull
          and env.get("GIT_CONFIG_NOSYSTEM") == "1" and env.get("GIT_NO_REPLACE_OBJECTS") == "1", env.get("GIT_CONFIG_GLOBAL"))
    from p2 import tierrun as TRN
    r = GapRepo(tmp, "h4")
    r.arm0()
    r.g("checkout", "-q", "-b", "side")
    r.score()
    r.g("checkout", "-q", "main")
    r.score()
    r.g("merge", "-q", "--no-edit", "-X", "ours", "side")
    r1 = raised(lambda: TRN.scoring_commit(r.sp))
    check("H4: score/ added on both sides of a merge is two scoring commits (--full-history), refused",
          r1 and "2 commits" in r1, r1)
    r = GapRepo(tmp, "h5")
    r.arm0()
    r.score()
    r.g("replace", "--graft", "HEAD")
    r1 = raised(lambda: TRN.scoring_commit(r.sp))
    check("H5: the scoring-arm commit is not derived from a history rewritten by git replace",
          r1 and "replace refs" in r1, r1)
    root6, sp6, g6 = binding_repo(tmp, "h6")
    run_copy(sp6, "seal", "--manifest", os.path.join(tmp, "h6-manifest.json"))
    commit_all(g6, "validation")
    g6("checkout", "-q", "-b", "side")
    t6 = os.path.join(sp6, "harness", "p2", "tiers.py")
    o6 = open(t6).read()
    open(t6, "a").write("# side edit\n")
    commit_all(g6, "a harness edit on a side branch")
    open(t6, "w").write(o6)
    commit_all(g6, "reverted on the side branch")
    g6("checkout", "-q", "main")
    g6("merge", "-q", "--no-ff", "--no-edit", "side")
    st, rs = BD.check(sp6, "arm0", "rust-book")
    check("H6: a harness edit on a merged side branch, reverted there, is still a later commit that touches the "
          "harness (--full-history)", not st["bound"] and any("after the validation commit" in x for x in rs), rs)
    _, sp5, g5 = binding_repo(tmp, "plantshadow")
    os.makedirs(os.path.join(sp5, "harness", "prereg2_plants"))
    shutil.copy(os.path.join(sp5, "harness", "prereg2_plants.py"), os.path.join(sp5, "harness", "prereg2_plants", "__init__.py"))
    rc, out = run_copy(sp5, "validate-export", os.path.join(tmp, "nothing"), "--unbound", "--transcript-dir",
                       os.path.join(tmp, "ps-t"))
    check("D3: an untracked prereg2_plants/ package that shadows prereg2_plants.py is refused",
          rc == 2 and "prereg2_plants was loaded from" in out, out[-200:])


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
                  "--manifest", mp, "--manifest-sha", sha, "--state-dir", os.path.join(tmp, "agg-st"),
                  "--repro-dir", os.path.join(tmp, "agg-rp"), "--out", os.path.join(tmp, "v.json"),
                  "--fixture-ok", "--unbound")
    check("the aggregate CLI on empty input exits non-zero with no verdict, for that reason",
          rc != 0 and "NO VERDICT: no Arm 0 result" in out and "OVERALL" not in out
          and not os.path.exists(os.path.join(tmp, "v.json")),
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
TMP = None


def main():
    global ARGS
    ap = argparse.ArgumentParser()
    ap.add_argument("--d8-dir", required=True)
    ARGS = a = ap.parse_args()
    a.d8_dir = os.path.abspath(a.d8_dir)
    Mx.load(a.d8_dir)
    global TMP
    tmp = TMP = tempfile.mkdtemp(prefix="prereg2-v3.")
    real_results = os.path.join(os.path.dirname(HERE), "results", "prereg2")

    def listing():
        # validation/ is where prereg2_validate.sh writes the V transcripts,
        # possibly while V3 runs; nothing else there may change.
        return sorted(p for p in (os.path.relpath(os.path.join(r, f), real_results)
                                  for r, _, fs in os.walk(real_results) for f in fs)
                      if not p.startswith("validation" + os.sep))
    before_results = listing()
    # Each section runs on its own: one that raises is a named failure, and
    # the sections after it still run.
    sections = [
        lambda: t_d8_pin(a, tmp),
        lambda: t_copied(a),
        lambda: t_repeat(a),
        lambda: t_known(a),
        lambda: t_split(a),
        lambda: t_wf(a),
        lambda: t_r_units(a),
        lambda: t_r_slug_t(a),
        lambda: t_rereview(a),
        lambda: t_r(a),
        lambda: t_plants(a, tmp),
        lambda: t_enumerators(a, tmp),
        lambda: t_repro(a, tmp),
        lambda: t_undecodable(a, tmp),
        lambda: t_bundles(a, tmp),
        lambda: t_m_arm(a, tmp),
        lambda: t_mfilter(a, tmp),
        lambda: t_sampler(a),
        lambda: t_counting(a),
        lambda: t_arm0(a, tmp),
        lambda: t_export(a, tmp),
        lambda: t_tier_run(a, tmp),
        lambda: t_manifest_c4(a, tmp),
        lambda: t_void(a),
        lambda: t_review_b5(a),
        lambda: t_review_a5_b1_a3(a),
        lambda: t_binding(a, tmp),
        lambda: t_preflight(a, tmp),
        lambda: t_round5(a, tmp),
        lambda: t_gaps(a, tmp),
        lambda: t_round6(a, tmp),
        lambda: t_aggregator(a, tmp),
    ]
    try:
        for fn in sections:
            try:
                fn()
            except BaseException as e:
                if isinstance(e, KeyboardInterrupt):
                    raise
                import traceback
                traceback.print_exc()
                check(f"section raised: {type(e).__name__}: {str(e)[:120]}", False)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    added = sorted(set(listing()) - set(before_results))
    check("V3 itself wrote nothing under this repository's results/prereg2/", not added, added[:3])
    fails = [lbl for lbl, ok in RESULTS if not ok]
    print(f"\n{len(RESULTS)} checks, {len(fails)} failed")
    print("V3:", "PASS" if not fails and RESULTS else "FAIL")
    return 0 if not fails and RESULTS else 1


if __name__ == "__main__":
    sys.exit(main())
