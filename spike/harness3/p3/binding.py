# SPDX-License-Identifier: MIT
"""PRE-REGISTRATION-3.md §9 H1: the binding, with its namespace as a
parameter.

This is p2/binding.py's logic, parameterised by a namespace `NS`, so that
prereg 3's markers, validation file and results live under their own names
and never collide with prereg 2's (round-2 review M2). The git helpers are
prereg 2's, imported unchanged.

On top of p2's checks, a prereg 3 bound command also refuses unless prereg 2's
bound paths -- harness/, PRE-REGISTRATION-2.md, ORACLE.md -- hold exactly
their bytes at prereg 2's validation commit d79bf2e, because prereg 3 runs
prereg 2's code (H1).

WHAT IT DOES NOT ENFORCE is what p2/binding.py's docstring says: whoever runs
the harness can run other code. The review step re-derives the validation
commit in a fresh clone.
"""
import json
import os
import re

from p2 import binding as B2

HEX64 = re.compile(r"^[0-9a-f]{64}$")
PREREG2_VALIDATION = "d79bf2e61f5f7c0bcfdde5e17d44604b0fac9301"


class NS:
    """A binding namespace."""

    def __init__(self, name, bound_paths, results_rel):
        self.name = name
        self.bound_paths = tuple(bound_paths)
        self.results_rel = results_rel
        self.validation_rel = os.path.join(results_rel, "VALIDATION")
        self.transcripts_rel = os.path.join(results_rel, "transcripts")
        self.executed_rel = os.path.join(results_rel, "executed")


PREREG2 = NS("prereg2", B2.BOUND_PATHS, B2.RESULTS_REL)
PREREG3 = NS("prereg3", ("harness3", "PRE-REGISTRATION-3.md"), os.path.join("results", "prereg3"))

_git = B2._git
git_env = B2.git_env
common_dir = B2.common_dir
history_unsound = B2.history_unsound
toplevel = B2.toplevel
transcript_tag = B2.transcript_tag


def derive_validation(spike, ns):
    """(validation commit, manifest sha256, reasons), for namespace ns."""
    _, added, _ = _git(spike, "log", "--full-history", "--format=%H", "--diff-filter=A", "--",
                       ns.validation_rel)
    added = added.split()
    if len(added) != 1:
        return None, None, [f"{len(added)} commits in HEAD's history add {ns.validation_rel}; "
                            "the validation commit is the one that adds it"]
    vc = added[0]
    _, touched, _ = _git(spike, "log", "--full-history", "--format=%H", "--", ns.validation_rel)
    if touched.split() != [vc]:
        return vc, None, [f"{ns.validation_rel} has changed since the validation commit added it"]
    rel = os.path.relpath(os.path.join(spike, ns.validation_rel), toplevel(spike))
    _, raw, _ = _git(spike, "show", f"{vc}:{rel}")
    try:
        v = json.loads(raw)
        sha = v["manifest_sha256"]
        assert isinstance(sha, str) and HEX64.match(sha) and set(v) == {"manifest_sha256"}
    except (ValueError, KeyError, AssertionError, TypeError):
        return vc, None, [f"{ns.validation_rel} must hold exactly a 64-hex manifest_sha256"]
    return vc, sha, []


def files_differ(spike, commit, paths):
    """Every file under `paths` whose work-tree bytes are not `commit`'s,
    plus every file there that `commit` does not hold."""
    top = toplevel(spike)
    prefix = os.path.relpath(spike, top)
    _, out, _ = _git(spike, "ls-tree", "-r", "--full-name", commit, "--", *paths)
    want = {}
    for line in out.splitlines():
        meta, path = line.split("\t", 1)
        want[os.path.relpath(path, prefix)] = meta.split()[2]
    bad = []
    if not want:
        bad.append(f"{commit[:12]} holds none of {', '.join(paths)}")
    for rel, blob in sorted(want.items()):
        p = os.path.join(spike, rel)
        if os.path.islink(p) or not os.path.isfile(p):
            bad.append(f"{rel}: missing or not a regular file")
            continue
        _, h, _ = _git(spike, "hash-object", "--no-filters", "--", p)
        if h.strip() != blob:
            bad.append(f"{rel}: work-tree bytes differ from {commit[:12]}")
    for b in paths:
        base = os.path.join(spike, b)
        if os.path.isdir(base):
            for root, _dirs, files in os.walk(base):
                for f in files:
                    rel = os.path.relpath(os.path.join(root, f), spike)
                    if rel not in want:
                        bad.append(f"{rel}: not in {commit[:12]} (untracked or ignored)")
    return bad


