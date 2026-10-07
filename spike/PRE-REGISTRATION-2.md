<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Pre-registration 2: does prose admit a silent-wrong under any edit?

**Status: DRAFT, for owner approval.** Here "committed" in the owner's
decision means *merged to `main`*. Nothing under this document runs before it
merges. Once merged, it supersedes `PRE-REGISTRATION.md` for blockspec#2.
`PRE-REGISTRATION.md` and `ORACLE.md` remain unchanged as the record of what
was registered first.

**Citations.** A blockspec path means its content at `d49e7ef3ea20`, and a
`research/` path means kindspec/research at `71d97a1e6f36`, unless another
commit is named. Every figure is followed by the command that produced it,
run from `spike/results/` unless stated.

---

## 0. Choices the owner is approving

The 2026-10-07 decision did not settle these. Approving the draft approves
all of them. To change one, edit the draft before it merges.

1. **Real history only.** FOUND needs a case from a pinned corpus's history (§2). *Alt:* count reachability; the answer is then already FOUND by `plant_cases/single-leg-01`.
2. **SPLIT is an undecidable verdict (§5.2).** It was named after reading `LOG.md` §12, so it is not blind. It disposes of the only two hardened, F5-eligible silent-wrongs the cheap arm printed (see the note below). *Alt:* split cases are decided by TLLC's plurality vote, then tiered blind.
3. **Arm 0 runs first, with a 10% twin-share bar (§6.5).** It is a backstop and is not expected to bind. *Alt:* report Arm 0 with no bar.
4. **The `yaml-fence` generated-file rule, with a hash-ranked sampler (§6.3).** `yaml-fence` excludes a subset of what `anywhere` excludes, so it is the more inclusive rule. *Alt:* FOUND must hold under `none`, `anywhere` and `yaml-fence`.
5. **`k8s-en` and `k8s-l10n` are separate arms (§6.4).** *Alt:* English only.
6. **FOUND needs the hardened policy (F4).** *Alt:* either policy.
7. **FOUND needs a natural-language type: `prose`, `list` or `heading` (F5).** *Alt:* any type.
8. **The cell floor is 300 distinct decided blocks (§6.6).** *Alt:* D8's 50 anchors.
9. **Sample sizes (§6.5):** 1,000 edits per arm for E, 500 pairs per gap per arm for S, and a full census for M. *Alt:* a full census everywhere.
10. **Named references (R) are a second mechanism (§3).** *Alt:* quote anchors (Q) only.
11. **What an overall NOT FOUND needs (§6.7).** Q must reach NOT FOUND in both `k8s-en` and `cncf-toc`, and R must reach it in one of them. If only Q does, the result is "NOT FOUND (Q only)". *Alt:* any one cell is enough.
12. **D8's corpora at D8 §3's pins (§6.2).** *Alt:* `harness/corpora.json`'s pins.
13. **`site-policy` (§6.2).** M can yield FOUND only from the strict set. E and S can yield FOUND, and commits by bot authors count there. *Alt:* the set of 25 for M, or bot commits excluded from E and S.
14. **The first registration's §5 exclusion of single-author and bot-dominated corpora is dropped.** After `LOG.md` §9 the single-author edit is part of the question, and generated *files* are handled by §6.3. *Alt:* keep the exclusion. E would then lose its point.
15. **E and S use TLLC in its one-leg form (§5.1), not D8's `line_oracle`.** One oracle governs every arm. *Alt:* `line_oracle` for E and S, for comparability with D8.
16. **NEAR MISS is narrowed (§4.2).** The frozen rule was "four of five". Here it is a decided mis-resolution that fails exactly one of F4, F5, F7 or F8. *Alt:* the frozen definition carried over unchanged.
17. **The first run's 85 records are not tiered (§7.3).** This reverses `STATE.md` §2 item 2, "tier the candidates, blind". *Alt:* tier them blind as a separate export that carries no verdict.

**The two cases SPLIT disposes of (§0 item 2).** These come from D8's
`line_oracle`, not TLLC, but they have the same shape. `LOG.md` §12
describes each as a block that split in two.

