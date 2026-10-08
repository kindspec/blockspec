# SPDX-License-Identifier: MIT
"""PRE-REGISTRATION-2.md §6.2 and §6.3: corpora, pins, bundles, selection,
the E and S enumerators, the pathspec-aware M filter, the site-policy subject
rule, and the hash-ranked sampler.

Nothing here reads a corpus except through git at its pin.
"""
import hashlib
import json
import os
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor

from . import mech as Mx

C, P = Mx.C, Mx.P

HERE = os.path.dirname(os.path.abspath(__file__))

# §6.2. `prefix` is the literal leading directory of the pathspec, handed to
# find_merge_cases(); the M filter then applies the pathspec itself.
ARMS = {
    "rust-book": {"bundle": "rust-book", "pin": "1500248d8f230566e4ec9f27fcbb8fe9e2898ab1",
                  "pathspec": "src/*.md", "prefix": "src/"},
    "obsidian-help": {"bundle": "obsidian-help", "pin": "327a782e90481268361b5ccccdb0c224b2b13fe6",
                      "pathspec": "en/*.md", "prefix": "en/"},
    "cmspec": {"bundle": "cmspec", "pin": "3da939428d80f146f270cd1765e4ba462e96bb1b",
               "pathspec": "*.md", "prefix": ""},
    "k8s-en": {"bundle": "kubernetes-website", "pin": "6b27baef1e44275fd4368e14375296e1dfe5af11",
               "pathspec": "content/en/*.md", "prefix": "content/en/"},
    "k8s-l10n": {"bundle": "kubernetes-website", "pin": "6b27baef1e44275fd4368e14375296e1dfe5af11",
                 "pathspec": "content/*.md :(exclude)content/en/", "prefix": "content/"},
    "cncf-toc": {"bundle": "cncf-toc", "pin": "144c2e3215884e498e744cc51e6b7cef82d654f1",
                 "pathspec": "*.md :(exclude).github/", "prefix": ""},
    "site-policy": {"bundle": "site-policy", "pin": "b9578b546d2506febda1da2cd7431644d58e512c",
                    "pathspec": "*.md :(exclude).github/", "prefix": ""},
}
ARM_ORDER = list(ARMS)
VERDICT_RULE = "yaml-fence"                      # §6.3
RULES = ("yaml-fence", "none", "anywhere")       # the other two: beside, no verdict
SAMPLE_E = 1000                                  # §6.5
SAMPLE_S = 500
GAPS = (5, 25)
SITE_POLICY_STRICT = ("automated-sync", "repo-sync")
SITE_POLICY_25 = ("automated-sync",)
SITE_POLICY_EXPECTED_STRICT = 21                 # first registration §5.1


# Where the bundles are read from (LOG.md §15): $PREREG2_BUNDLE_DIR, else the
# durable local copy of the release recorded in bundles.json.
DEFAULT_BUNDLE_DIR = os.environ.get("PREREG2_BUNDLE_DIR", "/home/cam/kindspec-data/prereg2-bundles")


class NoVerdict(Exception):
    """An arm that cannot be run: it reports NO VERDICT with this reason."""


def bundles():
    with open(os.path.join(HERE, "bundles.json")) as f:
        return json.load(f)


def git_env():
    e = dict(os.environ)
    e.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
              "GIT_CONFIG_SYSTEM": os.devnull, "LC_ALL": "C", "GIT_TERMINAL_PROMPT": "0"})
    for k in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY"):
        e.pop(k, None)
    return e


def git(repo, *a, input=None, check=True):
    r = subprocess.run(["git", "-C", repo, *a], capture_output=True, input=input,
                       env=git_env())
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(a)} -> {r.returncode}: "
                           f"{r.stderr.decode(errors='replace')[:300]}")
    return r


def gtext(repo, *a, **k):
    return git(repo, *a, **k).stdout.decode("utf-8")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def open_corpus(arm, bundle_dir, work_dir, table=None):
    """Verify the arm's bundle against its committed sha256, fetch it into a
    fresh repository under work_dir, and check out the pin. Raises NoVerdict
    when the pin is absent from the bundle (§6.2)."""
    table = table or ARMS
    spec = table[arm]
    want = bundles()[spec["bundle"]] if table is ARMS else spec["bundle_meta"]
    bpath = os.path.join(bundle_dir, spec["bundle"] + ".bundle")
    if not os.path.isfile(bpath):
        raise FileNotFoundError(f"{arm}: bundle not found: {bpath}")
    got = sha256_file(bpath)
    if got != want["sha256"]:
        raise RuntimeError(f"{arm}: bundle sha256 {got} != committed {want['sha256']}")
    repo = os.path.join(work_dir, spec["bundle"])
    if os.path.exists(repo):
        raise RuntimeError(f"{arm}: {repo} exists; corpora are always fetched fresh")
    os.makedirs(repo)
    git(repo, "init", "-q")
    git(repo, "fetch", "-q", bpath, "HEAD")
    if git(repo, "cat-file", "-e", spec["pin"] + "^{commit}", check=False).returncode != 0:
        raise NoVerdict(f"{arm}: pin {spec['pin']} is absent from its bundle")
    git(repo, "-c", "advice.detachedHead=false", "checkout", "-q", "--detach", spec["pin"])
    return repo


