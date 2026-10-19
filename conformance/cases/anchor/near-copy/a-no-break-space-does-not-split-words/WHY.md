# RESOLVED: a no-break space does not split words

The anchored paragraph is unchanged, `EXACT`. A new paragraph at the end
holds its text with every space replaced by U+00A0 NO-BREAK SPACE. Only
U+0009, U+000A, U+000D and U+0020 split words, so the new paragraph is one
word, which the anchored paragraph's seven do not include: `L = 0`, word
similarity 0. A split at every Unicode space, as some libraries' default
splits are, would make the two equal and refuse. By code points they are
similar (`L = 31`, `T = 74`), which 0003 refused.

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
