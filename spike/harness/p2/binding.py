# SPDX-License-Identifier: MIT
"""§9: "The harness at the validation commit is the implementation." This
module checks that, mechanically, before every bound run (reviews C1, C3, B6;
re-reviews H2, H3, M3, M-a, M-c; LOG.md §16, §18, §20).

WHAT IT DOES NOT ENFORCE. Whoever runs the harness can run other code: an
operator who edits this file, or runs a program of their own, defeats every
check here. A forged history -- an orphan branch carrying its own harness and
VALIDATION -- derives a validation commit of its own. These checks stop
mistakes and casual shortcuts; the guarantee is the review step in
spike/README.md: in each §9 pull request, re-derive the validation commit
in a fresh clone and compare it with every output's binding.validation_commit.

THE VALIDATION COMMIT IS DERIVED, never named. `prereg2.py seal` writes
`results/prereg2/VALIDATION`, which holds the sealed manifest's sha256 (§7.3:
"The manifest's sha256 is committed in the validation commit"). The validation
commit is the one commit in HEAD's history that added VALIDATION. VALIDATION
may never change after it, and no later commit may touch the harness,
PRE-REGISTRATION-2.md or ORACLE.md.

Every bound command checks:

- exactly one commit added VALIDATION, VALIDATION has not changed since, and
  its sha256 field is 64 hex characters;
- no commit after the validation commit touches the bound paths;
- the work tree holds exactly the validation commit's bytes there: each file
  is hashed with `git hash-object` and compared with `git ls-tree`, so
  `--assume-unchanged` cannot hide an edit, and no untracked or ignored file
  may sit under the harness;
- `results/prereg2/` has nothing uncommitted except this invocation's own
  transcript, so every earlier transcript, aborted ones included, is
  committed before the next bound run starts;
- for arm0, score and export: the command has not executed for that arm.
  An execution is marked by `results/prereg2/executed/<cmd>[-<arm>].json`,
  written only once the corpus (or, for export, the scored input) is
  actually opened, so a refusal or a usage error does not use up the arm
  (H3). A second copy goes in the common git directory
  (`$(git rev-parse --git-common-dir)/prereg2/`), shared by every worktree.
  The marker is looked for in the work tree, the common git directory, and
  every ref's history and reflog (`git log --all --reflog`), so `rm`,
  `git clean`, deleting a branch or a second worktree does not re-enable
  the arm (M3, M-a).
- the history is not shallow and is not rewritten by replace refs or
  grafts, every history walk uses --full-history, and every git call runs
  without the caller's GIT_* variables or user config (M-c).
"""
import json
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
SPIKE = os.path.dirname(os.path.dirname(HERE))
BOUND_PATHS = ("harness", "PRE-REGISTRATION-2.md", "ORACLE.md")
RESULTS_REL = os.path.join("results", "prereg2")
VALIDATION_REL = os.path.join(RESULTS_REL, "VALIDATION")
TRANSCRIPTS_REL = os.path.join(RESULTS_REL, "transcripts")
EXECUTED_REL = os.path.join(RESULTS_REL, "executed")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def git_env():
    """Git as a stranger's clone sees it: no GIT_* variable from the caller
    (GIT_DIR, GIT_WORK_TREE, ...), no system or user config, and no replace
    objects (re-review M-c)."""
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
              "GIT_CONFIG_SYSTEM": os.devnull, "GIT_NO_REPLACE_OBJECTS": "1",
              "GIT_TERMINAL_PROMPT": "0", "LC_ALL": "C"})
    return e


def _git(spike, *a):
    r = subprocess.run(["git", "-C", spike, *a], capture_output=True, text=True, env=git_env())
    return r.returncode, r.stdout, r.stderr


def common_dir(spike):
    rc, out, _ = _git(spike, "rev-parse", "--git-common-dir")
    return os.path.realpath(os.path.join(spike, out.strip())) if rc == 0 else None


def history_unsound(spike):
    """A history the derivation cannot trust: shallow, or rewritten by
    replace refs or grafts."""
    bad = []
    _, sh, _ = _git(spike, "rev-parse", "--is-shallow-repository")
    if sh.strip() == "true":
        bad.append("the repository is shallow; the validation commit cannot be derived from a cut history")
    _, rep, _ = _git(spike, "for-each-ref", "--format=%(refname)", "refs/replace/")
    if rep.strip():
        bad.append(f"replace refs rewrite this history: {rep.split()[0]}")
    cd = common_dir(spike)
    if cd and os.path.exists(os.path.join(cd, "info", "grafts")):
        bad.append("info/grafts rewrites this history")
    return bad


def toplevel(spike):
    rc, out, _ = _git(spike, "rev-parse", "--show-toplevel")
    return out.strip() if rc == 0 else None


