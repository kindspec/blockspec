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
three were found by trying to prove a check was armed. **§7, §5.3 and §5.4 are
three successive failures to check one property**; §5.5 is not a fourth — it is a
defect in the *evidence for* a check, and it sits alongside rather than
underneath. §5.6 states what that sequence supports and what it does not.

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

   **Third in a sequence:** the drops were uncounted (§7), the guard written for
   that was a tautology (§5.3), and the guard — once real — measured a
   denominator the loop could escape (here). See §5.6.

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

### 5.6 What the sequence supports, and what it does not

An earlier draft of this synthesis was attacked and mostly did not survive. What
is left is smaller, and is the part with evidence behind it.

**The property, stated once.** *No both-sides candidate leaves the selection
without a counter behind it.* One property. §7, §5.3 and §5.4 are three
successive failures to check that one property:

| | failure | what was wrong |
|---|---|---|
| §7 | no detector at all | two uncounted `continue`s, covering three drop shapes, dropped 29 candidates silently |
| §5.3 | the detector could not fire | `dropped = cand - acc` made the predicate a tautology |
| §5.4 | the detector's input was corruptible | `cand` was accumulated inside the loop it measures |

**The decomposition is the transferable part**, and it is principled rather than
narrative: a check has a **property**, a **detector**, and the **detector's
inputs**, and each is separately falsifiable. The org contract §2.2 — *"break the
thing it checks, watch it go red"* — addresses only the detector, and only
against the one mutation the author happened to choose. §5.4 is invisible to
§2.2's procedure as written, because every mutation one would naturally pick
turns the detector red while leaving its input corruptible.

**Three qualifications, each of which cost an earlier and larger claim.**

1. **These are not one defect at three depths.** §7 and §5.4 genuinely share a
   mechanism — an uncounted `continue` escaping accounting, first from the drop
   tally and then from the population tally. §5.3 does not: a tautological
   predicate is a different defect that merely happened *inside the fix for* §7.
   Two share a mechanism; the third shares only a location.
2. **"Arming the top says nothing about what is underneath" is false**, and this
   spike is the evidence against it. Arming said a great deal: attempting to arm
   each fix is precisely what exposed the next layer, in three consecutive review
   passes. The accurate form is weaker and more useful — **arming validates one
   layer and tends to surface the next, so one pass is a beginning rather than a
   completion.**
3. **The sequence terminated, and how it terminated is the better lesson.**
   §5.4's fix adds no fourth check. It moves `cand` out of the loop, so the
   denominator is no longer subject to the control flow it measures: **the
   failure class is removed rather than detected.** "It is a stack" invites
   indefinite regress and offers no way out. The regress ends when you stop
   adding checks and make the failure structurally impossible — which is what
   happened here, and it is the headline.

**n=1, and it stays in this file.** Three instances, one file, one afternoon, one
review loop — and only two of §5's five entries are instances (3 and 4); the
third is §7, which is not one of them
even within this log. Generalising it into the org contract on that basis would
be `PRE-REGISTRATION.md` §0's failure mode applied to process instead of results:
a rule written after seeing the outcome. Contract §4's *"measure before deciding"*
cuts the same way.

**What would earn a promotion:** a second instance found somewhere the contract
would actually bind — a check whose property, or whose detector's inputs, fail
while its detector passes its own mutation. rowspec's **mutation gate** and the
**conformance runner** are the two places to look: both have the shape, and both
have a recorded history of reporting a pass over a population nothing opened.
Until then this is an observation with three instances in one afternoon, recorded
where the next person will find it and not written into a rule.

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
were dropped**, by two `continue` statements covering three drop shapes, with
no counter, no report line
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

## 2026-10-07 — §11. Three statements above that are no longer current

No measurement in this entry. The sections it corrects are left as written,
because this file is append-only; read them with this entry.

### The duplicate-heavy corpora are named and pinned

