# blockspec

**Status: not started.** This repository is a stub. It exists so the decisions
already made are not lost, and so the design pass can begin from them rather
than from a blank page.

blockspec is the **block kind** in [kindspec](https://github.com/kindspec) — a
specification and conformance suite for prose documents that must survive
version control, alongside [rowspec](https://github.com/kindspec/rowspec) (the
row kind).

Each kind is named after its **unit of identity**, because identity is the hard
part of every one of them:

| | unit | identity | status |
|---|---|---|---|
| [rowspec](https://github.com/kindspec/rowspec) | rows | opaque row ids | draft 0, published |
| **blockspec** | blocks | **deliberately no minted ids** | not started |
| [nodespec](https://github.com/kindspec/nodespec) | nodes | named, not positional | not started |

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
