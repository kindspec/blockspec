# blockspec

**Status: draft 0, defined by its decisions and its conformance cases.**
Draft 0 is what `docs/adjudications/` decides, and `SPEC.md` writes it up:
0001, a pinned CommonMark 0.31.2 block-level profile with `<!-- #name -->`
region markers, and 0002, what a block is, each with addenda, and 0003,
how comments, suggestions and transclusions anchor. 0003 has no cases and no
implementation yet. `conformance/cases/` encodes 0001 and 0002 and came first, before any
implementation existed. `reference/blockspec/` is a standard-library-only
implementation written against that tree, and CI runs the tree against it
(`just conform`). There is one implementation, so nothing disagrees with it
yet.

The pre-registered spike, `spike/` (blockspec#2), asked whether prose has a
silent-wrong-merge worth a format. Its binding verdict is **FOUND**:
pre-registration 3's tier-run, run a second time under an owner ruling that
overrides four of that document's frozen rules (`spike/LOG.md` §34–§35). The
ruling was made after run 1's answers and its INCONCLUSIVE verdict were
public, and run 2 is what turned the verdict into FOUND.
Read the ruling, its disclosures and the noise figures beside the verdict
before relying on it. Start at `spike/README.md`.

blockspec is the **block kind** in [kindspec](https://github.com/kindspec) — a
specification and conformance suite for prose documents that must survive
version control, alongside [rowspec](https://github.com/kindspec/rowspec) (the
row kind).

Each kind is named after its **unit of identity**, because identity is the hard
part of every one of them:

| | unit | identity | status |
|---|---|---|---|
| [rowspec](https://github.com/kindspec/rowspec) | rows | opaque row ids | draft 0, published |
| **blockspec** | blocks | **deliberately no minted ids** | draft 0: decisions, cases, reference |
| [nodespec](https://github.com/kindspec/nodespec) | nodes | named, not positional | spike closed, not started |

## The thing that makes this different from rowspec

A row gets an opaque id. **A prose block does not**, and that is a measured
decision rather than a stylistic one — see `DESIGN-BRIEF.md`.

That single difference is why this is a fresh design pass and not a port. The
prior research is explicit about the trap: *"Do not use one syntax for documents
+ tables + slides. One syntax is a trap; one MODEL, several grammars is the
sound version."*

## Before writing anything

Read `DESIGN-BRIEF.md`. It carries what is already decided and measured, what is
still open, and — most importantly — the one process question that must be
settled first.
