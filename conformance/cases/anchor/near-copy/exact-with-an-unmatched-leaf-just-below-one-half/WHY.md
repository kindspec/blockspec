# RESOLVED: an unmatched leaf at a word similarity just below 0.5

As `near-copy/exact-with-an-unmatched-leaf-at-one-half`, with one more
word, `fast`, in the new paragraph:

    Every channel reads high on its own fast scans.

Its words are 10, of which the same six (`p`, `Every`, `channel`, `reads`,
`high`, `on`) are common with `k`'s 15, so `L = 6`, `T = 25`, and `2·6/25`
is 0.48, below 0.5 (`4·6 = 24 < 25`). The anchor resolves on `k`, `reads`
at 32 to 37.

By code points the new paragraph's similarity to `k` is `2·41/132`, at
least 0.5 (`4·41 = 164 ≥ 132`), so an implementation that kept §11.2's
similarity for near-copy refuses this case.

**What 0004 changed.** The case pinned the code-point boundary with `k`'s
text and 167 digits; under the word similarity that paragraph scores
`2·14/30`, a near-copy
(`near-copy/a-leaf-below-one-half-by-code-points-is-a-near-copy-by-words`).
It is rebuilt on the word similarity's boundary.

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
