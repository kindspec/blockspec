# EDITED: edited while its gap gained an unlike paragraph

Added under 0004, with the input `crowded-gap/edited-with-a-new-leaf-beside-it`
had under 0003, where it was `REFUSED(crowded-gap)`. The anchored paragraph
`k` was edited at its end, and `See the annex.` was added after it, in the
same gap.

**Pairing.** The edit's similarity to `k` is `2·200/413`, and
`See the annex.`'s is `2·14/218`: the margin is `40·200·218 − 40·14·413 =
1,512,720 ≥ 3·413·218 = 270,102`, so `k` pairs with its edit as `EDITED`
and `See the annex.` is unmatched in the gap.

**Word similarity.** `k`'s words are 34; `See the annex.`'s are `p`, `See`,
`the`, `annex.`. Only `p` and `the` are common, `L = 2`, `T = 38`:
`2·2/38`, about 0.11. That is below 0.3 (`20·2 = 40 < 3·38 = 114`), so the
crowded-gap rule does not apply, and below 0.5, so near-copy does not.

**The span.** `4.2 sigma`, with the short prefix
`The reactor scram threshold is ` and the suffix
` above baseline, measured over a`, both intact: one hit, at 31 to 40.

0004 gives this up on purpose: "An edited leaf beside an unlike new leaf
resolves".

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

0004, *Decision*:

> - **C. Crowded-gap needs a rival.** An unmatched leaf in an edited leaf's
>   gap refuses it as `crowded-gap` only when its word similarity to the leaf
>   is at least 0.3.

SPEC.md §11.6:

> | `EDITED` | `EDITED`, and the span found | the anchor, marked changed |
