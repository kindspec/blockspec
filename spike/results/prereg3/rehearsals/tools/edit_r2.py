"""Apply the round-2 review edits to the v2.1 draft (text and harness spec
only; Appendix A is not touched). Every replacement must match exactly once.

usage: python3 -I -S -B edit_r2.py <draft>
"""
import sys

f = sys.argv[1]
s = open(f, encoding="utf-8").read()
appa0 = s[s.index("## Appendix A"):s.index("## Appendix B")]


def rep(a, b):
    global s
    assert s.count(a) == 1, ("count", s.count(a), a[:80])
    s = s.replace(a, b)


# ---- M-3: governing rule in §8
rep("""**Which verdict governs blockspec#2.** This document's overall verdict decides
blockspec#2's next step, by prereg 2 §8's table, whatever prereg 2's verdict
is. That covers every form: FOUND; NOT FOUND and NOT FOUND (Q only), each with
or without "… with near misses"; and INCONCLUSIVE. Prereg 2's verdict stands as
published, and both are reported together, with any difference stated.

- If prereg 2's tiering is void, its verdict is INCONCLUSIVE (above), which
  under prereg 2 §8 keeps blockspec#2 open. This document's verdict then
  settles it.
- If prereg 2's tiering is not void, its tierer answered q3 "no" on a copy
  labelled as superseded, which is the "no" bias of §2.5. That outcome is less
  trustworthy than the void one, not more, so this document still re-tiers,
  and still governs. Owner approval items 3 and 4.""",
"""**Which verdict governs blockspec#2.** Owner approval item 3. The rule is
fixed now, before either verdict exists:

- **Prereg 2's tiering is void.** Its overall verdict is then INCONCLUSIVE
  (above), and prereg 2 §8 keeps blockspec#2 open. This document's overall
  verdict decides blockspec#2's next step, by prereg 2 §8's table, whatever
  form it takes. The forms are FOUND; NOT FOUND and NOT FOUND (Q only), each
  with or without "… with near misses"; and INCONCLUSIVE. This is the
  predicted case.
- **Prereg 2's tiering is not void.** Prereg 2's verdict decides blockspec#2's
  next step, as prereg 2 registered it. This document's verdict is still
  computed and published beside it, with any difference stated (item 4).

In both cases prereg 2's verdict stands as published and is published first.
The rule changes nothing in the predicted case, and it leaves prereg 2 §10
untouched in the other. *Alternative,* written out in item 3: this document's
verdict governs in both cases.""")

# ---- L-c: step 4 lands both commits
rep("""4. **Prereg 2's tier-model commit lands on `main`**, if it has not already.
   This is prereg 2's commit `ef62c84`, unchanged.""",
"""4. **Prereg 2's `prereg2/tiers` branch lands on `main`**, if it has not
   already: both of its commits, `da61140` (two refused tier-model attempts)
   and `ef62c84` (the tier model), unchanged.""")

# ---- L-e: corrections after step 2 go to LOG.md
rep("""§2 and §9's V-list may be
corrected only where they are wrong about a fact, with each correction logged
below with the original wording.""",
"""§2 and §9's V-list may be
corrected only where they are wrong about a fact. Until step 2 of §7, each
correction is logged below with the original wording. From step 2 on, it is
logged in `LOG.md` instead, with the original wording.""")

# ---- H-1: H2 wording and H8
rep("""  Its `void_reasons` applies §1's void rule to all five. `p2/export.py`'s
  `PLANT_EXPECT` stays at three and is not used.""",
"""  Its `void_reasons` applies §1's void rule to all five. `p2/export.py`'s
  `PLANT_EXPECT` stays at three plants. Prereg 2's code reads it in
  `p2.tiers.void_reasons` and `p2.export.load_manifest`, and
  `p2.aggregate.aggregate` computes `void` through the former (its line 102)
  before it builds any cell. With a five-plant manifest that path raises
  `KeyError` on P-D. So `harness3` never calls those three functions; H8 says
  what it calls instead.""")
rep("""- **H8. Aggregate.** `aggregate` calls `p2.aggregate.aggregate` with H6's
  inputs, this document's manifest through H2's loader, this document's
  `tiers.jsonl`, H7's reproductions, and H6's gaps, and replaces its `void`
  with H2's `void_reasons` over five plants. It then runs §5's per-name check.""",
"""- **H8. Aggregate.** Replacing `p2.aggregate.aggregate`'s returned `void`
  after the fact would not work. `cell()` has already used prereg 2's void, at
  its line 214, so a P-D or P-E failure would leave a cell FOUND. So
  `harness3/p3/aggregate3.py` reimplements only the top-level loop of
  `p2.aggregate.aggregate`, about 30 lines:
  - It computes `void` with H2's `void_reasons` over all five plants, from this
    document's manifest (H2's loader) and `tiers.jsonl`.
  - It calls `p2.aggregate.cell()` unchanged for every cell, passing that
    five-plant `void`. So every cell that exported at least one packet becomes
    NO VERDICT, with the reason, whenever any plant fails.
  - It applies H6's gaps as prereg 2 does.
  - It computes the overall verdict with `p2.aggregate.overall()` unchanged,
    from those cells.
  - Inputs are H6's, reproductions H7's.
  - It then runs §5's per-name check and the order check of H5.""")