- `k8s-website` gap=1, `content/zh-cn/docs/reference/glossary/cri-o.md`.
  This is hardened and prose-typed, and it appears under `anywhere` only.
- `site-policy` gap=5,
  `Policies/content-removal-policies/github-private-information-removal-policy.md`.
  This is hardened and heading-typed, with two records, and it appears under
  all three rules.

Under the three rules, the hardened silent-wrong lines are these:

- `none`: `html=1` and `heading=2`;
- `anywhere`: `prose=1` and `heading=2`;
- `yaml-fence`: `heading=2` only.

Command, for each of `anchors-no-generated-rule.txt`, `anchors.txt` and
`anchors-yaml-fence-rule.txt` in `cheap-arm/`:
`grep -B4 -E "^ +hard .*SILENT-WRONG .*\(n=[1-9]" <f> | grep -E "^###|^ +hard"`.

## 1. Why this supersedes `PRE-REGISTRATION.md`

The first registration's §8 allows §3, §4 and §6 to change only through a new
pre-registration.

**1.1 FOUND leaves out the shape that was found.** `LOG.md` §9 shows one
author, in one commit, producing a hardened `EXACT` prose silent-wrong
(`plant_cases/single-leg-01`). The frozen §3(5) requires a defect "created by
the merge". Merges are also a small share of editing. The three control
corpora have 195 accepted both-sides cases against 19,337 `.md` paths changed
on one side only. Commands, on `merge-arm.txt`:

- `grep -o "ACCEPTED [0-9]*" merge-arm.txt | awk '{s+=$2}END{print s}'`
  gives 195.
- `grep -o "exactly ONE side: [0-9]*" merge-arm.txt | awk '{s+=$4}END{print s}'`
  gives 19,337.

**1.2 TLLC cannot decide repeated blocks.** `LOG.md` §6.2 and
`harness/oracle_limitation.py` show this. `ORACLE.md` is frozen, so §5 is the
new oracle statement.

**1.3 Neither the unit nor the selection was fixed, and the result moved.**

- **The selection.** D8's sampler is `Random(7).shuffle(files)[:14]`.
  Excluding any file redraws the whole sample. The hardened prose-typed
  silent-wrong count was 0 under `none`, 1 under `anywhere` and 0 under
  `yaml-fence`. Command, per file: `grep -E "^ +hard .*by type:.*prose=" <f> |
  grep -oE "prose=[0-9]+"`, summed (empty is 0).
- **The unit.** Instance counts overstate distinct content. In
  `k8s-website`, 1,524 within-file duplicate prose instances at ≥40
  characters are 481 distinct contents (`sed -n 44p
  cheap-arm/uniqueness-distinct.txt`).

## 2. The question

> **In the real editing history of the pinned corpora, does a prose document
> under stock git come to contain a reference that a mechanism prose would
> need (§3) resolves silently to the wrong target? The result must be a
> well-formed file. The error must be false by an oracle independent of the
> mechanism, and a reader holding only that file must be unable to detect
> it. Any edit counts: one commit (arm E), a span of commits (arm S), or a
> two-parent merge (arm M).**

## 3. The mechanisms

The mechanism code is kindspec/research `experiments/D8-identity/` at
**`d51ce09cdb23`**. `anchor_eval.py`, `anchor_eval2.py` and `anchor_eval3.py`
are byte-identical there and at `f088cd76fd13`, the commit the control arm
imports. They differ at `71d97a1`. Command, in the research checkout:
`git show <c>:experiments/D8-identity/<f> | sha256sum`.

- **Q, the quote anchor.** It is imported unchanged. `anchor_eval.anchor_of`
  builds the anchor and `anchor_eval3.reanchor2` resolves it. This is D8
  §7.3, steps 2 to 5.
