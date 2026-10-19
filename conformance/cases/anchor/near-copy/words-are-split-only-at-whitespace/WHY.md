# RESOLVED: words joined by punctuation are one word

The anchored paragraph is unchanged, `EXACT`. A new paragraph at the end
holds the same settings with the spaces after the commas removed. Words
are split only at runs of tab, line feed, carriage return and space, so it
is two words, `Set` and `timeout=30,retries=5,backoff=2.`, against the
anchored paragraph's four, with one in common: `L = 1`, `T = 6`, below 0.5.
A word split that also broke at punctuation would find most words equal
and refuse. By code points the two are very similar (`L = 37`, `T = 76`),
which 0003 refused.

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
