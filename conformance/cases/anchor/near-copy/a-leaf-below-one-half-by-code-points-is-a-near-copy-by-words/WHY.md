# REFUSED(near-copy): below 0.5 by code points, a near-copy by words

Added under 0004, with the input
`near-copy/exact-with-an-unmatched-leaf-just-below-one-half` had under
0003, where it was `RESOLVED`. The anchored paragraph `k`,

    Every channel trips whenever it reads high on two successive scans of the window.

is unchanged and `EXACT` on the chain. A new paragraph after it holds
`k`'s text followed by 167 digits, written straight after `window.`.

**By code points** `k`'s key is 83 code points and the new paragraph's
250; the longest common subsequence is all of `k`'s key, `L = 83`,
`T = 333`, and `4·83 = 332 < 333`: below 0.5. Under 0003 the near-copy rule
did not apply.

**By words** both paragraphs have 15 words, and only the last differs
(`window.` against `window.` with the digits joined to it), so `L = 14`,
`T = 30`: `2·14/30`, at least 0.5 (`4·14 = 56 ≥ 30`), and the new
paragraph is not a copy of `k`. The `EXACT` near-copy rule refuses. An implementation
that kept the code-point similarity for near-copy reports `RESOLVED`.

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
