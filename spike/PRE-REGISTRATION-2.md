<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Pre-registration 2: does prose admit a silent-wrong under any edit?

**Status: DRAFT, for owner approval.** In the owner's decision, "committed"
means *merged to `main`*. Nothing under this document runs before it merges.
Once merged, it supersedes `PRE-REGISTRATION.md` for blockspec#2.
`PRE-REGISTRATION.md` and `ORACLE.md` stay unchanged as the record of what was
registered first.

**Citations.** A blockspec path means its content at `d49e7ef3ea20`. A
`research/` path means kindspec/research at `71d97a1e6f36`, unless another
commit is named. Every figure is given with the command that produced it, run
from `spike/results/` unless stated otherwise.

---

## 0. Choices the owner is approving

The 2026-10-07 decision left each of these open. Approving the draft approves
all of them. To change one, edit the draft before it merges.

1. **Real history only (§2).** FOUND needs a case from the history of a pinned corpus. *Alternative:* count reachability, in which case the answer is already FOUND by `plant_cases/single-leg-01`.
2. **SPLIT is an undecidable verdict (§5.2).** It was named after reading `LOG.md` §12, so it is not blind. It would dispose of the only two hardened silent-wrongs the cheap arm printed that are eligible under F5. Both are named below. *Alternative:* decide split cases by TLLC's plurality vote, then tier them blind.
3. **Arm 0 runs first, with a 10% twin-share bar (§6.5).** The bar is a backstop and is not expected to bind. *Alternative:* report Arm 0 with no bar.
4. **The generated-file rule is `yaml-fence`, and samples are hash-ranked (§6.3).** Its exclusions are a subset of `anywhere`'s, so it is the more inclusive rule. *Alternative:* FOUND must hold under all three rules.
5. **`k8s-en` and `k8s-l10n` are separate arms (§6.4).** *Alternative:* English only.
6. **FOUND needs the hardened policy (F4).** *Alternative:* either policy.
7. **FOUND needs a block of type `prose`, `list` or `heading` (F5).** *Alternative:* any type.
8. **A cell needs at least 300 distinct decided units to report NOT FOUND (§6.6).** *Alternative:* D8's floor of 50 anchors.
9. **Sample sizes (§6.5).** E takes 1,000 edits per arm, S takes 500 pairs per gap per arm, and M is a full census. *Alternative:* a full census everywhere.
10. **Named references (R) are a second mechanism (§3).** *Alternative:* quote anchors (Q) only.
11. **What NOT FOUND needs overall (§6.7).** Q must reach NOT FOUND in `k8s-en` and in `cncf-toc`, and R in at least one of them. If only Q does, the result is NOT FOUND (Q only). *Alternative:* any one cell is enough.
12. **D8's corpora are read at D8 §3's pins (§6.2).** *Alternative:* the pins in `harness/corpora.json`.
13. **`site-policy` (§6.2).** M can yield FOUND only from the strict set. E and S can yield FOUND, and commits by bots count. *Alternative:* the 25-case set for M, or exclude bot commits from E and S.
14. **The exclusion of single-author or bot-dominated corpora is dropped.** That exclusion is the first registration's §5. *Alternative:* keep it, and exclude any corpus predominantly single-author or bot-generated, measured on the cases each arm selects.
15. **E and S use TLLC's one-leg form (§5.1), not D8's `line_oracle`.** *Alternative:* use `line_oracle` for E and S, for comparability with D8.
16. **NEAR MISS is redefined (§6.7).** The first registration had two definitions: §3 says "four out of five is a near miss", and §6 says "NEAR MISS (tier C or D only)". Here a near miss is one of three named categories of decided mis-resolution. *Alternative:* carry over either first-registration definition.
17. **The first run's 85 records are not tiered (§7.3).** This reverses `STATE.md` §2 item 3 (kindspec/.github `cb976f4906a1`), "tier the candidates, blind". *Alternative:* tier them blind as a separate export that carries no verdict.
18. **Tiers are computed from answers, and one tier definition is adapted (§7.1, §7.2).** §7.2's rule defines the tier. The tier table is illustrative only. Tier A's "in both parents" becomes "before the edit", because E and S have one parent. *Alternative:* the first registration's wording with no adaptation, which leaves A undefined for E and S.
19. **The tierer model is pinned to `claude-opus-5-5`, tiering starts within 14 days of the scoring-arm commit, and there is one tiering run (§7.3).** If the pinned model is not served on the start day, the tierer is the most recent `claude-opus-*` model the Models API lists that day, logged. *Alternative:* the harness's default fresh agent, with its identity logged.
20. **The packet's reference is the quote text or the name only (§7.3).** *Alternative:* export the full selector (prefix, suffix, offset, status), whose context can let a reader see the mis-resolution.

