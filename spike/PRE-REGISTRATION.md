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

D8 reports two acceptance strategies, `naive` and `hard`. Both are given here
because quoting only one would misrepresent the source:

> **Amended 2026-09-09 — see the amendment log in §8.** As registered, this
> section rested on figures D8 had transcribed by hand, with no committed
> harness output behind them. kindspec/research#3 has since re-run the harness
> and committed its output, and one figure changed. What follows is the amended
> text; the original wording is quoted in §8 so it can be compared.

`anchor_eval3.py`, re-run 2026-09-09 against pinned clones and committed as
`research/experiments/D8-identity/results-anchor3.txt`:

```
rust-book gap=5      849 oracle-confident anchors (74% of sample)   prose=460
   naive  SILENT-WRONG 0.47% (n=4)   by type: code=3 html=1
   hard   SILENT-WRONG 0.12% (n=1)   by type: code=1

rust-book gap=25     200 oracle-confident anchors (38% of sample)   prose=124
   naive  SILENT-WRONG 2.00% (n=4)   by type: code=4
   hard   SILENT-WRONG 1.00% (n=2)   by type: code=2

obsidian-help gap=5  343 oracle-confident anchors                   prose=240
   naive  SILENT-WRONG 0.58% (n=2)   by type: list=1 prose=1
   hard   SILENT-WRONG 0.00% (n=0)

obsidian-help gap=25 too few (0) — not a measurement

cmspec gap=5          73 oracle-confident anchors                   prose=53
   naive  SILENT-WRONG 0.00% (n=0)
   hard   SILENT-WRONG 0.00% (n=0)

cmspec gap=25         56 oracle-confident anchors                   prose=36
   naive  SILENT-WRONG 0.00% (n=0)
   hard   SILENT-WRONG 0.00% (n=0)
```

**The load-bearing fact is still the by-type breakdown, and it is now narrower
than as registered: under the hardened acceptance policy, not one silent-wrong
is typed `prose`, in any of the five measuring arms. Under the naive policy that
holds in four arms; `obsidian-help` gap=5 has one.**

**That one matters and is not waved away.** It is
`en/Obsidian Sync/Version history.md` — a YAML frontmatter block resolving onto
`## Sync history`. `btype()` has no rule for frontmatter so it falls through to
`prose`, and substantively it is structured data, which is the category the
whole explanation below turns on. But *the harness prints `prose`*, and a
pre-registration does not get to reclassify its own inconvenient data point. The
hardened policy refuses it outright — `REFUSED_LOWENTROPY`, 17 distinct
characters against a threshold of 24 — so the refusal is a real mechanism firing,
not a lucky anchor.

**Two things this section will not do.** It will not use the denominator: D8's
"885 prose-block anchors in three corpora" reconciles exactly at D8's own pin —
460+124+**212**+53+36 — so §1 as registered was wrong to say it did not, and
wrong about why. But it sums five arms across three corpora and re-samples one
corpus at two gaps, so it counts anchor *evaluations*, not distinct blocks; and
that `212` is a pin-era figure the table above now prints as `240`, giving 913 on
a current clone. A denominator that changes with the clone is not one to build a
claim on. And it will not gate on the
naive policy, which is no longer stable across clones.

**The gate this spike must pass is therefore: zero `prose`-typed silent-wrongs
under the hardened policy, in each of the five measuring arms.** Not "0.00%
silent-wrong" — hardened is 0.12% and 1.00% in the two `rust-book` arms, both
typed `code`. The qualifier is the claim.

D8's own explanation is the one that matters: those blocks fail *because they are
structured data wearing prose clothing*, and structured data is what nominal
addressing already covers. Computed anchoring works precisely where nominal
addressing is unavailable, and fails precisely where nominal addressing is
already mandatory.

**So the honest prior is that prose does not have rowspec's defect**, and this
spike is testing a residual, not fishing in open water — though the amendment
above moves that prior slightly toward the spike's favour, not away from it, and
that is stated rather than buried. A positive finding has to
be strong enough to overturn a measurement that already exists — while noting
that the measurement's own coverage falls to 38% of the sample at gap=25, and
that D8 §11 says so itself. Registering that expectation now, at the strength the
evidence actually supports, is the point of registering anything.

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
   `rowspec/SPEC.md` §11 rule, because none of those travel. That section also
   carries the corollary this experiment depends on: `git merge-tree` reports
   only the paths where git *failed*, so a tool that inspects conflicts alone
   cannot see a clean-but-wrong merge at all.
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
| **A** | A **derived or transcluded** value or passage in the merged document is wrong — a count, an index, a transcluded figure, or transcluded prose that silently resolves to different content than it did in both parents | yes, this is rowspec's defect exactly |
| **B** | A reference resolves silently to the wrong target, and the reference carries an assertion about that target | yes |
| **C** | A reference resolves silently to the wrong target, carrying no assertion — a bare "see also" | **no** — report it, do not build on it |
| **D** | Content is reordered, duplicated or dropped in a way both authors would reject, but nothing asserts anything false | **no** — this is an ordinary bad merge and CSV has it too |
| **E** | The merge conflicts, or the reader refuses the file | **no** — this is the format working |

