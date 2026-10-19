# RESOLVED: a whitespace-only leaf has no words

The anchored leaf is a code block whose one line is two spaces, so its
text is `"  \n"` and it has no words. It is unchanged, `EXACT`. A new code
block below it holds one empty line, `"\n"`: it differs from the anchored
leaf only in whitespace, has no words either, and is not a copy. Word
similarity is 0 when either leaf has no words, so no leaf reaches 0.5 and
the comment resolves. A word similarity that took two empty word lists as
equal (as `difflib`'s ratio does) would refuse. By code points the two are
similar (`L = 6`, `T = 14`), which 0003 refused.
`near-copy/exact-with-a-whitespace-variant-beside-it` is the same shape for
a leaf that has words, and refuses.

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