def check_pin(arm, repo, pin):
    """d8_cheap_arm.check_corpus: a git root at the pin, no tracked changes."""
    C.check_corpus(arm, repo, pin)


def selection(arm, repo, pathspec):
    """{rule: [selected paths]} at the pin. The yaml-fence rule decides
    (§6.3); none and anywhere are reported beside it."""
    return {rule: C.select_files(arm, repo, pathspec, rule)[0] for rule in RULES}


def rank(arm, key):
    """§6.3: sha256("prereg2:" + arm + ":" + key)."""
    return hashlib.sha256(f"prereg2:{arm}:{key}".encode("utf-8")).hexdigest()


def sample(arm, keys, k):
    """The k lowest-ranked keys. Excluding a key that was not selected cannot
    change the sample, because each key's rank depends on nothing else."""
    return sorted(keys, key=lambda x: (rank(arm, x), x))[:k]


# ---------------------------------------------------------------- arm E

_STATUS = re.compile(r"^[ACDMRTUX][0-9]*$")


def _parse_diff_tree(raw):
    """Parse `git diff-tree --stdin -z --name-status` output into
    [(commit, status, [paths])]."""
    toks = raw.split(b"\0")
    out, commit, i = [], None, 0
    while i < len(toks):
        t = toks[i].decode("utf-8", errors="surrogateescape")
        if t == "":
            i += 1
            continue
        if _STATUS.match(t):
            n = 2 if t[0] in "RC" else 1
            paths = [toks[i + 1 + j].decode("utf-8", errors="surrogateescape") for j in range(n)]
            out.append((commit, t, paths))
            i += 1 + n
        else:
            commit = t
            i += 1
    return out


def enumerate_e(arm, repo, pin, selected):
    """§6.5 Arm E. Population: each (commit, path) where the commit is not a
    merge (`git rev-list --no-merges <pin>`), the path is selected at the pin,
    and the commit modifies the path against its parent (--no-renames).
    Adds, deletes and renames are excluded and counted.

    Returns (population [(commit, parent, path)], counts, authors)."""
    sel = set(selected)
    revs, entries, renames, parents, authors = _e_history(repo, pin)
    counts = {"commits:no_merges": len(revs), "population": 0, "excluded:add": 0,
              "excluded:delete": 0, "excluded:rename": 0, "excluded:other_status": 0,
              "path_not_selected": 0}
    pop = []
    for commit, st, paths in entries:
        path = paths[-1]
        if path not in sel:
            counts["path_not_selected"] += 1
            continue
        if st == "M":
            pop.append((commit, parents[commit], path))
        elif st == "A":
            counts["excluded:add"] += 1
        elif st == "D":
            counts["excluded:delete"] += 1
        else:
            counts["excluded:other_status"] += 1
    counts["excluded:rename"] = sum(1 for _, st, ps in renames
                                    if st.startswith("R") and (ps[0] in sel or ps[1] in sel))
    counts["population"] = len(pop)
    return pop, counts, authors


_E_CACHE = {}


def _e_history(repo, pin):
    """The non-merge history at the pin, read once per repository and pin:
    (revs, --no-renames entries, -M rename entries, parents, authors)."""
    key = (os.path.realpath(repo), pin)
    if key not in _E_CACHE:
        revs = gtext(repo, "rev-list", "--no-merges", pin).split()
        stdin = "\n".join(revs).encode() + b"\n"
        raw = git(repo, "diff-tree", "--stdin", "-r", "--root", "--no-renames",
                  "--name-status", "-z", input=stdin).stdout if revs else b""
        # Renames, counted with git's default rename detection. Under
        # --no-renames each is also one add and one delete, so this count
        # overlaps those; it is reported, never subtracted.
        rraw = git(repo, "diff-tree", "--stdin", "-r", "--root", "-M", "--diff-filter=R",
                   "--name-status", "-z", input=stdin).stdout if revs else b""
        parents = {}
        for line in gtext(repo, "rev-list", "--no-merges", "--parents", pin).splitlines():
            p = line.split()
            parents[p[0]] = p[1] if len(p) > 1 else None
        authors = {}
        for line in gtext(repo, "log", "--no-merges", "--format=%H%x00%an <%ae>", pin).splitlines():
            h, a = line.split("\0", 1)
            authors[h] = a
        _E_CACHE[key] = (revs, _parse_diff_tree(raw), _parse_diff_tree(rraw), parents, authors)
    return _E_CACHE[key]


