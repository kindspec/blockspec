# REFUSED(repeat) and REFUSED(unaccounted-copy): twins next to a moved leaf

Text-bearing leaves, base: heading, `Moved`, `U1`, `Twin`, `Twin`, `U2`;
current: heading, `U1`, `Moved`, `Twin`, `U2`. The unique pairs in base
order have current indices 0, 2, 1, 4. Two chains are longest, `0, 2, 4`
and `0, 1, 4`; the leftmost is `0, 1, 4`, so the heading, `U1` and `U2` are
the chain and `Moved` is `MOVED`. The gap between `U1` and `U2` holds both
twins in `base` and, leaving out `Moved`, one twin now. The alignment
pairs the first twin with it as `EXACT`, and the second twin is left with
no pair.

`nth` 0 is `EXACT` with a repeated key. Its gap, between `U1` and `U2`,
holds two copies in `base` and one in the current text:
`REFUSED(repeat)`. `nth` 1 has no pair, and a current leaf is a copy of
it: `REFUSED(unaccounted-copy)`.

SPEC.md §11.3:

> 1. **The chain.** Take each key that occurs exactly once in `base` and
>    exactly once in the current text, as a pair of positions. The longest
>    subsequence of those pairs, in base order, whose current positions
>    increase is the **chain**. Its pairs are `EXACT`. Every other such pair
>    is `MOVED`.

SPEC.md §11.3:

> 2. **Gaps.** The chain cuts each snapshot into gaps: the leaves between two
>    consecutive chain pairs, before the first, or after the last, leaving out
>    leaves paired as `MOVED`. Inside each gap, the longest common subsequence
>    alignment (§11.2) of the base leaves' keys onto the current leaves' keys
>    gives further `EXACT` pairs.

SPEC.md §11.4:

> The anchored leaf `k` is the leaf of `base` with key `leaf.type` and
> `leaf.text`, at ordinal `nth`. Its **gap** is bounded by the nearest chain
> pair before `k` and the nearest after it, in base order, or by a snapshot's
> edge where there is none. On the base side the gap is the leaves strictly
> between those two pairs' base positions, and on the current side the leaves
> strictly between their current positions.

SPEC.md §11.4:

> - **`EXACT`**:
>   - if `base` or the current text holds more than one copy of `k`, the
>     number of copies in `k`'s gap must be equal on both sides, or
>     `REFUSED(repeat)`. The pair always lies in the gap: a repeated key is
>     never on the chain, so `k`'s `EXACT` pair comes from §11.3 step 2's
>     alignment inside `k`'s own gap (0003, second addendum of 2026-10-16,
>     item 9);

SPEC.md §11.4:

> - **No pair**: `REFUSED(unaccounted-copy)` if any current leaf is a copy of
>   `k`, and `ORPHANED` otherwise.