# ---- M-1: guard is a mistake-catcher; aggregate-time order check
rep("""  Prereg 2's tier-run writes no marker in `<git common dir>/prereg2/`.
  `p2/binding.py` writes such markers only for `arm0`, `score` and `export`,
  so other work trees are scanned instead.""",
"""  Prereg 2's tier-run writes no marker in `<git common dir>/prereg2/`.
  `p2/binding.py` writes such markers only for `arm0`, `score` and `export`,
  so other work trees are scanned instead. **This guard catches mistakes; it
  is not a guarantee.** It cannot see a tier-run in a separate clone, in a
  work tree that was removed, or on a branch deleted with its work tree.
  **The committed order check** is what holds. `aggregate` runs it from
  committed records only, and refuses unless both hold:
  - the commit that adds `results/prereg3/export/` (step 3) is an ancestor of
    the commit that adds `results/prereg2/tiers.jsonl` (step 5);
  - the first `"started"` entry's `at` in the committed
    `results/prereg2/tier-runs.txt` is later than the `# executed:` time in
    step 3's committed export transcript.""")

# ---- M-2: gate
rep("""  **The gate.** It refuses unless one commit in HEAD's history adds
  `results/prereg2/verdict.json`, and that file, as committed, has
  `"bound": true` and a binding whose `validation_commit` is
  `d79bf2e61f5f7c0bcfdde5e17d44604b0fac9301`. It does not read the verdict's
  value: §0 item 4 re-tiers whatever it says.""",
"""  **The gate.** It refuses unless all of these hold in HEAD's history:
  - exactly one commit adds `results/prereg2/verdict.json`. As committed, the
    file has `"bound": true` and a binding whose `validation_commit` is
    `d79bf2e61f5f7c0bcfdde5e17d44604b0fac9301`, and it is unchanged since that
    commit;
  - a commit adds `results/prereg2/tiers.jsonl`, and it is an ancestor of the
    verdict commit;
  - `results/prereg2/tier-runs.txt` is committed with at least one
    `"started"` entry, in a commit that is an ancestor of the verdict commit.

  Prereg 2's `aggregate` accepts zero tier-runs, so a verdict alone is not
  proof that prereg 2's tiering ran. The gate does not read the verdict's
  value: §0 item 4 re-tiers whatever it says.""")

# ---- L-a: repro acceptance
rep("""  - `aggregate` accepts a reproduction result whose binding names `d79bf2e`,
    from `results/prereg2/repro/`, or this document's validation commit, from
    `results/prereg3/repro/`. A result whose binding names any other commit is
    a refusal, not an unbound result.""",
"""  - `aggregate` accepts a reproduction result only if it has `"bound": true`
    and its binding's `validation_commit` is `d79bf2e` (from
    `results/prereg2/repro/`) or this document's validation commit (from
    `results/prereg3/repro/`). Any other result is a refusal, not an unbound
    result. If two accepted results carry the same record id and disagree, that
    is a refusal too.""")

# ---- L-f: same_records reads prereg 2's export from e46e320's tree
rep("""**Same records, checked without reading them.** For each packet in prereg 2's
committed export and in the new one,""",
"""**Same records, checked without reading them.** The check reads prereg 2's
export from `e46e320`'s tree (`git show e46e320:<path>`), not from the work
tree. For each packet in that export and in the new one,""")

# ---- L-b: init check
rep("""- **No connectors.** The agent argv adds `--strict-mcp-config`. Before the
  agent reads anything, the harness checks the agent's first event, the
  `system/init` event. Its tool list must be exactly `Edit, Glob, Grep, Read,
  Write`, and its MCP server list must be empty. Otherwise the harness stops the
  agent.""",
"""- **No connectors.** The agent argv adds `--strict-mcp-config`. Before the
  agent reads anything, the harness checks the agent's first JSON event. It
  must be the `system/init` event, its tool list must be exactly `Edit, Glob,
  Grep, Read, Write`, and its MCP server list must be empty. The harness stops
  the agent if the first JSON event is anything else, if the list differs, or
  if the stream ends with no init event. The check also applies to stub
  agents.""")

