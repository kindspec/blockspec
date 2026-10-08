# SPDX-License-Identifier: MIT
"""§9: "The harness at the validation commit is the implementation." This
module makes the harness enforce that, rather than leave it to the operator
(review C1, C3, B6; LOG.md §16).

A bound run needs `results/prereg2/VALIDATION`, a JSON file naming the
validation commit and the sealed manifest's sha256. The first Arm 0 commit
adds it. Every bound command checks:

- the validation commit is an ancestor of HEAD;
- `git diff --quiet <validation> HEAD` over the harness, PRE-REGISTRATION-2.md
  and ORACLE.md;
- the work tree holds exactly the validation commit's bytes there: each file
  is hashed with `git hash-object` and compared with `git ls-tree`, so
  `--assume-unchanged` cannot hide an edit, and no untracked or ignored file
  may sit under the harness;
- `results/prereg2/` has nothing uncommitted except this invocation's own
  transcript (and VALIDATION itself, before any Arm 0 result is committed),
  so every earlier transcript, aborted ones included, is committed before
  the next bound run starts;
- for arm0, score and export, no earlier transcript of the same command and
  arm exists: the first execution binds.
"""
import json
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
SPIKE = os.path.dirname(os.path.dirname(HERE))
BOUND_PATHS = ("harness", "PRE-REGISTRATION-2.md", "ORACLE.md")
RESULTS_REL = os.path.join("results", "prereg2")
VALIDATION_REL = os.path.join(RESULTS_REL, "VALIDATION")
TRANSCRIPTS_REL = os.path.join(RESULTS_REL, "transcripts")


def _git(spike, *a):
    r = subprocess.run(["git", "-C", spike, *a], capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


def toplevel(spike):
    rc, out, _ = _git(spike, "rev-parse", "--show-toplevel")
    return out.strip() if rc == 0 else None


def read_validation(spike=SPIKE):
    p = os.path.join(spike, VALIDATION_REL)
    try:
        v = json.load(open(p))
    except (OSError, ValueError) as e:
        return None, f"no readable {VALIDATION_REL}: {e}"
    if not (isinstance(v, dict) and isinstance(v.get("validation_commit"), str)
            and len(v["validation_commit"]) == 40
            and isinstance(v.get("manifest_sha256"), str) and len(v["manifest_sha256"]) == 64):
        return None, f"{VALIDATION_REL} must name validation_commit (40 hex) and manifest_sha256 (64 hex)"
    return v, None


def harness_files_differ(spike, commit):
    """Every path under the bound paths whose bytes in the work tree are not
    the commit's, plus every file there the commit does not hold."""
    top = toplevel(spike)
    prefix = os.path.relpath(spike, top)
    rc, out, _ = _git(spike, "ls-tree", "-r", "--full-name", commit, "--", *BOUND_PATHS)
    want = {}
    for line in out.splitlines():
        meta, path = line.split("\t", 1)
        want[os.path.relpath(path, prefix)] = meta.split()[2]
    bad = []
    for rel, blob in sorted(want.items()):
        p = os.path.join(spike, rel)
        if os.path.islink(p) or not os.path.isfile(p):
            bad.append(f"{rel}: missing or not a regular file")
            continue
        rc, h, _ = _git(spike, "hash-object", "--no-filters", "--", p)
        if h.strip() != blob:
            bad.append(f"{rel}: work-tree bytes differ from the validation commit")
    for b in BOUND_PATHS:
        base = os.path.join(spike, b)
        if os.path.isdir(base):
            for root, dirs, files in os.walk(base):
                for f in files:
                    rel = os.path.relpath(os.path.join(root, f), spike)
                    if rel not in want:
                        bad.append(f"{rel}: not in the validation commit (untracked or ignored)")
    return bad


def transcript_tag(fname):
    """'<cmd>[-<arm>]' of a transcript named '<YYYY-MM-DDTHHMMSSZ>-<cmd>[-<arm>][.<n>].txt'."""
    stem = fname[:-4] if fname.endswith(".txt") else fname
    head, _, tail = stem.rpartition(".")
    if head and tail.isdigit():
        stem = head
    return stem[19:] if len(stem) > 19 and stem[18] == "-" else None


def check(spike=SPIKE, cmd=None, arm=None, own_transcript=None):
    """Returns (state, reasons). state is bound only when reasons is empty."""
    reasons = []
    rc, head, _ = _git(spike, "rev-parse", "HEAD")
    head = head.strip() if rc == 0 else None
    v, err = read_validation(spike)
    state = {"head": head, "validation_commit": v and v["validation_commit"],
             "manifest_sha256": v and v["manifest_sha256"]}
    if not head:
        reasons.append("not a git work tree")
    if err:
        reasons.append(err)
    if v and head:
        vc = v["validation_commit"]
        if _git(spike, "cat-file", "-e", vc + "^{commit}")[0] != 0:
            reasons.append(f"validation commit {vc} is not in this repository")
        else:
            if _git(spike, "merge-base", "--is-ancestor", vc, "HEAD")[0] != 0:
                reasons.append(f"validation commit {vc} is not an ancestor of HEAD")
            if _git(spike, "diff", "--quiet", vc, "HEAD", "--", *BOUND_PATHS)[0] != 0:
                reasons.append("HEAD's harness, PRE-REGISTRATION-2.md or ORACLE.md differ from "
                               "the validation commit")
            reasons += harness_files_differ(spike, vc)
    rc, st, _ = _git(spike, "status", "--porcelain", "--ignored", "--untracked-files=all",
                     "--", *BOUND_PATHS)
    if st.strip():
        reasons.append("uncommitted or ignored files under the harness or the frozen documents: "
                       + "; ".join(st.splitlines()[:5]))
    # results/prereg2: nothing uncommitted but this run's own transcript, and
    # VALIDATION before any Arm 0 result is committed.
    rc, st, _ = _git(spike, "status", "--porcelain", "--untracked-files=all", "--", RESULTS_REL)
    top = toplevel(spike) or spike
    own = os.path.realpath(own_transcript) if own_transcript else None
    _, arm0_tracked, _ = _git(spike, "ls-files", "--", os.path.join(RESULTS_REL, "arm0"))
    for line in st.splitlines():
        path = os.path.realpath(os.path.join(top, line[3:]))
        if own and path == own:
            continue
        if (line.startswith("?? ") and path == os.path.realpath(os.path.join(spike, VALIDATION_REL))
                and not arm0_tracked.strip()):
            continue
        reasons.append(f"uncommitted under {RESULTS_REL}: {line}")
    if cmd in ("arm0", "score", "export"):
        tdir = os.path.join(spike, TRANSCRIPTS_REL)
        want = cmd + (f"-{arm}" if arm else "")
        for f in sorted(os.listdir(tdir)) if os.path.isdir(tdir) else []:
            p = os.path.realpath(os.path.join(tdir, f))
            if p != own and transcript_tag(f) == want:
                reasons.append(f"an earlier {cmd}{' ' + arm if arm else ''} transcript exists "
                               f"({f}); the first execution binds")
    state["bound"] = not reasons
    state["reasons"] = reasons
    return state, reasons