**Tier A explicitly covers transcluded content, not only transcluded values.**
§2.3 names transclusion as one of the three unmeasured mechanisms, and it is
plausibly the likeliest to hold a defect, because *a transclusion does not
describe its target — it becomes it*. A transcluded paragraph that silently
re-resolves is neither a computed value nor a reference asserting something about
a target, so on a narrower reading of A it would fall between A and B with
nowhere to go. It goes in A. Recorded here because §8 means it could not be
placed later.

### 4.1 Who assigns the tier, and when — normative

§3.1 refuses human judgement as an oracle for *falsity*. Tiering is a different
question and is unavoidably a judgement call, so it gets a procedure instead of a
prohibition.

- **The tier is assigned from the written definitions above, before the frequency
  of that shape is computed**, by someone who has not seen the frequency.
- The tier and its one-line justification are **recorded at the moment of
  assignment**, in the spike's own log, not reconstructed for the write-up.
- **A tier is never revised upward after a count is known.** It may be revised
  *downward* at any time — a result can always turn out weaker than first
  assigned, never stronger.
- Where the assigner cannot place a case from the definitions alone, it is
  recorded as **UNPLACEABLE** with the reasoning, and reported as such. An
  unplaceable case is not a finding, and inventing a tier for it is exactly the
  move this section exists to prevent.

Without this, nothing stops a shape being promoted to tier B once it turns out to
be common — which is §0's failure mode reproduced one level down, inside the
document written to prevent it.
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
if the spike's harness does not reproduce D8's typed-prose result, the harness is
wrong and nothing else it reports means anything.

**Settled 2026-09-09 — `cmspec` is a full control arm.** As registered, this
section held `cmspec` out on the suspicion that its D8 line might be summarising
an arm skipped as `too few`. The re-run in kindspec/research#3 shows it was
measured in both arms — 73 and 56 oracle-confident anchors, 0.00% silent-wrong
under both policies. The arm actually skipped as `too few (0)` is
`obsidian-help` gap=25, which is why D8 never listed it, and which is a sampling
artefact rather than corpus shallowness: 13 of 176 files carry the required
depth, but the `seed=7` sample draws none deeper than 19.

**`rust-book` is the strongest control** — every arm reproduced to the digit,
including oracle-confident subsets 999 / 849 / 200 and sample sizes
1087 / 1141 / 533. `obsidian-help` has moved and its gap=5 arm no longer matches
what D8 printed, so it is a control on the *mechanism*, not on the figures.

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

### 5.1 Corpora named 2026-10-06, before the arm runs

This subsection is itself a measurement — of candidate corpora, not of the
merge behaviour §3 is about. §5's "before any measurement runs" means the arm's
own measurement, which has not run.

**The metric is accepted cases, not both-sides pairs.** An earlier draft of this
subsection ranked candidates on how often the same `.md` file is changed on both
sides of a two-parent merge, and said that is what `find_merge_cases` selects.
It is not. The function then drops convergent identical edits, add/add, and
delete/modify, and those drops are most of the population in a corpus that
syncs. Running the harness's own classification at the registered pins:

    corpus                both-sides  convergent  add/add+del  ACCEPTED
    github/site-policy          1321        1193           50        78
    cncf/toc                     100          20            9        71
    kubernetes/website            17           2            1        14   (400 merges)
    rust-book (control)          190           3            8       179

`site-policy` loses 90% of its headline figure to convergent identical edits.
Ranked on what the harness will actually evaluate, its 43.6% both-sides ratio
buys 78 cases against `cncf/toc`'s 71 — not 13× more, within 10%. Both are below
the control's 179.

**Merge author is a weak proxy, and it misleads in both directions.** Of the
accepted cases, by the author of the merge commit:

    corpus                ACCEPTED   human-authored merge   bot-authored merge
    github/site-policy          78                     29                   49
    cncf/toc                    71                     71                    0
    kubernetes/website          14                      1                   13

Taken at face value that makes `kubernetes/website` the worst candidate. It is
the opposite, and the merge subjects say why:

    kubernetes-prow[bot] | Merge pull request #57833 from xirehat/57743
    site-policy-bot      | Merge branch 'main' into automated-sync-25245277497

Kubernetes merges every human pull request through Prow, so a bot-authored merge
there carries human content — only the button is automated. `site-policy` is a
one-way mirror of another repository, and `site-policy-bot` is merging its own
generated export branch back into `main`. The same label covers a bot that
merges people's work and a bot that merges its own, and only the second is
disqualifying. Whoever extends this arm should classify on what produced the
*content*, not on who recorded the merge.

