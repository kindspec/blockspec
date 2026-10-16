# ORPHANED: a margin just below 0.15

As `correspondence/a-margin-of-exactly-0-15-pairs`, with `k2` sharing one
more code point with `j`: `L₂ = 60`, and `40·L₁·T₂ − 40·L₂·T₁ = 70400` is
below `3·T₁·T₂ = 76800`. `j` does not lead `k2` by 0.15, so `k` has no pair,
and nothing is a copy of it.

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

SPEC.md §11.3:

> A floating-point comparison is not conforming:
> `22/30 − 42/72` is exactly 0.15, and IEEE 754 doubles compute it as just
> below.
