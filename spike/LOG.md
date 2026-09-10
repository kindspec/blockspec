<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Spike log — blockspec#2

Append-only from here on. **§§1–8 were written up at the end of the run, not
incrementally** — the file lands whole in one commit and the git history says so.
`PRE-REGISTRATION.md` §4.1's requirement is about *tier assignment*, and it is
satisfied because no tier was assigned at all; but the "recorded at the moment of
assignment" standard is not one this file's own history can claim, and saying
otherwise would be the kind of unearned claim this project keeps catching. §9
onward is appended as the work happens.

**No verdict is recorded here.** §6's FOUND / NOT FOUND / NEAR MISS is not
decided. **No tier is assigned to anything**, and nothing in this file may be
read as one.

---

## 2026-09-09 — scope of this entry

Built and validated the harness. Ran the control arm. Ran the merge arm on the
control corpora for coverage. That is all.

Explicitly **not** done, and each for a reason in the pre-registration:

| not done | why |
|---|---|
| assign tiers | §4.1: the tier is assigned *before the frequency is known, by someone who has not seen the frequency*. Whoever ran this has seen frequencies and is disqualified from tiering their own results. |
| choose §5's duplicate-heavy corpora | §5 requires an amendment recorded in §8 with a date and a reason, before measurement, with an argument per choice. Not written, so that arm has not been run. |
| declare a verdict | §6. Not this task. |

---

## 1. Corpus pins

`harness/corpora.json`. `D8-identity.md`'s header states a commit count per
corpus. For each, the commit on the first-parent chain at which
`git rev-list --count HEAD` equals that number:

| corpus | pin | count | D8 states |
|---|---|---|---|
| rust-book | `917544888a55e4da7109bdba8c88c893c0da70f4` | 6286 | 6,286 |
| obsidian-help | `a3985b585904ddb9f109bd80849b378085308c15` | 2623 | 2,623 |
| cmspec | `3da939428d80f146f270cd1765e4ba462e96bb1b` | 1848 | 1,848 |

All three matched exactly, which is why the control arm reproduces D8 line for
line. Anyone re-running D8 should pin rather than clone at HEAD: the corpora have
moved, and §2.2 shows the movement changes a result.

~~The experiment files' mtimes are 2025-08-28 and therefore misleading.~~
**Retracted 2026-09-10.** They are `2026-08-21` and `2026-08-28`; nothing in that
tree carries a 2025 mtime. The error came from reading an `ls -la` listing, which
omits the year for recent files, and inferring one. The mtimes agree with the
pins and were never misleading. The pins stand on their own.

## 2. Control arm — PASS

`results/control-arm.txt`, `harness/run_control.sh`, gated by
`harness/check_control_gate.py`.

D8's own scripts, unmodified, imported from `kindspec/research` at
`f088cd76fd138c8244fa1315332468e8771e7040`. At the pins above the control arm
reproduces D8 **line for line**: sample sizes 1087 / 1141 / 533, oracle-confident
subsets 999 / 849 / 200 (92% / 74% / 38%), every percentage in §3.1 and §3.2, and
all three mis-anchor examples §3.2 quotes.

```
CONTROL GATE: PASS -- zero prose-typed silent-wrongs under the hardened
policy in every measuring arm     (5 measuring arms)
```

### 2.1 Two corrections to `PRE-REGISTRATION.md` §1, both evidenced

§8 forbids amending §3, §4 or §6. §1 is a statement of prior evidence, not a
criterion, and these are corrections to the record rather than amendments to the
bar. **Neither changes what would count as FOUND.**

**(a) The 885 denominator is backed, and the arithmetic in §1 is wrong.** §1
says the figure "appears exactly once in the research repository, in prose, with
no committed harness output behind it — and the per-arm prose counts printed
above total 796, not 885." The 796 counts only the three arms §1 chose to quote.
D8 §3.2 prints five measuring arms; the two `cmspec` arms carry `prose=53` and
`prose=36`, which this spike's control run reproduces:

```
460 + 124 + 212 + 53 + 36 = 885
```

So D8's "885 prose-block anchors in three corpora" is exactly the sum of its own
printed per-arm prose counts.

**Two limits on that reconciliation, both of which matter.**