**Chosen, and pinned:**

| corpus | source | pin | shape |
|---|---|---|---|
| `k8s-website` | `github.com/kubernetes/website` | `6b27baef1e44275fd4368e14375296e1dfe5af11` | i18n |
| `cncf-toc` | `github.com/cncf/toc` | `144c2e3215884e498e744cc51e6b7cef82d654f1` | governance minutes |
| `site-policy` | `github.com/github/site-policy` | `b9578b546d2506febda1da2cd7431644d58e512c` | legal and policy text |

Ranked by evaluable human-authored cases, which is the ranking that survived
measurement:

- **`k8s-website` is the largest arm.** 14 accepted in the 400 most recent of
  23,473 two-parent merges, essentially all human content through Prow.
  Extrapolated, roughly 800 accepted cases over full history — more than four
  times the control. **That figure is an extrapolation from a 400-merge sample
  and is labelled as one;** enumerate the full history before quoting it.
- **`cncf-toc` is the cleanest arm.** 71 accepted, every one a human-authored
  merge, no bot involvement at all, and it is the minutes shape §2.2 names
  first. The smallest absolute count of the three and the least ambiguous.
- **`site-policy` is the smallest real contribution and stays as a supporting
  arm.** Of its 78 accepted cases, 49 are the bot merging its own sync branch,
  leaving about 29 that are genuinely two parties editing near-duplicate legal
  text. That shape is exactly what §2.2 predicted and nothing else in the
  candidate set has it, which is why it stays — but 29 cases, not 1321, is what
  it brings, and a result quoted from this arm must say which cases it used.

Pins are recorded because a corpus that moves between registration and run turns
drift into a finding; §3.2's `obsidian-help` arm is what that costs.

**§5's bot exclusion, re-run on the right denominator.** The exclusion is for a
corpus "predominantly single-author or bot-generated", and it exists because the
concurrent case is the thing being tested — so the population that matters is
the cases the arm selects, not the commit log. An earlier draft cleared
`site-policy` on commit share (32% bot) while the arm selects on merge pairs,
where the bot is 1174 of 1321, or 89%. That is a guard measured on a denominator
the selection does not use, which is one of the shapes this project keeps
catching in itself. On accepted cases the bot share is 63%, which is why
`site-policy` is demoted rather than primary. It is not excluded outright
because its 29 human cases are real and are the only legal-text coverage
available.

**Author count does not predict concurrency.** 46 authors at `site-policy`
against 6,706 at `kubernetes/website` settles that much, and it is worth
recording because §5 as registered asked for "real multi-author git history",
which selected for the wrong property. What this arm needs is documents that get
edited together. The stronger claim — that the relation is close to inverse — is
not supported: ordered by author count the ratios go 46 → 43.6%, 523 → 0.5%,
711 → 1.3%, 6,706 → 0.015%, which is not monotone.

**Excluded, with the reason:**

- **`python/peps`** — excluded on volume. Over `.md` and `.rst` it has one
  both-sides path; over all paths, including the `.txt` era that covers most of
  its history, 11 both-sides against 807 one-side, a ratio of 1.3% that is
  slightly *above* the control's 1.1%. So it is not that PEPs have no
  concurrency — that reading was an artefact of the extension filter. Eleven
  pairs cannot carry an arm, and that is the reason. Recorded because §5 named
  proposal repositories first and the measurement refused them.
- Any corpus predominantly single-author or bot-generated, per the exclusion
  above, measured on the cases the arm selects.

**How these were measured.** `git rev-list --merges`, then per merge
`merge-base --all` (skipping multiple bases), `diff --name-only base parent` on
both sides for the shared paths, then `show` on base and both parents to apply
the harness's convergent and add/add and delete/modify drops. `cncf/toc` reports
100 both-sides here against 101 by the cruder count, the difference being one
merge dropped at `multi_base` before counting.

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

**§1 and §2 record prior evidence rather than criteria.** They decide nothing, so
a factual error in them is corrected rather than preserved — but the correction
is logged in full here, with the original wording, because a reader cannot
otherwise distinguish a good-faith correction from a convenient one. §7's method
constraints are likewise amendable only where they are wrong about a fact, never
where they are inconvenient.