def e_key(item):
    commit, _, path = item
    return f"{commit}:{path}"


# ---------------------------------------------------------------- arm S

_H_CACHE = {}


def path_history(repo, path):
    """`git log --format=%H --reverse -- <path>` at the pin (HEAD)."""
    key = (os.path.realpath(repo), path)
    if key not in _H_CACHE:
        _H_CACHE[key] = [c for c in gtext(repo, "log", "--format=%H", "--reverse", "--", path)
                         .split("\n") if c]
    return _H_CACHE[key]


def blob_ids(repo, specs):
    """{"<commit>:<path>": blob sha or None} by one cat-file --batch-check."""
    if not specs:
        return {}
    out = git(repo, "cat-file", "--batch-check=%(objectname) %(objecttype)",
              input=("\n".join(specs) + "\n").encode("utf-8")).stdout.decode().splitlines()
    res = {}
    for s, line in zip(specs, out):
        f = line.split()
        res[s] = f[0] if len(f) == 2 and f[1] == "blob" else None
    return res


def enumerate_s(arm, repo, selected, gaps=GAPS, workers=8):
    """§6.5 Arm S. For each selected path, its history; pairs (cs[i],
    cs[i+gap]) where both blobs exist and differ. Returns
    ({gap: [(path, i, ci, cj)]}, counts, authors)."""
    paths = list(selected)
    with ThreadPoolExecutor(workers) as ex:
        hist = dict(zip(paths, ex.map(lambda p: path_history(repo, p), paths)))
    specs = sorted({f"{c}:{p}" for p, cs in hist.items() for c in cs})
    blobs = blob_ids(repo, specs)
    pops, counts = {}, {"paths": len(paths)}
    for gap in gaps:
        pop = []
        pairs = missing = same = 0
        for p in paths:
            cs = hist[p]
            for i in range(len(cs) - gap):
                pairs += 1
                a, b = blobs.get(f"{cs[i]}:{p}"), blobs.get(f"{cs[i + gap]}:{p}")
                if a is None or b is None:
                    missing += 1
                elif a == b:
                    same += 1
                else:
                    pop.append((p, i, cs[i], cs[i + gap]))
        pops[gap] = pop
        counts[f"gap{gap}:pairs"] = pairs
        counts[f"gap{gap}:excluded:blob_missing"] = missing
        counts[f"gap{gap}:excluded:blobs_equal"] = same
        counts[f"gap{gap}:population"] = len(pop)
    authors = {}
    for line in gtext(repo, "log", "--format=%H%x00%an <%ae>").splitlines():
        h, a = line.split("\0", 1)
        authors[h] = a
    return pops, counts, authors


def s_key(item, gap):
    path, i, _, _ = item
    return f"{path}:{i}:{gap}"


# ---------------------------------------------------------------- arm M

def merge_subject(repo, merge):
    """`git log -1 --format=%s <merge>`."""
    return gtext(repo, "log", "-1", "--format=%s", merge).rstrip("\n")


def site_policy_sets(subject):
    """§6.2: (in the strict set, in the 25-case set). Case-sensitive
    substrings of the subject line."""
    return (not any(s in subject for s in SITE_POLICY_STRICT),
            not any(s in subject for s in SITE_POLICY_25))


def m_filter(arm, repo, cases, selected_by_rule):
    """§6.5 Arm M, the new pathspec-aware filter: keep a find_merge_cases()
    case only if its path is selected at the pin under some rule, and tag it
    with the rules that select it; for site-policy, tag the strict and
    25-case sets. Returns (kept cases, counts)."""
    sel = {r: set(v) for r, v in selected_by_rule.items()}
    kept, counts = [], {"cases_in": len(cases), "dropped:not_selected": 0}
    for c in cases:
        rules = [r for r in RULES if c["path"] in sel[r]]
        if not rules:
            counts["dropped:not_selected"] += 1
            continue
        c = dict(c, rules=rules)
        if arm == "site-policy":
            subj = merge_subject(repo, c["meta"]["merge"])
            strict, s25 = site_policy_sets(subj)
            c["meta"] = dict(c["meta"], subject=subj)
            c["strict"], c["set25"] = strict, s25
        kept.append(c)
    counts["kept"] = len(kept)
    for r in RULES:
        counts[f"kept:{r}"] = sum(1 for c in kept if r in c["rules"])
    if arm == "site-policy":
        counts["strict"] = sum(1 for c in kept if c["strict"] and VERDICT_RULE in c["rules"])
        counts["set25"] = sum(1 for c in kept if c["set25"] and VERDICT_RULE in c["rules"])
        # §6.2: "If the rule leaves a different number, the rule's count
        # stands and the difference is logged."
        counts["strict_expected"] = SITE_POLICY_EXPECTED_STRICT
        counts["strict_difference"] = counts["strict"] - SITE_POLICY_EXPECTED_STRICT
    return kept, counts
