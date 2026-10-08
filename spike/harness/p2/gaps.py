# SPDX-License-Identifier: MIT
"""PRE-REGISTRATION-2.md §9, the gap rule, implemented (re-review M-e; LOG.md
§20, §21). The rule is the document's; its boundaries are readings (§21):

  "A gap is a definition here that the harness cannot implement as written.
  ... Before the Arm 0 commit. A gap, shown by a committed red test, stops
  the work ... Between the Arm 0 commit and the scoring-arm commit. A gap may
  be declared only with a committed red test that shows it. It makes the
  affected cells NO VERDICT ... After the scoring-arm commit. No gap claim,
  code change or later supersession alters any cell."

A gap is declared in `results/prereg2/gaps.json`:

  {"gaps": [{"id": "G1", "log": "§21", "red_test": "results/prereg2/gaps/G1/...",
             "cells": [["k8s-en", "E", "Q"]], "why": "one line"}]}

The red test lives under `results/prereg2/gaps/`, outside the harness, so
committing it does not change the harness the validation commit binds. Each
entry is dated by the commit that first carries it, C:

- C not strictly after the Arm 0 commit: the gap was found before Arm 0,
  which stops the work, so the aggregator refuses;
- C strictly after the Arm 0 commit and strictly before the scoring-arm
  commit: its cells become NO VERDICT, and the reason names the gap;
- C at or after the scoring-arm commit, or outside its history: it alters
  no cell, and is listed. A gaps.json version from then on is never a
  reason to refuse, whatever it says, malformed included (round 6).

Up to the scoring-arm commit, an entry must not change or disappear once
committed, its LOG entry must exist at C, and its red test must be
committed at C. The red test is checked for being committed, not run: the
harness does not show that it is red (LOG §21).

The boundaries -- a gap in the Arm 0 commit itself counts as before Arm 0,
one in the scoring-arm commit itself as after it, and one outside the
scoring-arm commit's history as after it -- are readings, logged in §21.
"""
import json
import os
import re

from .binding import RESULTS_REL, _git, history_unsound, toplevel

GAPS_REL = os.path.join(RESULTS_REL, "gaps.json")
GAP_TESTS_REL = os.path.join(RESULTS_REL, "gaps") + os.sep
ARM0_REL = os.path.join(RESULTS_REL, "arm0")
KEYS = {"id", "log", "red_test", "cells", "why"}
MODES = ("E", "S5", "S25", "M")
MECHS = ("Q", "R")


class GapError(Exception):
    pass


def _rel_top(spike, rel):
    return os.path.relpath(os.path.join(spike, rel), toplevel(spike))


def _show(spike, commit, rel):
    rc, out, _ = _git(spike, "show", f"{commit}:{_rel_top(spike, rel)}")
    return out if rc == 0 else None


def _is_ancestor(spike, a, b):
    return _git(spike, "merge-base", "--is-ancestor", a, b)[0] == 0


def _one_adding_commit(spike, rel):
    _, out, _ = _git(spike, "log", "--full-history", "--format=%H", "--diff-filter=A", "--", rel)
    return out.split()


def validate_entry(e, arms):
    if not isinstance(e, dict) or set(e) != KEYS:
        raise GapError(f"a gap entry must have exactly the keys {sorted(KEYS)}: {e!r}")
    if not (isinstance(e["id"], str) and re.match(r"^G\d+$", e["id"])):
        raise GapError(f"gap id {e['id']!r} is not G<n>")
    if not (isinstance(e["log"], str) and re.match(r"^§\d+$", e["log"])):
        raise GapError(f"gap {e['id']}: log {e['log']!r} is not §<n>")
    rt = e["red_test"]
    if not (isinstance(rt, str) and rt.startswith(GAP_TESTS_REL) and ".." not in rt.split(os.sep)):
        raise GapError(f"gap {e['id']}: red_test must lie under {GAP_TESTS_REL}")
    if not (isinstance(e["cells"], list) and e["cells"]):
        raise GapError(f"gap {e['id']}: no cells")
    for c in e["cells"]:
        if not (isinstance(c, list) and len(c) == 3 and c[0] in arms and c[1] in MODES and c[2] in MECHS):
            raise GapError(f"gap {e['id']}: {c!r} is not a cell [arm, E|S5|S25|M, Q|R]")