**The two cases SPLIT would dispose of.** Both are D8 `line_oracle` cases from
`LOG.md` §12, and `LOG.md` §12 describes each as a block split in two. **That
TLLC would also call them SPLIT is a prediction that has not been run.**

- `k8s-website` gap=1, `content/zh-cn/docs/reference/glossary/cri-o.md`.
  Prose-typed, hardened, present under `anywhere` only.
- `site-policy` gap=5,
  `Policies/content-removal-policies/github-private-information-removal-policy.md`.
  Heading-typed, hardened, 2 records, present under all three rules.

Command, run on each of `cheap-arm/anchors-no-generated-rule.txt`,
`cheap-arm/anchors.txt` and `cheap-arm/anchors-yaml-fence-rule.txt`:
`grep -B4 -E "^ +hard .*SILENT-WRONG .*\(n=[1-9]" <f> | grep -E "^###|^ +hard"`.

## 1. Why this supersedes `PRE-REGISTRATION.md`

The first registration's §8 allows §3, §4 and §6 to change only through a new
pre-registration. There are three reasons to change them.

**1.1 FOUND excludes the shape that was found.** `LOG.md` §9 shows one author
in one commit producing a hardened `EXACT` prose silent-wrong
(`plant_cases/single-leg-01`). The first registration's §3(5) requires a defect
"created by the merge", which that case is not. Merges are also a small share
of editing. The three control corpora have 195 accepted both-sides cases
against 19,337 `.md` paths changed on one side only:

- `grep -o "ACCEPTED [0-9]*" merge-arm.txt | awk '{s+=$2}END{print s}'` gives
  195.
- `grep -o "exactly ONE side: [0-9]*" merge-arm.txt | awk '{s+=$4}END{print s}'`
  gives 19337.

**1.2 TLLC cannot decide repeated blocks.** `LOG.md` §6.2 and
`harness/oracle_limitation.py` show this. `ORACLE.md` is frozen, so §5 of this
document is the new oracle statement.

**1.3 The unit and the selection were not fixed, and the result moved.**

- **Selection.** D8 samples with `Random(7).shuffle(files)[:14]`, so excluding
  any one file redraws the whole sample. As a result, the count of hardened
  prose-typed silent-wrongs was 0 under `none`, 1 under `anywhere` and 0 under
  `yaml-fence`. Command, per file:
  `grep -E "^ +hard .*by type:.*prose=" <f> | grep -oE "prose=[0-9]+"`,
  summed, with an empty result counted as 0.
- **Unit.** Counting instances overstates distinct content. In `k8s-website`,
  1,524 within-file duplicate prose instances at ≥40 characters are 481
  distinct contents (`sed -n 44p cheap-arm/uniqueness-distinct.txt`).

## 2. The question

> **In the real editing history of the pinned corpora, does a prose document
> under stock git come to contain a reference which a mechanism that prose
> would need (§3) resolves silently to the wrong target? The file must be
> well-formed. The result must be wrong by an oracle independent of the
> mechanism, and a reader holding only that file and the reference's quote
> or name must be unable to detect it. The edit can be any of: one commit (arm E), a span of commits (arm S),
> or a two-parent merge (arm M).**

## 3. The mechanisms

The mechanism code is kindspec/research `experiments/D8-identity/` at
**`d51ce09cdb23`**. `anchor_eval.py`, `anchor_eval2.py` and `anchor_eval3.py`
are byte-identical there and at `f088cd76fd13`, which the control arm imports,
and they differ at `71d97a1`. Command, in the research checkout:
`git show <c>:experiments/D8-identity/<f> | sha256sum`.

- **Q, the quote anchor.** Imported unchanged. `anchor_eval.anchor_of` builds
  the anchor and `anchor_eval3.reanchor2` resolves it (D8 §7.3 steps 2–5).