- **R, the named reference.** This is D8 §7.2 and §7.3 step 1. It is **new
  harness code**, with two functions **copied verbatim** from `d51ce09`. Both
  source modules run experiments when imported, so they cannot be imported.
  - **Names.** `slugs()` from `e9_headings.py`, lines 8–13, is applied to
    each block that `btype()` types `heading`. Applying it only to those
    blocks keeps `#` lines inside code fences from becoming names. The
    `{#id}` syntax is not used, because D8 §7.2 rejects it.
  - **Region markers.** These use `REGION` and `regions()` from
    `e6_transclude.py`, lines 14 and 17–31. A region marker's target is the block
    after the marker. Begin/end spans have no D8 implementation and are not
    measured.
  - **Resolution.** Region markers are tried first, then slugs. Zero
    matches, or more than one, is `#REF!`, which counts as LOUD.
  - **The target of a slug** is its **section**: the heading block and every
    block up to the next heading of the same or a higher level.
  - **R is correct** iff the resolved section contains TLLC's plurality
    block for the base section (§5.1).
- **Transclusion** is a use of Q and R, not a third resolver. It is judged in
  tiering (§7.2).

Every evaluated block is anchored with Q. Every section or region whose name
resolves uniquely at the before-state is also anchored with R. Q and R are
reported separately.

## 4. FOUND, and NOT FOUND

### 4.1 FOUND: a single record must meet every condition

- **F1. Real history.** The before-state(s) and the edit are commits of a
  pinned corpus (§6.2). The path is in the arm's selection (§6.3). For
  `site-policy` M, the case is in the strict set.
- **F2. Stock git only.** No driver, `.gitattributes`, filter or hook is
  involved.
  - For M, `git merge` in the harness's hermetic repository exits 0, leaves
    no conflict markers, and `git ls-files -u` is empty.
  - For E and S, the committed after-blob comes out byte-identical when it is
    re-expressed through `stock_merge` with leg C set to the base.
- **F3. Well-formed.** Every input state and the result pass
  `fences_balanced`, and D8's `blocks()` yields at least two blocks for each.
  This is the only well-formedness check there is.
- **F4. Wrong under the hardened policy.** The mechanism resolves, not
  LOUD, somewhere other than the oracle's **decided** target. Resolving
  where the oracle says `DELETED` also counts. That case is reported as
  `WRONG_on_deleted`, and labelled weaker (`ORACLE.md` §4).
- **F5. A natural-language block.** For Q, the base block is typed `prose`,
  `list` or `heading` by `btype()`. Blocks inside a leading YAML fence are
  typed `frontmatter`. R targets always pass F5.
- **F6. The edit created it.** Every input state is well-formed, and the
  tierer does not record visible author error (question 4 in §7.2).
- **F7. A reader cannot see it.** The tierer records that the error is not
  visible from the after-file and the reference (question 3).
- **F8. Tier A or B**, by the blind procedure in §7.
- **F9. It reproduces.** A standalone reproduction from the pins, run from
  a clean checkout, regenerates the record byte for byte.

One qualifying distinct block is enough.

### 4.2 NOT FOUND, beyond what F1 to F9 already exclude

- A planted or constructed case.
- A verdict of `UNKNOWN` or `UNDECIDABLE-*` (§5.2).
- A case that qualifies only under a selection rule other than `yaml-fence`.

**NEAR MISS.** A decided record fails exactly one of F4 (it is naive-only),
F5, F7 or F8 (it is tier C or D), and meets every other condition.

## 5. The oracle

This is the superseding oracle statement that `LOG.md` §6.2 and §9 call for.

### 5.1 TLLC, plus its one-leg and section forms

- **TLLC.** The oracle is TLLC as `ORACLE.md` §2 defines it and
  `harness/prose_merge.py` `tllc()` implements it, unmodified. That includes
  `UNKNOWN`, `DELETED` and the fence in `ORACLE.md` §4.
- **The one-leg form, for E and S.** Leg C is the base and the merged text
  is the after-state. Both legs then reduce to one alignment, base to
  after.
- **The section form, for R.** The base unit is the section or region.
  `frac_L` and the plurality vote run over that unit's non-blank lines. The
  plurality vote gives one block of the after-state, and R is graded against
  it (§3).

### 5.2 What it cannot decide

Neither rule reads the mechanism's answer. Both rules run on every
`SURVIVED` verdict before grading. In each, `k` is the base unit, `t` is
TLLC's target and `M` is the after-text.

