# R2, RESOLVED: a rewrite unlike its old text by words only, the old wording quoted below

Added under 0004. As in `residual/r2-a-rewrite-with-its-old-wording-quoted-below`,
the anchored paragraph `k` was rewritten and a block quote of its old
wording sits directly below the rewrite. Here the rewrite capitalises
every word:

    The Reactor Scram Threshold Is 4.2 Sigma Above Baseline, Measured Over A Rolling 30-second Window By Each Of The Three Independent Channels, And Any Two Channels Voting To Trip Will Scram The Reactor.

The quote's paragraph has `k`'s key in `k`'s place in the chain, so it is
`k`'s pair, `EXACT`. The rewrite is unmatched.

**By code points** the rewrite's similarity to `k` is `2·172/404`, about
0.85: at least 0.5 (`4·172 = 688 ≥ 404`) and below 1. Under 0003 `k` was
`REFUSED(near-copy)`.

**By words** they share only `p`, `The`, `4.2` and `30-second`: `L = 4`,
`T = 68`, `2·4/68`, below 0.5 (`4·4 = 16 < 68`). The near-copy rule does
not apply, and the comment resolves on the quotation, 31 to 40.

**This outcome is a documented residual, not a defect.** §11.12 lists it
among the edits no resolver that reads only `base` and the current text
can tell from a legitimate one, so the case pins the resolution the rules
give, which is silently wrong for the history described here and right
for its twin.

**This is R2 as 0004 widened it.** §11.12's R2 row now measures "beyond
recognition" in words: a rewrite below 0.5 by word similarity resolves
silently onto the verbatim copy even where its code points reach 0.5, as
here.

0004, *The residual moves in two places*:

> **R2** is a leaf rewritten beyond recognition with its old wording left
> in order, and "beyond recognition" is now in words: a rewrite below 0.5
> by words resolves silently onto the copy even where its code points
> reach 0.5, as `residual/r2-a-rewrite-unlike-only-by-words-with-its-old-wording-quoted-below`
> shows, and one at 0.5 by words but below by code points now refuses.

The other half of that sentence is
`near-copy/a-leaf-below-one-half-by-code-points-is-a-near-copy-by-words`.

SPEC.md §11.12:

> Four mechanisms leave current bytes identical to those a legitimate edit
> produces, so they resolve, silently, to the wrong text (0003 §9):
>
> | | mechanism | indistinguishable from | suggestions |
> | --- | --- | --- | --- |
> | R1 | a leaf deleted, and a verbatim copy of it elsewhere | a move | not affected: stale on `MOVED` |
> | R2 | a leaf rewritten to word similarity below 0.5 (0004; by code points the rewrite may be more similar), with a verbatim copy of its old text left in its place in order | a new leaf inserted beside an unchanged one | affected |
> | R3 | inside one leaf, the span's sentence rewritten and the old sentence re-added with one side of its context or both (0004), on the same word boundaries | a sentence moved within its leaf | affected |
> | R4 | a different document at the same path, by archive-and-replace or copy-and-rewrite | an edit of the document | affected |

SPEC.md §11.4:

> - **`EXACT`**:
>   [...]
>   - an unmatched leaf that is not a copy of `k`, with word similarity to
>     `k` of at least 0.5: `REFUSED(near-copy)`. A leaf that differs from `k`
>     only in whitespace has word similarity 1 and is not a copy, so it
>     refuses (0004).

SPEC.md §11.2:

> The **word similarity** of two leaves is the same formula over words
> (0004): a leaf's **words** are its `leaf.type`, then its `leaf.text` split
> at each run of U+0009, U+000A, U+000D and U+0020, empty pieces left out.
> `m` and `n` count words, which are compared exactly, and `L` is the length
> of a longest common subsequence of the two word sequences. §11.3's
> correspondence uses the similarity; §11.4's near-copy and crowded-gap checks
> use the word similarity.

SPEC.md §11.3:

> | §11 states | compare |
> | --- | --- |
> | similarity at least 0.5 | `4·L ≥ T` |
> | similarity at least 0.3 | `20·L ≥ 3·T` |
> | similarity below 1 | `2·L < T` |
> | `2·L₁/T₁` exceeds `2·L₂/T₂` by at least 0.15 | `40·L₁·T₂ − 40·L₂·T₁ ≥ 3·T₁·T₂` |
>
> These apply wherever §11.3 and §11.4 compare a similarity or a word
> similarity with 0.3, 0.5, 1 or a margin of 0.15.
