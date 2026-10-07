<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Pre-registration 2: does prose admit a silent-wrong under any edit?

**Status: DRAFT, for owner approval.** It binds when it merges, and then
supersedes `PRE-REGISTRATION.md` for blockspec#2. Until then it decides
nothing. `PRE-REGISTRATION.md` and `ORACLE.md` stay unchanged as the record of
what was registered first. This document does not edit them. It replaces them
going forward and gives its reasons in §1.

The owner decided on 2026-10-07 to write this before blockspec#2 runs. No arm
under this document has run. It cites figures from runs under the first one,
and each figure gives its source.

**Citations.** A blockspec path means its content at `d49e7ef3ea20`. A
`research/` path means kindspec/research at `71d97a1e6f36`. Any other commit
is named where it is used.

---

## 0. Choices the owner is approving

The 2026-10-07 decision did not settle these. Each one is a choice made in
this draft, and the alternative is given beside it. Approving the draft
approves all of them. To change one, edit the draft before it merges.

1. **The question is about real history.** FOUND needs a case from the real
   history of a pinned corpus. Constructed cases show only that the shape
   *can* happen (§2). *Alternative:* count reachability. Then the answer is
   already FOUND through `harness/plant_cases/single-leg-01`, and nothing
   needs to run.
2. **Two new oracle verdicts, REPEAT and SPLIT (§5.2).** Neither counts as a
   pass or as a find. SPLIT was named *after* reading `LOG.md` §12, where two
   of the three silent-wrong blocks are splits, so it is not blind. It is
   disclosed here for that reason. *Alternative:* no SPLIT rule, and the
   blind tierer judges split cases as tier C or worse.
3. **Arm 0 runs first and can stop a cell (§6.5).** If more than 10% of a
   cell's distinct blocks have a byte-identical twin within their file, that
   cell does not run under this document. *Alternative:* report Arm 0
   without a bar.
4. **Selection rule: `yaml-fence`, with sampling that does not shift (§6.3).**
   FOUND must hold under `yaml-fence`. `none` and `anywhere` are reported
   beside it. *Alternative:* require FOUND under all three rules.
5. **Translations get their own arm (§6.4).** `k8s-en` and `k8s-l10n` are
   separate and never pooled. *Alternative:* English only, which drops the
   i18n shape that §5.1 chose this corpus for.
6. **FOUND needs the hardened policy (F4).** A silent-wrong under the naive
   policy only is a near miss. *Alternative:* either policy counts.
7. **Natural-language blocks only (F5).** FOUND needs the anchored block to be
   typed `prose`, `list` or `heading`. *Alternative:* any type, which is how
   the first registration's §3 reads literally.
8. **A floor of 300 (§6.6).** NOT FOUND in a cell needs at least 300 distinct
   decided blocks. *Alternative:* D8's floor of 50 oracle-confident anchors.
9. **Sample sizes (§6.5).** E takes 1,000 edits per cell, S takes 500 pairs
   per gap per cell, and M is a full census. *Alternative:* a full census
   everywhere.
10. **Named references are a second mechanism (§3).** Heading slugs and region
    markers resolve per D8 §7.2. *Alternative:* quote anchors only, and a NOT
    FOUND would then cover quote anchors only.
11. **What NOT FOUND needs overall (§6.7).** The quote mechanism must reach a
    cell verdict in both `k8s-en` and `cncf-toc`. Otherwise the result is
    INCONCLUSIVE. *Alternative:* a verdict in any one cell is enough.
12. **D8's corpora at D8 §3's pins (§6.2), not `harness/corpora.json`'s pins.**
    *Alternative:* `corpora.json`'s pins, which reproduce an earlier pass that
    was never committed.
13. **`site-policy` merges (§6.2).** FOUND comes only from the strict set of
    21 cases. *Alternative:* the set of 25.

## 1. Why this supersedes `PRE-REGISTRATION.md`

The first registration's §8 allows changes to §3, §4 and §6 only through a new
pre-registration that says why. There are three reasons.

