# REFUSED(crowded-gap): a new leaf at a word similarity of exactly 0.3

Added under 0004. The anchored paragraph `k` is

    The reactor scram threshold is 4.2 sigma above baseline, measured over a rolling 30-second window by each of the three channels, and any two channels voting to trip will scram the reactor.

which has 33 words: `p`, then 32 pieces of text. It was edited at its end
(`will scram the reactor.` became `shall scram the reactor at once.`), and a
new paragraph was added after it, in its gap.

    Any trip will scram the reactor.

**Word similarity.** The new paragraph's words are `p`, `Any`, `trip`,
`will`, `scram`, `the`, `reactor.`: seven. All but `Any` occur in `k`, in
that order (`trip`, `will`, `scram`, `the`, `reactor.` are `k`'s last five
words), so `L = 6`, `T = 33 + 7 = 40`, and the word similarity is
`2·6/40`, exactly 0.3: `20·6 = 120 ≥ 3·40 = 120`. It is at least 0.3, so
the paragraph refuses `k` as `crowded-gap`. It is below 0.5
(`4·6 = 24 < 40`), so near-copy would not.

**Pairing.** The edit's similarity to `k` is `2·188/389`, the new
paragraph's `2·33/224`, below 0.5 (`4·33 = 132 < 224`). The margin is
`40·188·224 − 40·33·389 = 1,171,000 ≥ 3·389·224 = 261,408`, and there is no
other leftover base leaf, so `k` pairs as `EDITED` and the new paragraph is
unmatched in its gap. `crowded-gap/a-new-leaf-just-below-word-similarity-0-3-resolves`
adds one word to the new paragraph.

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