- **R, the named reference** (D8 §7.2, §7.3 step 1). This is **new harness
  code**, with two pieces **copied verbatim** from `d51ce09`. They are copied
  because their modules run experiments when imported.
  - **Slugs.** `slugs()` from `e9_headings.py` lines 8–13, applied only to
    blocks that `btype()` types `heading`. The `{#id}` syntax, which D8 §7.2
    rejects, is not used.
  - **Region markers.** `REGION` and `regions()` from `e6_transclude.py`
    lines 14 and 17–31. The target is the block after the marker. Begin/end
    spans have no D8 implementation and are not measured.
  - **Resolution.** Region markers are tried first, then slugs. Zero matches,
    or more than one, is `#REF!`, and that counts as LOUD.
  - **Target.** A slug's target is its section: the heading plus the blocks up
    to the next heading of the same or a higher level. R is correct if and
    only if the resolved section contains TLLC's plurality block (§5.1).
- **Transclusion.** This is a way of using Q and R, not a third mechanism. It
  is judged in tiering (§7.2).

Every evaluated block is anchored with Q. Every name that resolves uniquely at
the before-state is anchored with R.

## 4. FOUND

A record is FOUND only if it meets all nine conditions:

- **F1. Real history.** The before-state(s) and the edit are commits of a
  pinned corpus (§6.2), and the path is in the arm's selection (§6.3). A
  `site-policy` M case must also be in the strict set.
- **F2. Stock git only.** No merge driver, `.gitattributes`, filter or hook.
  - **M.** `git merge` in the harness's hermetic repository exits 0, leaves no
    conflict marker, and `git ls-files -u` is empty.
  - **E and S.** No merge takes place. The before- and after-states are blobs
    read with `git show`, which applies no filter or driver. F2 cannot fail
    here, by construction, and that is accepted: these arms have no merge for
    it to test.
- **F3. Well-formed.** Every input state and the result pass
  `fences_balanced`, and D8's `blocks()` finds at least 2 blocks in each.
  This is the only well-formedness check the harness has.
- **F4. Wrong under the hardened policy.** The mechanism resolves without a
  LOUD refusal, and lands somewhere other than the oracle's **decided** target.
  If the oracle says the target was `DELETED`, any resolution counts as wrong.
  That variant is reported as `WRONG_on_deleted` and is weaker (`ORACLE.md`
  §4).
- **F5. A natural-language block.** For Q, the base block's type is `prose`,
  `list` or `heading`. Blocks inside a leading YAML fence are typed
  `frontmatter` and do not qualify. Every R unit meets F5.
- **F6. The edit created the defect.** Every input state is well-formed, and
  the tierer answers question 4 "no".
- **F7. A reader cannot see it.** The tierer answers question 3 "no".
- **F8. Tier A or B**, as §7.2 computes it.
- **F9. It reproduces.** The reproduction script, which is part of the
  harness at the validation commit and is V3-tested on `single-leg-01`, runs
  unmodified from the pins in a clean checkout and regenerates the record byte
  for byte.

One qualifying distinct unit is enough for FOUND.

Two further cases are not findings, whatever else holds:

- an oracle verdict of `UNKNOWN` or `UNDECIDABLE-*` (§5.2);
- a case that qualifies only under a selection rule other than `yaml-fence`.

## 5. The oracle

This section is the superseding oracle statement that `LOG.md` §6.2 and §9 call
for.

### 5.1 TLLC and its forms

- **TLLC.** `ORACLE.md` §2 defines it and `harness/prose_merge.py` `tllc()`
  implements it. It is used unmodified, including `UNKNOWN`, `DELETED` and the
  fence in `ORACLE.md` §4.
- **One-leg form (E and S).** Leg C is the base and the merged text is the
  after-state, so both legs reduce to the single alignment base→after.
- **Section form (R).** The base unit is the section or region. `frac_L` and
  the plurality vote run over the unit's non-blank lines, and the vote names
  the after-state block that R is graded against (§3).

### 5.2 What the oracle cannot decide

Neither rule below reads the mechanism's answer. Both run on every `SURVIVED`
verdict before it is graded. Terms:

- `B` is the base text (for M, the merge base), `k` is the base unit, `t` is
  TLLC's target, and `M` is the after-text. `B[i]` and `M[i]` are units by
  index.
- For Q, a unit is a block.
- For R, a unit **for this section only** is the span from a heading to the
  next heading of any level for a slug, and the single block after the marker
  for a region marker. The rules over R units are new code and must pass V3.
- A **twin** is a unit that is byte-identical to another unit in the same
  text.

**UNDECIDABLE-REPEAT.**

