# SPDX-License-Identifier: MIT
"""PRE-REGISTRATION-2.md §6.5 Arm 0: a census of oracle reach, at the pin,
over the whole selection, with no sampling.

Broken down by type, it counts:

- blocks under 20 characters, which the mechanism skips (skip:short_quote);
- distinct contents of 20 characters or more;
- those with a twin in the same file;
- of those, how many are single-line twins and how many are adjacent-run
  twins.

THE BAR. If more than 10% of an arm's distinct natural-language contents of
20 characters or more have a twin in the same file, the arm reports NO
VERDICT (oracle reach) and does not run.

"Adjacent-run twin" is not defined by §6.5. The owner accepted one labelled
reading on 2026-10-08, recorded in LOG.md §15 before Arm 0, for this
report-only line: ADJACENT_RUN_RULE below. No verdict reads it -- the bar uses
only "has a twin in the same file" -- and V3 checks that no aggregate or
verdict path refers to it.
"""
import os
from collections import defaultdict

from . import mech as Mx

MINLEN = 20
BAR = 0.10
ADJACENT_RUN_LABEL = "provisional reading (LOG §15)"
ADJACENT_RUN_RULE = (
    "a distinct content (type, content) of 20 characters or more counts as an "
    "adjacent-run twin if, in at least one selected file, two of its instances "
    "are consecutive blocks of that file -- positions i and i+1 in D8's "
    "blocks() sequence, where blocks of every length count toward the position")


def census_texts(texts):
    """texts: {path: text}. Returns {type: counts} and the bar's inputs.
    A distinct content is keyed (type, content)."""
    short = defaultdict(int)
    d_all, d_twin = defaultdict(set), defaultdict(set)
    d_single, d_adj = defaultdict(set), defaultdict(set)
    for path in sorted(texts):
        t = texts[path]
        bl = Mx.D8.blocks(t)
        typed = [(Mx.typer(t, b), b["content"]) for b in bl]
        seen = defaultdict(list)
        for i, (ty, c) in enumerate(typed):
            if len(c) < MINLEN:
                short[ty] += 1
                continue
            d_all[ty].add(c)
            seen[(ty, c)].append(i)
        for (ty, c), idx in seen.items():
            if len(idx) > 1:
                d_twin[ty].add(c)
                if "\n" not in c:
                    d_single[ty].add(c)
                if any(b - a == 1 for a, b in zip(idx, idx[1:])):
                    d_adj[ty].add(c)
    types = sorted(set(short) | set(d_all))
    by_type = {ty: {"short_lt20": short[ty], "distinct_ge20": len(d_all[ty]),
                    "twin_same_file": len(d_twin[ty]), "single_line_twin": len(d_single[ty]),
                    "adjacent_run_twin": len(d_adj[ty])} for ty in types}
    nl_all = sum(len(d_all[ty]) for ty in Mx.NL_TYPES)
    nl_twin = sum(len(d_twin[ty]) for ty in Mx.NL_TYPES)
    return {"by_type": by_type, "nl_distinct_ge20": nl_all, "nl_twin_same_file": nl_twin,
            "passes_bar": bar_passes(nl_twin, nl_all)}


def bar_passes(nl_twin, nl_all):
    """The bar: more than 10% twinned stops the arm. An arm with no
    natural-language content at all has nothing to pass on, and does not."""
    if nl_all == 0:
        return False
    return nl_twin <= BAR * nl_all


def census_repo(repo, paths):
    """A file that is not UTF-8 is not read, and is counted, as
    e4_uniqueness.py does; d8_cheap_arm prints the same count."""
    texts, unreadable = {}, []
    for p in paths:
        try:
            with open(os.path.join(repo, p), encoding="utf-8") as f:
                texts[p] = f.read()
        except (UnicodeDecodeError, OSError):
            unreadable.append(p)
    out = census_texts(texts)
    out["files_read"], out["unreadable"] = len(texts), unreadable
    if not texts:
        out["passes_bar"] = False
    return out
