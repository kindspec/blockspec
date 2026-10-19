# REFUSED(near-copy): an unmatched leaf at 0.5 by code points, far above by words

The anchored paragraph is unchanged, `EXACT`, and a new paragraph after it
holds its text followed by 166 digits. By code points the two are at
exactly 0.5 (`4·L = 332 = T`), which is why 0003 refused this. Since 0004
the near-copy check on an `EXACT` leaf compares words: the digits run onto
the last word, so thirteen of the anchored paragraph's fourteen words are
the new paragraph's first thirteen, `L = 13`, `T = 28`, well above 0.5. The
outcome is unchanged; the threshold it pinned is now pinned by words in
`near-copy/exact-with-a-word-similarity-of-one-half`.

This case was `near-copy/exact-with-an-unmatched-leaf-at-one-half`, renamed
because its name described the code-point similarity §11.4 no longer uses
here.

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