1. Let `T` be the units in `M`, other than `t`, that are twins of `t` or of
   `k`. If `T` is empty, the verdict is decided.
2. Otherwise, give each `c` in `{t} ∪ T` a score `ctx(c)` from 0 to 2: the
   number of these that hold:
   - `M[c-1]` is TLLC's target for `B[k-1]`;
   - `M[c+1]` is TLLC's target for `B[k+1]`.
3. A pair counts only if three things are true:
   - both indices exist, so a first or last unit gets nothing on the missing
     side;
   - the base neighbour has no twin in `B`;
   - its target has no twin in `M`.
4. The verdict is decided if and only if `ctx(t) ≥ 1` and `ctx(t)` is greater
   than `ctx(c)` for every `c` in `T`. Otherwise it is UNDECIDABLE-REPEAT.

**UNDECIDABLE-SPLIT.** The mapped lines of `k`, under the leg or legs that
proposed a target, fall in two or more units of `M`.

**Counting.**

- A distinct unit (§6.1) is **decided** if any of its instances is decided.
  A decided `SURVIVED` and a `DELETED` both count as decided.
- A distinct unit is **undecidable** if none of its instances is decided and
  at least one is `UNDECIDABLE-*`.
- A unit whose every instance is `UNKNOWN` is counted as `UNKNOWN`.
- A qualifying record must be a decided instance.
- Undecidable and `UNKNOWN` counts are reported per cell, as instances and as
  distinct units. They never enter a rate, a pass or a find.

TLLC decides descent, not falsity (`ORACLE.md` §5). Tiering (§7) settles
whether anything false is asserted.

## 6. Units, corpora, selection, sampling, floors

### 6.1 Unit

A distinct authored unit is keyed as:

- for Q, `(arm, sha256(block content))`;
- for R, `(arm, name, sha256(unit content))`.

Every verdict, floor and published rate counts distinct units. Instance counts
may appear beside them if labelled as instances.

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

- The first three arms use D8 §3's pins (see `cheap-arm/validation.txt`). The
  rest use the first registration's §5.1 pins.
- The pins in `harness/corpora.json` are used only for V1 and V2.
- Each corpus is archived as a git bundle, and the bundle's sha256 is
  committed at validation. A pin is unreachable only if it is absent from its
  bundle, and then its arm reports NO VERDICT.

**The strict `site-policy` set (M only).** An accepted merge is excluded if its
subject line contains `automated-sync` or `repo-sync`, matched as a
case-sensitive substring of the output of `git log -1 --format=%s <merge>`.
The first registration's §5.1 expects 21 cases to remain. If the rule leaves a
different number, the rule's count stands and the difference is logged. The
25-case set excludes `automated-sync` only. It is reported beside the strict
set and carries no verdict.

In E and S, every commit counts, whoever made it, and its author is recorded.

### 6.3 Selection and sampling

**Generated files.** A file is excluded if its leading YAML fence matches
`^auto_generated:[ \t]*true[ \t]*$` (multiline, case-insensitive), or if its
text contains `THIS FILE IS AUTO-GENERATED`. This is `d8_cheap_arm.py
--generated-rule yaml-fence`, evaluated at the pin. The reason is that a file
declares its provenance in its own metadata, and a key quoted inside an HTML
comment is a quotation, not a declaration. `none` and `anywhere` are reported
beside it and carry no verdict.

**Sampling.**

- A population is ranked by `sha256("prereg2:" + arm + ":" + key)`, and the
  sample is the *k* lowest-ranked. The key is `commit:path` for E and
  `path:i:gap` for S.
- Excluding an item that was not selected cannot change the sample.
- No ranking was computed before this merged, and the salt was not varied.
- There is no other randomness, except the export nonce in §7.3.

### 6.4 Translations

`k8s-en` and `k8s-l10n` are never pooled. Each translation of a paragraph has
different bytes, so `k8s-l10n` counts a translated paragraph once per language
(`LOG.md` §12). Its rates are labelled accordingly, and a FOUND there stands,
because a translation is authored text.

### 6.5 Arms, in order

**Arm 0: a census of oracle reach.** This runs at each pin over the whole
selection, with no sampling. Broken down by type, it counts:

- blocks under 20 characters, which the mechanism skips (`skip:short_quote`);
- distinct contents of 20 characters or more;
- those with a twin in the same file;
- of those, how many are single-line twins and how many are adjacent-run
  twins.