def load_gaps(spike, scoring_commit, arms):
    """({cell: reason}, [notes]).

    scoring_commit is None before the scoring-arm commit exists (the bound
    preflight of arm0 and score). Every version of gaps.json up to the
    scoring-arm commit is held to the rule, and a breach raises GapError. A
    version at or after the scoring-arm commit, or outside its history,
    never raises: per §9 no gap claim made then alters any cell, so it is
    listed in the notes, whatever it says, malformed or not (round 6,
    MEDIUM-1)."""
    if history_unsound(spike):
        raise GapError("; ".join(history_unsound(spike)))
    _, log, _ = _git(spike, "log", "--full-history", "--reverse", "--format=%H", "--", GAPS_REL)
    versions = log.split()
    if not versions and not os.path.lexists(os.path.join(spike, GAPS_REL)):
        return {}, []
    if not versions:
        raise GapError(f"{GAPS_REL} is not committed")
    arm0 = _one_adding_commit(spike, ARM0_REL)

    def judged(c):
        """Strictly before the scoring-arm commit, in its history."""
        return scoring_commit is None or (c != scoring_commit and _is_ancestor(spike, c, scoring_commit))
    first_seen, body, notes, listed = {}, {}, [], set()
    for c in versions:
        raw = _show(spike, c, GAPS_REL)
        if not judged(c):
            try:
                late = [e for e in json.loads(raw)["gaps"] if isinstance(e, dict)] if raw is not None else []
            except (ValueError, KeyError, TypeError):
                notes.append(f"{GAPS_REL} at {c[:12]} is malformed; it comes at or after the scoring-arm "
                             "commit, so per §9 it alters no cell")
                continue
            for e in late:
                key = (str(e.get("id")), json.dumps(e, sort_keys=True))
                if e.get("id") in body and body[e.get("id")] == e or key in listed:
                    continue
                listed.add(key)
                notes.append(f"gap {e.get('id')} (LOG {e.get('log')}) as it reads at {c[:12]}, at or after "
                             "the scoring-arm commit: per §9 it alters no cell")
            continue
        try:
            doc = json.loads(raw) if raw is not None else {"gaps": []}
            entries = doc["gaps"]
            assert isinstance(entries, list) and set(doc) == {"gaps"}
        except (ValueError, KeyError, AssertionError, TypeError):
            raise GapError(f"{GAPS_REL} at {c[:12]} is not {{\"gaps\": [...]}}")
        ids = set()
        for e in entries:
            validate_entry(e, arms)
            if e["id"] in ids:
                raise GapError(f"gap {e['id']} declared twice at {c[:12]}")
            ids.add(e["id"])
            if e["id"] in body and body[e["id"]] != e:
                raise GapError(f"gap {e['id']} changed at {c[:12]}; a declared gap is never edited")
            body.setdefault(e["id"], e)
            first_seen.setdefault(e["id"], c)
        gone = set(body) - ids
        if gone:
            raise GapError(f"gap(s) {sorted(gone)} removed at {c[:12]}; a declared gap is never withdrawn")
    out = {}
    for gid, c in first_seen.items():
        e = body[gid]
        if len(arm0) != 1 or c == arm0[0] or not _is_ancestor(spike, arm0[0], c):
            raise GapError(f"gap {gid} was declared at {c[:12]}, not after the Arm 0 commit: "
                           "§9 says a gap found before Arm 0 stops the work")
        logtxt = _show(spike, c, os.path.join("LOG.md")) or ""
        if not re.search(r"— " + re.escape(e["log"]) + r"\.", logtxt):
            raise GapError(f"gap {gid}: LOG.md at {c[:12]} has no entry {e['log']}")
        if _git(spike, "cat-file", "-e", f"{c}:{_rel_top(spike, e['red_test'])}")[0] != 0:
            raise GapError(f"gap {gid}: its red test {e['red_test']} is not committed at {c[:12]}")
        for cell in e["cells"]:
            out[tuple(cell)] = f"gap {gid} (LOG {e['log']}): {e['why']}"
    return out, notes
