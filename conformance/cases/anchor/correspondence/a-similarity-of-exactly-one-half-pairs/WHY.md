# EDITED: a similarity of exactly 0.5

The anchored paragraph is 81 code points with no digit, so its key is
83. The current paragraph is the same text followed by 166 digits,
a key of 249. The longest common subsequence is the whole old key,
`L = 83`, and `T = 332`, so `4·L = 332 = T`: the
similarity is exactly 0.5, which is at least 0.5, and the two pair as
`EDITED`. The span keeps its full contexts in the new text.
`correspondence/a-similarity-just-below-one-half-does-not-pair` adds one
digit.

SPEC.md §11.2:

> The **similarity** of two leaves is `2·L/(m+n)`, where `m` and `n` are the
> lengths in code points of their keys, each written as the type, U+001F and
> the text, and `L` is the length of a longest common subsequence of the two.

SPEC.md §11.3:

> 3. **Edits.** A base leaf `i` and a current leaf `j` left over in the same
>    gap pair as `EDITED` when all of these hold: their similarity is at least
>    0.5; it exceeds the similarity of `i` to every other leftover current
>    leaf in the gap by at least 0.15; and it exceeds the similarity of `j` to
>    every other leftover base leaf in the gap by at least 0.15.

SPEC.md §11.3:

> | §11 states | compare |
> | --- | --- |
> | similarity at least 0.5 | `4·L ≥ T` |
> | similarity below 1 | `2·L < T` |
> | `2·L₁/T₁` exceeds `2·L₂/T₂` by at least 0.15 | `40·L₁·T₂ − 40·L₂·T₁ ≥ 3·T₁·T₂` |
