# RESOLVED: an unrelated short leaf that is near only by code points

Added under 0004, from its *Why each*. The anchored paragraph `k` is the
link `[The Slice Type](ch04-03-slices.md)`, unchanged and `EXACT` on the chain. A new paragraph after it
is `[Generic Data Types](ch10-01-syntax.md)`, unmatched.

**By code points.** The keys are `p`, U+001F and the text: 37 and 41 code
points, `T = 78`. A longest common subsequence has `L = 24`, for example
`[eic Type](ch0-0-s.md)` with the `p` and U+001F in front, so the similarity
is `2·24/78`, about 0.62: at least 0.5 (`4·24 = 96 ≥ 78`) and below 1. Under
0003 this refused `k` as a near-copy.

**By words.** `k`'s words are `p`, `[The`, `Slice`, `Type](ch04-03-slices.md)`
and the new paragraph's `p`, `[Generic`, `Data`, `Types](ch10-01-syntax.md)`.
Only `p` is common, `L = 1`, `T = 8`: `2·1/8` is 0.25, below 0.5
(`4·1 = 4 < 8`). The near-copy rule does not apply, and the comment on
`The Slice Type` (1 to 15, with the short contexts `[` and
`](ch04-03-slices.md)` at the leaf's edges) resolves.

0004, *Why each*:

> Of the 275 near-copy
> refusals at gap 5 in pre-registration 4, 268 were on paragraphs whose text
> had not changed, refused because an unrelated short leaf scored at least
> 0.5: `[The Slice Type](ch04-03-slices.md)` and
> `[Generic Data Types](ch10-01-syntax.md)` share enough code points in order
> to reach 0.62; by words they score 0.25, sharing only the leaf type.

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
