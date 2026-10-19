<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Adjudication 0004: fewer refusals of surviving text

Pre-registration 4 replayed real document history against 0003's resolver
and found it refusing too much: with labels for truth, 17.0% (16.3% to
18.7%) of comments whose text survived five commits were refused, against a
5% bar (`0003-anchors/replay-verdict.md`). 0003 §12 named that result,
first, as what would reverse its design. This document decides what
changes.

The question:

> Which of 0003's refusals can be narrowed so that a comment on text that
> survives follows it, without letting a comment or a suggestion land on
> the wrong text where 0003 refused or detached it, beyond residuals this
> document names?

## Decision

**Decided by the owner, 2026-10-18,** in the form below, which replaced a
first version the same day and was then scoped to prose (*How it was
reached*). Two changes, both to the resolver (SPEC.md §11.2, §11.4, §11.5);
nothing in a document or a record changes.

- **A. An unchanged leaf's near-copy compares words.** For an `EXACT`
  leaf, §11.4's near-copy check uses a **word similarity**, `2·L/(m+n)`
  over the leaves' words (the text split at runs of tab, LF, CR and space),
  and any unmatched leaf that is not a copy counts. `MOVED` and `EDITED`
  leaves keep 0003's code-point check, and crowded-gap is unchanged.
- **D. On prose, a comment's span needs one side of its context and its
  neighbours.** An `EDITED` span hit needs the code points just before and
  after it to be unchanged (whitespace matching whitespace, a leaf's edge
  matching an edge). On a paragraph or heading, the context compares
  whitespace runs as one space, and a comment needs one side of it that
  holds and is not empty; a suggestion still needs both sides, as 0003 Q13
  said, whitespace aside. On a code block or table, comments and
  suggestions keep 0003's rule: both sides, compared exactly.

## Why each

**A.** The near-copy rules exist for one shape (0003 §4, `spike/LOG.md`
§9): a paragraph reworded while its old wording survives verbatim, so that
the verbatim copy matches exactly and the real descendant is only similar.
For an unchanged leaf the code-point similarity measured that badly: of the
275 near-copy refusals at gap 5 in pre-registration 4, 268 were on
paragraphs whose text had not changed (research `experiments/D8-anchor-replay/prereg4/kinds-gap5.txt` at `a0ea138`). Short, unrelated
leaves reach 0.5 by code points: `[The Slice Type](ch04-03-slices.md)` and
`[Generic Data Types](ch10-01-syntax.md)` score 0.62, and share no word. A
reworded paragraph keeps most of its words, so the shape the rule is for
still refuses. Words leave out the leaf's type, so two one-word headings
with different words are not near-copies of each other; the same word at
another heading level still is.

For `MOVED` and `EDITED` leaves words are not safe: a descendant
re-punctuated (`Set timeout=30, retries=5, backoff=2.` becoming
`Set timeout=30; retries=5; backoff=2;`) has word similarity 0.25 and
code-point similarity above 0.9, and comparing words would let the comment
follow a sibling. Those checks stay
as 0003 wrote them.

**D.** 0003 §5 kept both sides of the context "until a replay of real
history prices the detachments". It priced them: in pre-registration 4,
154 of the 168 `DETACHED` at gap 5 had an intact span whose stored context
had changed (the same file). One side of the context ties the span to
its place in the leaf; the neighbour rule keeps it from running into a
longer token (`4` in `4.5`, `can` in `can't`, `kube` in `kube-proxy`); and
a side whose stored context is empty does not count, so a span at the
leaf's start still needs its suffix. A suggestion writes into the document,
so it keeps 0003's stricter test.

In code and tables, whitespace and the cells beside a span carry meaning
that prose does not: a line's indentation is its scope in Python and its
parent in YAML, and a table row's first cell names what the others
describe. So those leaves keep 0003's exact, two-sided rule. The replay
scores paragraphs only, so the figures below do not depend on this.

## How it was reached

A first version, approved the same day, also narrowed crowded-gap to a
leaf with a rival, used words for every near-copy check (with the leaf's
type as a word), and accepted a comment's or a suggestion's hit on one side
of its context with only its word boundaries kept. Its review built inputs,
run against both resolvers, where it put comments and suggestions on the
wrong text where 0003 refused or detached:

