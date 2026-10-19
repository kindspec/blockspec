# RESOLVED: a pinned leaf edited while an unlike leaf joined its gap

Added under 0004, with the input `transclusion/pinned-crowded-gap` had
under 0003, where it was `REFUSED(pinned-crowded-gap)`. Inside the region
the first paragraph `k` was edited (` in turn` added) and `See the annex.`
added after it.

**Pairing.** The edit's similarity to `k` is `2·108/224`, and
`See the annex.`'s `2·13/124`; the margin is `40·108·124 − 40·13·224 =
419,200 ≥ 3·224·124 = 83,328`, so `k` pairs as `EDITED` and
`See the annex.` is unmatched in its gap.

**Word similarity.** `k` has 18 words; `See the annex.` has `p`, `See`,
`the`, `annex.`, of which only `p` is in `k` (`k` has `The`, capitalised):
`2·1/22`, below 0.3 (`20·1 = 20 < 66`) and below 0.5. For the `EXACT`
paragraph `Operators review the trip logs at the start of every shift.` it
is `2·2/16` (`p`, `the`), below 0.5. No leaf refuses, and both pairs lie
in the region as it binds now: the paragraphs at 2, 3 and 4.

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

SPEC.md §11.9:

> **The unit transcluded is what the name binds** (0002 §4): one node with its
> subtree, or the nodes of one region.