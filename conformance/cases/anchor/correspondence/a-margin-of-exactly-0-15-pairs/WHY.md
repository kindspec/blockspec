# EDITED: a margin of exactly 0.15, compared in integers

In `base` the gap between the heading and the last paragraph holds the
anchored paragraph `k` (69 code points) and a second paragraph `k2`; in the
current text it holds one paragraph `j`, which is `k` followed by 18
digits. `k2` is the first 57 code points of `j` followed by 12 capitals
that `j` does not hold.

`k` against `j`: `L₁ = 71`, `T₁ = 160`, similarity 0.8875. `k2` against `j`:
`L₂ = 59`, `T₂ = 160`, similarity 0.7375. The margin is exactly 0.15:
`40·L₁·T₂ − 40·L₂·T₁ = 76800` and `3·T₁·T₂ = 76800`. So `j`'s similarity to `k`
exceeds its similarity to every other leftover base leaf by at least 0.15,
and `k` and `j` pair as `EDITED`. In IEEE 754 doubles, `142/160 − 118/160`
is just below 0.15, and the leaves would not pair.

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
> | `2·L₁/T₁` exceeds `2·L₂/T₂` by at least 0.15 | `40·L₁·T₂ − 40·L₂·T₁ ≥ 3·T₁·T₂` |

SPEC.md §11.3:

> A floating-point comparison is not conforming:
> `22/30 − 42/72` is exactly 0.15, and IEEE 754 doubles compute it as just
> below.
