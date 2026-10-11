# SPDX-License-Identifier: MIT
"""PRE-REGISTRATION-3.md §6, §7, §9 H4/H5: the checks that order prereg 3's
steps against prereg 2's.

- order_guard: export refuses once prereg 2's tiering has started. It looks
  in the work tree, every other work tree, and every ref and reflog. It
  catches mistakes; it is not a guarantee: a tier-run in a separate clone,
  in a removed work tree, or on a branch deleted with its work tree is not
  seen.
- committed_order: from committed records only, the export-3 commit is an
  ancestor of the commit adding prereg 2's tiers.jsonl, and prereg 2's first
  started tier-run is later than export 3's execution. It catches a binding
  prereg 2 tier-run done out of order; it does not catch an earlier tier-run
  thrown away without a record.
- verdict_gate: prereg 2's verdict is committed, bound to d79bf2e and
  unchanged since; its tiers.jsonl and a tier-runs.txt with a started run
  are committed in the verdict commit's history.
- tier_model: results/prereg2/tier-model.json is the pinned blob.
- window: the start day and the 14-day window counted from the verdict
  commit's UTC day.
"""
import datetime
import json
import os

from . import binding as BD

R2 = os.path.join("results", "prereg2")
R3 = os.path.join("results", "prereg3")
TIER_RUNS2 = os.path.join(R2, "tier-runs.txt")
TIERS2 = os.path.join(R2, "tiers.jsonl")
VERDICT2 = os.path.join(R2, "verdict.json")
TIER_MODEL2 = os.path.join(R2, "tier-model.json")
TIER_MODEL_BLOB = "3ded7091b9b7b825853c140ee7ecc3c63bef2e96"
EXPORT3 = os.path.join(R3, "export")
WINDOW_DAYS = 14


class GateError(Exception):
    pass


def _rel(spike, rel):
    return os.path.relpath(os.path.join(spike, rel), BD.toplevel(spike))


def _adding(spike, rel, *rev):
    _, out, _ = BD._git(spike, "log", *rev, "--full-history", "--format=%H", "--diff-filter=A", "--", rel)
    return out.split()


def _ancestor(spike, a, b):
    return BD._git(spike, "merge-base", "--is-ancestor", a, b)[0] == 0


def _worktrees(spike):
    _, out, _ = BD._git(spike, "worktree", "list", "--porcelain")
    return [ln.split(" ", 1)[1] for ln in out.splitlines() if ln.startswith("worktree ")]


def prereg2_tiering_started(spike):
    """Reasons to believe prereg 2's tiering has started; empty if none seen."""
    found = []
    top = BD.toplevel(spike)
    spike_rel = os.path.relpath(spike, top)
    for wt in _worktrees(spike) or [top]:
        base = os.path.join(wt, spike_rel, R2)
        if os.path.lexists(os.path.join(base, "tier-runs.txt")):
            found.append(f"{os.path.join(base, 'tier-runs.txt')} exists")
        if os.path.isdir(base):
            found += [f"{os.path.join(base, d)} exists" for d in sorted(os.listdir(base))
                      if d.startswith("tier-work-")]
    for rel in (TIER_RUNS2, os.path.join(R2, "tier-work-1"), os.path.join(R2, "tier-work-2"), TIERS2):
        _, out, _ = BD._git(spike, "log", "--all", "--reflog", "--full-history", "--format=%H", "--", rel)
        if out.strip():
            found.append(f"{rel} is in the history at {out.split()[0][:12]}")
    return found


def order_guard(spike):
    found = prereg2_tiering_started(spike)
    if found:
        raise GateError("prereg 2's tiering has started; export 3 must come first (§7): " + "; ".join(found))


def _show(spike, commit, rel):
    rc, out, _ = BD._git(spike, "show", f"{commit}:{_rel(spike, rel)}")
    return out if rc == 0 else None


def _executed_time(text):
    for ln in (text or "").splitlines():
        if ln.startswith("# executed: "):
            return ln[len("# executed: "):].strip()
    return None