| date | section | change | reason |
|---|---|---|---|
| 2026-10-06 | §5 | Named and pinned three duplicate-heavy corpora — `kubernetes/website`, `cncf/toc`, `github/site-policy` — ranked by evaluable human-authored cases. `python/peps` excluded on volume. §5.1 carries the measurement. | The corpus-list amendment §5 requires and §8 permits, made before the arm runs. A first draft of §5.1 ranked on both-sides pairs and claimed that is what `find_merge_cases` selects; it is not, and running the harness's own classification cut `site-policy` from 1321 to 78 accepted, 49 of those being a bot merging its own sync branch. The ranking inverted. Also corrected: the bot exclusion had been cleared on commit share while the arm selects on merge pairs, and merge author turned out to be a proxy that misleads in both directions. |
| 2026-09-10 | §1, §8.2 | Withdrew the claim that the old `obsidian-help` bucket line "cannot be reconciled per-bucket"; it reconciles at `a3985b58` as `2+78+90+212+2 = 384`, the line having been truncated to its three largest buckets. Qualified the 885 reconciliation as pin-dependent. | Reproduced by the spike harness at `a3985b58`, not at §3's pin — see kindspec/research#8, which corrects the same conflation. A correction that itself carried two false claims. |
| 2026-09-09 | §5 | `cmspec` promoted from held-out to full control arm; `rust-book` named the strongest control and `obsidian-help` demoted to a mechanism control. | The re-run shows `cmspec` was measured in both arms, not skipped; the skipped arm is `obsidian-help` gap=25. `obsidian-help` has moved since D8 ran. This is the corpus-list amendment §8 expressly permits, made before measurement begins. |
| 2026-09-09 | §1 | The claim narrowed from "not one is typed `prose`, in either strategy, in any arm" to "not one is typed `prose` under the **hardened** policy, in any of the five measuring arms" — naive now has one. Table replaced with committed harness output. | kindspec/research#3 re-ran the harness and committed its output for the first time; `obsidian-help` has moved and one naive silent-wrong is now typed `prose`. Forced by evidence outside this spike, before this spike measured anything. See kindspec/blockspec#7. |

### 8.1 The original §1 wording, for comparison

Registered before any measurement, superseded 2026-09-09:

> ```
> rust-book gap=5    849 oracle-confident anchors (74% of sample)   prose=460
>    naive  SILENT-WRONG 0.47% (n=4)   by type: code=3 html=1
>    hard   SILENT-WRONG 0.12% (n=1)   by type: code=1
>
> rust-book gap=25   200 oracle-confident anchors (38% of sample)   prose=124
>    naive  SILENT-WRONG 2.00% (n=4)   by type: code=4
>    hard   SILENT-WRONG 1.00% (n=2)   by type: code=2
>
> obsidian-help g=5  384 oracle-confident anchors                   prose=212
>    naive  SILENT-WRONG 0.52% (n=2)   by type: list=2
>    hard   SILENT-WRONG 0.26% (n=1)   by type: list=1
> ```
>
> **The load-bearing fact is the by-type breakdown, and it is what this spike
> relies on: every silent-wrong D8 recorded is typed `code`, `html` or `list`.
> Not one is typed `prose`, in either strategy, in any arm.**
>
> That much is reproducible from the table above. **The denominator is not** […]
> The claim this spike proceeds on is therefore **"zero typed-prose
> silent-wrongs across the three arms D8 printed"**, which the by-type breakdown
> supports on its own, and not a rate over an unbacked denominator.

### 8.2 What did not change, and why that is the point

**§3, §4 and §6 are untouched.** The five conditions for FOUND, the severity
ranking with transclusion in tier A and the §4.1 tiering procedure, and what each
outcome publishes as — all stand exactly as registered.

That split is doing real work here. The amendment **moves the prior slightly
toward the spike's favour**: the evidence against prose having this defect is now
marginally weaker than as registered, because one naive silent-wrong is typed
`prose` where none was before. If the criteria were amendable, this is precisely
the moment a bar would drift — a document that had just watched its own prior
soften, quietly relaxing what counts as a finding. They are not amendable, and
nothing about §3, §4 or §6 has moved.

A note on the old `obsidian-help` line, because this document previously
misdiagnosed it and the misdiagnosis reached kindspec/research as well. The
registered table showed `heading=78 list=90 prose=212` against a printed `384`,
which does not sum, and both this section and D8 §3.2 concluded the figures
"cannot be reconciled per-bucket at all". **They reconcile.** Re-running the
harness against `a3985b58` prints the full bucket list — that tree, not
research §3's pin `327a782e`, which gives `anchors=343` and a different bucket
list for the same arm:

    obsidian-help en/*.md gap=5  oracle-confident anchors=384
       block types: code=2 heading=78 list=90 prose=212 table=2

`2+78+90+212+2 = 384`. The old line was **truncated to its three largest
buckets**, not corrupted — which also disposes of the guess that a `code=4`
bucket had gone missing. kindspec/research#8 carries the same correction, and
also corrects the tree: `a3985b58` is the commit the local corpus cache sat at,
seven first-parent commits behind §3's pin. Two repositories used "pin" for two
different trees, and this paragraph had the wrong one.

§8.1 quotes §1 as registered, uncorrected, because that is what it actually
said.