*It holds at D8's pin only.* On a current clone `obsidian-help` prints
`prose=240` rather than 212, and the sum is **913**. Measured, not inferred: 240
from this spike's own drift run, 53 and 36 from a cmspec pin identical to HEAD,
and 460 and 124 re-measured at `rust-book` HEAD (`1500248d`), which is byte-stable
across that commit.

*It answers only one of the two objections to the figure.* It shows the number is
not unsourced. It does **not** answer the other one: 885 sums five *arms* across
three corpora, and the same block sampled at gap=5 and gap=25 is counted twice, so
it is a count of **evaluations, not of distinct authored blocks** — which is
exactly the trap `PRE-REGISTRATION.md` §7 and the org contract §4 both name. That
objection is untouched and still stands. The earlier wording here, "§1's premise
for distrusting it does not hold", was too broad; only the *unsourced* premise
falls.

**(b) `cmspec` was measured, not skipped.** §5 suspected its arm might be a
`too few` skip. It is not: 73 and 56 oracle-confident anchors, both above
`anchor_eval3.py`'s threshold of 50, 0.00% silent-wrong in all four cells. The
arm that *is* skipped at these pins is **`obsidian-help` gap=25**, at
`too few (22)`. (kindspec/research#2 reached the same conclusion independently,
finding `too few (0)` for that arm on a clone at HEAD.)

### 2.2 The naive half of §1's claim does not survive corpus drift

`results/corpus-drift.txt`. Seven commits of `obsidian-help` move gap=5 from 384
to 343 anchors and produce one **naive** mis-anchor typed `prose`: YAML
frontmatter (`'---\naliases:\n  - Sync history\n---'` → `'## Sync history'`),
which `anchor_eval3.btype()` has no rule for and which therefore falls through to
`prose`. Substantively that is structured data — D8 §3.2's own category — but the
label printed is `prose`.

At D8's pin §1's claim holds under **both** strategies. Under drift only the
**hardened** half holds. `check_control_gate.py` therefore asserts the hardened
half and *reports* the naive half, because a gate that goes red for a reason
unrelated to what it gates is not a gate.

**The gate is easy to state one word short, and the short form is false.**
"The hardened policy at 0.00% silent-wrong across all five arms" contradicts
D8 §3.2's own table, which prints hardened silent-wrong at 0.12% (n=1, code) and
1.00% (n=2, code) for rust-book and 0.26% (n=1, list) for obsidian-help — so that
form goes red on the strongest control, and looks like a broken harness. The zero
applies to the **prose-typed count**, not to the total. The word that carries the
whole finding is `prose-typed`, and `check_control_gate.py` asserts it in that
form for exactly this reason.

**Why the hardened policy is clean here, verified rather than assumed.** It does
not merely happen to anchor the frontmatter block correctly — it *refuses* it.
`entropy_ok('---\naliases:\n  - Sync history\n---')` is False: 17 distinct
characters against H3's threshold of 24, and 3 distinct words against 8. The
status is `REFUSED_LOWENTROPY`, classed `LOUD`. That is the mechanism working as
designed, and it is worth carrying into any reading of this spike's own
loud-refusal counts: hardened anchoring converts low-entropy blocks into loud
refusals, which is exactly what D8 §3.2 claims for it.

**A related measurement is under re-verification and this spike does not use
it.** kindspec/research#5 reports that D8 §3.3's prose-uniqueness table (the
source of blockspec's "100% / 99.4% unique at ≥40 chars") cannot be reproduced
from `e4_uniqueness.py`, which takes no arguments and hardcodes a `>= 20`
threshold. Checked: nothing in this spike cites or depends on that figure. This
arm measures merge behaviour, not uniqueness.

## 3. The harness has two verdicts — demonstrated

`results/two-verdict-demo.txt`. Both planted cases run through the **same**
`evaluate_case()` as the corpus arm.

- `plant_cases/wrong-01` — stock `git merge` exits 0, no markers, and the
  standoff record resolves at status `EXACT`, block type `prose`, to leg C's
  block while the oracle's descendant is leg A's. Caught.
- `plant_cases/clean-01` — a **minimal pair** with `wrong-01`: identical base,
  identical leg C. The only difference is which paragraph leg A edits. Clean
  merge, correct resolution under both policies. Silent.

