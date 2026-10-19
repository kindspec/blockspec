# REFUSED(pinned-crowded-gap): a pinned leaf edited while a rival joined its gap

Inside the region, the first paragraph `k` was edited (` in turn` added)
and a paragraph added after it:

    The scram threshold is reviewed at every shift.

The heading, `Operators review ...` and `Changes ...` are unchanged and on
the chain, so `k`'s gap holds `k` on the base side and its edit and the
new paragraph on the current side.

**Pairing.** The edit's similarity to `k` is `2·108/224`; the new
paragraph's is `2·38/157`, below 0.5 (`4·38 = 152 < 157`). The margin is
`40·108·157 − 40·38·224 = 337,760 ≥ 3·224·157 = 105,504`, so `k` pairs as
`EDITED`, and the new paragraph is unmatched in its gap.

**Word similarity.** `k` has 18 words (`p` and 17 pieces). The new
paragraph has 9: `p`, `The`, `scram`, `threshold`, `is`, `reviewed`, `at`,
`every`, `shift.`, of which the first five are common with `k`, in order:
`L = 5`, `T = 27`, `2·5/27`, about 0.37. That is at least 0.3
(`20·5 = 100 ≥ 3·27 = 81`), so `k` is refused as `crowded-gap`, and step 3
refuses the transclusion as `pinned-crowded-gap`. It is below 0.5
(`4·5 = 20 < 27`). For `Operators review the trip logs at the start of
every shift.`, `EXACT`, the new paragraph's word similarity is `2·4/21`
(`p`, `at`, `every`, `shift.`), below 0.5, so that leaf does not refuse.

**What 0004 changed.** Under 0003 the added paragraph was `See the annex.`,
and any unmatched leaf in the gap refused. Its word similarity to `k` is
`2·1/22`, so under 0004 it no longer refuses and the transclusion resolves
(`transclusion/resolves-with-an-unlike-leaf-added-beside-an-edit`). This
case now adds a rival.

SPEC.md §11.9:

> 3. For each text-bearing leaf the name binds in the pinned blob, §11.3 and
>    §11.4 run with that blob as `base`. A refusal, or no pair, refuses the
>    transclusion, as `REFUSED(pinned-<reason>)`, where `<reason>` is §11.4's
>    reason or `orphaned`. Where several leaves refuse, the first in the
>    pinned blob's document order is reported.

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
