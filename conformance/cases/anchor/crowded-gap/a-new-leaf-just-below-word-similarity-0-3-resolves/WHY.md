# EDITED: a new leaf at a word similarity just below 0.3

Added under 0004, the control for
`crowded-gap/a-new-leaf-at-word-similarity-0-3-refuses`. The anchored paragraph `k` is

    The reactor scram threshold is 4.2 sigma above baseline, measured over a rolling 30-second window by each of the three channels, and any two channels voting to trip will scram the reactor.

which has 33 words: `p`, then 32 pieces of text. It was edited at its end
(`will scram the reactor.` became `shall scram the reactor at once.`), and a
new paragraph was added after it, in its gap.

    Any single trip will scram the reactor.

**Word similarity.** Its words are `p`, `Any`, `single`, `trip`, `will`,
`scram`, `the`, `reactor.`: eight. `Any` and `single` are not in `k`, so
`L = 6` and `T = 33 + 8 = 41`: `2·6/41`, about 0.293, below 0.3
(`20·6 = 120 < 3·41 = 123`). Neither crowded-gap nor near-copy applies.

**Pairing.** The edit's similarity to `k` is `2·188/389`, the new
paragraph's `2·39/231`; the margin is `40·188·231 − 40·39·389 = 1,130,280 ≥
3·389·231 = 269,577`, so `k` pairs as `EDITED`.

**The span.** `4.2 sigma` with its short prefix
`The reactor scram threshold is ` and its suffix
` above baseline, measured over a`, both intact: one hit, at 31 to 40.

SPEC.md §11.4:

> - **`EDITED`**:
>   - an unmatched copy of `k`: `REFUSED(exact-copy)`. A copy that is some
>     base leaf's pair does not count (0003 Q12);
>   - another unmatched leaf in `k`'s gap on the current side, with word
>     similarity to `k` of at least 0.3: `REFUSED(crowded-gap)` (0004);
>   - an unmatched leaf with word similarity to `k` of at least 0.5:
>     `REFUSED(near-copy)`.

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

SPEC.md §11.6:

> | `EDITED` | `EDITED`, and the span found | the anchor, marked changed |