**1.1 The FOUND criteria leave out the shape that was found.** `LOG.md` §9
shows that one author, in one commit and with no merge, produces a hardened
`EXACT` prose silent-wrong (`harness/plant_cases/single-leg-01`). The first
registration's §3(5) asks for a defect "created by the merge". This shape has
no merge, so it falls outside FOUND. Changing that means changing §3. The
merge is also a small share of the editing. Across the three control corpora
there are 195 accepted both-sides cases and 19,337 `.md` paths changed on
exactly one side, which is about 1% (`LOG.md` §7; `results/merge-arm.txt`). A
question limited to merges looks at about 1% of the editing.

**1.2 The oracle cannot decide the shape the duplicate-heavy arm is made of.**
`LOG.md` §6.2 and `harness/oracle_limitation.py` (`results/oracle-limitation.txt`)
show TLLC answering `SURVIVED` with full confidence when a single-line block
is repeated, and in that case the truth cannot be decided. `ORACLE.md` is
frozen, so the fix has to be a new oracle statement. §5 of this document is
that statement.

**1.3 The unit and the selection were not fixed, and the result moved with
them.** `LOG.md` §12.1 ran D8's anchor arm under three generated-file rules.
The number of hardened, prose-typed silent-wrongs was 0 under `none`, 1 under
`anywhere` and 0 under `yaml-fence`. The rule changes which human-authored
files D8's `Random(7).shuffle(files)[:14]` draws. Instance counts also
overstate distinct content: in `k8s-website`, 1,524 within-file duplicate
prose instances at ≥40 characters are 481 distinct contents
(`results/cheap-arm/uniqueness-distinct.txt`). §6 fixes the unit, the rule
and the sampler before anything runs.

**Carried over unchanged:** tiers A to E and their wording (§7.1), the
principles of the first registration's §4.1, its outcomes (§8), its method
constraints in §7, and the control gate.

**Dropped:** the first registration's §5 excluded "predominantly
single-author" corpora because the concurrent case was what it tested. After
§1.1 the single-author case is part of the question, so that exclusion no
longer applies.

## 2. The question

> **In the real editing history of the pinned corpora, does a prose document
> under stock git end up as a well-formed file in which a reference, resolved
> by a mechanism prose would need, silently asserts something false — false
> by an oracle independent of the mechanism, and undetectable by a reader
> holding only that file — through any edit: one author in one commit, a
> span of commits, or a two-parent merge?**

**What changed from the first registration's §3:**

- **"Created by the merge" becomes "created by the edit".** The edit may be a
  single commit (arm E), a span of commits (arm S) or a merge (arm M). This
  is the change §1.1 requires.
- **"Asserts something false" is tied to named mechanisms (§3)**, each of
  which resolves a reference to a target.
- **Real history, stated outright.** The first registration and `LOG.md` §8
  already worked this way: planted cases validate the harness, and occurrence
  is the open question. `single-leg-01` already shows that the shape can
  happen, so asking only whether it can happen would decide nothing (§0
  item 1).

## 3. The mechanisms under test

These are the mechanisms `research/design-findings/D8-identity.md` §7 would
give prose. Each is imported from `kindspec/research`, never reimplemented.

- **Q, the quote anchor.** `anchor_eval.anchor_of` builds a record over a
  block, and `anchor_eval3.reanchor2` resolves it. This is the cascade in D8
  §7.3, steps 2 to 5. The harness already measures it.
- **R, the named reference.** This is D8 §7.2 and §7.3 step 1. A region
  marker `<!-- #name -->` is tried first, then a heading slug. Zero matches
  or more than one gives `#REF!`, which counts as LOUD. The slug is fixed
  now:
  - An explicit `{#id}` at the end of a heading line is the name.
  - Otherwise the name is the heading text with surrounding whitespace
    stripped and lowercased. Every character that is not a Unicode letter, a
    digit, a space, `-` or `_` is removed, and each space becomes `-`.

  This is blockspec's candidate rule, not any corpus's renderer. A Hugo
  `-1` suffix is not applied. A duplicate name is `#REF!`. The target of a
  name is its **section**: the heading block plus every block up to the next
  heading of the same or a higher level. For a region marker, the target is
  the next block, or the span between a `:begin` and its `:end`.