**The bar.** If more than 10% of an arm's distinct natural-language contents
of 20 characters or more have a twin in the same file, that arm reports **NO
VERDICT (oracle reach)** and does not run.

The bar is a backstop and is not expected to bind. In the committed outputs
at 20 characters or more, the largest share under each rule is `list` in
`k8s-website` (all languages): `none` 879/22,002, `anywhere` 274/19,685,
`yaml-fence` 854/21,830. These come from the highest line of
`awk 'NR<=36&&/^###/{a=$2} NR<=36&&/^(heading|list|prose) /{print $(NF-1)/$(NF-2),a,$1,$(NF-1)"/"$(NF-2)}' <f> | sort -rn`
on each `cheap-arm/uniqueness-distinct*.txt`.

**Arm E: single commits.**

- **Population:** each `(commit, path)` where the commit is not a merge
  (`git rev-list --no-merges <pin>`), the path is selected at the pin, and the
  commit modifies the path against its parent (`--no-renames`).
- **Excluded:** adds, deletes and renames, each counted.
- **Sample:** 1,000 per arm, with every block evaluated.

**Arm S: spans of commits.**

- **History:** for each selected path, `git log --format=%H --reverse --
  <path>` at the pin.
- **Pairs:** `(cs[i], cs[i+gap])` for gaps 5 and 25, where both blobs exist
  and differ.
- **Sample:** 500 per gap per arm, with every block evaluated.

**Arm M: merges.** A census of every merge.

- `find_merge_cases` supplies the enumeration and drop counters. Convergent
  edits stay out (`LOG.md` §7).
- **New code:** a pathspec-aware filter that applies §6.2 and §6.3. It must
  pass V3.

**Cells.** A cell is one arm, crossed with one of E, S5, S25 or M, crossed with
one mechanism, Q or R.

### 6.6 Cell verdicts

