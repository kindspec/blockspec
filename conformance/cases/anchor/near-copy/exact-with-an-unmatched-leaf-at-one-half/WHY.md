# REFUSED(near-copy): an unmatched leaf at a word similarity of exactly 0.5

The anchored paragraph `k`,

    Every channel trips whenever it reads high on two successive scans of the window.

is unchanged and pairs on the chain as `EXACT`. A new paragraph follows it:

    Every channel reads high on its own scans.

**Word similarity.** `k`'s words are `p` and 14 pieces of text, 15 in all.
The new paragraph's are `p`, `Every`, `channel`, `reads`, `high`, `on`,
`its`, `own`, `scans.`: 9. The first six occur in `k` in that order; `its`,
`own` and `scans.` do not (`k` has `scans`, without the full stop). So
`L = 6`, `T = 15 + 9 = 24`, and `2·6/24` is exactly 0.5: `4·6 = 24 ≥ 24`,
and the new paragraph is not a copy of `k`. The `EXACT` near-copy rule
refuses.

**What 0004 changed.** The case pinned the code-point similarity's 0.5
boundary, with `k`'s text and 166 digits appended. Near-copy now uses the
word similarity, under which that paragraph scores `2·14/30` (its last
word differs from `k`'s, the other 14 are equal), so the case is rebuilt on
the word similarity's boundary. The code-point boundary is still pinned
for §11.3's pairing by `correspondence/a-similarity-of-exactly-one-half-pairs`.

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

0004, *Decision*:

> - **A. Near-copy compares words, not code points.** The three near-copy
>   checks of §11.4 use a **word similarity**: `2·L/(m+n)` over the leaves'
>   words (the leaf type, then the text split at runs of tab, LF, CR and
>   space), compared exactly. §11.3's correspondence keeps the code-point
>   similarity.
