<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Pre-registration — what would count as a prose silent-wrong-merge

**Status: committed before the experiment runs.** Nothing in this document may
be revised in light of a result. If it turns out to ask the wrong question, the
answer is a second pre-registration that says so and explains why, not an edit
to this one.

Registered against `blockspec#2`. Resolves `blockspec#1`.

---

## 0. Why this exists

`DESIGN-BRIEF.md` §2 makes blockspec conditional:

> rowspec has a specific, demonstrated one: two branches insert rows, git merges
> cleanly, the total is 480 where the truth is 660. **blockspec does not yet have
> its equivalent, and should not be built until it does.** If prose has no
> silent-wrong-merge of comparable severity, that is a finding, and the honest
> response is a smaller format or none.

A conditional that can be reinterpreted after the results are in is not a
conditional. This project has already reached "do not build this" once, and that
verdict is worth something only because the bar could not move afterwards.

## 1. The prior evidence points at NO, and that is stated up front

This is the part a post-hoc bar would quietly omit.

`research/design-findings/D8-identity.md` §3.1–3.2 has **already measured
computed-anchor resolution over real version-control history** — hundreds of real
`(commit_i, commit_j)` pairs from `rust-lang/book`, with the author's real
subsequent edit applied by stock `git merge-file`, against an independent
line-correspondence oracle.

```
rust-book gap=5    849 anchors    SILENT-WRONG 0.47% (n=4)   by type: code=3 html=1
rust-book gap=25   200 anchors    SILENT-WRONG 2.00% (n=4)   by type: code=4
obsidian-help g=5  384 anchors    SILENT-WRONG 0.52% (n=2)   by type: list=2
cmspec  gap=5, gap=25             SILENT-WRONG 0.00% both arms
```

> **Across 885 prose-block anchors in three corpora, there was not one silent
> mis-anchor.** Every failure was a code fence, a raw-HTML block, or a
> table-of-contents list item.

D8's own explanation is the one that matters: those blocks fail *because they are
structured data wearing prose clothing*, and structured data is what nominal
addressing already covers. Computed anchoring works precisely where nominal
addressing is unavailable, and fails precisely where nominal addressing is
already mandatory.

**So the honest prior is that prose does not have rowspec's defect**, and this
spike is testing a residual, not fishing in open water. A positive finding has to
be strong enough to overturn a measurement that already exists. Registering that
expectation now is the point of registering anything.

## 2. What D8 did NOT measure, which is where the spike goes

Three gaps, in descending order of how likely they are to hold a defect.

**2.1 D8 measured rebase, not a two-branch three-way merge.** `git merge-file`
applying one author's real edit is *one* editor moving under a citation. rowspec's
defect needs **two** branches changing different things and git reconciling both
cleanly. Nobody has run the concurrent case for prose with standoff annotations
present.

**2.2 All three corpora are technical documentation in English.** D8 §11 names
this as its own most likely failure: prose-block uniqueness (100% / 99.4% at ≥40
chars) *"may not hold for meeting notes, legal boilerplate, or templated
documents, which are exactly the duplicate-heavy shapes a work substrate will
meet."* That is a written prediction of where the measurement breaks, made before
this spike, and it is the first place to look.

**2.3 Anchoring is not the only mechanism that can assert falsely.** D8 measured
whether an anchor resolves to the right block. A document can also carry
transclusions, cross-references, and tracked changes, and none of those was
tested under merge.

## 3. What counts as FOUND — normative

All five conditions must hold simultaneously. Four out of five is a near miss and
is reported as a near miss.

1. **Stock `git merge` succeeds.** No conflict, no marker anywhere in the tree.
   No merge driver, no `.gitattributes`, no clean/smudge filter, no hook — the
   `SPEC.md` §11 rule, because none of those travel.
2. **The merged file is well-formed** under whatever grammar the experiment
   assumes, and a conforming reader accepts it without error.
3. **The merged document asserts something false**, where *false* is decided by
   an **oracle independent of the merge** — see §4. Not "unexpected", not "not
   what either author intended", not "ugly". False.
4. **The falsehood is not visible in the file.** A reader with the merged file
   and no access to either parent cannot tell. This is the whole distinction
   between a silent-wrong merge and a bad one.
5. **Both parent states were correct.** The defect is created by the merge, not
   carried in by an author.

### 3.1 The oracle requirement, stated separately because it is where this fails

**Without an oracle there is no finding.** rowspec's defect is checkable because
a total is a computed value with one right answer: 480 against a truth of 660,
and LibreOffice will confirm it independently.

Prose has no arithmetic, so an experiment must **construct** its oracle and name
it before running. Acceptable forms:

- **A resolution oracle.** An anchor, transclusion or cross-reference has exactly
  one correct target, established at the parent commit and carried forward
  independently of the mechanism under test — D8's line-correspondence oracle is
  the model, and it must be *a different algorithm at a different granularity*
  from the one being measured.
- **A derived-value oracle.** If the document computes anything — a count, an
  index, a table of contents, a transcluded total — the derived value has a right
  answer computable from the merged content.

Not acceptable: the author's stated intent, a diff that looks wrong, a human
judgement call, or the mechanism under test grading itself.

## 4. Severity — the line, drawn in advance

"Comparable severity" is the phrase doing the work in the brief, so it gets a
definition rather than a vibe.