- **FOUND.** At least one record meets F1–F9.
- **NOT FOUND.** No record qualifies, and all of these hold:
  - the arm passed Arm 0;
  - the cell has at least **300** distinct decided natural-language units;
  - distinct undecidable units are at most 10% of decided plus undecidable.

  A NOT FOUND reports its actual *n* and the bound 3/*n* at 95% (the rule of
  three). The floor is expected not to bind in the large arms.
- **NO VERDICT, with its reason.** Every other case. It is never reported as
  zero.

### 6.7 Overall verdict

The overall verdict is the first of these that applies:

1. **FOUND**, if any cell is FOUND.
2. **NOT FOUND**, if both hold:
   - for Q, `k8s-en` and `cncf-toc` each have a NOT FOUND cell in E, S5 or
     S25;
   - for R, at least one of those two arms has a NOT FOUND cell.
3. **NOT FOUND (Q only)**, if only the Q condition in 2 holds.
4. **INCONCLUSIVE**, otherwise.

**Near misses** do not form a separate verdict. They are reported alongside
verdict 2 or 3, which is then published as "… with near misses". There are
three categories, each counted in distinct units:

- **(i)** an exported record that meets every condition except F7 or F8
  (tier C), according to its answers;
- **(ii)** a decided hardened mis-resolution that fails only F5. These are not
  tiered, and are labelled untiered.
- **(iii)** a decided mis-resolution under the naive policy only, meeting
  F1–F3 and F5. These are not tiered, and are labelled untiered.

## 7. Severity, and blind tiering

### 7.1 Tiers

The rule in §7.2 defines the tier. This table illustrates it, using the first
registration's wording with one adaptation (§0 item 18). Tiers D and E are not
in the packet, because an exported record is already a decided, clean, silent
mis-resolution.

| tier | shape | qualifies |
|---|---|---|
| **A** | A derived or transcluded value or passage is wrong — transcluded prose that silently resolves to different content than it did before the edit | yes |
| **B** | A reference resolves silently to the wrong target, and the reference carries an assertion about that target | yes |
| **C** | A reference resolves silently to the wrong target, carrying no assertion — a bare "see also" | **no**: report, do not build on |

Tiers are assigned before any frequency is known, by someone who has not seen
one. **No tier is revised after `tiers.jsonl` is committed.**

### 7.2 Questions, and the computed tier

For each packet the tierer answers four questions from the files alone:

1. **Assertion use.** Would a statement that is true of the oracle's target,
   about what it says or what it applies to, be false of the mechanism's
   target?
2. **Transclusion use.** Would rendering the mechanism's target in place of the
   oracle's change what the document says?
3. **Visibility (F7).** Could a reader holding only the after-file and that
   quote or name tell that the reference landed wrong?
4. **Author error (F6).** Is the mis-resolution explained by an author error
   that is visible in the file?

The tier is **computed** from the answers: A if question 2 is yes, otherwise B
if question 1 is yes, otherwise C. If the tierer cannot answer question 1 or
question 2, the packet is UNPLACEABLE, which is not a finding.

### 7.3 Procedure

**The export.** One packet is exported for each distinct (unit, mechanism
target, oracle target) whose record:

- is a decided mis-resolution under the hardened policy;
- meets F1–F5;
- has well-formed input states.

Each packet holds:

- the before-file or files, the after-file, and for M both legs;
- the reference: for Q the quote text only, for R the name. The prefix,
  suffix, offset and resolver status are not exported;
- the text of both targets;
- §7.1's table, §7.2 and Appendix A.

A packet holds no counts, rates, denominators, sharing information, other
records, totals or `LOG.md`. A committed validator fails any field outside an
allow-list.

**Names, order and the nonce.** Before any arm runs, a 32-byte nonce is drawn
from `os.urandom` and written into a sealed manifest. The manifest also holds
the plant names and their expected answers. The manifest's sha256 is committed
in the validation commit, and the manifest itself is committed after
`tiers.jsonl`. Each packet is named by the first 16 hex characters of
`sha256(nonce + ":" + packet key)`, and packets are ordered by name.

**Plants.** The three plants in Appendix B are mixed into the export, named and
ordered in the same way as real packets. Each plant's packet fields are
generated by running the harness on the plant's before and after files, as for
a real record: TLLC's one-leg form gives the oracle target, and the hardened
quote resolver gives the mechanism target. All three are realisable. At
drafting, `python3 -I harness/prereg2_plants.py --d8-dir <D8 at d51ce09>`
printed `PLANTS: PASS`, and it goes red when P-C's after-state is replaced by
the base with only the window sentence edited. **The tiering is void if any plant's
computed tier falls on the wrong side of the B/C line, or if any plant's answer
to question 3 or question 4 differs from the expected answer.** Confusing A
with B does not void it, because F8 accepts either. When the tiering is void,
every cell that exported at least one packet becomes NO VERDICT. Cells that
exported none are unaffected.

**The tierer.**

- **Model.** A fresh agent on the pinned model `claude-opus-5-5`, with no
  authoring conversation.
- **Isolation.** It works in a directory that holds only the export, with no
  blockspec checkout. That is the filesystem barrier of org contract §2.1. The
  network barrier depends on the agent following its prompt, and is honoured,
  not enforced.
- **Start.** Tiering starts within 14 days of the scoring-arm commit. If the
  pinned model is not served on the start day, the tierer is the most recent
  `claude-opus-*` model that the Models API lists that day, and it is logged.
  A later start is logged with its reason and changes nothing else.
- **Runs.** The first run's `tiers.jsonl` binds and is committed as written.
  At most one rerun is allowed, and only if the first run wrote zero lines.
  Any other untiered packet, plants included, is UNPLACEABLE, and an untiered
  plant does not void the tiering. Every run's transcript is committed.
- **Disqualification.** Whoever ran an arm may not tier.

**What `LOG.md` records:** the export manifest (sha256 of each file), the
packet count, Appendix A as sent, the date, the model id, and the commit.

**Accepted leak.** The packet count (exported mis-resolutions plus 3) is
visible: a numerator with no denominator.

## 8. Outcomes

The first registration's §6 stands. The differences are below.

- **FOUND.** The write-up is the reproduction.
  - For M: the merge base, the two legs and the stock-git command line.
  - For E: the parent commit and the commit, with `git show <c>:<path>` for
    each side.
  - For S: the two endpoint commits, with the same `git show` commands.

  Every write-up also gives the before- and after-files, the oracle's decided
  verdict, the packet answers, and per-cell distinct qualifying and decided
  counts with the undecidable counts. blockspec then proceeds to blockspec#3,
  #4 and #5.
- **NOT FOUND (needs Q and R).** The published finding is that prose does not
  earn a format under these mechanisms. It gives each cell's *n* and its bound,
  Arm 0's count of blocks under 20 characters, and every undecidable count. It
  states that blockspec is not being built. Org contract §7 requires it to go
  to the owner first.
- **NOT FOUND (Q only).** The finding is about quote anchors only. R is listed
  as unmeasured, blockspec#2 stays open for R, and there is no "not being
  built" statement.
- **INCONCLUSIVE.** The write-up names the cells that lacked coverage.
  blockspec#2 stays open and nothing is built (`DESIGN-BRIEF.md` §2).

## 9. Validation, and the order of work

**The first execution of each arm binds and is the content of its commit.
Every invocation of an arm, the exporter or the tierer, aborted ones included,
writes a transcript under `results/prereg2/` that is committed.**

**A V step fails when its committed transcript shows a non-zero exit, a `cmp`
or sha256 mismatch, or a surviving or BROKEN mutant.** V steps run only before
the validation commit, whose harness sha binds. A failed V step stops the work
until it is fixed and re-validated, before any scoring arm runs. A failure
found after the validation commit is a gap.

- **V1.** The control gate (`run_control.sh` then `check_control_gate.py`)
  passes at the pins in `corpora.json`.
- **V2.** Each of the following regenerates byte-identically, checked with
  `cmp` and sha256:
  - `results/control-arm.txt`;
  - `merge-arm.txt` and `merge-arm-candidates.jsonl`, using the command in
    `spike/README.md` at the pins in `corpora.json`;
  - research's `results-e4.txt` and `results-anchor3.txt`, at D8 §3's pins;
  - all of `results/cheap-arm/`, using `run_cheap_arm.sh`.
- **V3.** Each new component goes red on a planted case, and on an empty input.
  - **REPEAT.** `oracle_limitation.py`'s case comes out UNDECIDABLE-REPEAT. Two
    identical multi-line paragraphs in different contexts, one of them edited,
    come out decided and `WRONG`.
  - **REPEAT and SPLIT leave known cases alone.** `wrong-01`, `single-leg-01`
    and `clean-01` stay decided, with their committed verdicts.
  - **SPLIT.** A paragraph split in two comes out UNDECIDABLE-SPLIT.
  - **R units.** The R form of REPEAT and of SPLIT each has its own planted
    case.
  - **R.**
    - A heading renamed onto another section's name comes out decided and
      `WRONG`.
    - A name that disappears gives `#REF!`, and so does a duplicated name.
    - A `#` line inside a code fence is not a name.
    - The copied `slugs()` and `regions()` match their source lines at
      `d51ce09` byte for byte.
  - **Plants.** `harness/prereg2_plants.py` prints `PLANTS: PASS` and goes
    red on a mutated plant.
  - **Reproduction script (F9).** It regenerates `single-leg-01`'s record byte
    for byte.
  - **E and S enumerators.** A repository that holds `single-leg-01` as one
    commit yields that record. An empty repository exits non-zero.
  - **M filter and §6.3 rule.** A generated key in a file's own fence excludes
    the file. The same key inside an HTML comment does not.
  - **Sampler.** Removing an item that was not selected leaves the sample
    byte-identical.
  - **Distinct count.** A duplicate is counted once.
  - **Decided rule.** One decided instance plus one undecidable instance
    counts as decided.
  - **Floor.** 299 gives NO VERDICT, 300 gives NOT FOUND, and an empty cell
    gives NO VERDICT, never zero.
  - **Arm 0 bar.** A planted corpus over 10% stops its arm.
  - **Export validator.** It rejects a packet that carries a count.
  - **Void rule.** It fires on a plant that crosses the B/C line, and on a plant
    whose question 3 or question 4 answer mismatches. It does not fire on A↔B
    confusion.
  - **Aggregator.** Empty input gives no verdict and exits non-zero.
- **V4.** A mutation sweep over the new gates, in the style of
  `armed_check.sh`. Each mutation is hash-verified, and a mutation that does
  not apply is reported as BROKEN. It passes only if every mutant is killed,
  with none surviving and none BROKEN.
- **V5.** `armed_check.sh`, `--selftest-selection`, `selection_guard_red.sh`
  and `oracle_limitation.py` stay green and armed.

**Commit order.** These are separate commits, in this order:

1. validation, with the harness sha and the hash of the sealed manifest;
2. Arm 0 results;
3. scoring-arm results and the export;
4. `tiers.jsonl`;
5. the sealed manifest, the join and the verdict.

**The harness at the validation commit is the implementation, and its sha is
recorded in `LOG.md`.**

**Gaps.** A gap is a definition here that the harness cannot implement as
written. What happens depends on when it is found:

- **Before the Arm 0 commit.** A gap, shown by a committed red test, stops
  the work, and the owner may supersede this pre-registration.
- **Between the Arm 0 commit and the scoring-arm commit.** A gap may be
  declared only with a committed red test that shows it. It makes the affected
  cells NO VERDICT, and it is not grounds to supersede.
- **After the scoring-arm commit.** No gap claim, code change or later
  supersession alters any cell.

## 10. Amendment rules

**Frozen when this merges:** §0, §2–§8, §9's commit order, the gap rules and
the V-failure rule, §10 itself, and Appendices A and B.

- **A frozen section that is wrong.** Before the Arm 0 commit it may be
  replaced by a further pre-registration. After that commit, no further
  pre-registration may address this question in a way that changes any cell
  or the overall verdict computed here. That verdict is published first.
- **§1 and §9's V-list.** These may be corrected only where they are wrong
  about a fact. Each correction is logged below, with the original wording.
- **Pins.** Pins never change.

Edits made while this is a draft PR are not amendments.

| date | section | change, with the original wording | reason |
|---|---|---|---|

## Appendix A — the tierer's prompt, verbatim

> You are answering questions about records from an experiment. Work only with
> the files in this directory. Do not open, search for, or fetch any kindspec
> repository, issue or pull request, locally or over the network.
>
> Each packet describes one hypothetical reference — a quote anchor or a name —
> taken against a "before" file and resolved against an "after" file. It gives
> the target the mechanism resolved to and the target an independent oracle
> says is correct. They differ. Read the four questions in the packet.
>
> For every packet, answer the four questions from the files alone. If you
> cannot answer question 1 or question 2, set `"unplaceable": true` and say
> why.
>
> Write one JSON object per line to `tiers.jsonl`:
> `{"packet": <name>, "q1": "yes"|"no", "q2": "yes"|"no",
> "q3": "yes"|"no", "q4": "yes"|"no", "unplaceable": true|false,
> "why": <one line>}`.
>
> Write each line as you decide it, and do not revise a line once it is
> written. Stop when every packet has a line.

## Appendix B — planted packets, verbatim

The texts below are the plants' before and after files. Their packet fields
are not written by hand. `harness/prereg2_plants.py` produces them by running
TLLC in its one-leg form and the hardened quote resolver at `d51ce09`. Block
indices count from 0 and include headings. In every plant, the reference is the
quote of the anchored block.

**P-A.** Expected answers: q1 yes, q2 yes, q3 no, q4 no. Expected tier: **A**.

Before:

    ## Ingest service

    Failed jobs are retried three times
    before an alert is raised.

    ## Export service

    Exports are written to the archive bucket nightly.

After: Ingest's first line reads `five` in place of `three`, and the
unchanged two-line block is appended after the Export paragraph, under Export.

- Anchored block: 1.
- TLLC: `SURVIVED`, target 1 (Ingest's edited block).
- Hardened resolver: `EXACT`, target 4 (the copy under Export).
- REPEAT: decided.

**P-B.** Expected answers: q1 yes, q2 no, q3 no, q4 no. Expected tier: **B**.

Before:

    ## Project Alpha

    Alpha moves sandbox telemetry into the shared pipeline.

    Status: this proposal was approved by TOC vote on 2026-03-04.

    ## Project Beta

    Beta adds a conformance badge to the landscape.

    Status: this proposal was approved by TOC vote on 2026-03-04.

After: Alpha's description reads `Alpha was rescoped to cover only audit
logs.`, and Beta's reads `Beta moves sandbox telemetry into the shared
pipeline.`. Nothing else changes.

- Anchored block: 2 (Alpha's status line).
- TLLC: `SURVIVED`, target 2.
- Hardened resolver: `EXACT_CTX`, target 5 (Beta's status line).
- REPEAT: decided.

**P-C.** Expected answers: q1 no, q2 no, q3 no, q4 no. Expected tier: **C**.

Before:

    ## Maintenance windows

    > **Note:** All times in this section are UTC.

    Windows open at 02:00 and close at 04:00 on Sundays.

    Emergency windows may open at any time with one hour's notice.

    > **Note:** All times in this section are UTC.

After: the block order is heading, Emergency sentence, Note, window sentence,
Note. The window sentence reads `03:00 and close at 05:00`.

- Anchored block: 4 (the second Note).
- TLLC: `SURVIVED`, target 2.
- Hardened resolver: `EXACT_CTX`, target 4.
- REPEAT: decided.
