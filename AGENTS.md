# AGENTS.md

Instructions for AI coding agents working in this repository.

**Read the org contract first:**
[kindspec/.github/AGENTS.md](https://github.com/kindspec/.github/blob/main/AGENTS.md)
— the two standing rules, the worktree information barrier, the review gate, and
the conventions that travel between kinds. This file carries only what is
specific to blockspec, and wins where the two conflict.

## Status

**Nothing is specified yet.** blockspec is the **blocks kind** — identity is
deliberately no minted ids — alongside [rowspec](https://github.com/kindspec/rowspec) and [nodespec](https://github.com/kindspec/nodespec).

There is no `SPEC.md`, no conformance suite and no implementation, and saying so
is cheaper than being asked.

## Before writing anything

**Read `DESIGN-BRIEF.md` completely.** It carries what is already decided *with
the measurement that decided it*, what is genuinely open, and the one process
question that must be settled first. It exists so this design pass argues about
the open questions rather than rediscovering the settled ones.

The evidence it cites lives in
[kindspec/research](https://github.com/kindspec/research) —
`design-findings/` and `experiments/`. Cite it by path and commit. The corpora
themselves are not redistributed; `CORPORA.md` names each one and its source.

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
