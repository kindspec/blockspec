# REFUSED(near-copy): an unmatched leaf that differs from it only in whitespace

Added under 0004. The anchored paragraph `k` is unchanged and `EXACT` on
the chain. A new paragraph after it holds `k`'s text with two spaces
between `three` and `independent` instead of one. Its key differs from
`k`'s, so it is not a copy, and it is unmatched.

**Word similarity.** Splitting at runs of whitespace gives the two
paragraphs the same 34 words, so `L = 34`, `T = 68`, and the word
similarity is exactly 1, at least 0.5 (`4·34 = 136 ≥ 68`). The `EXACT`
near-copy rule takes "an unmatched leaf that is not a copy of `k`" at that
word similarity, so it refuses. `k` has one copy in each snapshot, so the
repeat rule, which comes first, does not apply.

By code points the similarity is `2·202/405`, at least 0.5 and below 1, so
under 0003 this was `REFUSED(near-copy)` as well. An implementation that
kept 0003's "below 1" with the word similarity would report `RESOLVED`.
`near-copy/an-exact-copy-elsewhere-is-not-a-near-copy` is the control on
the other side of "not a copy": there the unmatched leaf is a copy of
`k`, also at word similarity 1, and `k` resolves.

**What changed since this case was first written.** It was added as
`near-copy/a-whitespace-variant-is-not-a-near-copy-of-an-exact-leaf`,
`RESOLVED`, when §11.4 said "at least 0.5 and below 1". 0004 now replaces
"below 1" with "not a copy" for exactly this shape.

0004, *Decision*:

> For an `EXACT` leaf, 0003's "below 1" becomes "not a copy":
> a leaf differing from it only in whitespace has word similarity 1, and
> still refuses.

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
