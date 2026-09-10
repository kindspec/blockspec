#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Two-branch three-way prose merge harness — blockspec#2, spike arm.

WHAT THIS IS NOT: a specification, a format, or an implementation of anything.
blockspec does not exist. This is an experiment that runs stock git.

WHAT IT DOES. `PRE-REGISTRATION.md` §2.1 says D8 measured a *rebase* --
`git merge-file` applying one author's real edit -- and that nobody has run the
concurrent case: two branches changing different things, git reconciling both
cleanly, with standoff annotations present. This runs that case.

  * cases come from REAL 2-parent merge commits in real corpora: merge-base B,
    parents A and C, one .md path changed on BOTH sides;
  * a standoff record is built over each block at B (`anchor_eval.anchor_of`,
    imported from D8 -- nothing is written into the document);
  * A and C are merged by STOCK `git merge` in a hermetic scratch repository:
    no merge driver, no .gitattributes, no clean/smudge filter, no hook;
  * the record is re-resolved against the merged text by D8's own
    `anchor_eval3.reanchor2`, under both the `naive` and `hard` policies;
  * the answer is graded against TLLC, the oracle named in `spike/ORACLE.md`,
    which is committed and frozen.

The mechanism under test is imported from `kindspec/research`, never
reimplemented, so the control arm (D8's own scripts, unmodified) and this arm
measure the same thing.

NO TIER IS ASSIGNED HERE. `PRE-REGISTRATION.md` §4.1 requires the tier to be
assigned from the written definitions by someone who has not seen the frequency.
Every candidate is emitted with `"tier": "UNASSIGNED"`.
"""
import argparse
import difflib
import hashlib
import json
import os
import random
import re
import subprocess
import sys
import tempfile
from collections import Counter

# --------------------------------------------------------------------------
# the mechanism under test, imported from D8 rather than reimplemented
# --------------------------------------------------------------------------

DEFAULT_D8 = os.path.abspath(
    os.path.join(os.path.dirname(__file__),
                 "..", "..", "..", "..", "research", "experiments", "D8-identity"))


def load_d8(path):
    if not os.path.isdir(path):
        sys.exit(f"D8 experiments directory not found: {path}\n"
                 f"clone kindspec/research and pass --d8-dir")
    sys.path.insert(0, path)
    import anchor_eval          # noqa: E402
    import anchor_eval3         # noqa: E402
    missing = [n for n in ("blocks", "anchor_of") if not hasattr(anchor_eval, n)]
    missing += [n for n in ("reanchor2", "btype") if not hasattr(anchor_eval3, n)]
    if missing:
        sys.exit(f"D8 modules present but missing {missing}; wrong checkout?")
    return anchor_eval, anchor_eval3


D8 = D83 = None

# --------------------------------------------------------------------------
# stock git merge, hermetic
# --------------------------------------------------------------------------

# Every one of these exists to satisfy PRE-REGISTRATION §3(1): the merge must be
# what a stranger with a fresh clone gets. `core.attributesFile` and the empty
# `core.hooksPath` disable the user's global attributes and hooks;
# GIT_CONFIG_* disable system and global config entirely.
def _env(hooks_dir):
    e = dict(os.environ)
    e.update({
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_SYSTEM": os.devnull,
        "GIT_AUTHOR_NAME": "h", "GIT_AUTHOR_EMAIL": "h@invalid",
        "GIT_COMMITTER_NAME": "h", "GIT_COMMITTER_EMAIL": "h@invalid",
        "GIT_AUTHOR_DATE": "2000-01-01T00:00:00Z",
        "GIT_COMMITTER_DATE": "2000-01-01T00:00:00Z",
        "GIT_TERMINAL_PROMPT": "0",
        "LC_ALL": "C",
    })
    e.pop("GIT_DIR", None)
    e.pop("GIT_WORK_TREE", None)
    return e


_CFG = ["-c", "core.attributesFile=" + os.devnull,
        "-c", "commit.gpgsign=false",
        "-c", "core.autocrlf=false",
        "-c", "merge.conflictStyle=merge"]

MERGE_CMDLINE = "git -c core.attributesFile=/dev/null -c core.hooksPath=<empty> merge --no-edit legC"
# `=======` alone is NOT a usable conflict-marker test: a line of equals signs is
# a setext heading underline, which is legal markdown and occurs in cmspec. Only
# the angle-bracket markers are unambiguous. Detecting on `=======` classified a
# clean merge as marker-bearing and silently dropped it from the sample -- an
# error in the conservative direction, which is still an error.
CONFLICT_MARKERS = ("<<<<<<<", ">>>>>>>")


def stock_merge(base, side_a, side_c, path="doc.md", keep=None):
    """Real two-branch three-way merge by stock `git merge`.

    Returns dict(clean, merged, rc, markers, stderr, workdir).
    """
    d = keep or tempfile.mkdtemp(prefix="pmerge.")
    hooks = os.path.join(d, ".nohooks")
    os.makedirs(hooks, exist_ok=True)
    cfg = _CFG + ["-c", "core.hooksPath=" + hooks]
    env = _env(hooks)
    fp = os.path.join(d, path)
    os.makedirs(os.path.dirname(fp) or d, exist_ok=True)

    def G(*a, check=True):
        r = subprocess.run(["git", "-C", d, *cfg, *a],
                           capture_output=True, text=True, env=env)
        if check and r.returncode != 0:
            raise RuntimeError(f"git {' '.join(a)} -> {r.returncode}\n{r.stderr}")
        return r

    def W(text):
        with open(fp, "w", encoding="utf-8", newline="") as f:
            f.write(text)

    G("init", "-q", "-b", "main")
    W(base)
    G("add", "-A")
    G("commit", "-q", "-m", "base")
    G("checkout", "-q", "-b", "legA")
    W(side_a)
    G("add", "-A")
    G("commit", "-q", "-m", "a")
    G("checkout", "-q", "-b", "legC", "main")
    W(side_c)
    G("add", "-A")
    G("commit", "-q", "-m", "c")
    G("checkout", "-q", "legA")

    # PRE-REGISTRATION §3(1): assert the merge really is driverless.
    attr = G("check-attr", "merge", "--", path).stdout.strip()
    if not attr.endswith("unspecified"):
        raise RuntimeError(f"a merge attribute is in force ({attr!r}) -- "
                           f"§3(1) forbids it")

    m = G("merge", "--no-edit", "legC", check=False)
    merged = None
    if os.path.exists(fp):
        with open(fp, encoding="utf-8", newline="") as f:
            merged = f.read()

    # "No conflict, no marker anywhere in the tree" -- both halves checked.
    # git's own unmerged-index entries are the authoritative signal; the textual
    # scan is §3(1)'s "no marker anywhere in the tree" clause.
    unmerged = bool(G("ls-files", "-u").stdout.strip())
    markers = False
    for root, dirs, names in os.walk(d):
        if ".git" in dirs:
            dirs.remove(".git")
        if ".nohooks" in dirs:
            dirs.remove(".nohooks")
        for n in names:
            try:
                with open(os.path.join(root, n), encoding="utf-8") as f:
                    t = f.read()
            except (UnicodeDecodeError, OSError):
                continue
            if any(l.startswith(CONFLICT_MARKERS) for l in t.splitlines()):
                markers = True
    out = {"clean": m.returncode == 0 and not markers and not unmerged,
           "merged": merged, "unmerged": unmerged,
           "rc": m.returncode, "markers": markers,
           "stderr": m.stderr.strip()[:400], "workdir": d if keep else None}
    if not keep:
        subprocess.run(["rm", "-rf", d])
    return out


# --------------------------------------------------------------------------
# TLLC -- the oracle. spike/ORACLE.md is normative; this implements it.
# --------------------------------------------------------------------------

def fences_balanced(text):
    """§3(2): 'the merged file is well-formed under whatever grammar the
    experiment assumes'. The grammar here is D8's boundary-only block parser,
    whose only stateful construct is the fenced block, so well-formed means an
    even number of fence lines. An unbalanced fence desynchronises the parser
    for the rest of the file and glues code to the prose after it -- which
    produces block boundaries that no oracle can be expected to track."""
    return sum(1 for l in text.splitlines()
               if l.strip().startswith(("```", "~~~"))) % 2 == 0


ORACLE_NAME = "TLLC (two-leg line correspondence)"
ORACLE_CONFIDENCE = 0.5      # frac of a block's non-blank lines that must map
ORACLE_DELETED_SIM = 0.3     # below this, a vanished block is DELETED not UNKNOWN


def _line_map(src_lines, dst_lines):
    """Partial map src line -> dst line, by longest-matching-block alignment."""
    sm = difflib.SequenceMatcher(None, src_lines, dst_lines, autojunk=False)
    m = {}
    for a, b, n in sm.get_matching_blocks():
        for k in range(n):
            m[a + k] = b + k
    return m


def _line_to_block(text, bl):
    """Line number -> block index, using each block's true offset.

    Deliberately not D8's `lineidx`, which locates a block by
    `text.index(b['content'])` and therefore mis-locates every duplicate block
    to its first occurrence. Duplicate blocks are the point of this arm.
    """
    idx = {}
    for n, b in enumerate(bl):
        s = text.count("\n", 0, b["off"])
        e = s + b["content"].count("\n")
        for L in range(s, e + 1):
            idx[L] = n
    return idx


def tllc(base, side_a, side_c, merged, bb, bm):
    """Oracle: base block index -> ('SURVIVED', merged_block) | ('DELETED', None)
    | ('UNKNOWN', None).  See spike/ORACLE.md §2."""
    lb, lm = base.splitlines(), merged.splitlines()
    legs = []
    for leg in (side_a, side_c):
        ll = leg.splitlines()
        b2l = _line_map(lb, ll)
        l2m = _line_map(ll, lm)
        legs.append({L: l2m[j] for L, j in b2l.items() if j in l2m})
    bidx = _line_to_block(base, bb)
    midx = _line_to_block(merged, bm)

    out = {}
    for n, blk in enumerate(bb):
        mine = [L for L, bn in bidx.items() if bn == n and lb[L].strip()]
        if not mine:
            out[n] = ("UNKNOWN", None)
            continue
        proposals, fracs = [], []
        for phi in legs:
            mapped = [phi[L] for L in mine if L in phi]
            fracs.append(len(mapped) / len(mine))
            if len(mapped) / len(mine) >= ORACLE_CONFIDENCE:
                tgt = Counter(midx[M] for M in mapped if M in midx)
                proposals.append(tgt.most_common(1)[0][0] if tgt else None)
            else:
                proposals.append(None)
        got = [p for p in proposals if p is not None]
        if len(got) == 2 and got[0] != got[1]:
            out[n] = ("UNKNOWN", None)                 # legs disagree -> refuse
        elif got:
            out[n] = ("SURVIVED", got[0])
        elif fracs[0] == 0.0 and fracs[1] == 0.0:
            best = max((difflib.SequenceMatcher(None, blk["content"],
                                                x["content"]).ratio()
                        for x in bm), default=0)
            out[n] = ("DELETED", None) if best < ORACLE_DELETED_SIM else ("UNKNOWN", None)
        else:
            out[n] = ("UNKNOWN", None)
    return out


# --------------------------------------------------------------------------
# evaluation -- ONE code path, shared by the corpus arm and the planted cases
# --------------------------------------------------------------------------

POLICIES = (("naive", False), ("hard", True))


def evaluate_case(case, only_block=None, max_blocks=0, seed=7, keep=None):
    """case: dict(id, path, base, a, c, meta).  Returns (Counter, [records])."""
    t, recs = Counter(), []
    res = stock_merge(case["base"], case["a"], case["c"],
                      case.get("path", "doc.md"), keep=keep)
    t["cases"] += 1
    if res["merged"] is None:
        t["merge:no_file"] += 1
        return t, recs
    if res["markers"]:
        t["merge:markers"] += 1
    if res["rc"] != 0:
        t["merge:conflict"] += 1
    if not res["clean"]:
        # PRE-REGISTRATION §4 tier E: the format working. Counted, not scored.
        return t, recs
    t["merge:clean"] += 1

    merged = res["merged"]
    # Harness validation, not a measurement: where git recorded a merge commit
    # for this path and our reconstruction merged cleanly, the two should agree.
    # They can legitimately differ -- the recorded commit may carry a human's
    # conflict resolution or an extra edit -- so this is reported, not asserted.
    if case.get("recorded"):
        t["recon:" + ("matches" if merged == case["recorded"] else "differs")] += 1

    # §3(5) "Both parent states were correct" and §3(2) "the merged file is
    # well-formed". A case whose PARENT was already malformed cannot be a
    # finding -- the defect was carried in by an author, not created by the
    # merge. Recorded per case and per candidate; counted, never silently
    # filtered.
    parents_ok = (fences_balanced(case["base"]) and fences_balanced(case["a"])
                  and fences_balanced(case["c"]))
    merged_ok = fences_balanced(merged)
    t["wf:parents_ok" if parents_ok else "wf:parent_malformed"] += 1
    if parents_ok and not merged_ok:
        # A clean merge that BROKE well-formedness. Would be a real result.
        t["wf:merge_broke_wellformedness"] += 1
    bb, bm = D8.blocks(case["base"]), D8.blocks(merged)
    if len(bb) < 2 or len(bm) < 2:
        t["skip:tiny"] += 1
        return t, recs
    orc = tllc(case["base"], case["a"], case["c"], merged, bb, bm)

    ks = [only_block] if only_block is not None else list(range(len(bb)))
    if only_block is None and max_blocks and len(ks) > max_blocks:
        random.Random(seed).shuffle(ks)
        ks = ks[:max_blocks]

    for k in ks:
        anc = D8.anchor_of(case["base"], bb[k])
        if len(anc["quote"]) < 20:
            t["skip:short_quote"] += 1
            continue
        truth, tgt = orc[k]
        t["ORACLE:" + truth] += 1
        if truth == "UNKNOWN":
            continue
        ty = D83.btype(bb[k]["content"])
        t["EV"] += 1
        t["TY:" + ty] += 1
        # §7 "cell counts lie": the unit is a distinct authored block.
        t.setdefault("_distinct", set())
        for lab, hard in POLICIES:
            st, hit = D83.reanchor2(merged, anc, bm, hard)
            if truth == "SURVIVED":
                cls = "LOUD" if hit is None else ("correct" if hit == tgt else "WRONG")
            else:
                cls = "correct" if hit is None else "WRONG"
            t[f"{lab}:{cls}"] += 1
            if cls == "WRONG":
                t[f"{lab}:WRONG:{ty}"] += 1
                if parents_ok:
                    t[f"{lab}:WRONGwf:{ty}"] += 1
                    t[f"{lab}:WRONGwf"] += 1
                if truth == "DELETED":
                    t[f"{lab}:WRONG_on_deleted"] += 1
                recs.append({
                    "tier": "UNASSIGNED",
                    "parents_wellformed": parents_ok,
                    "merged_wellformed": merged_ok,
                    "disqualified_by": (None if parents_ok else
                                        "PRE-REGISTRATION §3(5): a parent was "
                                        "already malformed (unbalanced fence)"),
                    "policy": lab, "status": st, "block_type": ty,
                    "oracle_truth": truth,
                    "case": case.get("id"), "path": case.get("path"),
                    "meta": case.get("meta", {}),
                    "block_index": k,
                    "quote": bb[k]["content"][:220],
                    "oracle_target": (bm[tgt]["content"][:220]
                                      if tgt is not None else None),
                    "mechanism_target": (bm[hit]["content"][:220]
                                         if hit is not None else None),
                    "merge_cmdline": MERGE_CMDLINE,
                })
    return t, recs


def key_of(case, blk):
    return hashlib.sha1(
        (case.get("path", "") + "\0" + blk["content"]).encode()).hexdigest()


# --------------------------------------------------------------------------
# corpus arm -- real two-branch merges out of real history
# --------------------------------------------------------------------------

def g(repo, *a):
    return subprocess.run(["git", "-C", repo, *a],
                          capture_output=True, text=True).stdout


def find_merge_cases(repo, prefix, limit=0):
    """Real 2-parent merges where the same .md changed on BOTH sides."""
    cases, n2 = [], 0
    for line in g(repo, "rev-list", "--merges", "HEAD", "--parents").split("\n"):
        parts = line.split()
        if len(parts) != 3:            # merge commit + exactly two parents
            continue
        n2 += 1
        m, p1, p2 = parts
        bases = [b for b in g(repo, "merge-base", "--all", p1, p2).split("\n") if b]
        if len(bases) != 1:            # criss-cross: no single base, skip + report
            cases.append({"_skip": "multi_base"})
            continue
        base = bases[0]
        ca = {x for x in g(repo, "diff", "--name-only", base, p1).split("\n")
              if x.startswith(prefix) and x.endswith(".md")}
        cb = {x for x in g(repo, "diff", "--name-only", base, p2).split("\n")
              if x.startswith(prefix) and x.endswith(".md")}
        for path in sorted(ca & cb):
            tb = g(repo, "show", f"{base}:{path}")
            ta = g(repo, "show", f"{p1}:{path}")
            tc = g(repo, "show", f"{p2}:{path}")
            if not (tb and ta and tc):
                continue
            if ta == tc or ta == tb or tc == tb:
                continue
            cases.append({"id": f"{m[:10]}:{path}", "path": path,
                          "base": tb, "a": ta, "c": tc,
                          # what git ACTUALLY recorded for this path at the
                          # merge commit, used to validate the reconstruction
                          "recorded": g(repo, "show", f"{m}:{path}"),
                          "meta": {"merge": m, "base": base,
                                   "legA": p1, "legC": p2}})
            if limit and len([c for c in cases if "_skip" not in c]) >= limit:
                cases.append({"_skip": "counted", "n2": n2})
                return cases
    cases.append({"_skip": "counted", "n2": n2})
    return cases


# --------------------------------------------------------------------------
# planted cases -- PRE-REGISTRATION §7, "the harness must be able to fail"
# --------------------------------------------------------------------------

PLANT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plant_cases")


def load_plant(d):
    exp = json.load(open(os.path.join(d, "expect.json")))
    rd = lambda n: open(os.path.join(d, n), encoding="utf-8", newline="").read()
    return {"id": os.path.basename(d), "path": exp.get("path", "doc.md"),
            "base": rd("base.md"), "a": rd("a.md"), "c": rd("c.md")}, exp


def run_plants(verbose=True):
    """Both directions, both demonstrated, through the SAME evaluate_case()."""
    ok = True
    for name in sorted(os.listdir(PLANT_DIR)):
        d = os.path.join(PLANT_DIR, name)
        if not os.path.isdir(d):
            continue
        case, exp = load_plant(d)
        t, recs = evaluate_case(case, only_block=exp["anchor_block"])
        got = {}
        for lab, _ in POLICIES:
            got[lab] = ("WRONG" if t[f"{lab}:WRONG"] else
                        "LOUD" if t[f"{lab}:LOUD"] else
                        "correct" if t[f"{lab}:correct"] else "NOT-EVALUATED")
        want = {"naive": exp["expect_naive"], "hard": exp["expect_hard"]}
        good = got == want and bool(t["merge:clean"]) == exp.get("expect_clean_merge", True)
        ok &= good
        if verbose:
            print(f"--- plant {name}: {exp['what']}")
            print(f"      merge: rc={0 if t['merge:clean'] else 1} clean={bool(t['merge:clean'])} "
                  f"markers={bool(t['merge:markers'])}   [{MERGE_CMDLINE}]")
            print(f"      oracle {ORACLE_NAME}: "
                  + " ".join(f"{k[7:]}={v}" for k, v in sorted(t.items())
                             if k.startswith("ORACLE:")))
            print(f"      want {want}")
            print(f"      got  {got}   -> {'PASS' if good else 'FAIL'}")
            for r in recs:
                print(f"      [{r['policy']}] status={r['status']} type={r['block_type']} "
                      f"tier={r['tier']}")
                print(f"        anchor quote      : {r['quote']!r}")
                print(f"        oracle says       : {r['oracle_target']!r}")
                print(f"        mechanism resolved: {r['mechanism_target']!r}")
    print(f"\nPLANTED-CASE GATE: {'PASS' if ok else 'FAIL'} "
          f"(both verdicts required: at least one WRONG case and one clean case)")
    verdicts = set()
    for name in sorted(os.listdir(PLANT_DIR)):
        d = os.path.join(PLANT_DIR, name)
        if os.path.isdir(d):
            verdicts.add(json.load(open(os.path.join(d, "expect.json")))["expect_naive"])
    if not {"WRONG", "correct"} <= verdicts:
        print("PLANTED-CASE GATE: FAIL -- the fixtures do not cover both verdicts")
        ok = False
    return ok


# --------------------------------------------------------------------------

def report(name, t, extra=""):
    ev = t["EV"]
    print(f"\n### {name}{extra}")
    print(f"  merges: clean={t['merge:clean']} conflicted={t['merge:conflict']} "
          f"marker-bearing={t['merge:markers']} (tier E, counted not scored)")
    rec = t["recon:matches"] + t["recon:differs"]
    if rec:
        print(f"  reconstruction vs the merge commit git actually recorded: "
              f"{t['recon:matches']}/{rec} byte-identical  "
              f"(differences are legitimate -- a recorded merge may carry a "
              f"human resolution)")
    print(f"  oracle {ORACLE_NAME}: SURVIVED={t['ORACLE:SURVIVED']} "
          f"DELETED={t['ORACLE:DELETED']} UNKNOWN={t['ORACLE:UNKNOWN']}"
          f"  -> confident {ev}/{ev + t['ORACLE:UNKNOWN']} "
          f"({100 * ev / max(1, ev + t['ORACLE:UNKNOWN']):.0f}%)")
    if not ev:
        print("  no oracle-confident anchors; nothing scored")
        return
    print("  block types: " + " ".join(f"{k[3:]}={v}" for k, v in sorted(t.items())
                                       if k.startswith("TY:")))
    print(f"  well-formedness (§3(2), §3(5)): cases with all parents well-formed "
          f"{t['wf:parents_ok']}, with a parent already malformed "
          f"{t['wf:parent_malformed']}; clean merges that BROKE well-formedness: "
          f"{t['wf:merge_broke_wellformedness']}")
    for lab, _ in POLICIES:
        w = t[f"{lab}:WRONG"]
        print(f"  {lab:<6} correct {100 * t[lab + ':correct'] / ev:5.1f}%   "
              f"LOUD-refusal {100 * t[lab + ':LOUD'] / ev:5.1f}%   "
              f"MIS-RESOLVED {100 * w / ev:5.2f}%  (n={w})"
              + ("  by type: " + " ".join(f"{k.split(':')[2]}={v}" for k, v in
                                          sorted(t.items())
                                          if k.startswith(lab + ":WRONG:"))
                 if w else "")
              + (f"  [of which on oracle-DELETED, see ORACLE.md §4: "
                 f"{t[lab + ':WRONG_on_deleted']}]"
                 if t[lab + ":WRONG_on_deleted"] else ""))
    for lab, _ in POLICIES:
        w = t[f"{lab}:WRONGwf"]
        print(f"  {lab:<6} of those, with ALL PARENTS WELL-FORMED (§3(5)): n={w}"
              + ("  by type: " + " ".join(f"{k.split(':')[2]}={v}" for k, v in
                                          sorted(t.items())
                                          if k.startswith(lab + ":WRONGwf:"))
                 if w else ("   <- all "
                            f"{t[lab + ':WRONG']} disqualified by §3(5)"
                            if t[f"{lab}:WRONG"] else
                            "   (none to disqualify: no mis-resolutions here)")))
    print("  NOTE: MIS-RESOLVED is not a finding. ORACLE.md §5 -- the oracle "
          "establishes\n        descent, not falsity. Every case is emitted with "
          "tier UNASSIGNED.")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--d8-dir", default=DEFAULT_D8)
    ap.add_argument("--plant", action="store_true",
                    help="run the planted cases (§7 two-verdict demonstration)")
    ap.add_argument("--corpus", action="append", default=[], metavar="NAME=REPO:PREFIX")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--max-blocks", type=int, default=0)
    ap.add_argument("--records", metavar="FILE", help="write candidate cases as JSONL")
    a = ap.parse_args()

    global D8, D83
    D8, D83 = load_d8(a.d8_dir)

    rc = 0
    if a.plant:
        rc |= 0 if run_plants() else 1

    allrecs = []
    for spec in a.corpus:
        name, rest = spec.split("=", 1)
        repo, prefix = rest.rsplit(":", 1)
        sha = g(repo, "rev-parse", "HEAD").strip()
        cases = find_merge_cases(repo, prefix, a.limit)
        n2 = next((c["n2"] for c in cases if c.get("_skip") == "counted"), 0)
        skipped = sum(1 for c in cases if c.get("_skip") == "multi_base")
        cases = [c for c in cases if "_skip" not in c]
        t = Counter()
        distinct = set()
        for c in cases:
            ct, recs = evaluate_case(c, max_blocks=a.max_blocks)
            t.update({k: v for k, v in ct.items() if not k.startswith("_")})
            for b in D8.blocks(c["base"]):
                distinct.add(key_of(c, b))
            for r in recs:
                r["corpus"] = name
                r["corpus_sha"] = sha
            allrecs += recs
        report(name, t,
               f"  pin={sha[:12]}  two-parent merges examined={n2}"
               f"  ->  file-merges={len(cases)}"
               f"  (skipped {skipped} criss-cross merges with >1 base)")
        print(f"  distinct authored base blocks across those merges: {len(distinct)}"
              f"   (§7: a corpus that ships the same document twice contributes once)")

    if a.records and allrecs:
        with open(a.records, "w") as f:
            for r in allrecs:
                f.write(json.dumps(r) + "\n")
        print(f"\nwrote {len(allrecs)} candidate records (tier UNASSIGNED) -> {a.records}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
