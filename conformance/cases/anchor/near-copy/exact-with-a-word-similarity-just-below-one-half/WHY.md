# RESOLVED: a word similarity just below 0.5

As `near-copy/exact-with-a-word-similarity-of-one-half`, with one more word
(`each`) in the new paragraph: four words of eight and nine in common,
`L = 4`, `T = 17`, and `4·L = 16 < 17`. The new paragraph is no near-copy
by words. By code points it would be one (`L = 33`, `T = 102`, a
similarity of about 0.65), which 0003 refused, and which §11.4 no longer
uses for an `EXACT` leaf.

SPEC.md §11.2:

> The **word similarity** of two leaves (0004) is the same formula over
> words. A leaf's **words** are its `leaf.text` split at each run of U+0009,
> U+000A, U+000D and U+0020, empty pieces left out; `m` and `n` count words,
> which are compared exactly, and `L` is the length of a longest common
> subsequence of the two word sequences. It is 0 when either leaf has no
> words. Only §11.4's near-copy check on an `EXACT` leaf uses it, including
> where §11.9 runs §11.4 for a transclusion.

SPEC.md §11.4:

> - **`EXACT`**:
>   [...]
>   - an unmatched leaf that is not a copy of `k`, with word similarity to
>     `k` of at least 0.5: `REFUSED(near-copy)` (0004). When `k` has words,
>     a leaf that differs from it only in runs of U+0009, U+000A, U+000D and
>     U+0020 has word similarity 1 and is not a copy, so it refuses; when `k`
>     has none, no leaf reaches 0.5. Words leave out the type, so a heading
>     with `k`'s text at another level, or a paragraph, refuses.

SPEC.md §11.3:

> **Thresholds compare exactly, in integer arithmetic** (0003, addendum,
> detail 5). With a similarity written `2·L/T`, where `T = m+n` is at least 2:
>
> | §11 states | compare |
> | --- | --- |
> | similarity at least 0.5 | `4·L ≥ T` |
> | `2·L₁/T₁` exceeds `2·L₂/T₂` by at least 0.15 | `40·L₁·T₂ − 40·L₂·T₁ ≥ 3·T₁·T₂` |
>
> These apply wherever §11.3 and §11.4 compare a similarity or a word