- **Transclusion is a use of Q and R, not a third resolver.** D8 §8 gives it
  the same address grammar and resolution order. Its severity is judged in
  tiering (§7.2). A transcluded passage that silently re-resolves stays in
  tier A, as the first registration's §4 placed it.

Every evaluated block is anchored with Q. Every block that a name resolves to
uniquely at the before-state is also anchored with R. Results for Q and R are
reported separately.

## 4. FOUND, and what is NOT FOUND

### 4.1 FOUND: every one of these must hold for a single record

- **F1. Real history.** The before-state(s) and the edit are commits of a
  pinned corpus (§6.2), and the path is in the cell's selection (§6.3).
- **F2. Stock git only.** No merge driver, no `.gitattributes`, no
  clean/smudge filter and no hook.
  - For M, `git merge` in the harness's hermetic repository exits 0, leaves no
    conflict marker, and `git ls-files -u` is empty.
  - For E and S, the after-state is the committed blob. It is re-expressed
    through the same `stock_merge` path, with leg C equal to the base, and the
    result is byte-identical.
- **F3. Well-formed.** Every input state and the result pass
  `fences_balanced`, and D8's `blocks()` yields at least 2 blocks for each.
  That is the only well-formedness check the harness has, and nothing
  stronger is claimed for it.
- **F4. False by the oracle, under the hardened policy.** The mechanism
  resolves without a LOUD refusal to a block other than the oracle's
  **decided** target (§5). It also counts if the mechanism resolves at all
  where the oracle says `DELETED`. That variant is reported as
  `WRONG_on_deleted` and labelled weaker, as `ORACLE.md` §4 requires.
- **F5. A natural-language block.** For Q, the anchored base block is typed
  `prose`, `list` or `heading` by D8's `btype()`. Blocks inside a leading
  YAML fence are typed `frontmatter` instead (D8 §11 item 8;
  `harness/d8_cheap_arm.py --frontmatter-type`). For R, the target is a
  section or a region, which counts as natural language.
- **F6. The edit created the defect.** Every input state is well-formed, and
  the blind tierer does not record the error as visible author error in the
  file (§7.2, question 4).
- **F7. A reader cannot see it.** The blind tierer records that a reader with
  only the after-file and the reference could not tell (§7.2, question 3).
- **F8. Tier A or B**, assigned blind (§7).
- **F9. It reproduces.** A standalone reproduction from the pinned commits,
  re-run from a clean checkout, produces a byte-identical record.

One qualifying distinct block (§6.1) is enough. A frequency is reported, but
it does not stand in for severity.

### 4.2 Not FOUND, by name

None of these can become a finding, however they are written up:

- a planted or constructed case
- a case with an input state that is already malformed: a defect carried in,
  as in `LOG.md` §6.1
- an author error the tierer records as visible in the file
- a LOUD refusal or `#REF!`
- a conflicted merge (tier E)
- an oracle verdict of `UNKNOWN`, `UNDECIDABLE-REPEAT` or `UNDECIDABLE-SPLIT`
- a silent-wrong under the naive policy only
- an anchored block typed `code`, `html`, `table` or `frontmatter`
- a file that the primary rule marks as generated, or a path outside the
  selection
- a record tiered C, D, E or UNPLACEABLE
- a `site-policy` merge outside the strict set of 21 cases
- a case that qualifies only under a selection rule other than `yaml-fence`

**NEAR MISS.** Nothing qualifies, but at least one decided mis-resolution
falls short on exactly one of F4 (naive only), F5, F7 or F8 (tier C or D).
It is published as NOT FOUND with the near misses described, as the first
registration's §6 did.

## 5. The oracle