**A finding qualifies if the false assertion would change a reader's action.**
A comment reading *"this figure is wrong, do not ship"* that silently re-anchors
onto a different, correct figure meets this: it condemns the wrong thing and
absolves the right one, and no one can see it happened.

**Ranked, so the write-up cannot promote a weak result:**

| tier | shape | qualifies |
|---|---|---|
| **A** | A derived value in the merged document is wrong — a count, an index, a transcluded figure | yes, this is rowspec's defect exactly |
| **B** | A reference resolves silently to the wrong target, and the reference carries an assertion about that target | yes |
| **C** | A reference resolves silently to the wrong target, carrying no assertion — a bare "see also" | **no** — report it, do not build on it |
| **D** | Content is reordered, duplicated or dropped in a way both authors would reject, but nothing asserts anything false | **no** — this is an ordinary bad merge and CSV has it too |
| **E** | The merge conflicts, or the reader refuses the file | **no** — this is the format working |

Tier D is called out because it is the tempting one. rowspec's README already
concedes the analogous case: *"Two branches each adding a column conflict badly…
That is inherent to one-row-per-line and it is exactly what happens to a CSV.
Nothing here fixes it."* A prose equivalent is not a reason to build a format.

**Frequency does not substitute for severity.** A tier-A defect at 0.01% is a
finding. A tier-D annoyance at 40% is not.

## 5. Corpora, named now

Fixed before running so the sample cannot be selected after seeing results. Each
is public and already in `research/CORPORA.md` or is added there by the spike.

**Already measured by D8 — the control arm.** Re-run against these first, because
if the spike's harness does not reproduce D8's 0.00% for prose, the harness is
wrong and nothing else it reports means anything.

| corpus | source |
|---|---|
| `rust-book` | `github.com/rust-lang/book` |
| `obsidian-help` | `github.com/obsidianmd/obsidian-help` |
| `commonmark-spec` | `github.com/commonmark/commonmark-spec` |

**The duplicate-heavy arm — D8's own predicted failure point.** At least three of
the following, chosen for templated or boilerplate-heavy prose with real
multi-author git history:

| candidate | why |
|---|---|
| a public RFC/PEP/RFC-style proposal repo | templated section headers, heavy boilerplate |
| a public meeting-notes or governance-minutes repo | the shape D8 names first |
| a public policy, licence or legal-text repo | near-duplicate clauses by construction |
| a public i18n/translation repo | the same sentence many times over |
| a large public wiki or handbook with many contributors | scale plus real concurrency |

The exact repositories are chosen and **committed to this file in an amendment
before any measurement runs**, not after. An amendment naming corpora is
permitted; an amendment changing §3 or §4 is not.

**Exclusion, stated now:** a corpus whose history is predominantly single-author
or bot-generated is out, because the concurrent case is the thing being tested.

## 6. What each outcome publishes as

Both are deliverables. Neither is a failure.

**FOUND (tier A or B).** The write-up is the reproduction: two branches, the
stock-git command line, the merged file, the oracle's verdict, and the frequency
across the corpora. That becomes blockspec's justification, and the design pass
opens with the defect it exists to prevent — as rowspec's does.

**NOT FOUND.** `blockspec` draft 0 is published as a **finding**, not as a
format: prose does not have a silent-wrong-merge of comparable severity, here is
what was measured and how, and here is what would change the answer. The
repository states that it is not being built and why. `DESIGN-BRIEF.md`'s open
questions are answered with "not applicable" and the reasoning is preserved.

This is the same standard rowspec applies to itself — *"if your table is a list
of facts, you probably do not need this"* — and nodespec's brief already
anticipates the verdict: *"Be willing to conclude 'do not build this.' That
verdict has already been reached once in this project's history, correctly."*

**NEAR MISS (tier C or D only).** Published as NOT FOUND, with the near misses
described. A tier-C or tier-D result does not become a tier-B result by being
written up enthusiastically.

## 7. Method constraints

- **Reproduce before reporting.** A silent-wrong merge is demonstrated by an
  actual `git merge` of two actual branches producing an actual file. An argument
  that one could exist is not a finding.
- **The harness must be able to fail.** Before it reports anything, plant a known
  silent-wrong case and confirm the harness catches it; plant a known-clean case
  and confirm it stays silent. Both directions, both demonstrated. A harness that
  has only ever reported one verdict has not been shown to have two.
- **The control arm is the gate.** If the harness does not reproduce D8's prose
  result on D8's corpora, stop and fix the harness.
- **Report what was covered, not what was attempted.** Name the excluded
  population. D8 reported that its oracle's confident subset falls to 38% at
  gap=25 and that its numbers therefore carry real uncertainty; that is the
  standard.
- **Cell counts lie, and so do block counts.** Frequency inflated by templating
  and fill-down is the same trap as `research` #1 and rowspec #28. The unit is a
  distinct authored block, and a corpus that ships the same document six times
  contributes one.

## 8. Amendment log

Amendments to §5's corpus list are permitted before measurement begins and must
be recorded here with a date and a reason. Amendments to §3, §4 or §6 are not
permitted at all; if one of those is wrong, this pre-registration is superseded
by a new one that says so.

| date | section | change | reason |
|---|---|---|---|
| — | — | none yet | — |