For Q, the unit is a block. For R, the unit is the section or region, and
"block" below means "section". The R form of each rule is new code. It must
pass V3.

**UNDECIDABLE-REPEAT.**

- **Twins.** A twin is a unit whose content is byte-identical to another
  unit's content in the same text.
- **The twin set.** `T` is the set of units in `M`, other than `t`, that are
  twins of `t` or of `k`. If `T` is empty, the verdict is decided.
- **Context score.** Otherwise, each `c` in `{t} ∪ T` gets a score
  `ctx(c)` from 0 to 2. It counts how many of these two pairs hold:
  - `M[c-1]` is TLLC's target for `B[k-1]`;
  - `M[c+1]` is TLLC's target for `B[k+1]`.

  A pair counts only if three things hold:
  - both of its indices exist (a first or last unit contributes nothing for
    the missing side);
  - the base neighbour has no twin in `B`;
  - its target has no twin in `M`.
- **Decision.** The verdict is decided iff `ctx(t) ≥ 1` and `ctx(t) >
  ctx(c)` for every `c` in `T`. Otherwise it is UNDECIDABLE-REPEAT.

**UNDECIDABLE-SPLIT.** A verdict is UNDECIDABLE-SPLIT when the mapped lines
of `k`, under the proposing leg(s), fall in two or more units of `M`.

**Counting.**

- A distinct unit (§6.1) is **decided** if any of its instances is decided.
  `SURVIVED`-decided and `DELETED` both count as decided.
- A distinct unit is **undecidable** if no instance is decided and at least
  one is `UNDECIDABLE-*`.
- A unit whose every instance is `UNKNOWN` is counted as `UNKNOWN`.
- A qualifying record must be a decided instance.
- Undecidable and `UNKNOWN` counts are reported per cell, in instances and
  in distinct units. They never enter a rate, a pass or a find.

TLLC decides descent, not falsity (`ORACLE.md` §5). Falsity is settled by
tiering (§7).

## 6. Units, corpora, selection, sampling, floors

### 6.1 Unit

The distinct authored unit is keyed as follows:

- a Q block: `(arm, sha256(block content))`;
- an R unit: `(arm, name, sha256(unit content))`.

Every verdict, floor and published rate counts distinct units. Instance
counts may appear beside them, labelled as instances.

### 6.2 Corpora and pins

| arm | source | pin | pathspec |
|---|---|---|---|
| `rust-book` | rust-lang/book | `1500248d8f230566e4ec9f27fcbb8fe9e2898ab1` | `src/*.md` |
| `obsidian-help` | obsidianmd/obsidian-help | `327a782e90481268361b5ccccdb0c224b2b13fe6` | `en/*.md` |
| `cmspec` | commonmark/commonmark-spec | `3da939428d80f146f270cd1765e4ba462e96bb1b` | `*.md` |
| `k8s-en` | kubernetes/website | `6b27baef1e44275fd4368e14375296e1dfe5af11` | `content/en/*.md` |
| `k8s-l10n` | kubernetes/website | same | `content/*.md :(exclude)content/en/` |
| `cncf-toc` | cncf/toc | `144c2e3215884e498e744cc51e6b7cef82d654f1` | `*.md :(exclude).github/` |
| `site-policy` | github/site-policy | `b9578b546d2506febda1da2cd7431644d58e512c` | `*.md :(exclude).github/` |

- **Where the pins come from.** The D8 rows use D8 §3's pins, where the
  research artifacts reproduce (`cheap-arm/validation.txt`). The others use
  the first registration's §5.1 pins.
- **`harness/corpora.json`'s pins** serve only V1 and V2.
- **An unreachable pin** makes its arm NO VERDICT. No substitute is used.

**The strict `site-policy` set (M only).** An accepted merge is excluded when
its subject line, `git log -1 --format=%s <merge>`, contains `automated-sync`
or `repo-sync` as a case-sensitive substring. The first registration's §5.1
expects this to leave 21 cases. If the rule gives a different count, the
rule's count stands and the difference is logged. The set of 25 (excluding
`automated-sync` only) is reported beside it and is not verdict-bearing. In
E and S, every commit counts, whoever authored it, and the author is
recorded.