The 2026-09-09 scope table ("choose §5's duplicate-heavy corpora … Not
written"), §7 ("the whole of §5's duplicate-heavy arm, which has not been
chosen") and §8 ("which has not been written") were true when written and are
not now. `PRE-REGISTRATION.md` §5.1 names and pins three corpora, by the §5
amendment logged in its §8 on 2026-10-06 and corrected on 2026-10-07. That
landed in kindspec/blockspec#11 and #12, which changed `PRE-REGISTRATION.md`
only and wrote no entry here; this is that entry.

**What has not changed:** the arm has not been run, and §6.2 still stands.
§6.2 predates the corpus choice and characterises the duplicate-heavy arm in
general: the corpora §5 calls for are the short, repeated-block shape TLLC
cannot adjudicate, so that arm needs a superseding oracle statement before its
prose numbers can be believed. Whether the three corpora §5.1 now names exhibit
that shape has not been measured. Whether to write a superseding
pre-registration before running blockspec#2, or to run it under the current one
as it stands, is an open owner decision. This file records it as open and decides neither way.

### kindspec/research#5 is closed

§2.2 says D8 §3.3's prose-uniqueness table is "under re-verification". It is
not: research#5 closed 2026-09-11, and kindspec/research#7 made the table
reproducible — `e4_uniqueness.py` now takes `minlen`, and its output is
committed as `experiments/D8-identity/results-e4.txt`. §2.2's conclusion
stands: nothing in this spike cites or depends on that figure.

### §6.1's "85 candidates" counts records, not cases

"44 of the 85 candidates" in §6.1 is a count of **records** in
`results/merge-arm-candidates.jsonl` — one per mis-resolved base block per
policy — not of merge cases. Elsewhere in this file "candidate" means a
both-sides `.md` path (§7's 224), so the word is carrying two units. Counted
from the committed file, run from the repository root:

```
$ python3 -I -c "import json,collections
r=[json.loads(l) for l in open('spike/results/merge-arm-candidates.jsonl')]
print(len(r), collections.Counter(x['policy'] for x in r))
print(len({x['case'] for x in r}), 'distinct cases')
print(len({(x['case'],x['block_index']) for x in r}), 'distinct blocks')"
85 Counter({'naive': 64, 'hard': 21})
16 distinct cases
64 distinct blocks
```

So: 85 records, over 64 distinct base blocks, from **16 distinct cases**, all
`rust-book`. The single case §6.1 names contributes 44 of the 85 records.

## 2026-10-07 — §12. The cheap arm: D8's anchor and uniqueness drivers on the §5.1 corpora

**This decides nothing.** It is input to a superseding pre-registration that has
not been written. No tier is assigned, no verdict is drawn, and nothing below is
read against §3's FOUND conditions or §1's control gate. `PRE-REGISTRATION.md`
and `ORACLE.md` are untouched.

### What was run

D8's single-edit anchor analysis (`anchor_eval3.py`: anchor a block at `C_i`,
re-resolve it at `C_{i+gap}` of the same file, grade against D8's line oracle)
and its quote-uniqueness measurement (`e4_uniqueness.py`), on the three corpora
`PRE-REGISTRATION.md` §5.1 names, at its pins:

| name | source | pin |
|---|---|---|
| `k8s-website` | `github.com/kubernetes/website` | `6b27baef1e44275fd4368e14375296e1dfe5af11` |
| `cncf-toc` | `github.com/cncf/toc` | `144c2e3215884e498e744cc51e6b7cef82d654f1` |
| `site-policy` | `github.com/github/site-policy` | `b9578b546d2506febda1da2cd7431644d58e512c` |

Full working-tree clones checked out at the pin. The mechanism is
kindspec/research at `d51ce09cdb23af32f35e7a3c6111ac21ab0f033f`, unmodified.

```sh
CORPORA=/path/to/clones \
D8_DIR=/path/to/research/experiments/D8-identity \
  spike/harness/run_cheap_arm.sh
```

`harness/run_cheap_arm.sh` runs three stages and stops on the first failure;
`harness/d8_cheap_arm.py` is the driver. Outputs are in `results/cheap-arm/`.

### The adaptation, and what it does not touch

Both originals hardcode `corpora/rust-book`, `corpora/obsidian-help` and
`corpora/cmspec` relative to the working directory, so they cannot be pointed
anywhere else. `d8_cheap_arm.py` **imports** the mechanism (`blocks`,
`anchor_of`, `git`, `line_oracle`, `reanchor2`, `btype`) from `--d8-dir` and
**copies only the two driver loops**, `anchor_eval3.run()` with its printer and
`e4_uniqueness.py`'s top-level loop. Changed in the copies, and nothing else:

1. The corpus is `--corpus NAME REPO PIN PATHSPEC`. Headers print `NAME` where
   the originals printed `basename(repo)`.
2. The file list is D8's rule (`git ls-files PATHSPEC`, keep `*.md`, in that
   order), minus generated files under `--generated-rule` (`none`, the default,
   leaves D8's list unchanged; `anywhere` and `yaml-fence` are described below
   and in §12.1).
3. `--frontmatter-type` (off by default) labels blocks inside a leading YAML
   fence `frontmatter` instead of calling `btype()`. This is D8 §11 item 8's
   missing rule. It changes labels only, because `reanchor2()` never sees a type.
4. `--gaps` (default `5,25`, as D8), `--show-wrong` (off by default; prints
   each silent-wrong, as D8 §3.2 quotes its own), and `--distinct` (off by
   default; adds the uniqueness counts over distinct block contents).
5. It fails loudly: exit 2 on a missing or non-git corpus, a HEAD that is not
   the stated pin, tracked changes in the work tree (the uniqueness arm reads
   the work tree), an empty selection, a corpus that yields no blocks, or an
   anchor run that evaluates no version pair at any gap; exit 1 if an arm raised.
   e4's silent skip of unreadable files is printed whenever it is non-zero.
   None fired on these corpora.

It never writes bytecode, so the research checkout is not modified.

### Validation, before any new corpus was read

**Stage 1. Byte-identical reproduction** (`results/cheap-arm/validation.txt`).
At D8 §3's pins (`rust-book` `1500248d…`, `obsidian-help` `327a782e…`,
`cmspec` `3da93942…`, which are **not** `harness/corpora.json`'s pins), the
adapted driver's `uniqueness` at 20, 40 and 120, concatenated, is byte-identical
to `results-e4.txt`, and its `anchors` output is byte-identical to
`results-anchor3.txt`. The sha256s are equal and `cmp` is silent on both. The
unmodified originals reproduce both artifacts too, run from a directory holding
those clones.

**Stage 2. Red states** (`results/cheap-arm/red-states.txt`).

- *The originals' defect, shown* (kindspec/research#6). Run from a directory
  with no `corpora/`, `e4_uniqueness.py 40` prints `files=0 blocks>=40ch=0` and
  exits 0, and `anchor_eval3.py` prints six `too few (0)` lines and exits 0.
- *The adapted driver, each way of reading nothing:* a missing path, a non-git
  path, a HEAD that is not the pin, a tracked file modified in the work tree, a
  pathspec that selects nothing (for both subcommands), files that yield zero
  blocks, a corpus with no version pair at any gap, and a `--d8-dir` without
  the scripts. **All nine exit 2.**
- *The stage-1 gate, broken:* `anchors --frontmatter-type` on D8's corpora
  relabels the YAML silent-wrong D8 §3.2 discusses, and `cmp` against
  `results-anchor3.txt` reports `differ: byte 741, line 13`. So the gate can
  see a single changed label.

### The prose-subset rule

Applied to all three corpora alike. **When this rule was set relative to when
the first outputs were read is not recorded**: the rule, the runner and the
outputs landed in one commit, and `selection-before-generated-rule.txt` is
itself an output. Read it as a rule chosen by the person who ran the arm, not
as a pre-registered one. §12.1 runs the alternatives.

- **Root.** Use the directory the published site renders from where there is
  one (`kubernetes/website`: `content/`). Otherwise use the whole repository.
- **Minus forge metadata.** Drop `.github/` (issue and PR templates).
- **Minus files that say they are generated** (`--generated-rule anywhere`). A
  file is dropped when its text matches, anywhere in the file,
  `^auto_generated:[ \t]*true[ \t]*$` (multiline, case-insensitive;
  kubernetes/website's frontmatter key for generator output) or
  `THIS FILE IS AUTO-GENERATED` (case-insensitive; cncf/toc's generator banner,
  from `tags.yaml`). "Anywhere" is wider than "its own frontmatter": §12.1
  counts the translations it drops only because they quote the English
  frontmatter in an HTML comment.
- **Nothing else.** Translations, archives (`cncf-toc/.archive/`) and templated
  project documents stay in.

`k8s-website-en` (`content/en/`, the English source) is reported **beside** the
all-languages arm, not instead of it. §5.1 chose this corpus for its i18n shape,
so dropping the translations would have dropped the reason for choosing it.

From `results/cheap-arm/selection.txt` and `selection-before-generated-rule.txt`:

| arm | pathspec | before generated rule | excluded as generated | measured |
|---|---|---|---|---|
| `k8s-website` | `content/*.md` | 8259 | 566 | **7693** |
| `k8s-website-en` | `content/en/*.md` | 2513 | 305 | **2208** |
| `cncf-toc` | `*.md :(exclude).github/` | 598 | 11 | **587** |
| `site-policy` | `*.md :(exclude).github/` | 61 | 0 | **61** |

Every excluded path is listed in `selection.txt`. These are excluded before the
pathspec, by `git ls-files '*.md' | wc -l` at the pin less the pathspec's count:
17 in `kubernetes/website` outside `content/` (`archetypes/`, root files,
`.github/`, `static/`, `scripts/`, `update-imported-docs/`), 7 under `cncf/toc`'s
`.github/`, and 2 under `site-policy`'s `.github/`.

### Quote uniqueness: the prose rows

**This section is the `anywhere` selection only, and like the anchor result it
is not robust to the selection rule.** `anywhere` is one of three committed
selections, not a default. For example, `k8s-website` prose at ≥40 has 481
distinct within-file-duplicated contents under `anywhere`, 933 under
`yaml-fence` and 959 under `none`. §12.1 has all three.

`results/cheap-arm/uniqueness.txt`, D8's classifier, verbatim. The ≥40 rows
are the threshold `DESIGN-BRIEF.md` §1 argues from:

```
### k8s-website     files=7693  blocks>=40ch=196405 | prose     110918      1524 ( 1.4%)         13358 ( 12.0%)
### k8s-website-en  files=2208  blocks>=40ch=56643  | prose      37948       482 ( 1.3%)          1955 (  5.2%)
### cncf-toc        files=587   blocks>=40ch=20532  | prose      12120       121 ( 1.0%)          1574 ( 13.0%)
### site-policy     files=61    blocks>=40ch=1799   | prose       1412         9 ( 0.6%)            55 (  3.9%)
```

The columns are: prose blocks, duplicated within the same file, duplicated
anywhere in the corpus. All three are **instance** counts. For comparison, D8's corpora at ≥40, from
`results-e4.txt`: `rust-book` `prose 2938 0 ( 0.0%) 0 ( 0.0%)` and
`obsidian-help` `prose 2526 16 ( 0.6%) 48 ( 1.9%)`. The 20 and 120 arms, and
every non-prose row, are in the file.

**Instances are not distinct authored blocks** (contract §4,
`PRE-REGISTRATION.md` §7). A paragraph repeated within one file, in each of
seventeen translated copies, is seventeen within-file instances. `--distinct`
counts distinct block contents instead (`uniqueness-distinct.txt`, same
selection). Its three columns are distinct prose contents, distinct contents
duplicated within some file, and distinct contents duplicated anywhere in the
corpus. At ≥40, verbatim:

```
k8s-website     | prose     110918      1524 ( 1.4%)         13358 ( 12.0%)  |     102489        481     4929
k8s-website-en  | prose      37948       482 ( 1.3%)          1955 (  5.2%)  |      36701        172      708
cncf-toc        | prose      12120       121 ( 1.0%)          1574 ( 13.0%)  |      11098         39      552
site-policy     | prose       1412         9 ( 0.6%)            55 (  3.9%)  |       1382          3       25
```

So `k8s-website`'s 1524 within-file instances are **481 distinct contents**,
and `cncf-toc`'s 121 are **39**. What those contents are (shortcodes,
templated notes, or authored sentences) is not classified by any committed
output.

Typing frontmatter separately (`uniqueness-frontmatter.txt`) moves the ≥40
prose rows to `k8s-website 101829 1524 ( 1.5%) 12059 ( 11.8%)` and
`k8s-website-en 35143 482 ( 1.4%) 1923 ( 5.5%)`. The prose within-file counts
do not change. That does not mean no within-file duplicate is frontmatter:
`k8s-website` at ≥40 prints `frontmatter 9619 1`, and the heading row drops
from 299 to 298 within-file duplicates. So the one duplicated frontmatter
block had been typed `heading` by `btype()`, not `prose`.
`cncf-toc` moves to `prose 12118 121 ( 1.0%)` and `site-policy` to
`prose 1355 9 ( 0.7%)`.

### Anchor resolution

**This section is the `anywhere` selection only, and its result is not robust
to the selection rule.** §12.1 has the other two selections.

`results/cheap-arm/anchors.txt`, at gaps 1, 5 and 25. D8's sampling is
unchanged: 14 files per corpus, 30 blocks per pair, `seed=7`, and an arm with
fewer than 50 oracle-confident anchors prints `too few (N)` and is not scored.

```
### k8s-website content/*.md gap=1  pairs=30  oracle-confident anchors=407
### k8s-website content/*.md gap=5: too few (36)
### k8s-website content/*.md gap=25: too few (0)
### k8s-website-en content/en/*.md gap=1  pairs=13  oracle-confident anchors=223
### k8s-website-en content/en/*.md gap=5  pairs=10  oracle-confident anchors=203
### k8s-website-en content/en/*.md gap=25  pairs=4  oracle-confident anchors=81
### cncf-toc *.md :(exclude).github/ gap=1  pairs=16  oracle-confident anchors=385
### cncf-toc *.md :(exclude).github/ gap=5  pairs=6  oracle-confident anchors=164
### cncf-toc *.md :(exclude).github/ gap=25  pairs=4  oracle-confident anchors=52
### site-policy *.md :(exclude).github/ gap=1  pairs=46  oracle-confident anchors=627
### site-policy *.md :(exclude).github/ gap=5  pairs=16  oracle-confident anchors=178
### site-policy *.md :(exclude).github/ gap=25: too few (0)
```

That is 9 scored arms of 12. Across them, the harness printed **8 silent-wrong
records** (`anchors-silent-wrongs.txt` has each with its quote, the resolved
block and the oracle's block). They come from **three distinct blocks**:

- **`k8s-website` gap=1, naive and hard, typed `prose`.** The file is
  `content/zh-cn/docs/reference/glossary/cri-o.md`, `24d17ed091..dcaafc7335`.
  The file carries its English original in HTML comments after the real YAML
  fence. At `C_i` the anchored block is the tail of that commented-out English
  frontmatter (`aka:\ntags:\n- tool\n-->`), followed by the commented English
  definition and its Chinese translation. At `C_j` those are two blocks. The
  oracle names the first and `reanchor2` resolved to the second, `FUZZY` under
  both policies. `--frontmatter-type` still types it `prose`, because the block
  starts after the YAML fence closes.
- **`cncf-toc` gap=5, naive only, typed `prose`, two records.** The file is
  `projects/kserve/kserve-incubation-dd.md`, the same quoted text in two
  version pairs. An adopter-interview reference line for Cloudera resolves
  onto the near-identical line for Nutanix. The oracle's target is the Cloudera line
  with its link rewritten. The hardened policy refuses it in both pairs as
  `REFUSED_MARGIN`. That was checked by calling `reanchor2` on those two pairs,
  and it is not in a committed file.
- **`site-policy` gap=5, naive and hard, typed `heading`, four records.** The
  file is `Policies/content-removal-policies/github-private-information-removal-policy.md`,
  the same quoted text in two version pairs. A heading plus its first
  paragraph becomes two blocks. The oracle names the heading and the anchor
  resolved to the paragraph.

So, under the `anywhere` selection, the hardened policy and D8's classifier, one
scored arm prints a
`prose`-typed silent-wrong (`k8s-website` gap=1, n=1). Two of the three blocks,
including that one, are a block **split in two** between `C_i` and `C_j`.
Whether resolving to either half is wrong is a question about the oracle, which
this measurement does not settle.

### What these numbers do not say

- **Nothing about merges.** This is D8's version-skip arm: one file, two
  commits, no `git merge`. `LOG.md` §9 is why that is still informative, and
  it is all this is.
- **Nothing about blocks under 20 characters.** Both drivers discard them, and
  the anchor driver also discards quotes under 20. §6.2's undecidable shape is
  *short* single-line repeated blocks. So the shape §11 says "has not been
  measured" in these corpora **still has not been**. The uniqueness rows bound
  duplication at ≥20 characters and nothing shorter.
- **The anchor arms are thin.** 14 files per corpus is D8's sample size, kept
  so the method is D8's. Over 7693 `k8s-website` files it is a small sample:
  the all-languages arm scores only at gap=1, and its 14 sampled files include
  translations with shallow history. Any rate from a 4- to 46-pair arm is
  labelled by its pair count above, and should be quoted with it.
- **Instance counts are not distinct authored blocks, in either column.**
  `k8s-website` replicates content across 17 languages, and untranslated code
  and identifiers count as corpus-wide duplicates. Each translated copy also
  carries its own within-file duplicates, so the within-file column is
  inflated too. Contract §4's trap applies to both. The distinct-content
  columns remove duplication *within* a language, because the same bytes count
  once. They do not remove replication *across* languages: a translated
  paragraph has different bytes in each language and counts once per language
  (`k8s-website` 481 against `k8s-website-en` 172). So they are not "distinct
  authored blocks" in the contract §4 sense either.
- **`btype()` is D8's.** Every type label above is the harness's, frontmatter
  aside, and both runs are committed. Hugo shortcodes, HTML comments inside
  translated files, and adopter reference lines all type as `prose`.
- **The entropy predicate is word-based** (D8 §11 item 3). `k8s-website`
  includes zh-cn, ja and ko, and the one hardened prose-typed silent-wrong
  under the `anywhere` selection is in a zh-cn file. That is an observation, not a diagnosis. It was not
  investigated further.
- **No tier, no verdict, no comparison to §1's gate.** §1's gate is defined
  over D8's five control arms, and these are not those arms.

### §12.1 The anchor result is not robust to the selection rule

Added after an independent review of §12. §12 above was corrected in place
while unmerged: the claims about distinct blocks, about frontmatter
duplicates and about when the rule was set, plus the regex text.

**Why the rule moves the anchor result.** D8's sample is
`Random(7).shuffle(files)[:14]`. Removing one file from the list re-draws all
14. So the generated-file rule does more than drop generated files from the
sample: it changes which human-authored files are drawn. Three selections are
run and committed. **None is preferred here.** Which one to use belongs to the
superseding pre-registration, along with whether 14 files is enough.

| `--generated-rule` | what it drops | k8s-website | k8s-website-en | cncf-toc | site-policy |
|---|---|---|---|---|---|
| `none` | nothing (D8's list) | 8259 | 2513 | 598 | 61 |
| `anywhere` | §12's rule | 7693 | 2208 | 587 | 61 |
| `yaml-fence` | the k8s key only inside the leading YAML fence, the cncf banner anywhere | 7935 | 2208 | 587 | 61 |

These counts come from `selection-before-generated-rule.txt`, `selection.txt`
and `selection-yaml-fence-rule.txt`. **`yaml-fence` is post hoc**: it was
written after `anywhere`'s outputs and the review had been read, and it is
reported as a comparison, not as a correction. The two rules differ on
**242** `k8s-website` files, all under `content/zh-cn/`. In each, the key
appears only inside an HTML comment that quotes the English page's
frontmatter, not in the file's own YAML. Checked over every occurrence of the
key in those files. The count, run from `spike/results/cheap-arm/`:

```
$ python3 -I -c "
import collections
def ex(p):
    out=set(); on=False
    for l in open(p):
        if l.startswith('### '): on=l.split()[1]=='k8s-website'
        elif on and l.startswith('  - '): out.add(l[4:].rstrip())
    return out
d=ex('selection.txt')-ex('selection-yaml-fence-rule.txt')
print(len(d), collections.Counter(f.split('/')[1] for f in d))"
242 Counter({'zh-cn': 242})
```

**Reconciled with the review's 261.** Counted the same way over the
`k8s-website` excluded lists in `selection.txt` and
`selection-yaml-fence-rule.txt`:

- `anywhere` drops 566 files: en 305, zh-cn 259, bn 1, ko 1.
- `yaml-fence` drops 324 files: en 305, zh-cn 17, bn 1, ko 1.
- Every `yaml-fence` drop is also an `anywhere` drop.

261 is every non-English `anywhere` drop. It splits into the 242 above, which
only `anywhere` drops and where the key sits only inside an HTML comment, and
19 that both rules drop, where the key is in the file's own leading YAML
fence. None of the 19 matches the banner.

**Hardened, prose-typed silent-wrongs, per selection** (D8's classifier;
`anchors.txt`, `anchors-no-generated-rule.txt`, `anchors-yaml-fence-rule.txt`;
each record is quoted in the matching `anchors-silent-wrongs*.txt`):

| selection | scored arms | silent-wrong records (blocks) | hardened, `prose`-typed |
|---|---|---|---|
| `none` | 8 of 12 | 7 (3): k8s gap=5 `html` (2 blocks), site-policy gap=5 `heading` | **0** |
| `anywhere` | 9 of 12 | 8 (3): k8s gap=1 `prose`, cncf gap=5 `prose` (naive only), site-policy gap=5 `heading` | **1** |
| `yaml-fence` | 10 of 12 | 6 (2): cncf gap=5 `prose` (naive only), site-policy gap=5 `heading` | **0** |

**So whether this arm shows any hardened, prose-typed silent-wrong depends on
which files are excluded before sampling.** The one §12 reports appears under
one of the three selections only. The site-policy records are the only ones
present in all three, because site-policy's file list is the same under every
rule.

**The uniqueness counts move too.** They read every selected file, so the
change is in population, not sample. Prose at ≥40, from the three
`uniqueness-distinct*.txt` files (instances, then distinct contents):

```
none        k8s-website  prose 119180  3255 ( 2.7%)  16892 ( 14.2%) | 108405  959  6117
anywhere    k8s-website  prose 110918  1524 ( 1.4%)  13358 ( 12.0%) | 102489  481  4929
yaml-fence  k8s-website  prose 116662  3122 ( 2.7%)  15600 ( 13.4%) | 106648  933  5586
```

`k8s-website-en` and `site-policy` are identical under `anywhere` and
`yaml-fence`. `cncf-toc` is identical under those two and differs under `none`
only by its 11 banner files (`prose 12126 121 ( 1.0%)`). The full tables are
in the files.

**Also added: a clean-tree check.** The uniqueness arm reads the work tree, not
`HEAD`, so a pinned HEAD with modified tracked files would have measured
something other than the pin. `check_corpus` now exits 2 on any tracked change
(`git status --porcelain --untracked-files=no`), and `red-states.txt` shows it
firing on a clone with one edited file. The six corpora were clean, and the
`anywhere` outputs regenerate byte-identically with the check in place.

## 2026-10-07 — §13. A superseding pre-registration is drafted

No measurement in this entry. The owner decided to write a superseding
pre-registration before blockspec#2 runs, which settles the question §11
recorded as open. The draft is `PRE-REGISTRATION-2.md`. It is not binding
until the owner approves it and it merges. `PRE-REGISTRATION.md` and
`ORACLE.md` are unchanged. No arm has run under the draft.

## 2026-10-07 — §14. The harness for `PRE-REGISTRATION-2.md`, before validation

No arm has run. Arm 0, E, S, M, R, the exporter and the tierer have not been
executed against any corpus, and no sealed manifest exists. This entry
records a harness that is **not yet validated**: under §9 the harness at the
validation commit is the implementation, and that commit has not been made.
It waits on an independent review and on the owner decisions below.

- **Built:** `harness/prereg2.py`, `harness/p2/`, `harness/prereg2_v3.py`
  (V3), `harness/prereg2_v4.py` (V4) and `harness/prereg2_validate.sh`
  (V1-V5 and a bundle check).
- **V transcripts, from the harness commit they name:**
  `results/prereg2/validation/`. V1, V2, V3, V4 and V5 each end in `PASS`.
  These are pre-review runs. The V steps run again at the validation commit.
- **Bundles (§6.2):** made, not committed. Each one's sha256, size and head
  are in `harness/p2/bundles.json`, and `results/prereg2/validation/bundles.txt`
  checks them. Where the bundles are stored is open.

Open before the validation commit, for the owner:

1. §6.5 does not define "adjacent-run twin". Arm 0 counts it under a
   provisional reading, `p2/arm0.py` `ADJACENT_RUN_RULE`. No verdict reads it.
2. `find_merge_cases()` decodes git output strictly. kubernetes/website's
   history holds `.md` blobs that are not UTF-8, three of them on paths
   under `content/`. If any of these is on a both-sides path of a merge, the
   `k8s-l10n` M arm aborts. That has not been checked, because checking it
   means enumerating merges.
3. V2's `merge-arm.txt` regenerates byte-identically only with `--records`
   spelled `spike/results/...`, which is how the committed file was made. It
   does not regenerate from `spike/README.md`'s command as written.
   `control-arm.txt` embeds its D8 path and research commit, so it
   regenerates only with research at `f088cd76` at that path.
4. The tierer's working directory holds only the export. Other paths on the
   host are still readable to it, so the filesystem barrier is weaker than
   org contract §2.1 describes.

## 2026-10-08 — §15. Owner rulings on §14's open items, before Arm 0

No arm has run. This entry records the owner's rulings of 2026-10-08 on the
items §14 left open, as the harness implements them. Each is fixed here
before Arm 0, as §9 requires of a reading the harness depends on.

**Bundle storage (§6.2).** The six bundles and their `SHA256SUMS` are held
in a private release owned by the kindspec org owner, tag
`prereg2-bundles-v1`. The owner verified a download round trip. A durable
local copy is at `/home/cam/kindspec-data/prereg2-bundles/`.
`harness/p2/bundles.json` records both locations. The harness reads bundles
from `--bundle-dir`, else `$PREREG2_BUNDLE_DIR`, else that local copy.

**"Adjacent-run twin" (§6.5): a labelled reading for a report-only line.**
§6.5 does not define the term. Arm 0 prints this line labelled
"provisional reading (LOG §15)", and the reading is:

> A distinct content (type, content) of 20 characters or more counts as an
> adjacent-run twin if, in at least one selected file, two of its instances
> are consecutive blocks of that file — positions *i* and *i*+1 in D8's
> `blocks()` sequence, where blocks of every length count toward the
> position.

No verdict reads this line. The bar uses only "has a twin in the same file".
V3 checks that Arm 0 prints the label. It also checks that no aggregate or
verdict path imports Arm 0 or reads this count.

**Blobs that are not valid UTF-8.** This rule applies to E, S and M. A case is
excluded if any of these is not valid UTF-8:

- its base;
- any of its legs;
- its after-state or merged text.

Each excluded case is counted as `undecodable`, per arm and per mode, and
the count is printed in the arm's output and its transcript.

`find_merge_cases()` stays the supplied enumeration, called unchanged. For
that call only, its git reader is replaced by one that decodes with
`surrogateescape` instead of raising. Text that is valid UTF-8 reads exactly
as before. Under the strict reader, one non-UTF-8 blob on a both-sides path
aborted the whole census. V3 builds a fixture merge with such a blob and
checks three things:

- the supplied reader raises on it;
- the arm completes;
- the arm excludes that case and counts it.

This rule replaces §14's open item 2. No probe of the corpora was run.

**The tierer's isolation (§7.3).** The tierer runs under bubblewrap. The
sandbox gives it read-only views of these and nothing else:

- `/usr`, with its usual links;
- `/etc/ssl`, `/etc/resolv.conf`, `/etc/hosts` and `/etc/nsswitch.conf`;
- the agent's own binary.

Inside the sandbox, `HOME` is a fresh tmpfs. The only file in it is the one
credential file the CLI reads, `~/.claude/.credentials.json`, mounted
read-only.

The working directory, `/work`, is an empty host directory that the agent
can write `tiers.jsonl` into. The export's `PROMPT.md` and `packets/` are
mounted read-only inside it. Every namespace is unshared except the
network, which stays on. As §7.3 says, the network barrier is honoured, not
enforced.

V3 runs a stub agent through this wrapper. Inside the sandbox the stub
cannot read a planted file under `/home/cam/repos_kindspec`, and cannot read
`~/.claude` or `~/.claude/projects`. It can read the export and the one
bound credential file. The same stub, run without the sandbox, can read
both of the host paths. This replaces §14's open item 4.

**V2 reproductions that need a documented condition.** §10 lets the V-list
be corrected on a fact before Arm 0. These conditions are recorded here, and
no result is changed:

- `results/merge-arm.txt` ends with the line `wrote 85 candidate records
  ... -> spike/results/merge-arm-candidates.jsonl`. So it regenerates
  byte-identically only when `--records` is spelled
  `spike/results/merge-arm-candidates.jsonl`, run from the repository root
  or a directory laid out like it. `spike/README.md`'s command, run from
  `spike/` with `results/...`, differs in that last line alone.
- `results/control-arm.txt` embeds, on its second line, the D8 directory
  `/home/cam/repos_kindspec/research/experiments/D8-identity` and research
  HEAD `f088cd76`. So it regenerates byte-identically only with a research
  checkout at `f088cd76` at that path. `harness/prereg2_validate.sh` takes
  that path as `CONTROL_D8_DIR`. The V1 transcripts so far got there by
  bind-mounting a `f088cd76` clone over that path, in a private mount
  namespace.

## 2026-10-08 — §16. Independent review of the harness: the binding is enforced, and the readings are logged

No arm has run. Three independent reviews looked at blockspec#16 at `312b415`:
fidelity to the document, checks that pass silently, and binding mechanics.
This entry records how the harness now answers them, before validation.

### The binding, enforced by the harness (`harness/p2/binding.py`)

`results/prereg2/VALIDATION` names the validation commit and the sealed
manifest's sha256. `prereg2.py bind` writes it after checking it, and the
first Arm 0 commit adds it.

Every bound command checks four things before it runs:

- the validation commit is an ancestor of HEAD;
- `git diff --quiet` from that commit to HEAD over `harness/`,
  `PRE-REGISTRATION-2.md` and `ORACLE.md`;
- every one of those files, hashed with `git hash-object`, against the
  commit's `git ls-tree`. This means `--assume-unchanged` cannot hide an edit.
  No untracked or ignored file may sit under the harness;
- nothing under `results/prereg2/` is uncommitted except the command's own
  transcript. VALIDATION is also exempt, until an Arm 0 result is committed.

For arm0, score and export there is one more check: no earlier transcript of
the same command and arm may exist.

A bound command takes every path from its fixed place and accepts no
override of any path, mode, sample size, manifest sha or agent. The
manifest's sha256 comes from VALIDATION. A transcript opens before the
arguments are parsed, so a usage error is recorded too. An unbound or
fixture run must name all its outputs outside `results/prereg2/`.

`aggregate` checks three more things before it gives a verdict:

- every input is bound by the same validation commit;
- every score run used §6.5's sample sizes;
- the transcripts show exactly one bound arm0 and one bound score per arm,
  one export, and at most two tiering runs. If there are two, the first
  wrote zero lines.

**What this does to §9's commit order.** Before each bound run, everything
under `results/prereg2/` must be committed. So each invocation's transcript
and output are committed before the next one starts. The reading taken here
has three parts:

- Each §9 step lands on `main` as one commit, from its own pull request:
  validation, Arm 0, scoring and export, tiers, verdict. The repository
  allows squash merges only.
- The commits made within that pull request are squashed into it.
- The validation commit is `main`'s squash commit for the validation pull
  request. The scoring-arm commit is the one commit in HEAD's history that
  added `results/prereg2/score/`.

`tier-run` refuses if more than one commit added it. Both §9's grouping and
the ruleset interact here, so this is put to the owner rather than decided
silently.

### Tiering (`harness/p2/tierrun.py`)

- `tier-model` runs on the start day. It fetches the Models API listing
  itself and takes the day from the response's `Date` header. It writes
  `models-listing.json` and `tier-model.json`, which are committed.
- `tier-run` writes "started" to `tier-runs.txt` before the agent starts.
  Its working directory, `tier-work-<n>/`, is never deleted. The first
  started run binds whether or not it completed.
- `tiers.jsonl` is read without following a symlink.

### Readings, each fixed here before Arm 0

1. **§5.2 R slug units.** These are the heading spans and nothing else.
   Blocks before the first heading lie in no unit. In step 1, `t` is the
   unit holding the plurality block `p` of the §3 section's TLLC verdict
   under check. The targets of the neighbouring units come from TLLC over
   each neighbouring unit. If `p` lies in no unit, the rule has no `t` and
   the record is UNDECIDABLE-REPEAT, with the note "TLLC's target lies in no
   §5.2 unit".
2. **SPLIT** counts every mapped line of `k` under each leg that proposed a
   target. A mapped line in no unit is not counted.
3. **An unplaceable plant (§7.3's void list).** UNPLACEABLE "is not a
   finding" (§7.2), so it lies on the non-qualifying side of the B/C line.
   An unplaceable P-A or P-B therefore voids the tiering. An unplaceable P-C
   whose q3 and q4 answers are as expected does not.
4. **Arm 0's bar** stops an arm only above 10%. An arm with no
   natural-language content, 0 of 0, passes the bar, and its cells then fail
   §6.6's floor.
5. **The packet representative.** It is the record with the smallest id over
   every mode of its arm. F6 and F9 are judged on that one record, for every
   cell that exported the packet. The packet key holds no mode.
6. **F9.** A record reproduces only if its reproduction result is bound by
   the same validation commit and the committed and regenerated sha256s are
   equal. A record that does not reproduce is named in its cell's reason.
7. **Reported beside each verdict, with no verdict of their own:**
   - every cell computed under `none` and `anywhere`;
   - site-policy M's 25-case set;
   - the strict set's count against the first registration's 21, with the
     difference;
   - each FOUND's count of finds that rest on an oracle-DELETED target,
     labelled `WRONG_on_deleted`, weaker, `ORACLE.md` §4.
8. **R resolution.** If any region marker carries the name, the region
   count decides and slugs are not consulted. A region's target is the D8
   block that holds its first line. Slugs come from blocks `btype()` types
   `heading`, as §3 names it.
9. **E.** Renames are counted in a separate `-M` pass, and that count
   overlaps the add and delete counts. Blobs are read as text, with
   universal newlines, as D8 and `find_merge_cases()` read them. An
   undecodable case (§15) is not replaced in the sample.
10. **The selection rules.** E and S draw one sample per rule. The union is
    evaluated, and each record is tagged with its rules. Only `yaml-fence`
    carries a verdict.
11. **Arm 0's distinct contents** are keyed by (type, content), summed over
    the natural-language types. A file at the pin that is not UTF-8 is
    counted and excluded.
12. **Floors** count decided units whatever F3 says.
13. **R has no naive policy**, so near miss (iii) is Q only. Near miss (i)
    needs F9.
14. **Packets.**
    - The nonce enters the name as its 32 raw bytes.
    - `PROMPT.md` is Appendix A with its `> ` quoting removed.
    - A DELETED target is a fixed sentence.
15. **Tiering.** The first well-formed line for a packet binds, and a
    malformed line leaves its packet untiered.
16. **§6.7.** The R condition accepts a NOT FOUND cell in any mode,
    including M. The Q condition names E, S5 and S25 only.

### A V-list fact (§10)

V3's REPEAT item says `oracle_limitation.py`'s case "comes out
UNDECIDABLE-REPEAT". Its NOTE blocks are 16 characters long. That is under
the mechanism's 20-character quote floor, so Q skips them and never grades
them.

V3 therefore checks two things. The §5.2 rule returns UNDECIDABLE-REPEAT on
that exact case. And the whole evaluation path returns the same once the
NOTE is lengthened past 20 characters.

§10 lets the V-list be corrected on a fact, "logged below" in the
document's own table. The document cannot change by a byte: its sha256 is
pinned in `harness/p2/export.py`, because packets are cut from it. So the
correction is logged here, and whether to amend the table itself is put to
the owner.

## 2026-10-08 — §17. PRE-REGISTRATION-2.md is binding

`PRE-REGISTRATION-2.md` still opens with "Status: DRAFT, for owner approval",
and §13 above says it is "not binding until the owner approves it and it
merges". Both conditions now hold:

- the owner approved it on 2026-10-07;
- blockspec#15 merged it to `main` at 2026-10-07T23:28:22Z, as `f59c109`.

Run from the repository root:

```
$ gh pr view 15 --repo kindspec/blockspec --json mergedAt,mergeCommit -q '.mergedAt+" "+.mergeCommit.oid'
2026-10-07T23:28:22Z f59c109f96b38c888368ab4b6fcbf6ac58628099
```

It is binding, and it supersedes `PRE-REGISTRATION.md` for blockspec#2. The
document is frozen, so its status line is not edited. This entry is the
record.

## 2026-10-08 — §18. Re-review of the harness: findings applied

No arm has run.

### The owner's rulings

The owner ruled on the two questions §16 left open:

- **The commit-order reading is accepted.** Each §9 step lands on `main` as
  one squash commit from its own pull request, and that squash commit is the
  binding §9 commit.
- **The frozen document is not amended for the V-list fact.** §16's
  "A V-list fact" is the record.

### What the re-review found, and the change for each

The re-review looked at blockspec#16 at `281fb4f`.

- **H1, options.** No option may be abbreviated, on the parser or on any
  subcommand, and no option may be given twice. Every check runs on the
  parsed arguments. `aggregate` also checks each Arm 0 and score input's
  pin and bundle sha256 against `ARMS` and `bundles.json`.
- **H2, the validation commit.** It is now derived, not named. `seal` writes
  `results/prereg2/VALIDATION`, which holds only the sealed manifest's
  sha256 and is committed in the validation commit itself (§7.3). The
  validation commit is the one commit in HEAD's history that added
  VALIDATION. A bound run is refused in any of these cases:
  - VALIDATION has changed since that commit, or was added more than once;
  - its sha256 is not 64 hex characters;
  - any later commit touches the harness, `PRE-REGISTRATION-2.md` or
    `ORACLE.md`.

  `bind` is removed. §16's account of VALIDATION naming the validation
  commit, and of `bind`, is superseded.
- **H3, first execution.** "First execution" is now marked by
  `results/prereg2/executed/<cmd>[-<arm>].json`. That file is written only
  once the corpus is opened (for export, once its scored input is), and the
  transcript gains an "# executed:" line at the same moment. So a refused or
  mistyped run leaves its transcript but does not use up the arm.
  `aggregate` counts executed transcripts and their markers.
- **M3, the marker's history.** The marker is looked for in the history of
  every ref as well as in the work tree, so deleting it does not re-enable
  an arm.
- **M1, isolation.** The harness refuses to run without `python3 -I`; its
  shebang is `env -S python3 -I -B`. It never reads a bytecode cache, because
  `sys.pycache_prefix` points at a directory that does not exist. So a
  forged `.pyc` beside a verified D8 source is not loaded.
- **M2, real bundles.** An unbound run never opens a real bundle. Only a
  fixture run reaches a corpus.

**Reading 1 of §16 is amended (H4).** This entry replaces §16's clause
saying "If `p` lies in no unit, the rule has no `t` and the record is
UNDECIDABLE-REPEAT". The amended reading follows §5.2 step 1:

- when `p` lies in no §5.2 unit, `t` is undefined and T is the units that
  are twins of `k`;
- if T is empty, the verdict is decided;
- otherwise step 4's "ctx(t) ≥ 1" cannot hold, and the verdict is
  UNDECIDABLE-REPEAT.

The re-review's case (`scripts/a4case.py`) now comes out decided and WRONG.

**F6's first half.** F6 is "every input state is well-formed" and q4 "no".
The first half is already a condition of export: §7.3 exports only records
with well-formed input states. So it holds for every representative the
aggregator sees, and `aggregate` checks only q4. The code says so.

**If `tier-model` is not run on the start day,** the tierer's model cannot
be chosen, because the listing must carry the start day's `Date`. Then
`tier-run` refuses, no packet is tiered, and the untiered plants void the
tiering (§7.3). Every cell that exported a packet becomes NO VERDICT.

### A correction to §16 and to the pull request's description

Both say that each review fix was shown red first by
`results/prereg2/validation/V3-new-checks-against-312b415.txt`, "20 checks
red". That overstates it:

- 6 of those 20 reds are sections that crashed (`grep -c "^  FAIL  section
  raised"` on that file);
- 2 more are red only because the old aggregator takes a different
  reproduction-result format, not because of the behaviour the check names;
- so 12 are named checks red on their own behaviour;
- only 201 of the 271 checks ran, because the crashed sections' later checks
  never ran.

The re-review gave 8 such reds; counted from the file, they are these 6 and 2.

The new checks for this re-review were run red first against `281fb4f`, and
their transcript states the same counts.

## 2026-10-08 — §19. What the red-first run against `281fb4f` shows

`results/prereg2/validation/V3-new-checks-against-281fb4f.txt` runs V3 as of
`a58727b` against the harness at `281fb4f`, from before §18's fixes. It
prints `250 checks, 4 failed`. Of those four, one is a named check: H4.
The other three are sections that crash on interfaces new since `281fb4f`:
`is_late`, a VALIDATION written by `seal`, and the execution markers. So it
is weak evidence that the new checks are red first.

The evidence per finding is `V4.txt`. Every §18 finding, and every surviving
mutant from the re-review, is a V4 mutant, and V4 reports
`158 mutants: 158 killed, 0 survived, 0 BROKEN`. Each kill names the check
that went red; none is a crash.

## 2026-10-08 — §20. Round-5 review of the harness: findings applied

No arm has run. The round-5 review looked at blockspec#16 at `4de5c56`.

### What the harness checks, and what it does not

The binding is checked by the harness. It is not guaranteed by it. Anyone
who runs the harness can run other code: an edited `binding.py`, or a
program of their own. A forged history also derives a validation commit of
its own, for example an orphan branch carrying its own harness and
VALIDATION.

So the checks stop mistakes and casual shortcuts. The guarantee is a review
step, now in `spike/README.md`: each §9 pull request's review re-derives the
validation commit in a fresh clone, and compares it with every output's
`binding.validation_commit`.

### Corrections to §18 and §19

- **§18, H3.** §18 says "a refused or mistyped run leaves its transcript but
  does not use up the arm". That was not true of every failure.

  `score` created `score/<arm>/` before it opened the corpus. A run whose
  bundle could not be opened (missing, wrong sha256, or an existing work
  repository) therefore left an empty directory, and the next run refused
  on it: "exists; the first execution binds".

  Now `arm0` and `score` create their output only after the execution
  marker is written. The first-execution refusal is keyed on the marker, or
  on a result file, never on a directory. `export` and `tier-run` already
  created their output only after their checks.
- **§19.** §19 says that in V4, "none is a crash". That was false. V4's
  mutant 115 (R1) was killed only by a section crash, which V4 counted as a
  red check.

  Now V4 counts a mutant that only crashes a V3 section, with no named
  check red, as surviving. V3's `one()` turns an evaluation that raises into
  a red named check.

### What changed

- **M-a, the marker.** The execution marker gets a second copy in the
  common git directory, `$(git rev-parse --git-common-dir)/prereg2/executed/`.
  It is looked for in three places:
  - the work tree;
  - that directory;
  - `git log --all --reflog --full-history`.

  So deleting a branch, `rm` or `git clean` of an uncommitted marker, and a
  second worktree each leave the arm refused. A marker reaches only the
  repository it was written in: a fresh clone has no git-directory copy and
  no reflog. That gap is closed by the review step above, not by the
  harness.
- **M-c, the derivation's history.** Every history walk in the derivation
  uses `--full-history`. A shallow repository is refused, as is a history
  rewritten by replace refs or `info/grafts`. Binding git calls run without
  the caller's `GIT_*` variables, without user or system config, and with
  `GIT_NO_REPLACE_OBJECTS=1`.
- **M-d, module loading.** The harness requires `python3 -I -S`, and its
  shebang is `env -S python3 -I -S -B`. It loads the three D8 files by
  explicit path, and takes `--d8-dir` back off `sys.path` once they have
  run. It checks that every harness module's `__file__` is the tracked file
  it names.
- **M-e, §9's gap rule.** This implements the document's rule; it is not a
  reading.
  - A gap is declared in `results/prereg2/gaps.json`. Its red test lives
    under `results/prereg2/gaps/`, outside the harness. Each entry names its
    LOG entry and its cells.
  - An entry is dated by the first commit that carries it.
  - An entry dated at or before the Arm 0 commit is refused: §9 says such a
    gap stops the work.
  - An entry strictly between the Arm 0 commit and the scoring-arm commit
    makes its cells NO VERDICT, and the reason names the gap.
  - An entry at or after the scoring-arm commit alters no cell, and is
    listed.
  - Two choices are this harness's own, not the document's: an entry may
    never be edited or withdrawn once committed, and its LOG entry and red
    test must be committed with it.
- **LOW.**
  - `seal`'s "outside the repository" check now uses the repository's top
    level.
  - Of the 33 round-4 mutants, F6a was dropped on purpose: §18 removed the
    unread well-formedness half of F6 that it mutated.

## 2026-10-08 — §21. Round-6 review: the gap rule's edges, and the validation commit

No arm has run. The round-6 review looked at blockspec#16 at `e563655`. It
found no HIGH and three MEDIUMs. This entry records the changes, and one
correction to §20.

### Gaps after the scoring-arm commit never block a verdict

Before this change, `load_gaps` held every version of `gaps.json` to the
rule. A later version broke it in three ways the review reproduced:

- a typo in a LOG section;
- a reworded `why`;
- JSON that does not parse.

Any of these made the bound `aggregate` refuse for good. Nothing could
repair it, because gaps are immutable and the ruleset forbids rewriting
history. That contradicts §9: "After the scoring-arm commit … no gap claim
… alters any cell."

Now a version of `gaps.json` at or after the scoring-arm commit is never a
reason to refuse. It is listed, whatever it says, malformed included.

The rule is also checked before the end:

- `arm0`, `score`, `export`, `tier-model` and `tier-run` check it in their
  bound preflight, so a breach inside the window shows up while it can
  still be dealt with;
- a gap declared before Arm 0 now stops `arm0` and `score`, not only
  `aggregate`, as §9's "stops the work" says.

### The validation commit adds VALIDATION only

A bound run refuses when the validation commit's diff against its parent
touches `spike/harness`, `PRE-REGISTRATION-2.md` or `ORACLE.md`. The review
showed the case this closes: a validation pull request that also set
`FLOOR = 1` produced a bound NOT FOUND.

The README's fresh-clone review step now:

- runs the same diff;
- re-derives the Arm 0 commit and the scoring-arm commit;
- checks the scoring-arm commit against the one `tier-model.json`
  recorded, so a rebase that backdates a gap is caught.

### A correction to §20: the gap rule has readings

§20 says the gap rule "implements the document's rule; it is not a reading".
The rule is the document's. Where its edges fall, the document does not say,
so these are readings:

- **In the Arm 0 commit itself.** A gap declared there counts as declared
  before Arm 0, so it stops the work.
- **In the scoring-arm commit itself.** A gap declared there counts as
  after scoring, so it alters no cell.
- **Outside the scoring-arm commit's history.** A gap on a side branch
  that is merged only after the scoring-arm commit counts as after, so it
  alters no cell.

### What the gap check does not do

It checks that a gap's red test is committed under
`results/prereg2/gaps/` by the gap's own commit. It does not run the test,
so it does not show the test is red. Running an arbitrary test inside the
harness would make that test part of the harness, which the validation
commit binds. The red state is for the gap's reviewers to confirm.

## 2026-10-08 — §22. Round-7 review: a gap chosen after seeing results

No arm has run. The round-7 review looked at blockspec#16 at `5655248`. It
found one gap in the gap rule, and checks that were missing. This entry
records the changes.

### A gap counts only if every score run saw it

The review's scenario: the scoring arms run on their branch, so their
results are known. A separate gap pull request is then squash-merged to
`main`, and only then the score pull request. The gap's commit lies before
the scoring-arm commit and in its history, so under §21 it made a cell NO
VERDICT. It was chosen with the results in view.

Each score output records `binding.head`, the commit its run executed at.
A gap now counts only if its commit is an ancestor of every score output's
`binding.head`, as well as strictly between the Arm 0 commit and the
scoring-arm commit. Any other gap is listed as "declared after scoring
ran" and alters no cell. A `binding.head` that is missing, or that is not
in the repository, is refused rather than read either way; fetching the
score pull request's head resolves it.

This is a reading. §9 dates a gap by the scoring-arm commit: "Between the
Arm 0 commit and the scoring-arm commit". Under one squash commit per §9
step, that commit lands after the runs it records, so the letter admits a
gap chosen after the results were seen. The reading implements §9's intent,
that no gap claim made with the results in view alters a cell. It is
stricter than the letter: it can only take a gap away, never add one.

It also implies §21's boundary for a gap in the scoring-arm commit itself.
That commit records each run's `binding.head`, so it cannot be an ancestor
of any of them. The separate test for that boundary was removed: no input
could reach it, and V4's mutant of it survived as an equivalent mutant.

### Checks added

- `score` and `export` each refuse a malformed `gaps.json` in their bound
  preflight, and `tier-model` is not blocked by one after the scoring-arm
  commit (its preflight reads the scoring-arm commit, as `aggregate` does).
- The validation-diff refusal is tested for `ORACLE.md` and
  `PRE-REGISTRATION-2.md`, not only the harness, and for a validation
  commit with no parent.

### The fresh-clone review step is a script

The README's review step is now `harness/prereg2_reverify.sh`, committed
with the harness, so the validation commit binds it. It prints PASS or FAIL
for each check, and exits 1 if any failed. V3 runs it on fixture
repositories, and V4 mutates it.

## 2026-10-08 — §23. The validation commit

No arm has run. This entry belongs to the validation pull request, §9's
first commit. That PR's squash commit, the one commit that adds
`results/prereg2/VALIDATION`, is the validation commit.

### The merged harness

blockspec#16 merged as `0dd32dde58ed0dbea6c3575876e51ef24ff5a29e`. That is
the harness this validation binds. Its subject line ends "(do not merge)".
That is the pull request's stale title, carried into the squash; the
history is published and is not rewritten. The pull request's title has
since been corrected.

§9 records the harness's sha here. The validation commit's own sha exists
only once this PR is squash-merged, so it is recorded in the next entry.
The harness it binds is unchanged from `0dd32dd`, and the validation commit
must not change it (`p2/binding.py`, `harness/prereg2_reverify.sh`):

| path | git tree or blob sha at `0dd32dd` |
|---|---|
| `spike/harness` | `cf57ca84e353810fa4c8f34f1c50ac43d10d2f54` |
| `spike/PRE-REGISTRATION-2.md` | `24496a7385ca2748f899f5db7eaea20b9082ec21` |
| `spike/ORACLE.md` | `4a72c84cefbd0a91cd15573caf11a6c3dff2ffe6` |

### The sealed manifest

`prereg2.py seal` drew the nonce and wrote the sealed manifest outside the
repository, at `/home/cam/kindspec-data/prereg2-seal/sealed-manifest.json`,
in a directory of mode 700. Its sha256 is
`11e509133bc2603a3ff3cc64fcfabd5310b7cfe0285ea725bc937a895e299bdb`, and
`results/prereg2/VALIDATION` holds it. §7.3 commits the manifest itself
after `tiers.jsonl`.

The PR also commits two transcripts of `seal`. The first is
`seal --help`, run to check the command's arguments. Every invocation
writes a transcript, so it is kept.

### V steps

V1 to V5 and the bundle check were re-run with this PR's VALIDATION in
place. Their transcripts are in `results/prereg2/validation/`, committed in
this PR, as §9 requires.

## 2026-10-08 — §24. Arm 0

### The validation commit

blockspec#17 merged as `d79bf2e61f5f7c0bcfdde5e17d44604b0fac9301`. It is
the one commit that adds `results/prereg2/VALIDATION`, so it is the
validation commit, and every bound run from here on names it. Its harness
is `0dd32dd`'s, byte for byte (§23). `harness/prereg2_reverify.sh` passed
on a fresh clone of `main` at that commit.

### Before the runs

- All six bundles in `/home/cam/kindspec-data/prereg2-bundles/` matched
  `harness/p2/bundles.json` in sha256 and size. `git bundle list-heads`
  showed each one's only head as its §6.2 pin.
- The work directories were under `/home/cam/kindspec-data/prereg2-arm0-work/`,
  outside every repository, one fresh directory per arm. That disk had
  1.5 TB free.
- `--d8-dir` was kindspec/research `experiments/D8-identity` at
  `d51ce09`, which the harness verifies before it loads anything.
- `arm0 --help` was run once, to check the arguments. It wrote the
  transcript `2026-10-08T170814Z-arm0.txt`, unbound, and was committed
  before the first bound run.

### The runs

`prereg2.py arm0` ran under `python3 -I -S -B`, bound, once for each arm in
§6.2's order: `rust-book`, `obsidian-help`, `cmspec`, `k8s-en`, `k8s-l10n`,
`cncf-toc` and `site-policy`. Each invocation was committed before the
next. Each exited 0, and each transcript records the binding as true with
validation commit `d79bf2e`. No run refused, and none was repeated.

Every arm passes the bar. Under the verdict rule, `yaml-fence`, the share
of distinct natural-language contents (`prose`, `list` and `heading`, per
F5) of 20 characters or more with a twin in the same file was:

| arm | with a twin / distinct | share |
|---|---|---|
| `rust-book` | 0 / 3,524 | 0.00% |
| `obsidian-help` | 10 / 3,909 | 0.26% |
| `cmspec` | 0 / 43 | 0.00% |
| `k8s-en` | 305 / 48,788 | 0.63% |
| `k8s-l10n` | 2,220 / 112,397 | 1.98% |
| `cncf-toc` | 69 / 19,393 | 0.36% |
| `site-policy` | 4 / 2,110 | 0.19% |

Each figure is from `results/prereg2/arm0/<arm>.json`,
`rules.yaml-fence`. `none` and `anywhere` are reported there beside it,
with no verdict.

## 2026-10-09 — §25. The scoring arms

This entry belongs to §9's third commit, the scoring-arm results. Once the
pull request is squash-merged, its squash commit is the scoring-arm commit:
the one commit that adds `results/prereg2/score/`. blockspec#18 merged as
`c5ddbe6`, the Arm 0 commit, and every arm passed Arm 0's bar (§24).

### The runs

`prereg2.py score` ran under `python3 -I -S -B`, bound by validation commit
`d79bf2e`. It ran once for each arm, in §6.2's order, with the default
modes E, S5, S25 and M and §6.5's sample sizes. Each invocation was
committed before the next.

- An unbound `score --help` was run first, to check the arguments, and
  committed.
- The work directories were under `/home/cam/kindspec-data/prereg2-score-work/`.
- The runs went from 2026-10-08T17:13Z to 2026-10-09T11:20Z. Every run
  exited 0. No run refused, and none was repeated.

Per arm, under the verdict rule: instances evaluated / not evaluated /
undecodable (LOG §15). For E and S the sample is from the population given.
Each figure is from `results/prereg2/score/<arm>/status.json`, `counts`.

| arm | E (population) | S5 (population) | S25 | M (kept cases) |
|---|---|---|---|---|
| `rust-book` | 1000/0/0 (3,443) | 500/0/0 (3,146) | 500/0/0 | 118/23/0 (141) |
| `obsidian-help` | 1000/0/0 (1,697) | 500/0/0 (1,098) | 148/0/0 | 3/2/0 (5) |
| `cmspec` | 92/0/0 (92) | 85/0/0 (85) | 62/0/0 | 1/0/0 (1) |
| `k8s-en` | 1097/0/0 (14,082) | 538/0/0 (11,668) | 518/0/0 | 1232/110/0 (1,342) |
| `k8s-l10n` | 1056/0/0 (19,825) | 525/0/1 (9,083) | 500/0/0 | 249/31/0 (280) |
| `cncf-toc` | 1120/0/0 (1,018) | 571/0/0 (665) | 367/0/0 | 17/6/0 (23) |
| `site-policy` | 1000/0/0 (1,578) | 216/0/0 (216) | 2/0/0 | 33/14/0 (47) |

An evaluated count above the sample size is expected. Each rule (`yaml-fence`,
`none`, `anywhere`) draws its own sample of 1,000 or 500, and the union is
evaluated, each instance tagged with the rules whose sample holds it.

### The strict `site-policy` set is empty

§6.2 sets the strict set's rule: exclude an accepted merge whose subject line
contains `automated-sync` or `repo-sync`. It also says: "The first
registration's §5.1 expects 21 cases to remain. If the rule leaves a
different number, the rule's count stands and the difference is logged."

The rule leaves **0**. The difference is −21. The 25-case set, which
excludes `automated-sync` only, also has 0.

Of the 78 merge cases `find_merge_cases()` found, 31 touch a path that is
not selected at the pin. The 25-case count of 0 means each of the 47 that
remain has `automated-sync` in its subject. The 33 that were evaluated
record their subjects in `results/prereg2/score/site-policy/instances.jsonl`,
`meta.subject`, and each has the form
`Merge branch 'main' into automated-sync-<n>`.

This is the rule's count, and it stands. `site-policy` M therefore has no
unit in its verdict cell. The first registration's 21 were counted over all
78 cases, before any path selection. That the 21 fell among the 31 cases
dropped by path selection is a reading of these counts; it was not checked.

## 2026-10-09 — §26. The export

§9's third commit is "scoring-arm results and the export", so the export is
committed in the same pull request as the scoring arms (§25), and both land
in the one squash commit.

`prereg2.py export` ran once, bound by validation commit `d79bf2e`, under
`python3 -I -S -B`. It read the sealed manifest at
`/home/cam/kindspec-data/prereg2-seal/` and exited 0. An unbound
`export --help` was run first, to check the arguments, and committed.

The export is `results/prereg2/export/`. It holds `PROMPT.md` and 486
packets, three of them Appendix B's plants. Each packet is named by the
first 16 hex characters of `sha256(nonce + ":" + key)`. Each packet holds:

- `packet.json`, with only the fields `packet`, `reference_kind`,
  `reference`, `mechanism_target`, `oracle_target`, `files` and
  `questions`;
- `QUESTIONS.md`;
- either `before.md` and `after.md` (436 packets), or `base.md`,
  `leg-a.md`, `leg-c.md` and `after.md` (50 packets).

`results/prereg2/export-manifest.txt`, outside the export, lists the
sha256 of each file.

Checks on the export after the run:

- `p2/export.validate` reports it clean.
- It holds no `.git` and no symlinks, and every packet name is 16 hex
  characters.
- The nonce does not appear anywhere under `results/prereg2/`, whether in
  full, as its first 16 hex characters, or as raw bytes.
- No arm name, corpus or bundle name, plant name, or oracle or resolver
  field appears in `PROMPT.md`, `QUESTIONS.md` or the metadata fields of any
  `packet.json`.
- The corpus texts themselves name their own projects in places, for
  example a `site-policy` link or a `cncf-toc` mailing list. That is the
  file content §7.3 requires.

**Who tiers.** §7.3 says "Whoever ran an arm may not tier." A recorded
owner decision reads this as follows: a fresh agent with no access to the
authoring conversation counts as independent, and the barrier is the export
directory, with no `.git`. The sandboxed tierer sees only the export, so it
meets §7.3.
