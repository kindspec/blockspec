# ORPHANED: a similarity just below 0.5

As `correspondence/a-similarity-of-exactly-one-half-pairs`, with 167
digits: `4·L = 332` and `T = 333`, so the similarity is
below 0.5. The two leaves do not pair, and nothing is a copy of the old
text.

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

SPEC.md §11.4:

> - **No pair**: `REFUSED(unaccounted-copy)` if any current leaf is a copy of
>   `k`, and `ORPHANED` otherwise.