### 3.1 What building them established

> **A near-duplicate alone is not a silent-wrong merge.** With the anchored block
> intact, the mechanism sees two exact matches and disambiguates on prefix/suffix
> context — correctly. The precondition is that the base bytes survive
> **somewhere** in the resolved text *while the anchored block's true descendant
> has moved*.

Found by mutating the first draft of `clean-01` to add a duplicate and watching
the gate **stay green**. The harness was right and the mutation was wrong; see
`results/armed-check.txt` mutation 5 for the corrected form.

> ~~The defect needs **both legs to act** … that is precisely why a single-leg
> rebase cannot reach it.~~ **Retracted 2026-09-10 — see §9.** One author in one
> commit reproduces it. The both-legs framing was wrong, and it was the wrong
> necessary condition, not merely an overstatement.

`clean-01` and `wrong-01` **are** now a minimal pair: byte-identical base,
byte-identical leg C, and leg A makes one edit in each, differing only in which
paragraph it lands on. They were not when first written — `clean-01`'s leg C also
rewrote the escalation paragraph, so two variables differed while the text here
claimed one. Corrected 2026-09-10 by making leg C identical and re-running; both
verdicts are unchanged.

## 4. The gates are armed — each broken and watched to go red

`results/armed-check.txt`. Five mutations, each hash-verified before and after so
a mutation that fails to apply is reported `BROKEN` rather than as a survived
mutant. Baseline green, all five red:

| mutation | breaks |
|---|---|
| `verdict-always-correct` | the verdict rule cannot report WRONG — the org contract's named failure |
| `oracle-never-confident` | an oracle that abstains from everything must not yield a pass |
| `oracle-self-grading` | §3.1's "the mechanism under test grading itself" |
| `wrong-01-drop-leg-C-duplicate` | the WRONG verdict must track the input, not the fixture's name |
| `clean-01-move-leg-A-edit-onto-the-anchor` | the correct verdict must too |

`check_control_gate.py --selftest` does the same for the control gate, including
a stale-parser guard: every `###` header in the transcript must become a parsed
arm, because a regex that silently stops matching is this project's
most-repeated defect. It fired for real during development — the `too few` arm
line did not match and was being silently dropped.

## 5. Harness defects found by running it, and fixed

The first two were found by output that looked wrong, not by review. The last
three were found by trying to prove a check was armed — and 3, 4 and 5 are the
same defect at three depths, which is the point of listing them separately.

1. **`=======` is not a conflict marker.** A line of equals signs is a setext
   heading underline, legal markdown, present in cmspec. Detecting on it
   classified cmspec's only concurrent merge as marker-bearing and dropped it
   from the sample — an error in the conservative direction, which is still an
   error, and it silently removed a whole corpus's coverage. Now only the
   angle-bracket markers are used, plus `git ls-files -u` as the authoritative
   signal.
2. **The reconstruction was never validated against reality.** Added: for every
   clean reconstruction, compare the merged bytes to what git actually recorded
   at the merge commit. **157/157 byte-identical** across all three corpora. The
   harness reproduces the merges git really performed.
3. **The balance guard added in §7's own fix was a check that cannot fail.**
   This is the clearest instance of the org contract §2.2 defect this spike has
   produced, and it is recorded here rather than only in a commit message
   because a squash merge destroys commit messages.

   The guard was meant to catch a drop path with no counter behind it. As first
   written it computed

   ```python
   dropped = cand - acc                     # <- derived, not counted
   ...
   if cand != acc + dropped:                # <- therefore always False
       print("*** selection counters do not balance ***")
   ```

   `cand != acc + (cand - acc)` is a tautology, so the guard could never fire.
   It was written **in the commit whose entire purpose was to fix an uncounted
   drop path**, and it reported a clean balance while doing it.

   Caught by mutation, not by reading: removing the `drop:convergent` increment
   should have unbalanced the total, and instead the run went quietly green and
   printed `DROPPED 9 (27%)` where the truth was 18 (55%). `dropped` now sums the
   four named drop counters, and the same mutation turns it red.

   **This class has a name here already:** kindspec/rowspec#44 — a same-size
   edit to a module served from a stale `__pycache__` entry, so the mutation
   appears to apply and the check appears to survive it. Same signature,
   different mechanism: *the mutation looks applied and the check looks green.*
   §5.3 is the home for that class in this repository, and the mitigation
   (`PYTHONDONTWRITEBYTECODE=1` in `armed_check.sh` and
   `selection_guard_red.sh`) is recorded in §5.5.

   **Watchable from committed code:** `prose_merge.py --selftest-selection`
   drives eight cases through `report()` — balanced stays silent, each named
   counter zeroed fires, `drop:unchanged_side` is forced reachable so it is shown
   to count toward the balance *and* to raise its investigate line, and
   merge-level drops are shown to stay out. Restoring the original `cand - acc`
   turns four of the eight red. `results/selection-guard-selftest.txt` is that
   output, regenerated by `harness/selection_guard_red.sh` so its hashes are
   always of the file as committed. Every other check here had such an artifact;
   this one did not until now, which is the same gap one level down.