def committed_order(spike):
    """Raises GateError unless §9 H5's committed order holds. Returns lines."""
    e3 = _adding(spike, EXPORT3)
    t2 = _adding(spike, TIERS2)
    if len(e3) != 1 or len(t2) != 1:
        raise GateError(f"{len(e3)} commits add {EXPORT3} and {len(t2)} add {TIERS2}; want one each")
    if not _ancestor(spike, e3[0], t2[0]) or e3[0] == t2[0]:
        raise GateError(f"the export-3 commit {e3[0][:12]} is not an ancestor of {t2[0][:12]}, "
                        f"which adds prereg 2's tiers.jsonl")
    runs = _show(spike, "HEAD", TIER_RUNS2)
    started = []
    for ln in (runs or "").splitlines():
        try:
            o = json.loads(ln)
        except ValueError:
            continue
        if o.get("event") == "started":
            started.append(o.get("at"))
    if not started:
        raise GateError(f"no committed {TIER_RUNS2} with a started run")
    marker = _show(spike, "HEAD", os.path.join(R3, "executed", "export.json"))
    try:
        tname = json.loads(marker)["transcript"]
    except (TypeError, ValueError, KeyError):
        raise GateError("no committed export-3 execution marker")
    when = _executed_time(_show(spike, "HEAD", os.path.join(R3, "transcripts", tname)))
    if not when:
        raise GateError("export 3's committed transcript records no '# executed:' time")
    first = datetime.datetime.fromisoformat(started[0])
    ex = datetime.datetime.fromisoformat(when.replace("Z", "+00:00"))
    if not first > ex:
        raise GateError(f"prereg 2's first tier-run started at {started[0]}, not after export 3 "
                        f"executed at {when}")
    return [f"export 3 ({e3[0][:12]}) is an ancestor of prereg 2's tiers.jsonl ({t2[0][:12]})",
            f"prereg 2's first tier-run started {started[0]}, after export 3 executed {when}"]


def verdict_gate(spike):
    """§9 H4's gate. Returns the verdict commit. Never reads the verdict's
    value: §0 item 4 re-tiers whatever it says."""
    vs = _adding(spike, VERDICT2)
    if len(vs) != 1:
        raise GateError(f"{len(vs)} commits add {VERDICT2}; want exactly one")
    vc = vs[0]
    _, touched, _ = BD._git(spike, "log", "--full-history", "--format=%H", "--", VERDICT2)
    if touched.split() != [vc]:
        raise GateError(f"{VERDICT2} has changed since {vc[:12]} added it")
    try:
        v = json.loads(_show(spike, vc, VERDICT2))
    except (TypeError, ValueError):
        raise GateError(f"{VERDICT2} at {vc[:12]} is not JSON")
    if v.get("bound") is not True or (v.get("binding") or {}).get("validation_commit") != BD.PREREG2_VALIDATION:
        raise GateError(f"{VERDICT2} is not a bound output of {BD.PREREG2_VALIDATION[:12]}")
    t2 = _adding(spike, TIERS2)
    if len(t2) != 1 or not _ancestor(spike, t2[0], vc):
        raise GateError(f"no commit adding {TIERS2} in the verdict commit's history")
    runs = _show(spike, vc, TIER_RUNS2)
    if not runs or not any(json.loads(ln).get("event") == "started" for ln in runs.splitlines() if ln.strip()):
        raise GateError(f"{TIER_RUNS2} with a started run is not committed in the verdict commit's history")
    return vc


def tier_model(spike):
    """The tierer model, from the pinned tier-model.json."""
    rc, blob, _ = BD._git(spike, "rev-parse", f"HEAD:{_rel(spike, TIER_MODEL2)}")
    if rc != 0 or blob.strip() != TIER_MODEL_BLOB:
        raise GateError(f"{TIER_MODEL2} at HEAD is not blob {TIER_MODEL_BLOB[:12]}")
    p = os.path.join(spike, TIER_MODEL2)
    _, h, _ = BD._git(spike, "hash-object", "--no-filters", "--", p)
    if h.strip() != TIER_MODEL_BLOB:
        raise GateError(f"the work tree's {TIER_MODEL2} differs from the pinned blob")
    return json.load(open(p))["model"]


def commit_day(spike, commit):
    rc, out, _ = BD._git(spike, "log", "-1", "--format=%cI", commit)
    if rc != 0 or not out.strip():
        raise GateError(f"cannot read the committer date of {commit}")
    return datetime.datetime.fromisoformat(out.strip()).astimezone(datetime.timezone.utc).date()


def window(cday, today, late_reason=None):
    """Start day: the first UTC day after cday. Within 14 days of cday, or a
    logged late run. Returns a line to log."""
    start = cday + datetime.timedelta(days=1)
    if today < start:
        raise GateError(f"prereg 3's tiering starts on {start}, the first UTC day after prereg 2's "
                        "verdict commit")
    if (today - cday).days > WINDOW_DAYS:
        if not late_reason:
            raise GateError(f"{(today - cday).days} days after prereg 2's verdict commit: a run after "
                            f"{WINDOW_DAYS} days needs --late-reason")
        return f"LATE RUN, {(today - cday).days} days after the verdict commit. Reason: {late_reason}"
    return f"verdict commit day {cday}; start day {start}; today {today}; within the window"
