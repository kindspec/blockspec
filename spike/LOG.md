<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Spike log — blockspec#2

Append-only. Entries are written at the moment of the work, not reconstructed
for a write-up (`PRE-REGISTRATION.md` §4.1).

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

## 1. Corpus pins — and the discovery that D8's run is recent

`harness/corpora.json`. `D8-identity.md`'s header states a commit count per
corpus. For each, the commit on the first-parent chain at which
`git rev-list --count HEAD` equals that number:

| corpus | pin | count | D8 states |
|---|---|---|---|
| rust-book | `917544888a55e4da7109bdba8c88c893c0da70f4` | 6286 | 6,286 |
| obsidian-help | `a3985b585904ddb9f109bd80849b378085308c15` | 2623 | 2,623 |
| cmspec | `3da939428d80f146f270cd1765e4ba462e96bb1b` | 1848 | 1,848 |

All three matched exactly. The pins date to **2026-07 / 2026-08 / 2026-04**, so
D8's run is weeks old, not a year — the experiment files' mtimes (2025-08-28)
are misleading and should not be used to date it. Anyone re-running D8 should
pin, not clone at HEAD.

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
printed per-arm prose counts. §1's premise for distrusting it does not hold.

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

A first coordinator instruction gave the gate as "the hardened policy at 0.00%
silent-wrong across all five arms". That form is false at both pins and
contradicts D8 §3.2's own table, which prints hardened silent-wrong at 0.12%
(n=1, code) and 1.00% (n=2, code) for rust-book and 0.26% (n=1, list) for
obsidian-help — i.e. it fails on the strongest control. The zero applies to the
**prose-typed count**, not to the total. The gate as built asserts the true form,
and a subsequent coordinator correction independently arrived at the same
wording. No change to the harness was needed.

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

The two fixtures started out differing in more than one variable. Making them a
minimal pair produced the mechanism, which is sharper than the hypothesis
`ORACLE.md` §6 was written with:

> **A near-duplicate alone is not a silent-wrong merge.** With the anchored block
> intact, the mechanism sees two exact matches and disambiguates on prefix/suffix
> context — correctly. The defect needs **both legs to act**: one editing the
> anchored block *out of the exact-match set*, one resurrecting its old bytes.
> That is precisely why a single-leg rebase cannot reach it, and it is a stronger
> statement of §2.1's gap than "nobody ran the concurrent case".

Recorded at the moment it was found: the first draft of `clean-01` was mutated to
add a duplicate and the gate **stayed green**. The harness was right and the
mutation was wrong. See `results/armed-check.txt` mutation 5 for the corrected
form.

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

Both were found by output that looked wrong, not by review.

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

## 6. Merge arm — coverage, not a verdict

`results/merge-arm.txt`, candidates in `results/merge-arm-candidates.jsonl`.

Cases are real 2-parent merge commits with a single merge-base where the same
`.md` changed on **both** sides.

| corpus | file-merges | criss-cross skipped | clean | conflicted (tier E) | oracle-confident | distinct base blocks |
|---|---|---|---|---|---|---|
| rust-book | 179 | 3 | 147 | 32 | 11706 / 12230 (96%) | 6651 |
| obsidian-help | 15 | 2 | 9 | 6 | 182 / 189 (96%) | 304 |
| cmspec | 1 | 0 | 1 | 0 | 57 / 62 (92%) | 73 |

Mis-resolutions, **all `tier: UNASSIGNED`**:

```
rust-book   naive  n=64  code=41 heading=4 html=8 list=1 prose=10
            hard   n=21  code=13 heading=1               prose=7
obsidian-help / cmspec: n=0 in both policies
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
**clean merges that broke well-formedness: 0** across all 157.

### 6.2 A named limitation of TLLC, found by running it

`ORACLE.md` §4 and §5 named two limitations in advance. This is a third, found by
use and **not** fixed, because `ORACLE.md` says nothing in it may be adjusted in
light of a result:

> For a **single-line block whose text repeats many times in one file**, TLLC
> accepts a leg's proposal on the strength of one mapped line, with no margin
> test and no corroboration. `difflib`'s alignment can legitimately pair base
> occurrence *i* with leg occurrence *j*. The oracle has no way to notice.

This is separate from the parser desynchronisation above and would survive
fixing it. The candidates in §6.1 are excluded by §3(5) on their own, so nothing
currently reported depends on this — but **any future arm containing short,
highly repeated blocks needs a stronger oracle before its prose numbers can be
believed**, and the duplicate-heavy corpora §5 calls for are exactly that shape.
Fixing it means a second oracle statement, not an edit to this one.

## 7. Coverage actually obtained, stated as §7 requires

- Two-branch three-way merges are **rare** in these corpora: 195 (file, merge)
  cases from 1,821 two-parent merge commits, and only 16 outside rust-book.
  cmspec contributes one. Any frequency from the merge arm rests almost entirely
  on rust-book.
- 5 criss-cross merges (more than one merge-base) were **skipped**, not resolved.
- 38 of 195 reconstructions conflicted and are tier E — counted, not scored.
- Excluded population: everything not a `.md` file changed on both sides of a
  two-parent merge; every merge with >1 base; the whole of §5's duplicate-heavy
  arm.
- The oracle's confident subset is 96% / 96% / 92%, much higher than the rebase
  arm's 92% / 74% / 38%, because two legs corroborate. That is a property of the
  oracle, not evidence about merging.

## 8. Open, and it is the deciding question for the next step

The planted case proves the shape in `ORACLE.md` §6 is **reachable** — clean
stock-git merge, well-formed output, prose block, `EXACT` status, hardened policy
never engaging. The corpus arm has **not** found it occurring naturally in
technical documentation in English, which is what D8 already predicted and what
§1 registered as the honest prior.

That is exactly the boundary `PRE-REGISTRATION.md` §2.2 draws, and it is where
the next arm goes. It does not have a verdict attached, and it must not get one
from this file.