This section is the superseding oracle statement that `LOG.md` §6.2 and §9
call for. `ORACLE.md` is still the record of the first statement.

### 5.1 TLLC, unchanged, plus its single-leg form

The oracle is TLLC as defined in `ORACLE.md` §2 and implemented in
`harness/prose_merge.py` `tllc()`. It is used without modification, including
its `UNKNOWN` and `DELETED` rules and the fence in `ORACLE.md` §4.

For E and S, TLLC runs with leg C equal to the base and the merged text equal
to the after-state. Both legs then reduce to one alignment, base to after, so
this is TLLC's one-leg form, not a different oracle. For R, the unit is the
target section or region rather than the block: `frac_L` and the plurality
vote run over that unit's non-blank lines.

### 5.2 What the oracle cannot decide

Neither rule below reads the mechanism's answer. Both are applied to every
`SURVIVED` verdict (base unit `k`, target `t`, in the result text `M`) before
grading.

**UNDECIDABLE-REPEAT.** `LOG.md` §6.2 shows the failure: base occurrence *i*
can be paired with any of several byte-identical occurrences, and nothing in
the bytes chooses between them. The rule:

- A **twin** is a block whose content, as D8's `blocks()` returns it, is
  byte-identical to another block's.
- Let `T` be the blocks in `M`, other than `t`, that are twins of `t` or of
  `k`.
- If `T` is empty, the verdict is decided.
- If `T` is not empty, score each `c` in `{t} ∪ T` with `ctx(c)`, which runs
  from 0 to 2. It counts how many of these two pairs hold:
  - `M[c-1]` is TLLC's target for `B[k-1]`;
  - `M[c+1]` is TLLC's target for `B[k+1]`.

  A pair counts only if that neighbour has no twin in `B` and its target has
  no twin in `M`.
- The verdict is decided only if `ctx(t) ≥ 1` and `ctx(t)` is strictly
  greater than every `ctx(c)` for `c` in `T`. Otherwise it is
  UNDECIDABLE-REPEAT.

The duplicate-heavy hypothesis is that boilerplate is repeated in different
contexts and one copy is edited. That case stays decided, because context
separates the copies. Adjacent copies, which only an arbitrary pairing could
tell apart, do not stay decided. §9 V3 requires showing both.

**UNDECIDABLE-SPLIT.** This applies when the mapped lines of `k`, under the
legs that proposed a target, fall in two or more blocks of `M`. Each of those
blocks is a descendant, and TLLC's plurality vote picks one of them
arbitrarily.

**Reporting.** Each undecidable verdict is counted per cell, in instances
and in distinct blocks (§6.1). It is reported next to `UNKNOWN`, and it never
enters any rate. It cannot pass and it cannot be a finding. Reporting a cell
without its undecidable counts is a reporting defect.

### 5.3 What the oracle still does not do

TLLC decides **descent, not falsity**, as `ORACLE.md` §5 says. A decided
mis-resolution is a candidate. Whether anything false is asserted is decided
in tiering (§7), by someone who has not seen the frequencies.

## 6. Units, corpora, selection, sampling, floors

### 6.1 The unit is a distinct authored block

The identity key of a block is `(arm, sha256(content))`. For an R target it
is `(arm, name, sha256(section content))`.

- A block evaluated in several cases, or copied into several files of one
  arm, counts once.
- Every count in a verdict, a floor or a published rate is a count of
  distinct blocks.
- Instance counts may be reported beside them, labelled as instances.

Precedents: `LOG.md` §11 (85 records, 64 distinct blocks, 16 cases) and
`research/design-findings/X9-demand-correction.md`, where one data point was
presented as four.

### 6.2 Corpora and pins