4. **The guard protected the partition but not its denominator.**
   `st["paths:both_sides"] += 1` sat *inside* the candidate loop, so the
   population count was itself in the region a `continue` can jump out of. An
   uncounted `continue` above the increment shrinks `cand` and `acc` together,
   the balance `cand == acc + dropped` still holds, and nothing fires.
   Reproduced, hash-verified: obsidian-help's 33 candidates silently became 19.

   ```python
   st["paths:both_sides"] += len(ca & cb)   # once, from the set size
   for path in sorted(ca & cb):             # never accumulated inside
   ```

   **The invariant is that `cand` is set from the set size, never accumulated**,
   and it is stated in a comment at the line itself because
   `--selftest-selection` structurally cannot pin it: the selftest *supplies*
   `paths:both_sides` rather than deriving it, so no synthetic-`Counter` case can
   catch this. Verified both directions on the real corpus — with the uncounted
   `continue` the balance now fires (33 against 6+13); without it, silence, which
   given `cand == acc + dropped` is itself the confirmation that `cand` is 33
   again.

   **This is the third distinct layer of one defect, and the sequence is the
   lesson.** The drops were uncounted (§7). The guard written for that was a
   tautology (§5.3). The guard, once real, covered the partition but not its
   denominator (here). Each fix was correct, each was verified, and each left the
   next layer standing. A check is not one thing to arm but a stack, and arming
   the top of it says nothing about what is underneath.

   Fixing this also broke `--limit`, which returns mid-enumeration: `cand` then
   counts paths in merges never examined, so the balance would fire spuriously.
   `report()` now says the census is partial instead. No committed result uses
   `--limit`.
5. **A recorded hash that named nothing.** `results/selection-guard-selftest.txt`
   carried a mutation hash pair for a working-tree state no committed file
   matched — `prose_merge.py` was edited again before being committed. The
   verdict was reproducible, so the substance held, but **a hash a reader cannot
   check against the artifact it names is worse than no hash, because it looks
   checkable.** The transcript is now generated by
   `harness/selection_guard_red.sh`, which hashes the file it actually runs, so
   it cannot go stale by hand. That script and `armed_check.sh` both set
   `PYTHONDONTWRITEBYTECODE=1` — see §5.3 on kindspec/rowspec#44.

## 6. Merge arm — coverage, not a verdict

`results/merge-arm.txt`, candidates in `results/merge-arm-candidates.jsonl`.

Cases are real 2-parent merge commits with a single merge-base where the same
`.md` changed on **both** sides.

| corpus | both-sides candidates | accepted | dropped | criss-cross skipped | clean | conflicted (tier E) | oracle-confident | distinct base blocks |
|---|---|---|---|---|---|---|---|---|
| rust-book | 190 | 179 | 11 (6%) | 3 | 147 | 32 | 11706 / 12230 (96%) | 6651 |
| obsidian-help | 33 | **15** | **18 (55%)** | 2 | 9 | 6 | 182 / 189 (96%) | 304 |
| cmspec | 1 | 1 | 0 | 0 | 1 | 0 | 57 / 62 (92%) | 73 |

**Read the obsidian-help row before quoting its zero below.** More than half its
both-sides candidates were dropped — 7 add/add, 2 delete/modify, 9 convergent —
so its `n=0` rests on 15 cases out of 33 available, not on 33. §7 has the full
selection.

