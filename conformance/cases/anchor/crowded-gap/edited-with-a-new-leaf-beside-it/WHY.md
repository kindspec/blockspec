# REFUSED(crowded-gap): edited while its gap gained a rival

The anchored paragraph `k` was edited (`will scram the reactor.` became
`shall scram the reactor at once.`), and a new paragraph was added after
it, in the same gap:

    Two channels voting to trip will scram the reactor.

**Pairing.** The edit's similarity to `k` is `2·200/413`; the new
paragraph's is `2·53/255`, below 0.5 (`4·53 = 212 < 255`), so it cannot
pair with `k` itself. The margin holds: `40·200·255 − 40·53·413 =
1,164,440 ≥ 3·413·255 = 315,945`. There is no other leftover base leaf, so
`k` pairs with its edit as `EDITED`, and the new paragraph is unmatched in
`k`'s gap.

**Word similarity.** `k` has 34 words (`p` and 33 pieces of text); the new
paragraph has 10 (`p`, `Two`, `channels`, `voting`, `to`, `trip`, `will`,
`scram`, `the`, `reactor.`). All but `Two` occur in `k` in that order
(`k` has `two`, lower case, and words compare exactly), so `L = 9` and
`T = 44`: `2·9/44`, about 0.41. It is at least 0.3 (`20·9 = 180 ≥ 3·44 =
132`), so the new paragraph is a rival, and below 0.5 (`4·9 = 36 < 44`), so
the near-copy rule would not have refused on its own.

**What 0004 changed.** Under 0003 any unmatched leaf in the gap refused,
and the new paragraph was `See the annex.`. Under 0004 that one is too
unlike `k` to count, and resolves
(`crowded-gap/edited-with-an-unlike-new-leaf-beside-it`); this case now
adds a paragraph that is a second candidate. 0003 §8: the anchored leaf's
gap gains leaves while it is edited.

SPEC.md §11.3:

> 3. **Edits.** A base leaf `i` and a current leaf `j` left over in the same
>    gap pair as `EDITED` when all of these hold: their similarity is at least
>    0.5; it exceeds the similarity of `i` to every other leftover current
>    leaf in the gap by at least 0.15; and it exceeds the similarity of `j` to
>    every other leftover base leaf in the gap by at least 0.15.

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
