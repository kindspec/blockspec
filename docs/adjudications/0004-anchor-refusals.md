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
> survives follows it, without letting any comment land silently on the
> wrong text where 0003 refused it?

## Decision

**Decided by the owner, 2026-10-18.** Three changes, all to the resolver
(SPEC.md §11.2, §11.4, §11.5); nothing in a document or a record changes.

- **A. Near-copy compares words, not code points.** The three near-copy
  checks of §11.4 use a **word similarity**: `2·L/(m+n)` over the leaves'
  words (the leaf type, then the text split at runs of tab, LF, CR and
  space), compared exactly. §11.3's correspondence keeps the code-point
  similarity.
- **C. Crowded-gap needs a rival.** An unmatched leaf in an edited leaf's
  gap refuses it as `crowded-gap` only when its word similarity to the leaf
  is at least 0.3.
- **D. A span hit needs one side of its context, with its word boundaries
  kept.** A hit needs its prefix or its suffix, not both, each compared
  with whitespace runs as one space; and the occurrence's start and end
  must be word boundaries exactly where the base span's are. This replaces
  0003 Q13's requirement of both sides.

A change B, whitespace-tolerant context with both sides still required, was
weighed and folded into D, which compares context that way.

## Why each

**A.** The near-copy rules exist for one shape (0003 §4, `spike/LOG.md`
§9): a paragraph reworded while its old wording survives verbatim, so that
the verbatim copy matches exactly and the real descendant is only similar.
The code-point similarity measured that shape badly. Of the 275 near-copy
refusals at gap 5 in pre-registration 4, 268 were on paragraphs whose text
had not changed, refused because an unrelated short leaf scored at least
0.5: `[The Slice Type](ch04-03-slices.md)` and
`[Generic Data Types](ch10-01-syntax.md)` share enough code points in order
to reach 0.62; by words they score 0.25, sharing only the leaf type. A reworded paragraph keeps most of
its words, so the shape the rule is for still refuses: every near-copy case
of the suite for it, and R1 to R4, keep their outcomes under 0004.

**C.** 0003 §4 gives crowded-gap's reason: when a gap gains paragraphs
while the anchored one is edited, "which of the near candidates descends
from it is a guess". A new leaf with almost no words in common is not a
candidate, and §11.3 already pairs an edit only when it leads every other
leftover leaf in the gap by 0.15. The rule now refuses only where there is
a second candidate.

**D.** 0003 §5 kept both sides of the context "until a replay of real
history prices the detachments". It priced them. In pre-registration 4,
154 of the 168 `DETACHED` at gap 5 had an intact span whose stored context
had changed (`kinds-gap5.txt`), and after A and C `DETACHED` is the largest
cause left. One side of the context still ties the span
to its place in the paragraph. The word-boundary condition is what makes
one side safe in the case the replay found: without it, a comment on
`turn on [[Highlight` followed its characters into
`turn on [[Highlighter|`, a different link, once the suffix was ignored.

## The measurement, and what it is not

Measured with research `experiments/D8-anchor-replay/replay.py` at
`735091e`, against this resolver (0004's), on the four arms of
pre-registration 4 and its rehearsal arm, site-policy, with the oracle for
truth (no labels). Pooled over the five arms:

| | gap 1 | gap 5 |
| --- | --: | --: |
| 0003's rules (the published `prereg4/replay-ARM.txt` and `rehearsal-site-policy.txt`) | 2.2% | 12.0% |
| 0004's rules | 0.6% | 3.0% |

Each figure is loud comments over surviving spans, from the `counted:`
lines of each arm's stdout. No comment at gap 5 is `WRONG` under 0004's
rules. Two at gap 1 are, both on one k8s-en file, and both are the oracle's:
a full stop was added after the span (`...and failover capabilities` became
`...and failover capabilities.`), so the oracle's word comparison calls the
span gone, and the resolver kept the comment on exactly those words.

**These rules were chosen on these arms**, so this is not a test of them.
The test is a new pre-registration on held-out repositories, decided by the
owner the same day.

## What it gives up

Each designed case below changes its expected outcome; each is rewritten
under this document by an author who has not read the resolver.

- **An edit right next to a span no longer detaches it** while the other
  side of the context and the word boundaries hold
  (`context/an-edit-on-the-first-code-point-of-the-prefix-detaches`,
  `status/detached-when-the-context-is-edited`). That was 0003 Q13's recall
  cost, kept on purpose; it is now traded the other way.
- **A short context away from the leaf's edge** no longer detaches when
  the other side holds (`context/a-short-prefix-must-sit-at-the-leaf-start`,
  `context/a-short-suffix-must-sit-at-the-leaf-end`).
- **An edited leaf beside an unlike new leaf resolves**
  (`crowded-gap/edited-with-a-new-leaf-beside-it`,
  `transclusion/pinned-crowded-gap`).
- **Near-copy's threshold is in words**, so the cases that pin the
  code-point boundary at 0.5 are rewritten for the word similarity.

**The residual widens in one place.** 0003 §9's R3 is a sentence rewritten
and the old sentence re-added in the same leaf with the same context, and
the comment follows the re-added copy. Under D the re-added copy needs only
one side of its context, so R3 also covers a re-add that keeps one side.
The alignment of §11.5 still has to carry the old span onto the copy, and
the copy's ends must sit on the same word boundaries.

## The cost of reversing it

Each change is in the resolver alone, and every record keeps its `base`, so
reversing any of them recomputes anchors with nothing rewritten. A and C
reversed restore refusals; D reversed restores detachments.

## What would reverse it

- **The held-out replay** fails the bar, or finds a resolution that is a
  resolver defect.
- **A real case of R3's wider form**: a comment carried onto re-added text
  with only one side of its context, in real history.