Mis-resolutions, **all `tier: UNASSIGNED`**:

```
rust-book   naive  n=64  code=41 heading=4 html=8 list=1 prose=10
            hard   n=21  code=13 heading=1               prose=7
obsidian-help / cmspec: n=0 in both policies
            (obsidian-help: 15 of 33 candidates; cmspec: 1 of 1)
```

### 6.1 Every prose-typed candidate traces to one file, and §3(5) disqualifies it

All 17 prose-typed candidates (10 naive, 7 hard) come from a single case,
`bffe7c1ec7:src/ch02-00-guessing-game-tutorial.md`, which contributes 44 of the
85 candidates. That file has an **odd number of fence lines**, so D8's
boundary-only block parser desynchronises partway through and glues code fences
to the prose that follows — the merged file has 135 blocks where the base has
185, and a `Filename: src/main.rs` line appears to "resolve" into a 2 kB
pseudo-block.

The question that matters is whether the **merge** created that. It did not:

```
clean merges=147   merge-created-odd-fences=0   parent-already-odd=1
```

A parent was already malformed. `PRE-REGISTRATION.md` §3(5) — *"Both parent
states were correct. The defect is created by the merge, not carried in by an
author."* — therefore disqualifies the case outright, and §3(2)'s well-formedness
condition fails on it too.

Excluding it, by §3(5) and by nothing else:

```
rust-book   naive  n=32  code=23 html=8 list=1
            hard   n=9   code=9
```

**Zero prose-typed, in both policies, in all three corpora** — the same shape as
D8's rebase arm. The harness now reports this split itself
(`wf:parents_ok` / `wf:parent_malformed`) rather than requiring the
investigation to be repeated.

Also recorded, because it would have been a real result had it been non-zero:
**clean merges that broke well-formedness: 0**. The denominator is **156**, not
157: the counter fires only where all parents were well-formed, and one of the
157 clean merges had a malformed parent and so was never eligible to be counted.

### 6.2 A named limitation of TLLC, found by running it

`ORACLE.md` §4 and §5 named two limitations in advance. This is a third, found by
use and **not** fixed, because `ORACLE.md` says nothing in it may be adjusted in
light of a result:

> For a **single-line block whose text repeats many times in one file**, TLLC
> accepts a leg's proposal on the strength of one mapped line, with no margin
> test and no corroboration. `difflib`'s alignment can legitimately pair base
> occurrence *i* with leg occurrence *j*. The oracle has no way to notice.

**Reproduced, not asserted:** `harness/oracle_limitation.py` builds a three-line
case in which leg A inserts a byte-identical copy of a single-line block directly
after it. Which of the two adjacent identical merged blocks is "the descendant"
is undecidable from the bytes, and TLLC answers `SURVIVED`, target *n+1*, with no
margin, no corroboration and no signal that it guessed. The naturally occurring
instance is the `Filename: src/main.rs` blocks in
`bffe7c1ec7:src/ch02-00-guessing-game-tutorial.md`.

This is separate from the parser desynchronisation above and would survive
fixing it. The candidates in §6.1 are excluded by §3(5) on their own, so nothing
currently reported depends on this — but **any future arm containing short,
highly repeated blocks needs a stronger oracle before its prose numbers can be
believed**, and the duplicate-heavy corpora §5 calls for are exactly that shape.
Fixing it means a second oracle statement, not an edit to this one.

## 7. Coverage actually obtained, stated as §7 requires

**Corrected 2026-09-10.** This section previously gave the excluded population as
*"everything not a `.md` file changed on both sides of a two-parent merge"*. That
sentence was false: **29 candidates that WERE `.md` files changed on both sides
were dropped**, by three `continue` statements with no counter, no report line
and no mention. A coverage claim nobody can check is not a coverage claim, and
this is the one sentence `PRE-REGISTRATION.md` §7 specifically demands. Every
drop path is now counted in `find_merge_cases` and printed by `report()`, so the
figures below come from committed code rather than from prose.

### Selection, in full