| arm | source | pin | pathspec before the rule |
|---|---|---|---|
| `rust-book` | rust-lang/book | `1500248d8f230566e4ec9f27fcbb8fe9e2898ab1` | `src/*.md` |
| `obsidian-help` | obsidianmd/obsidian-help | `327a782e90481268361b5ccccdb0c224b2b13fe6` | `en/*.md` |
| `cmspec` | commonmark/commonmark-spec | `3da939428d80f146f270cd1765e4ba462e96bb1b` | `*.md` |
| `k8s-en` | kubernetes/website | `6b27baef1e44275fd4368e14375296e1dfe5af11` | `content/en/*.md` |
| `k8s-l10n` | kubernetes/website | same | `content/*.md :(exclude)content/en/` |
| `cncf-toc` | cncf/toc | `144c2e3215884e498e744cc51e6b7cef82d654f1` | `*.md :(exclude).github/` |
| `site-policy` | github/site-policy | `b9578b546d2506febda1da2cd7431644d58e512c` | `*.md :(exclude).github/` |

**Where the pins come from.** The D8 pins are D8 §3's pins, the trees at
which the committed research artifacts reproduce (`results/cheap-arm/validation.txt`).
The others are the first registration's §5.1 pins. `harness/corpora.json`'s
pins are used only to validate the control gate and the committed merge arm
(§9 V1, V2).

**If a pin cannot be fetched, that arm reports NO VERDICT.** No other commit
is substituted.

**The strict `site-policy` set** is chosen mechanically. Of the accepted
merges, those whose merge subject matches `automated-sync` or `repo-sync` are
excluded. The first registration's §5.1 puts the result at 21 cases. If
the rule gives a different count, the rule's count is used and the
difference is logged. The set of 25, which excludes `automated-sync` only, is
reported beside it.

### 6.3 The prose subset and the generated-file rule

**The pathspec** is the one in §6.2. It follows `LOG.md` §12's root rule:
use the site's content directory where there is one, minus `.github/`.

**Generated files.** A file is excluded when its own leading YAML fence
matches `^auto_generated:[ \t]*true[ \t]*$` (multiline, case-insensitive), or
when its text contains `THIS FILE IS AUTO-GENERATED`. This is
`--generated-rule yaml-fence`, evaluated on the file's content at the pin.

**Why `yaml-fence`.** A file declares where it came from in its own metadata.
The same key inside an HTML comment is a quotation of another page's
frontmatter, not a declaration about this file. That reason does not depend
on any count. The bias risk is disclosed:

- `yaml-fence` is the rule under which `LOG.md` §12.1 printed 0.
- That 0 does not come from excluding the one file that matters.
  `content/zh-cn/docs/reference/glossary/cri-o.md` is in neither rule's
  excluded list. `grep -c cri-o` gives 0 for
  `results/cheap-arm/selection.txt` and 0 for
  `results/cheap-arm/selection-yaml-fence-rule.txt`.
- The record disappeared because D8's sampler drew a different set of files,
  which the sampler below cannot do.

The results under `none` and `anywhere` are reported beside `yaml-fence` and
carry no verdict.

**The sampler cannot be redrawn by the rule.** Each sampled population is
ranked by `sha256("prereg2:" + arm + ":" + key)`. The sample is the *k*
smallest. Excluding an item that was not selected cannot change the sample.
Excluding a selected item only brings in the next one in rank. The key is
`commit:path` for E and `path:i:gap` for S.

### 6.4 Translations

`k8s-en` and `k8s-l10n` are separate arms and are never pooled.

- A translation is authored, so `k8s-l10n` can yield FOUND.
- Its per-language breakdown is reported but carries no verdict of its own.
- Distinct-block keys are already per arm, so a paragraph does not count
  once for each of the 17 languages (`LOG.md` §12).

### 6.5 Arms, in the order they run

**Arm 0, the census of oracle reach.** It runs at each pin over the full
selection, with no sampling, and reports per arm:

- every block, and how many are under 20 characters (excluded, because the
  mechanism as measured skips quotes under 20; `evaluate_case`
  `skip:short_quote`);
- among blocks of 20 characters or more, the distinct contents;
- the distinct contents that have a twin within the same file;
- of those, the ones that are a single line, and the ones in a run of
  adjacent twins.

All of these are broken down by type.