# ---- V3 additions
rep("""  - **Void rule.** It fires on P-D answering q3 "no", on P-E answering q4 "no",
    on P-A answering q3 "yes", on P-C landing in tier B, and on each plant left
    untiered. It does not fire on A↔B confusion.""",
"""  - **Void rule.** It fires on P-D answering q3 "no", on P-E answering q4 "no",
    on P-A answering q3 "yes", on P-C landing in tier B, and on each plant left
    untiered. It does not fire on A↔B confusion.
  - **Void reaches the cells (H8).** Take a fixture that is FOUND with every
    plant right. Change only P-D's q3 to "no". Every cell that exported a
    packet then becomes NO VERDICT, with the void as its reason, and the
    overall verdict becomes INCONCLUSIVE.""")
rep("""    is in the work tree; when it is only in another work tree; when it was
    committed and then deleted, so that only history holds it; and when only a
    reflog holds it. The same applies to a `tier-work-1/` directory. It runs
    when none exists.""",
"""    is in the work tree; when it is only in another work tree; when it was
    committed and then deleted, so that only history holds it; and when only a
    reflog holds it. The same applies to a `tier-work-1/` directory. It runs
    when none exists.
  - **Committed order check.** `aggregate` refuses on a fixture history in
    which the commit adding `results/prereg2/tiers.jsonl` does not descend from
    the export-3 commit. It also refuses when the first started `at` in
    `tier-runs.txt` is earlier than export 3's `# executed:` time. It passes on
    a fixture history in the order of §7.""")
rep("""  - **Gate.** `tier-run` refuses with no `results/prereg2/verdict.json`, with
    one marked `"bound": false`, and with one bound to another commit.""",
"""  - **Gate.** `tier-run` refuses on each of these fixtures:
    - no `results/prereg2/verdict.json`;
    - one marked `"bound": false`;
    - one bound to another commit;
    - one changed after it was added;
    - a verdict with no committed `tiers.jsonl`;
    - a verdict with no committed `tier-runs.txt`, or with one that has zero
      started runs.""")
rep("""  - **Reproductions.** A repro bound to `d79bf2e` is accepted, and so is one
    bound to this document's validation commit. One bound to any other commit
    is refused.""",
"""  - **Reproductions.** A repro bound to `d79bf2e` is accepted, and so is one
    bound to this document's validation commit. One bound to any other commit
    is refused, as is one with `"bound": false`, and so is a pair of accepted
    results with the same id that disagree.""")
rep("""  - **Init check.** A stub that reports an extra tool, or a non-empty MCP
    server list, in its `system/init` event is stopped, and the run records
    zero lines.""",
"""  - **Init check.** Each of these stubs is stopped, and the run records zero
    lines:
    - one that reports an extra tool in its `system/init` event;
    - one that reports a non-empty MCP server list there;
    - one whose first JSON event is not `system/init`;
    - one that ends its stream with no init event.

    A stub with the exact init event runs.""")
rep("""  the order guard; the plant-content check; the `tier-model.json` blob pin;
  the gate; the init check; and the five-plant void rule.""",
"""  the order guard; the committed order check; the plant-content check; the
  `tier-model.json` blob pin; the gate and each of its three conditions; the
  init check; the five-plant void rule; and **the propagation of that void
  into `cell()`**. The last means a mutant that passes prereg 2's three-plant
  void, or none, to `cell()`, which the V3 case above must kill.""")

# ---- M-5: V6 prompt-sha assertion
rep("""  expected. Any failed run is reported, not rerun away. All transcripts are
  committed.""",
"""  expected. Any failed run is reported, not rerun away. All transcripts are
  committed. For every run in the passing series, V6 asserts that
  `sha256(prompt_text3())` equals the `prompt_sha256` that the run's
  `run-info.txt` records.""")

# ---- L-g and L-d: how prereg 2's plants were found; redact ids
rep("""  `<P2-PLANT-A-NAME>` (P-A), `<P2-PLANT-B-NAME>` (P-B) and `<P2-PLANT-C-NAME>`
  (P-C) in prereg 2's export. The coordinator of this work located them by
  content match against Appendix B, not through the nonce.""",
"""  three packets of prereg 2's export. Their names are withheld here until
  prereg 2's manifest commit (§7, step 5), because blockspec is public and the
  names would mark the plants in the export before then. They were located
  without the nonce. A program content-matched all 486 packets of prereg 2's
  export against Appendix B's plants and printed only the three matches; no
  other packet's content was printed or read by a person.""")

assert s[s.index("## Appendix A"):s.index("## Appendix B")] == appa0, "Appendix A changed"
open(f, "w", encoding="utf-8").write(s)
print("ok")