| | rust-book | obsidian-help | cmspec | total |
|---|---|---|---|---|
| two-parent merges | 1317 | 352 | 152 | **1821** |
| octopus merges, never examined | 2 | 0 | 0 | 2 |
| skipped, >1 merge-base | 3 | 2 | 0 | 5 |
| **`.md` changed on BOTH sides** | 190 | 33 | 1 | **224** |
| → accepted | 179 | 15 | 1 | **195** |
| → dropped: add/add | 0 | 7 | 0 | 7 |
| → dropped: delete/modify | 8 | 2 | 0 | 10 |
| → dropped: convergent identical edits | 3 | 9 | 0 | 12 |
| `.md` changed on exactly ONE side | 16496 | 2773 | 68 | **19337** |

**29 of 224 both-sides candidates — 13% — are dropped**, and for `obsidian-help`
it is 18 of 33, **55%**. Any obsidian-help figure in this arm rests on 15 cases
out of 33 available.

### Which drops are forced and which are a choice

- **add/add (7) — forced.** The path does not exist at the merge base, so there
  is no base block to build a standoff record over and nothing for the oracle to
  carry forward. Worth seeing rather than hiding, because it is structurally
  *rowspec's own defect shape* — two branches inserting — and it swallows 21% of
  obsidian-help's both-sides candidates.
- **delete/modify (10) — forced.** One leg removed the file, the other edited it.
  Also invisible in the tier-E count: these are dropped *before* `stock_merge`, so
  they are not among the 38 conflicts.
- **convergent identical edits (12) — a CHOICE, not a necessity.** A base exists,
  both legs acted, and git merges them cleanly. They are evaluable, and they would
  have contributed *correct* resolutions, so excluding them **mildly inflates the
  mis-resolution rate** — 12 against 157. Kept excluded so the reported numbers do
  not move under a late change, but named here so the choice is arguable rather
  than invisible. Including them is a reasonable thing for the next arm to do.

### The ratio §9 makes the point of

**195 both-sides cases against 19,337 `.md` paths changed on exactly one side.**
Concurrent edits to the same prose file are roughly **1%** of the editing these
projects do. Combined with §9 — the defect shape needs no merge at all — this is
the number showing why the merge topology was never where the answer lived, and
why §2.2's question about the *corpora* is the one that survives.

### The rest of the excluded population

- 38 of 195 reconstructions conflicted and are tier E — counted, not scored.
- Everything not a `.md` file; every non-merge commit; the whole of §5's
  duplicate-heavy arm, which has not been chosen.
- The oracle's confident subset is 96% / 96% / 92%, much higher than the control
  arm's 92% / 74% / 38%, because two legs corroborate. That is a property of the
  oracle, not evidence about merging.

## 8. Open, and it is the deciding question for the next step

The planted cases prove the shape is **reachable** — clean stock-git merge,
well-formed output, prose block, `EXACT` status, the hardened policy never
engaging. **§9 then established it is reachable without any merge at all**, which
moves where the next arm should go.

The corpus arm has not found it occurring naturally in technical documentation in
English. Neither did D8, across five arms that — per §9 — were capable of
exhibiting it. Both are the same population, and
`PRE-REGISTRATION.md` §2.2 already names that population as the most likely place
the recommendation breaks: *"meeting notes, legal boilerplate, or templated
documents, which are exactly the duplicate-heavy shapes a work substrate will
meet."*

So the deciding question is **the corpora, not the merge topology** — and the
resurrect-the-old-bytes shape has an obvious home in exactly those corpora, where
"previous wording kept for audit" is a genre convention rather than an accident.
Choosing them requires a §5 amendment logged in §8 of the pre-registration with a
date, a reason and an argument per choice, which has not been written.

None of this has a verdict attached, and it must not get one from this file.

---

## 2026-09-10 — §9. Retraction: the defect is single-leg reachable

**The claim that this spike's whole rationale leaned on is false, and it was
refuted by running it.**

Asserted in `LOG.md` §3.1, both `expect.json` files, `armed_check.sh`,
`ORACLE.md` §6 and the PR body: *the defect needs both legs to act, and a
single-leg rebase cannot reach it.*

### The reproduction

One author, one commit, no merge of any kind. Reword the anchored paragraph
**and** quote its original wording in a new appendix — the shape any "superseded
wording", changelog or audit-trail edit has:

```python
from anchor_eval import blocks, anchor_of          # D8's own code
from anchor_eval2 import line_oracle
from anchor_eval3 import reanchor2

base  = open('plant_cases/wrong-01/base.md').read()
after = base.replace("queued on the primary worker pool,",
                     "queued on either worker pool,") + APPENDIX_QUOTING_THE_ORIGINAL

bi, bj = blocks(base), blocks(after)
anc    = anchor_of(base, bi[1])
truth, tgt = line_oracle(base, after, bi, bj)[1]      # SURVIVED, target 1
for hard in (False, True):
    print(reanchor2(after, anc, bj, hard))            # ('EXACT', 7) -- not 1
```

```
policy=naive status=EXACT verdict=SILENT-WRONG
policy=hard  status=EXACT verdict=SILENT-WRONG
```

Committed as `plant_cases/single-leg-01/`, which runs through the same
`evaluate_case()` as everything else. Its leg C is byte-identical to the base, so
there is no second author and `git merge` yields leg A exactly; the harness
needed `--allow-empty` before it could express the case at all, which is itself
telling — **it had been built unable to represent its own counterexample.**

### Two errors under it

1. **"Left standing" was the wrong necessary condition.** The condition is that
   the base bytes survive *somewhere* in the resolved text while the anchored
   block's true descendant has moved. Nothing requires those to be done by
   different people, or in different commits.
2. **D8's by-type arm is not a rebase.** `ORACLE.md` §6 says the shape "cannot
   occur in D8's arm" because `git merge-file` has one leg. But
   `anchor_eval3.run()` **never calls `merge3`** — it imports it at line 15 and
   never uses it (`anchor_eval3.py:56-84`). It anchors at `ti` and resolves
   against `tj`, up to 25 commits later. The arm carrying D8's by-type breakdown
   is a **version skip**. `anchor_eval2.py` does call `merge3`, but only to feed
   the *stored-`^id`* arm; its computed arm is a skip too. So the computed
   anchoring result that `PRE-REGISTRATION.md` §1 rests on measured neither a
   rebase nor a merge.

### Why this inverts the reading, and what it does not settle

`PRE-REGISTRATION.md` §2.1 identifies "D8 measured rebase, not a two-branch
three-way merge" as the most likely place a defect hides. If the shape is
reachable without any merge, then **D8's five arms were already able to exhibit
it and recorded zero prose-typed silent-wrongs.** That makes D8 *stronger*
evidence against prose having this defect, not weaker, and it makes the
two-branch case one more route to a precondition rather than a privileged one.

Stated precisely, because the temptation is to overclaim in the other direction
now: D8's method does not *exclude* the shape, so D8's zero is evidence about it.
Whether D8's sampled transitions actually contained resurrect-the-old-bytes edits
is a separate question this spike has not measured. The bound D8 provides is on
the shape's frequency in technical documentation in English, which is the same
population `PRE-REGISTRATION.md` §2.2 already flags as the wrong one.

**`ORACLE.md` is not edited.** It says nothing in it may be adjusted in light of
a result, and that includes being adjusted because it turned out to be wrong.
§6 of that file stands as written and is wrong on both counts; this is the
correction of record. Fixing it means a superseding oracle statement.

### §2.1's premise, restated

The gap §2.1 names is real but narrower than it claims. Nobody had run the
concurrent case — true. But the *defect shape* it worried about was never
exclusive to the concurrent case, so running the concurrent case was never going
to be the thing that decided it. The question that survives is
`PRE-REGISTRATION.md` §2.2's: **the corpora, not the merge topology.**

## §10. A reconciliation that corrects a claim upstream

At the pin, `results/corpus-drift.txt` prints for `obsidian-help` gap=5:

```
block types: code=2 heading=78 list=90 prose=212 table=2      -> sums to 384
```

384 is exactly that arm's oracle-confident anchor count. D8 §3.2's own line for
that arm prints only `heading=78 list=90 prose=212`, which sums to 380, and the
four-anchor shortfall has been read as evidence the line cannot be reconciled
per-bucket and as a missing `code=4`.

Neither. The line was **truncated to its three largest buckets**, and the missing
four are `code=2` **and** `table=2`. The other two by-type lines D8 prints
(rust-book gap=5 summing to 849, gap=25 to 200) are complete, so only the
obsidian line was abridged. The data is intact; the presentation dropped the two
smallest buckets.
