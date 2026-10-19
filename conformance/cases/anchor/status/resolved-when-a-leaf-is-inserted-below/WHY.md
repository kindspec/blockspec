# RESOLVED: an unlike leaf inserted directly below

A short new paragraph sits directly below the anchored one. It is
unmatched, but its word similarity to the anchored paragraph is far below
0.5 (`L = 1`, `T = 36`), so `EXACT`'s near-copy rule does not fire. (Its
code-point similarity, which 0003 used, is far below 0.5 too.) 0003 §8: a new leaf, unlike the
anchored one, inserted directly above or below it, `RESOLVED`.

SPEC.md §11.4:

> - **`EXACT`**:
>   [...]
>   - an unmatched leaf that is not a copy of `k`, with word similarity to
>     `k` of at least 0.5: `REFUSED(near-copy)` (0004). When `k` has words,
>     a leaf that differs from it only in runs of U+0009, U+000A, U+000D and
>     U+0020 has word similarity 1 and is not a copy, so it refuses; when `k`
>     has none, no leaf reaches 0.5. Words leave out the type, so a heading
>     with `k`'s text at another level, or a paragraph, refuses.

SPEC.md §11.6:

> | `RESOLVED` | `EXACT`, and the span found | the anchor |
