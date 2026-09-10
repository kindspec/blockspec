<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# The oracle — named and fixed before the merge arm runs

`PRE-REGISTRATION.md` §3.1: *"Without an oracle there is no finding."* It requires
a **resolution oracle** that is *"a different algorithm at a different granularity
from the one being measured"*, established independently of the mechanism under
test, and it names D8's line-correspondence oracle as the model. It rules out the
author's intent, a diff that looks wrong, a human judgement call, and the
mechanism grading itself.

This file names the oracle. It is committed before any measurement of the merge
arm runs. Nothing below may be adjusted in light of a result; if it turns out to
be the wrong oracle, that is reported, not fixed.

---

## 1. What is being measured (the mechanism under test)

Unchanged from D8, deliberately — reused by import, not reimplemented, so the
control arm and the merge arm measure the same thing:

- `anchor_eval.anchor_of` builds a W3C-shaped standoff record over a block at the
  **merge base**: `{quote, prefix (48 chars), suffix (48 chars), pos, len}`.
  Nothing is written into the document. The record lives outside the merged tree,
  which is D8 §11's I7 corollary: *the referrer never writes to the target*.
- `anchor_eval3.reanchor2` resolves that record against the **merged** document:
  exact block match → exact-plus-context → fuzzy (`difflib` ratio ≥ 0.5), under
  two acceptance policies, `naive` and `hard` (margin ≥ 0.15, context ≥ 0.30,
  entropy ≥ 24 distinct chars or ≥ 8 distinct words).

The mechanism therefore works on **block content strings**, scored by
**similarity ratio**, with context as a tie-break. Remember both properties; the
oracle must share neither.

## 2. The oracle: TLLC — two-leg line correspondence

**Granularity: lines. Algorithm: longest-matching-block alignment, composed
across the two merge legs. No similarity ratio over block content, no quote, no
context window.**

Inputs are the four texts of a three-way merge — base `B`, leg `A`, leg `C`,
merged output `M` — and the block decomposition of `B` and `M`.

For each leg `L ∈ {A, C}`:

1. `difflib.SequenceMatcher(None, lines(B), lines(L))` → `get_matching_blocks()`
   → a partial map `B-line → L-line`.
2. `difflib.SequenceMatcher(None, lines(L), lines(M))` → a partial map
   `L-line → M-line`.
3. Compose them into `φ_L : B-line → M-line`, defined only where both steps are.

For base block `k` occupying non-blank base lines `S_k`:

- `frac_L = |{l ∈ S_k : φ_L(l) defined}| / |S_k|`.
- If `frac_L ≥ 0.5`, leg `L` proposes the merged block containing the plurality
  of `{φ_L(l)}` as `k`'s descendant.

The two legs are then combined:

| legs confident | proposals | verdict |
|---|---|---|
| both | agree | `SURVIVED`, that block |
| both | disagree | `UNKNOWN` — **excluded and reported** |
| exactly one | — | `SURVIVED`, that block |
| neither, and `frac_A = frac_C = 0` | — | `DELETED` if no merged block is similar (§4), else `UNKNOWN` |
| neither, otherwise | — | `UNKNOWN` — **excluded and reported** |

**Two legs, not one, is the whole reason this oracle is new.** D8's oracle
composed nothing: one edit, one alignment. A merged file is reachable from the
base by two different paths, and a block whose two paths land in different places
is exactly the case a single-leg oracle cannot see. TLLC does not resolve such a
case — it *refuses* it, which is the only honest thing an oracle can do with a
question that has two answers.

## 3. The verdict rule

Identical to `anchor_eval3.py`, so the two arms are directly comparable:

- oracle `UNKNOWN` → excluded from the denominator, counted, reported.
- oracle `SURVIVED` with target `t`:
  - mechanism refuses (`hit is None`) → **LOUD** (safe).
  - mechanism returns `t` → **correct**.
  - mechanism returns anything else → **SILENT-WRONG**.
- oracle `DELETED`:
  - mechanism refuses → **correct**.
  - mechanism resolves to anything → **SILENT-WRONG** (broken out separately as
    `WRONG_on_deleted`; see §4).

A silent-wrong is only recorded when `git merge` exited 0 **and** no conflict
marker appears anywhere in the merged tree. A conflicted merge is tier E by
§4 of the pre-registration — the format working — and is counted, not scored.

## 4. Where this oracle is NOT independent, stated now

The `DELETED` / `UNKNOWN` discriminator asks whether any merged block resembles
the base block, and it asks with `difflib.SequenceMatcher` over block content —
which is the mechanism's own algorithm at the mechanism's own granularity. D8's
`line_oracle` has the identical seam (`anchor_eval2.py` line 42).

It is kept, for comparability, and fenced:

- It can only push a case from `DELETED` to `UNKNOWN`, i.e. **out** of the
  denominator. It cannot manufacture a `SURVIVED` target.
- Every `SURVIVED` verdict — which is where the great majority of silent-wrongs
  are adjudicated — is computed purely from line correspondence and never
  consults it.
- `WRONG_on_deleted` is reported as its own count so any result resting on the
  contaminated path is visible rather than folded into a total.

**A finding that depends on `WRONG_on_deleted` is weaker than one that does not,
and must be reported as such.** Written here so it cannot be discovered
convenient later.

## 5. The other thing this oracle cannot do

TLLC establishes *which merged block is the descendant of a base block*. It says
nothing about whether the merged prose is **true**. Pre-registration §3(3)
requires the merged document to assert something **false**, not merely to
mis-resolve.

For a bare anchor those are the same question only if the anchor carries an
assertion — which is exactly the pre-registration's tier B/tier C line, and it is
a **tiering** judgement, not an oracle judgement. §4.1 assigns tiers separately,
from the written definitions, by someone who has not seen the frequency.

So: **TLLC produces mis-resolutions, not findings.** It is a necessary condition
for a tier A/B result and not a sufficient one. Every case it emits is recorded
with its reproduction and `tier: UNASSIGNED`.

## 6. The hypothesis this arm exists to test

Recorded before running so it cannot be retrofitted.

**Resurrection by concurrent insert.** Leg A rewords the anchored block. Leg C
independently inserts, or leaves standing elsewhere, a block whose bytes match
the base wording. `git merge` takes both hunks and exits 0. The standoff record's
*exact quote now matches leg C's block exactly*, so resolution succeeds at the
mechanism's **highest-confidence** status — `EXACT`, no fuzzy scoring, no margin
test, no entropy test — and the `hard` policy never engages. Meanwhile the true
descendant is leg A's reworded block.

This shape cannot occur in D8's arm. `git merge-file` applying one author's real
edit has one leg; a block cannot simultaneously be edited and left standing.
That is the gap `PRE-REGISTRATION.md` §2.1 names, stated as a mechanism rather
than as a worry.

If the corpus arm finds this shape, `plant_cases/wrong-01/` is its minimal
reproduction. If it does not, the planted case still demonstrates the harness has
two verdicts, and the absence is the result.