**The bar.** If more than 10% of a cell's distinct natural-language contents
of 20 characters or more have a twin within their file, that cell does not
run under this document. It reports **NO VERDICT (oracle reach)**, and the
remedy is a further oracle statement.

**The bar was set with this data in view.** At 20 characters or more, under
`anywhere`, the within-file twin shares for prose in the four arms of
`LOG.md` §12 are 726 of 108,410, 244 of 37,979, 46 of 11,669 and 4 of 1,437
(`results/cheap-arm/uniqueness-distinct.txt`, lines 8, 17, 26 and 35). For
`k8s-website`, heading is 241 of 25,856 and list is 274 of 19,685 (lines 5
and 6). The bar is expected to hold everywhere measured so far, so it is a
backstop. It is not expected to bind. What has not been measured is the
single-line and sub-20 shape that `LOG.md` §11 names, and Arm 0 is where that
gets measured.

**Arm E, single commits.** The population is every `(commit, path)` where:

- the commit is not a merge (`git rev-list --no-merges <pin>`);
- the path is in the selection at the pin;
- the commit modifies the path relative to its one parent, under
  `--no-renames`.

Adds, deletes and renames are counted and excluded. The sample is the 1,000
lowest-ranked pairs, or the whole population if it is smaller. Every block is
evaluated (`--max-blocks 0`).

**Arm S, spans of commits.** For each selected path, the history is D8's
`git log --format=%H --reverse -- <path>` at the pin. Pairs are
`(cs[i], cs[i+gap])` with gap 5 and gap 25, where both blobs exist and
differ. The sample is the 500 lowest-ranked pairs per gap. Every block is
evaluated.

**Arm M, merges.** `find_merge_cases` as committed, over every merge at the
pin, restricted to the selection. Drops are counted as committed. Convergent
edits stay out, so that the committed arm still reproduces (`LOG.md` §7).
This is a full census.

**Cells.** A cell is one arm, one of E, S5, S25 or M, and one of Q or R.
Each cell is reported on its own.

### 6.6 The floor, and what a cell can report

A cell reports exactly one of:

- **FOUND.** At least one record meets every F condition. No floor applies.
- **NOT FOUND.** No record qualifies, and all of these hold:
  - the cell passed Arm 0;
  - it has at least **300** distinct decided natural-language blocks;
  - distinct undecidable blocks (§5.2) are at most 10% of decided plus
    undecidable.
- **NO VERDICT**, with its reason. This covers everything else. A cell below
  the floor reports NO VERDICT and never zero.

**Why 300.** Zero events in 300 trials bounds the per-block rate at about 1%,
at 95% (the rule of three, 3/n). A NOT FOUND therefore says something at the
scale of the rate the first registration's §1 treated as residual.

### 6.7 The overall verdict

- **FOUND** if any cell reports FOUND.
- **NOT FOUND** if no cell reports FOUND, and both `k8s-en` and `cncf-toc`
  have at least one Q cell in E, S5 or S25 that reports NOT FOUND. These are
  the largest and the cleanest duplicate-heavy arms (first registration
  §5.1).
- **NEAR MISS** if the NOT FOUND conditions hold and §4.2's near-miss
  condition also holds. It is published as NOT FOUND.
- **INCONCLUSIVE** otherwise.

A NOT FOUND names only the mechanisms and cells that reached a verdict. A
mechanism with no such cell, R for example, is listed as unmeasured.

## 7. Severity, and blind tiering

### 7.1 The tiers, unchanged from the first registration's §4

| tier | shape | qualifies |
|---|---|---|
| **A** | A derived or transcluded value or passage in the result is wrong: a count, an index, a transcluded figure, or transcluded prose that silently resolves to different content than it did before the edit | yes |
| **B** | A reference resolves silently to the wrong target, and the reference carries an assertion about that target | yes |
| **C** | A reference resolves silently to the wrong target, and nothing asserted becomes false | **no**: report it, do not build on it |
| **D** | Content is reordered, duplicated or dropped in a way the authors would reject, but nothing asserts anything false | **no** |
| **E** | The merge conflicts, or the reader refuses the file | **no** |