def derive_validation(spike=SPIKE):
    """(validation commit, manifest sha256, reasons)."""
    _, added, _ = _git(spike, "log", "--full-history", "--format=%H", "--diff-filter=A", "--", VALIDATION_REL)
    added = added.split()
    if len(added) != 1:
        return None, None, [f"{len(added)} commits in HEAD's history add {VALIDATION_REL}; "
                            "the validation commit is the one that adds it"]
    vc = added[0]
    _, touched, _ = _git(spike, "log", "--full-history", "--format=%H", "--", VALIDATION_REL)
    if touched.split() != [vc]:
        return vc, None, [f"{VALIDATION_REL} has changed since the validation commit added it"]
    top = toplevel(spike)
    rel = os.path.relpath(os.path.join(spike, VALIDATION_REL), top)
    rc, raw, _ = _git(spike, "show", f"{vc}:{rel}")
    try:
        v = json.loads(raw)
        sha = v["manifest_sha256"]
        assert isinstance(sha, str) and HEX64.match(sha) and set(v) == {"manifest_sha256"}
    except (ValueError, KeyError, AssertionError, TypeError):
        return vc, None, [f"{VALIDATION_REL} must hold exactly a 64-hex manifest_sha256"]
    return vc, sha, []


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
    if not want:
        bad.append(f"the validation commit {commit} holds no harness")
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


def marker_rel(cmd, arm):
    return os.path.join(EXECUTED_REL, f"{cmd}" + (f"-{arm}" if arm else "") + ".json")


def executed(spike, cmd, arm):
    """Whether this command has executed for this arm: its marker is in the
    work tree, or was ever added in any ref's history."""
    rel = marker_rel(cmd, arm)
    if os.path.lexists(os.path.join(spike, rel)):
        return True
    cd = common_dir(spike)
    if cd and os.path.lexists(os.path.join(cd, "prereg2", os.path.basename(rel))):
        return True
    _, out, _ = _git(spike, "log", "--all", "--reflog", "--full-history", "--format=%H",
                     "--diff-filter=A", "--", rel)
    return bool(out.strip())


def mark_executed(spike, cmd, arm, transcript_path):
    """Written once the corpus (or, for export, its input) is opened. An
    existing marker is never overwritten."""
    body = json.dumps({"cmd": cmd, "arm": arm, "transcript": os.path.basename(transcript_path)},
                      sort_keys=True) + "\n"
    cd = common_dir(spike)
    paths = [os.path.join(spike, marker_rel(cmd, arm))]
    # A second copy outside the work tree, in the repository's common git
    # directory: shared by every worktree, and not removed by `rm`,
    # `git clean` or deleting a branch (re-review M-a).
    if cd:
        paths.append(os.path.join(cd, "prereg2", os.path.basename(marker_rel(cmd, arm))))
    for p in paths:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        with os.fdopen(fd, "w") as f:
            f.write(body)


def check(spike=SPIKE, cmd=None, arm=None, own_transcript=None):
    """Returns (state, reasons). state is bound only when reasons is empty."""
    reasons = []
    rc, head, _ = _git(spike, "rev-parse", "HEAD")
    head = head.strip() if rc == 0 else None
    state = {"head": head, "validation_commit": None, "manifest_sha256": None}
    if not head:
        reasons.append("not a git work tree")
    elif history_unsound(spike):
        reasons += history_unsound(spike)
    else:
        vc, msha, rs = derive_validation(spike)
        reasons += rs
        state.update(validation_commit=vc, manifest_sha256=msha)
        if vc and not rs:
            _, later, _ = _git(spike, "rev-list", "--full-history", f"{vc}..HEAD", "--", *BOUND_PATHS)
            if later.strip():
                reasons.append(f"a commit after the validation commit {vc[:12]} changes the harness, "
                               f"PRE-REGISTRATION-2.md or ORACLE.md: {later.split()[0][:12]}")
            reasons += harness_files_differ(spike, vc)
    rc, st, _ = _git(spike, "status", "--porcelain", "--ignored", "--untracked-files=all",
                     "--", *BOUND_PATHS)
    if st.strip():
        reasons.append("uncommitted or ignored files under the harness or the frozen documents: "
                       + "; ".join(st.splitlines()[:5]))
    rc, st, _ = _git(spike, "status", "--porcelain", "--untracked-files=all", "--", RESULTS_REL)
    top = toplevel(spike) or spike
    own = os.path.realpath(own_transcript) if own_transcript else None
    for line in st.splitlines():
        path = os.path.realpath(os.path.join(top, line[3:]))
        if own and path == own:
            continue
        reasons.append(f"uncommitted under {RESULTS_REL}: {line}")
    if cmd in ("arm0", "score", "export") and executed(spike, cmd, arm):
        reasons.append(f"{cmd}{' ' + arm if arm else ''} has already executed "
                       f"({marker_rel(cmd, arm)}); the first execution binds")
    state["bound"] = not reasons
    state["reasons"] = reasons
    return state, reasons
