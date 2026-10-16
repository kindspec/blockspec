# AGENTS.md

Instructions for AI coding agents working in this repository.

**Read the org contract first:**
[kindspec/.github/AGENTS.md](https://github.com/kindspec/.github/blob/main/AGENTS.md)
— the two standing rules, the worktree information barrier, the review gate, and
the conventions that travel between kinds. This file carries only what is
specific to blockspec, and wins where the two conflict.

## Status

**Draft 0 is decided, and `SPEC.md` writes it up.** blockspec is
the **blocks kind** — identity is deliberately no minted ids — alongside [rowspec](https://github.com/kindspec/rowspec) and [nodespec](https://github.com/kindspec/nodespec).

Draft 0 is what `docs/adjudications/` 0001, 0002 and 0003 decide; `SPEC.md`
restates it, defers to them, and lists what they leave open. 0003, anchors
and transclusion, has cases under `conformance/cases/anchor/`, written blind
from `main` by an author who had not read the resolver, and an
implementation, `reference/blockspec/anchor.py`, which was written before
those cases and then run against them with no case changed. The spike's binding verdict is FOUND, under an owner ruling that
overrides frozen rules; see `spike/README.md`, The verdict. `conformance/cases/` holds draft 0's conformance cases.
Those for 0001 and 0002 were written before any implementation existed, and
the reader, `reference/blockspec/document.py`, was written afterwards against
them and `docs/adjudications/`, with no case changed. For 0003 the order was
the reverse, as above: the resolver came first, and its cases were written
without reading it. CI checks the tree itself, and runs it against the
reference (`just conform`). There is no second implementation.

The mutation gate, `just mutants`, is not in CI: it reports mutants the tree
does not kill, which are holes for the case author to close, not bugs in the
reference. It gates the reader and the anchor resolver, each with its own
table in `conformance/mutants.py`. Run it to see the current list. Saying so is cheaper than being
asked.

## Before writing anything

**Read `DESIGN-BRIEF.md` completely.** It carries what is already decided *with
the measurement that decided it*, what is genuinely open, and the one process
question that must be settled first. It exists so this design pass argues about
the open questions rather than rediscovering the settled ones.

The evidence it cites lives in
[kindspec/research](https://github.com/kindspec/research) —
`design-findings/` and `experiments/`. Cite it by path and commit. Its
`CORPORA.md` names each corpus and its source. The spike's experiment packets
and results carry corpus excerpts, and whole corpus files in the prereg 2 and
prereg 3 export packets, under their upstream terms; `NOTICE` lists each
corpus, its pin and its licence.

## The constraint specific to this kind

**This kind must earn its existence before it is built.** The brief says so
explicitly, and a finding that it does not is a legitimate and valuable outcome —
the same standard rowspec applies to itself in its own README: *"if your table is
a list of facts, you probably do not need this."*

An experiment that decides whether a format should exist has its criterion
**pre-registered**: written down and committed before the experiment runs, so the
bar cannot move once the results are in.

## Do not

- **Do not reuse rowspec's syntax.** One syntax for documents and tables is a
  trap; one MODEL, several grammars is the sound version. JATS learned this in
  2003 and encoded the lesson architecturally.
- **Do not port rowspec's identity design.** It does not transfer, and the brief
  explains why with the measurement.
- **Do not write an implementation before the conformance cases exist.** A format
  that does not exist yet has nothing to disagree with, and the adversarial
  discipline cannot be retrofitted — rowspec's second implementation drifted 117
  cases behind the moment nothing ran it.