The principles of the first registration's §4.1 carry over:

- A tier is assigned from these definitions, before the frequency is known,
  by someone who has not seen it.
- It is recorded when it is assigned.
- It is never revised upward. It may be revised downward at any time, with
  the reason logged.
- A record that cannot be placed is **UNPLACEABLE**. That is reported, and it
  is not a finding.

### 7.2 What the tierer judges

The harness anchors every block, so each record is a *hypothetical*
reference. The tierer answers four questions for each record:

1. **Under assertion use**, where a comment or reference asserts something
   about its target: would an assertion that is true of the oracle's target
   be false, or change a reader's action, if read as being about the
   mechanism's target? Yes gives **B**.
2. **Under transclusion use**: would rendering the mechanism's target in
   place of the oracle's target change what the transcluding document says?
   Yes gives **A**.
3. **Visibility (F7):** could a reader holding only the after-file and the
   reference tell that it landed wrong?
4. **Author error (F6):** is the mis-resolution explained by an author error
   visible in the file, such as a stray paste?

If neither use makes anything false, the record is **C**. A bare "see also"
is C by definition and is not asked about.

### 7.3 The procedure: the independence decision of 2026-10-07

**The export.** Before any tiering, a committed script exports one packet
per distinct triple of (block, mechanism target, oracle target). Each packet
holds:

- the before-file(s) and the after-file;
- for M, both legs;
- the reference: the quote selector or the name;
- the mechanism's status (`EXACT`, `EXACT_CTX` or `FUZZY` for Q, `NAME`
  for R);
- the text of both targets;
- §7.1 and §7.2 of this document, verbatim.

**What the export leaves out.** It holds no counts, rates or denominators,
nothing about how many records share a block, no other records, no cell or
corpus totals, and no LOG. Packets are named by an opaque hash and shuffled
with a seed. A committed validator fails the export if any packet contains a
field outside an allow-list. The total number of packets is visible to the
tierer, and the log says so.

**The tierer** is a fresh agent with no access to the authoring conversation.
It works in a directory that holds the export and nothing else, with no
blockspec checkout. That is the filesystem barrier in org contract §2.1. It
writes `tiers.jsonl` into that directory. The file is committed as it was
written, before any join with frequencies.

**What is logged in `LOG.md`:** the export manifest, with the sha256 of every
file and the packet count; the prompt, verbatim; the date; the agent and
model; and the commit of `tiers.jsonl`.

Whoever ran any arm is disqualified from tiering. Records from the first
registration (`results/merge-arm-candidates.jsonl`, 85 records) are not
tiered under this document. Arm M at D8 §3's pins regenerates that
population, and those records are tiered like any others.

## 8. Outcomes, and what each publishes

Both directions are deliverables. Neither one is a failure.

**FOUND.** The write-up is the reproduction. It gives:

- the pinned commit(s) and the stock-git command line;
- the before and after files;
- the oracle's decided verdict and the tier record;
- the frequency as distinct qualifying blocks over distinct decided blocks,
  per cell, with undecidable counts beside it.

blockspec then proceeds to blockspec#3 and #4, the adjudications, and to
blockspec#5, the case tree, and its design pass opens with this defect.

**NOT FOUND.** A finding is published, not a format: "prose does not earn a
format under these mechanisms", with:

- the mechanisms and cells that reached a verdict;
- the covered and excluded populations, including Arm 0's sub-20 count and
  every undecidable count;
- what would change the answer.

The repository then states that blockspec is not being built, and why.
`DESIGN-BRIEF.md`'s open questions are answered "not applicable", with the
reasoning kept. Org contract §7 lists "a spike result that would kill a
kind", so this goes to the owner before it is published.

**NEAR MISS.** Published as NOT FOUND, with the near misses described. A tier
C or D result does not become tier B by being written up with enthusiasm.