def prereg2_untouched(spike, commit=PREREG2_VALIDATION):
    """H1: prereg 2's harness and frozen documents are byte-identical to
    prereg 2's validation commit, and no commit after it touched them."""
    bad = files_differ(spike, commit, PREREG2.bound_paths)
    _, later, _ = _git(spike, "rev-list", "--full-history", f"{commit}..HEAD", "--", *PREREG2.bound_paths)
    if later.strip():
        bad.append(f"a commit after {commit[:12]} changes prereg 2's harness or frozen documents: "
                   f"{later.split()[0][:12]}")
    return bad


def marker_rel(ns, cmd, arm=None):
    return os.path.join(ns.executed_rel, f"{cmd}" + (f"-{arm}" if arm else "") + ".json")


def executed(spike, ns, cmd, arm=None):
    """Whether `cmd` has executed in namespace ns: its marker is in the work
    tree, in <git common dir>/<ns.name>/, or in any ref's history or reflog."""
    rel = marker_rel(ns, cmd, arm)
    if os.path.lexists(os.path.join(spike, rel)):
        return True
    cd = common_dir(spike)
    if cd and os.path.lexists(os.path.join(cd, ns.name, os.path.basename(rel))):
        return True
    _, out, _ = _git(spike, "log", "--all", "--reflog", "--full-history", "--format=%H",
                     "--diff-filter=A", "--", rel)
    return bool(out.strip())


def mark_executed(spike, ns, cmd, arm, transcript_path):
    """Written once the command's input is opened. Never overwritten."""
    body = json.dumps({"cmd": cmd, "arm": arm, "transcript": os.path.basename(transcript_path)},
                      sort_keys=True) + "\n"
    cd = common_dir(spike)
    paths = [os.path.join(spike, marker_rel(ns, cmd, arm))]
    if cd:
        paths.append(os.path.join(cd, ns.name, os.path.basename(marker_rel(ns, cmd, arm))))
    for p in paths:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        with os.fdopen(fd, "w") as f:
            f.write(body)


def check(spike, ns=PREREG3, cmd=None, arm=None, own_transcript=None, once=("export",)):
    """(state, reasons) for a bound command in namespace ns. state is bound
    only when reasons is empty."""
    reasons = []
    rc, head, _ = _git(spike, "rev-parse", "HEAD")
    head = head.strip() if rc == 0 else None
    state = {"head": head, "validation_commit": None, "manifest_sha256": None}
    if not head:
        reasons.append("not a git work tree")
    elif history_unsound(spike):
        reasons += history_unsound(spike)
    else:
        vc, msha, rs = derive_validation(spike, ns)
        reasons += rs
        state.update(validation_commit=vc, manifest_sha256=msha)
        if vc and not rs:
            if _git(spike, "rev-parse", "--verify", "-q", f"{vc}^")[0] != 0 or _git(
                    spike, "diff", "--quiet", f"{vc}^", vc, "--", *ns.bound_paths)[0] != 0:
                reasons.append(f"the validation commit {vc[:12]} itself changes "
                               f"{' or '.join(ns.bound_paths)}; it may add VALIDATION only")
            _, later, _ = _git(spike, "rev-list", "--full-history", f"{vc}..HEAD", "--", *ns.bound_paths)
            if later.strip():
                reasons.append(f"a commit after the validation commit {vc[:12]} changes "
                               f"{' or '.join(ns.bound_paths)}: {later.split()[0][:12]}")
            reasons += files_differ(spike, vc, ns.bound_paths)
        if ns is PREREG3:
            reasons += prereg2_untouched(spike)
    _, st, _ = _git(spike, "status", "--porcelain", "--ignored", "--untracked-files=all",
                    "--", *ns.bound_paths)
    if st.strip():
        reasons.append("uncommitted or ignored files under " + ", ".join(ns.bound_paths) + ": "
                       + "; ".join(st.splitlines()[:5]))
    _, st, _ = _git(spike, "status", "--porcelain", "--untracked-files=all", "--", ns.results_rel)
    top = toplevel(spike) or spike
    own = os.path.realpath(own_transcript) if own_transcript else None
    for line in st.splitlines():
        path = os.path.realpath(os.path.join(top, line[3:]))
        if own and path == own:
            continue
        reasons.append(f"uncommitted under {ns.results_rel}: {line}")
    if cmd in once and executed(spike, ns, cmd, arm):
        reasons.append(f"{cmd} has already executed ({marker_rel(ns, cmd, arm)}); the first execution binds")
    state["bound"] = not reasons
    state["reasons"] = reasons
    return state, reasons