| input | 0003 | first version | this version |
| --- | --- | --- | --- |
| a suggestion on `4` in "4 sigma", now "4.5 sigma" | DETACHED, stale | EDITED, writes "5.5 sigma" | DETACHED, stale |
| a suggestion on `can`, now "can't" | DETACHED, stale | EDITED, applies | DETACHED, stale |
| a comment on unit A's line, unit A rewritten beside a new unit B line | REFUSED(crowded-gap) | EDITED on unit B | REFUSED(crowded-gap) |
| an edited line re-punctuated, a sibling line kept in place | REFUSED(near-copy) | EDITED on the sibling | REFUSED(near-copy) |
| a suggestion whose suffix was rewritten | DETACHED, stale | EDITED, applies | DETACHED, stale |
| an unchanged one-word heading beside a new one | RESOLVED | REFUSED(near-copy) | RESOLVED |

The owner approved the version with those holes closed on the
measurements below. Its own review then found rule D, as first worded for
every leaf type, putting text in the wrong place in code and tables where
0003 detached it, and the owner scoped D to prose:

| input | 0003 | D on every leaf | this version |
| --- | --- | --- | --- |
| a suggestion on `remove(f)`, the line moved out of its `for` loop | DETACHED, stale | EDITED, applies | DETACHED, stale |
| a suggestion on `name: web`, re-parented under `spec:` in YAML | DETACHED, stale | EDITED, applies | DETACHED, stale |
| a comment on row api's limit, the row renamed db | DETACHED | EDITED on db's limit | DETACHED |

## The measurement, and what it is not

Measured with research `experiments/D8-anchor-replay/replay.py` at
`735091e`, against the resolver this document specifies (the change of the
pull request that follows its cases, measured again at that pull
request's merge), on the four arms of pre-registration 4
and its rehearsal arm, site-policy, with the oracle for truth (no labels).
Pooled over the five arms, loud comments over surviving spans, from the
`counted:` lines of each arm's stdout:

| | gap 1 | gap 5 |
| --- | --: | --: |
| 0003's rules (the published `prereg4/replay-ARM.txt` and `rehearsal-site-policy.txt`) | 2.2% | 12.0% |
| this version | 0.9% | 4.8% |

No comment the oracle counts is `WRONG` at either gap. That is weak
evidence for D: the oracle grades a landing on the span's surviving words
as correct, so it cannot see an edit beside the span (*What it gives up*).
`REFUSED(crowded-gap)` is the largest cause left at gap 5, 159 of the 299.

**These rules were chosen on these arms**, so this is not a test of them.
The test is a new pre-registration on held-out repositories, decided by the
owner the same day.

## What it gives up

- **On prose, a comment follows its span through an edit beside it** while
  one side of its context and its neighbours hold: "Unit A: trip at 4.2
  sigma" becoming "Unit B: trip at 4.2 sigma", or "should restart every
  replica" becoming "should not restart every replica". The comment lands
  `EDITED`, shown as changed (SPEC.md §11.6), but the words around it may
  now mean something else; SPEC.md §11.12 names it. This was 0003 Q13's
  cost, kept on purpose, and is now traded the other way for comments on
  prose only.
- **A short context away from the leaf's edge** no longer detaches a
  comment when the other side holds. The neighbour rule still detaches it
  when a code point was added at that edge and the context there was
  empty; with a short context there, as "Note: restart every replica"
  becoming "Urgent note: restart every replica", the comment follows on
  the other side.
- **Transclusions.** SPEC.md §11.9 runs §11.4, so A also changes a pinned
  transclusion's near-copy check. The replay does not measure
  transclusions.
- **The cases that pin 0003's behaviour here** (three on `main` fail
  against this resolver) are rewritten under this document by an author
  who has not read the resolver.

**The residual moves in two places** (SPEC.md §11.12):

- **R2** is a leaf rewritten beyond recognition with its old wording left
  in order, and "beyond recognition" is now in words for the near-copy
  check: a rewrite below 0.5 by words resolves onto the copy even where its
  code points reach 0.5, and one at 0.5 by words but below by code points
  now refuses.
- **R3** is a sentence rewritten and the old one re-added in the same leaf;
  a comment now follows the re-added copy when one side of its context and
  its neighbours hold, where 0003 needed both sides. A suggestion still
  needs both.

## The cost of reversing it

Each change is in the resolver alone, and every record keeps its `base`, so
reversing either recomputes anchors with nothing rewritten. A reversed
restores refusals; D reversed restores detachments.

## What would reverse it

- **The held-out replay** fails the bar, or finds a resolution that is a
  resolver defect.
- **A real case of R2's or R3's wider form** in real history.