**INCONCLUSIVE.** Published as such, naming the cells that lacked coverage
and what each would need. blockspec#2 stays open. Nothing is built, because
`DESIGN-BRIEF.md` §2 says not to build until the defect exists.

## 9. Validation before trust

Org contract §2.2 applies. Each step's transcript is committed under
`results/prereg2/` before the next step starts. A failure stops the work, is
logged in `LOG.md`, and is diagnosed before anything else happens.

- **V1. The control gate.** `harness/run_control.sh` followed by
  `check_control_gate.py` passes at `harness/corpora.json`'s pins, as
  `PRE-REGISTRATION.md` §7 requires.
- **V2. Byte-identical reproduction.** Each of these is regenerated from the
  committed code:
  - `results/control-arm.txt`;
  - `results/merge-arm.txt` and `results/merge-arm-candidates.jsonl`, using
    the command in `spike/README.md` at `corpora.json`'s pins;
  - `research/experiments/D8-identity/results-e4.txt` and
    `results-anchor3.txt` at D8 §3's pins;
  - every file in `results/cheap-arm/`, using `harness/run_cheap_arm.sh`.

  Each must be byte-identical, checked by `cmp` and sha256.
- **V3. Every new component is shown to go red on a planted case and on an
  empty input.** At minimum:
  - **REPEAT.** `oracle_limitation.py`'s case comes out UNDECIDABLE-REPEAT.
    `wrong-01`, `single-leg-01` and `clean-01` keep their committed verdicts.
    A new planted case, two identical multi-line paragraphs in different
    contexts with one of them edited, comes out decided and `WRONG`. That
    last case shows the rule does not remove the hypothesis.
  - **SPLIT.** A planted paragraph split in two comes out UNDECIDABLE-SPLIT.
  - **R.** A planted case where a heading is renamed onto another section's
    name comes out decided and `WRONG`. A name that disappears gives `#REF!`.
    A duplicated name gives `#REF!`.
  - **The E and S enumerators.** A planted repository that holds
    `single-leg-01` as one commit yields that record. An empty repository
    exits non-zero.
  - **The selection filter.** The generated key inside the file's own fence
    excludes the file. The same key inside an HTML comment does not.
  - **The sampler.** Removing an item that was not selected leaves the
    sample byte-identical.
  - **Distinct counting.** A planted duplicate counts once.
  - **The floor.** 299 decided blocks report NO VERDICT. 300 report NOT
    FOUND. An empty cell reports NO VERDICT and never zero.
  - **The Arm 0 bar.** A planted corpus over 10% stops its cell.
  - **The export validator.** A packet carrying a count field fails.
  - **The aggregator.** Empty input reports no verdict and exits non-zero.
- **V4. A mutation sweep over the new gates,** in the `armed_check.sh` style.
  Each mutation is hash-verified before and after. A mutation that does not
  apply is reported as BROKEN, never as survived.
- **V5. The existing checks stay green and armed:** `armed_check.sh`,
  `prose_merge.py --selftest-selection`, `selection_guard_red.sh` and
  `oracle_limitation.py`.

**The commit order is what keeps the bar from moving.** Validation is
committed, then Arm 0's results, then the scoring arms' results and the
export, then `tiers.jsonl`, then the join and the verdict. Each is a separate
commit. If the harness cannot implement a definition in this document as it
is written, the work stops and the gap is reported. The definition is not
reinterpreted.

## 10. Amendment rules

**Frozen when this merges:** §0, and §2 to §8. A frozen section that turns out
to be wrong is replaced by a further pre-registration, never by an edit.

**Correctable after it merges:** §1, which records why this was written, and
§9, which records method. These may be corrected only where they are wrong
about a fact. Each correction is logged below with the original wording,
because otherwise a reader cannot tell a good-faith correction from a
convenient one.

**Pins never change.** A pin that becomes unreachable makes its arm NO
VERDICT. Edits made while this is a draft PR are not amendments.

| date | section | change, with the original wording | reason |
|---|---|---|---|
