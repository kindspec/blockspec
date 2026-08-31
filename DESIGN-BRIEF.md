<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# blockspec — design brief

Carried forward from the research and build that produced rowspec 0.1.0. Nothing
here is a specification; it is the state a fresh design pass should start from,
so that pass argues about the open questions rather than rediscovering the
settled ones.

---

## 0. Settle this before anything else

Every substantive defect found while building rowspec was found by **two
independent implementations disagreeing** — an author who had written the
reference, and an author forbidden to read it, each measured against the same
fixture tree. That found uncaught crashes, three stale-value bugs, an illegal
`#REF!` shape, a valid file being wrongly refused, and a §6 violation present in
*both* implementations at once.

**A format that does not exist yet has nothing to disagree with.**

And the discipline cannot be added later: rowspec's second implementation
drifted 117 cases behind the moment nothing ran it, and nobody noticed until it
was wired into CI as a hard gate.

So the first decision of the blockspec pass is a *process* decision, not a
format one: **how does this format get an adversary from day one?** Plausible
answers include writing the conformance suite before any implementation,
commissioning two implementations in parallel from the same prose, or treating
an existing document processor as the second opinion. Pick deliberately.

## 1. Decided, with the measurement

**The canonical artifact is UTF-8 text, one document per file, hand-editable.**
Forced by git rather than by taste: a serialized AST loses the merge experiment
badly, and the Pandoc AST loses the *archival* experiment outright.

**The in-memory model is an AST with an attribute triple on every node**
(`id`, `classes`, `key=value`), Pandoc-shaped. It is derived and disposable, and
is never committed.

**A prose block gets NO minted id.** This is the sharpest difference from
rowspec, and it is measured, not aesthetic:

    corpus           minlen  prose blocks  dup in file
    rust-book            40          2938    0 (0.00%)
    obsidian-help        40          2515   16 (0.64%)

A prose block of ≥40 characters is unique within its file in 100.0% of
rust-book's blocks and 99.4% of obsidian-help's. **Code and raw HTML are not** —
raw-HTML blocks in rust-book duplicate at 23.6% within a single file.

The residual ambiguity is *detectable at resolve time*: the resolver reads the
whole file and sees two matches, so it becomes a loud error rather than a silent
wrong answer. Minted ids have no such property.

**The tree is not sufficient.** Comments, annotations and tracked changes
provably do not nest. Anything spanning structure must live in **standoff** with
stable anchors — which is the real reason attributes are non-negotiable, and the
real reason markdown is disqualified rather than merely unfashionable.

**Do not reuse rowspec's syntax.** *"One syntax is a trap; one MODEL, several
grammars is the sound version."* JATS learned this in 2003 and encoded the
lesson architecturally.

## 2. Open, and genuinely undecided

**djot or markdown?** The research says djot — *"but only if you own a parser
dependency you are willing to maintain."* rowspec is standard-library-only and
that constraint has paid for itself repeatedly. Taking a parser dependency is a
real reversal and should be argued, not assumed.

**What is a block, exactly?** The unit of identity has to be defined before
anything else can be. Paragraph? Any top-level node? Does a list count as one
block or many?

**Quote-anchoring's failure modes.** Anchoring to content means an edit to the
content moves the anchor. The 40-character measurement says collisions are rare
and detectable; it does not say what happens when an anchored block is *edited*
rather than duplicated.

**What is the merge failure this format prevents?** rowspec has a specific,
demonstrated one: two branches insert rows, git merges cleanly, the total is 480
where the truth is 660. **blockspec does not yet have its equivalent, and should
not be built until it does.** If prose has no silent-wrong-merge of comparable
severity, that is a finding, and the honest response is a smaller format or
none.

## 3. The method that must carry over

- The **conformance suite is the deliverable**; the spec exists so the suite has
  something to check.
- **The suite is not written by whoever writes the implementation.** A standing
  role, not a review step.
- **The mutation gate**: deliberately break the implementation, and the suite
  must notice. A surviving mutant is a failure, and so is a *stale* one whose
  pattern no longer matches — because a check that quietly stopped running is
  the failure this project keeps finding in itself.
- **Measure before deciding.** Every rowspec question settled by reading was
  wrong at least once; every one settled by measuring both implementations first
  was right.
- **Cell counts lie.** Corpus frequency is inflated by replication and fill-down;
  the unit that matters is a *distinct authored expression*.

## 4. Where the prior work lives

The research, experiments and findings that produced the above are in the
`working-git-backed-gws` design workspace: `D5-document-models.md` (syntax and
model), `D8-identity.md` (the uniqueness measurements), `DESIGN.md` (the overall
verdict), and rowspec's own `docs/rationale.md` (what was measured, and what was
measured and found wanting).
