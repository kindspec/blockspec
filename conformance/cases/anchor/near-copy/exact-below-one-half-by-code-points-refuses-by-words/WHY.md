# REFUSED(near-copy): an unmatched leaf below 0.5 by code points, a near-copy by words

As `near-copy/exact-at-one-half-by-code-points-and-above-by-words`, with
167 digits, so by code points the new paragraph is just below 0.5
(`4·L = 332`, `T = 333`), and 0003 resolved the comment. Since 0004 the
near-copy check on an `EXACT` leaf compares words, and by words the new
paragraph is far above 0.5 (`L = 13`, `T = 28`): `REFUSED(near-copy)`.
0004 names this movement of R2: a rewrite "at 0.5 by words but below by
code points now refuses".

This case was `near-copy/exact-with-an-unmatched-leaf-just-below-one-half`,
which expected `RESOLVED`. 0004 changed the outcome, and the case was
renamed for it.

SPEC.md §11.4:

> - **`EXACT`**:
>   [...]
>   - an unmatched leaf that is not a copy of `k`, with word similarity to
>     `k` of at least 0.5: `REFUSED(near-copy)` (0004). When `k` has words,
>     a leaf that differs from it only in runs of U+0009, U+000A, U+000D and
>     U+0020 has word similarity 1 and is not a copy, so it refuses; when `k`
>     has none, no leaf reaches 0.5. Words leave out the type, so a heading
>     with `k`'s text at another level, or a paragraph, refuses.

SPEC.md §11.2:

> The **word similarity** of two leaves (0004) is the same formula over
> words. A leaf's **words** are its `leaf.text` split at each run of U+0009,
> U+000A, U+000D and U+0020, empty pieces left out; `m` and `n` count words,
> which are compared exactly, and `L` is the length of a longest common
> subsequence of the two word sequences. It is 0 when either leaf has no
> words. Only §11.4's near-copy check on an `EXACT` leaf uses it, including
> where §11.9 runs §11.4 for a transclusion.

0004, *What it gives up*:

> - **R2** is a leaf rewritten beyond recognition with its old wording left
>   in order, and "beyond recognition" is now in words for the near-copy
>   check: a rewrite below 0.5 by words resolves onto the copy even where its
>   code points reach 0.5, and one at 0.5 by words but below by code points
>   now refuses.