### 6.3 Selection and sampling

**Generated files.** A file is excluded when its leading YAML fence matches
`^auto_generated:[ \t]*true[ \t]*$` (multiline, case-insensitive), or when
its text contains `THIS FILE IS AUTO-GENERATED`. This is `d8_cheap_arm.py
--generated-rule yaml-fence`, evaluated at the pin.

- **Why this rule.** A file declares its provenance in its own metadata. The
  same key inside an HTML comment is a quotation of another file's
  metadata.
- **The disclosure.** `yaml-fence` printed 0 in §1.3. That 0 does not come
  from excluding the file behind the 1. `cri-o.md` is in neither excluded
  list: `grep -c cri-o cheap-arm/selection.txt
  cheap-arm/selection-yaml-fence-rule.txt` gives 0 and 0. The record
  disappeared because the sample was redrawn.
- **The other rules.** `none` and `anywhere` are reported beside it and
  carry no verdict.

**The sampler.**

- **Ranking.** A population is ranked by `sha256("prereg2:" + arm + ":" +
  key)`, and the sample is the *k* lowest. The key is `commit:path` for E and
  `path:i:gap` for S.
- **Stability.** Excluding an unselected item cannot change the sample.
- **What has not been done.** No ranking was computed before this merged,
  and the salt `prereg2` was not varied.
- **Packet order.** The export (§7.3) is ordered by `sha256("prereg2-export:"
  + packet key)`.

No other randomness is used.

### 6.4 Translations

- **Separate arms.** `k8s-en` and `k8s-l10n` are never pooled.
- **What the per-arm key does not do.** It does not stop a translated
  paragraph from counting once per language. Each translation has different
  bytes (`LOG.md` §12), so `k8s-l10n`'s distinct counts are per
  (language, content).
- **Reporting.** The per-language breakdown is reported. Rates from
  `k8s-l10n` are labelled this way.
- **FOUND.** A translation is authored text, so FOUND from `k8s-l10n`
  stands.

### 6.5 Arms, in order

**Arm 0, the census of oracle reach.** It runs at each pin over the whole
selection. It counts:

- blocks under 20 characters, which are excluded because the mechanism skips
  them (`skip:short_quote`);
- distinct contents of 20 characters or more;
- those contents that have a within-file twin;
- of those, the single-line twins and the adjacent-run twins.

Every count is broken down by type.

**The bar.** If more than 10% of an arm's distinct natural-language contents
of 20 characters or more have a within-file twin, that arm does not run under
this document. It reports **NO VERDICT (oracle reach)**.

The bar is a backstop and is not expected to bind. Under `yaml-fence` at 20
characters or more, the largest share in any committed output is `list` in
`k8s-website` (all languages): 854 of 21,830, or 3.9%. Prose there is 1,283
of 113,275, or 1.1%. Commands, using `uniqueness-distinct-yaml-fence-rule.txt`
(lines 5–35):

    awk 'NR<=36&&/^###/{a=$2} NR<=36&&/^(heading|list|prose) /{print NR,a,$1,$(NF-1)"/"$(NF-2)}'

No committed output separates `k8s-l10n`.

**Arm E, single commits.**

- **Population.** `(commit, path)` pairs where the commit is a non-merge
  (`git rev-list --no-merges <pin>`), the path is in the selection at the
  pin, and the commit modifies the path against its parent (`--no-renames`).
  Adds, deletes and renames are counted and excluded.
- **Sample.** 1,000 pairs per arm, or the whole population if smaller.
- **Blocks.** All blocks are evaluated.

**Arm S, spans of commits.**

- **History.** Per selected path, `git log --format=%H --reverse -- <path>`
  at the pin.
- **Pairs.** `(cs[i], cs[i+gap])` for gaps 5 and 25, where both blobs exist
  and differ.
- **Sample.** 500 pairs per gap per arm.
- **Blocks.** All blocks are evaluated.

**Arm M, merges.**

- **Census.** All merges at the pin.
- **Enumerator.** `find_merge_cases`'s enumeration and drop counters are
  kept, and convergent edits stay out (`LOG.md` §7).
- **New code.** The committed function filters on a path prefix. This arm
  needs a **new pathspec-aware filter** that applies §6.2's pathspec and
  §6.3's rule, and it must pass V3.

**Cells.** A cell is an arm, crossed with one of E, S5, S25 or M, crossed
with Q or R.

### 6.6 Cell verdicts

- **FOUND.** At least one record meets F1 to F9.
- **NOT FOUND.** No record qualifies, and all of these hold:
  - the arm passed Arm 0;
  - at least **300** distinct decided natural-language units;
  - distinct undecidable units are at most 10% of decided plus undecidable.

  A NOT FOUND reports the actual *n* and the bound it supports, 3/*n* at 95%
  (the rule of three). In the large arms the floor is expected to be
  non-binding, so the *n* is the content of the result.
- **NO VERDICT, with its reason.** Every other case. It is never reported
  as zero.

### 6.7 Overall verdict

- **FOUND** if any cell is FOUND.
- **NOT FOUND** if no cell is FOUND and both of these hold:
  - for Q, `k8s-en` and `cncf-toc` each have a NOT FOUND cell in E, S5 or
    S25;
  - for R, at least one of those two arms has a NOT FOUND cell.
- **NOT FOUND (Q only)** if the Q condition holds and the R condition does
  not.
- **NEAR MISS** if the NOT FOUND conditions hold and at least one near miss
  exists (§4.2).
- **INCONCLUSIVE** otherwise.

## 7. Severity, and blind tiering

### 7.1 Tiers, unchanged from the first registration's §4

| tier | shape | qualifies |
|---|---|---|
| **A** | A derived or transcluded value or passage in the result is wrong: a count, an index, a transcluded figure, or transcluded prose that silently resolves to different content than it did before the edit | yes |
| **B** | A reference resolves silently to the wrong target, and the reference carries an assertion about that target | yes |
| **C** | A reference resolves silently to the wrong target, and nothing asserted becomes false | **no**: report it, do not build on it |
| **D** | Content is reordered, duplicated or dropped in a way the authors would reject, but nothing asserts anything false | **no** |
| **E** | The merge conflicts, or the reader refuses the file | **no** |

- **When.** A tier is assigned from these definitions, before the frequency
  is known, by someone who has not seen it.
- **Unplaceable.** A record that cannot be placed is UNPLACEABLE, which is
  not a finding.
- **Revision.** After the join, a tier changes only through a **second blind
  tierer** who receives the same packet and the same prompt (Appendix A).
  The second tier replaces the first only if it is lower. No other revision
  is allowed.

### 7.2 The four questions

Every record is a hypothetical reference, so the tierer answers four
questions:

1. **Assertion use.** Would an assertion true of the oracle's target be
   false, or change a reader's action, about the mechanism's target?
2. **Transclusion use.** Would rendering the mechanism's target instead of
   the oracle's change what the document says?
3. **Visibility (F7).** Could a reader holding only the after-file and the
   reference tell?
4. **Author error (F6).** Is this explained by an author error visible in
   the file?

**The tier** is A if question 2 is yes. Otherwise it is B if question 1 is
yes. Otherwise it is C.

### 7.3 The procedure

**The export.** One packet is exported per distinct (unit, mechanism target,
oracle target) among records that meet all of these:

- they are decided mis-resolutions under the **hardened** policy;
- they meet F1 to F5;
- their input states are well-formed.

Naive-only records and records outside F5 are not exported. They are
reported as near misses, untiered.

**What a packet holds:**

- the before-file(s), the after-file and, for M, both legs;
- the reference (the quote selector or the name);
- the mechanism status;
- the text of both targets;
- §7.1, §7.2 and Appendix A.

**What a packet leaves out:** counts, rates, denominators, sharing
information, other records, totals, the corpus, and `LOG.md`. The order and
names come from §6.3's export hash. A committed validator fails any packet
that carries a field outside an allow-list.

**Planted packets.** The export mixes in planted packets, named and ordered
the same way as real ones:

| packet | expected tier | why |
|---|---|---|
| `single-leg-01` | **A** | Transcluding the appendix shows the superseded wording. |
| two proposals, each with the same status line ("Status: approved by TOC vote."), where the anchor lands on the other proposal's line | **B** | The text is identical, so question 2 is no, but an assertion about the approval moves to the wrong proposal. |
| a sentence repeated byte-identically within one paragraph group, with the mechanism landing on the other copy | **C** | Nothing becomes false under either use. |

**If any planted packet gets a different tier, the tiering is void and every
cell is NO VERDICT.** The plants are built and committed with V3. They are
identified in a sealed manifest whose sha256 is committed before tiering.

**The tierer** runs **exactly once**, and the first `tiers.jsonl` it writes
is binding. A packet it leaves untiered is UNPLACEABLE, and no rerun
happens.

- **Who.** The tierer is a fresh agent of whatever kind the harness
  provides. Its model and identity are logged.
- **What it gets.** No authoring conversation. It works in a directory that
  holds only the export, with no blockspec checkout. That is the filesystem
  barrier in org contract §2.1.
- **The network barrier is honour-system.** The prompt forbids access to
  kindspec repositories, and nothing enforces it.
- **The output.** `tiers.jsonl` is committed as written, before any join.
- **The log.** `LOG.md` records the export manifest (each file's sha256 and
  the packet count, which the tierer can see), Appendix A as sent, the date,
  the agent and model, and the commit.

Whoever ran an arm may not tier. The first run's 85 records are not tiered
(§0 item 17). Arm M here runs at D8 §3's pins, which differ from the first
run's for `rust-book` and `obsidian-help` (`harness/corpora.json`), so it
does not regenerate that population.

## 8. Outcomes

The first registration's §6 stands, and both directions are deliverables.
What changes:

- **FOUND.** The reproduction gives the frequency per cell, as distinct
  qualifying units over distinct decided units, with the undecidable counts
  beside it. blockspec then proceeds to blockspec#3, #4 and #5.
- **NOT FOUND.** This requires both Q and R. A finding is published: prose
  does not earn a format under these mechanisms. It gives each cell's *n*
  and its bound, Arm 0's sub-20 count, and every undecidable count. The
  repository says it is not being built. This goes to the owner before
  publication (org contract §7).
- **NOT FOUND (Q only).** It is published as a finding about quote anchors.
  Named references are listed as unmeasured, blockspec#2 stays open for R,
  and there is no "not being built" statement.
- **NEAR MISS.** Published as NOT FOUND, with the near misses described.
- **INCONCLUSIVE.** Published with the cells that lacked coverage.
  blockspec#2 stays open, and nothing is built (`DESIGN-BRIEF.md` §2).

## 9. Validation, and the order of work

Each step's transcript is committed under `results/prereg2/` before the next
step starts.

- **V1.** The control gate (`run_control.sh`, then `check_control_gate.py`)
  passes at `corpora.json`'s pins.
- **V2.** Each of these regenerates **byte-identically**, checked by `cmp`
  and sha256:
  - `results/control-arm.txt`;
  - `results/merge-arm.txt` and `merge-arm-candidates.jsonl`, using
    `spike/README.md`'s command at `corpora.json`'s pins;
  - research's `results-e4.txt` and `results-anchor3.txt` at D8 §3's pins;
  - all of `results/cheap-arm/`, using `run_cheap_arm.sh`.
- **V3.** Every new component goes red on a planted case and on an empty
  input. At minimum:
  - **REPEAT.** `oracle_limitation.py`'s case comes out UNDECIDABLE-REPEAT.
    A planted case with two identical multi-line paragraphs in different
    contexts, one of them edited, comes out decided and `WRONG`.
  - **REPEAT and SPLIT on the existing plants.** `wrong-01`,
    `single-leg-01` and `clean-01` keep their committed verdicts and stay
    decided.
  - **SPLIT.** A planted paragraph split in two comes out UNDECIDABLE-SPLIT.
  - **The section forms of REPEAT and SPLIT.** Each has a planted case of
    its own.
  - **R.**
    - A heading renamed onto another section's name comes out decided and
      `WRONG`.
    - A vanished name gives `#REF!`, and so does a duplicated name.
    - A `#` line inside a code fence is not a name.
    - The copied `slugs()` and `regions()` are byte-identical to their
      source lines at `d51ce09`.
  - **Arm E and Arm S.** A repository holding `single-leg-01` as one commit
    yields that record. An empty repository exits non-zero.
  - **The M filter and §6.3's rule.** A generated key in the file's own
    fence excludes the file. The same key in an HTML comment does not.
  - **The sampler.** Removing an unselected item leaves the sample
    byte-identical.
  - **Distinct counting.** A duplicate counts once.
  - **The decided rule.** One decided instance plus one undecidable instance
    counts as decided.
  - **The floor.** 299 gives NO VERDICT, 300 gives NOT FOUND, and an empty
    cell gives NO VERDICT, never zero.
  - **The Arm 0 bar.** A planted corpus over 10% stops its arm.
  - **The export validator.** A packet that carries a count fails it.
  - **The planted-packet check.** A misplaced plant voids the tiering.
  - **The aggregator.** Empty input gives no verdict and exits non-zero.
- **V4.** A mutation sweep over the new gates, in `armed_check.sh` style.
  Hashes are taken before and after each mutation, and a mutation that does
  not apply is reported as BROKEN, never as survived.
- **V5.** `armed_check.sh`, `--selftest-selection`,
  `selection_guard_red.sh` and `oracle_limitation.py` stay green and armed.

**The commit order** is a sequence of separate commits:

1. validation;
2. Arm 0's results;
3. the scoring arms' results and the export, with the sealed manifest of the
   planted packets;
4. `tiers.jsonl`;
5. the join and the verdict.

**The stop rule.** Sometimes the harness cannot implement a definition here
as written.

- **Before Arm 0's results are committed,** the work stops and the gap goes
  to the owner, who may approve a superseding pre-registration. No arm runs
  in the meantime.
- **After that commit,** a gap found then makes the affected cells NO
  VERDICT; it is not grounds to supersede.

No definition is reinterpreted, at either stage.

## 10. Amendment rules

**Frozen when this merges:** §0, §2 to §8, §9's commit order and stop rule,
§10 itself, and Appendix A.

- **A frozen section that is wrong** is replaced by a further
  pre-registration, not edited. Any later pre-registration cannot change the
  verdict computed under this one, and that verdict is published first.
- **§1 and the V-list in §9** may be corrected only where they are wrong
  about a fact. Each correction is logged below with the original wording.
- **Pins never change.**

Edits made while this is a draft PR are not amendments.

| date | section | change, with the original wording | reason |
|---|---|---|---|

## Appendix A — the tierer's prompt, verbatim

> You are tiering records for an experiment. Work only with the files in
> this directory. Do not open, search for, or fetch any kindspec repository,
> issue or pull request, locally or over the network. Do not ask how many
> records exist elsewhere or how often anything occurs.
>
> Each packet describes one hypothetical reference: a quote anchor or a
> name, taken against a "before" file and resolved against an "after" file.
> The packet gives the target the mechanism resolved to and the target an
> independent oracle says is correct. They differ. Read the tier
> definitions and the four questions included in each packet (§7.1, §7.2).
>
> For every packet, answer the four questions from the files alone, and
> assign a tier: A if question 2 is yes, otherwise B if question 1 is yes,
> otherwise C. If you cannot place a packet from the definitions, record
> UNPLACEABLE with your reasoning. Do not invent a tier.
>
> Write one JSON object per line to `tiers.jsonl`, in any order:
> `{"packet": <name>, "q1": "yes"|"no", "q2": "yes"|"no",
> "q3_visible": "yes"|"no", "q4_author_error": "yes"|"no",
> "tier": "A"|"B"|"C"|"UNPLACEABLE", "why": <one line>}`.
> Write each line when you decide it. Do not revise a line once written.
> When every packet has a line, stop.
