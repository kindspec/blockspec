# REFUSED(near-copy): an unmatched leaf at a similarity of exactly 0.5

The anchored paragraph is unchanged, and a new paragraph after it holds
its text followed by 166 digits: `4·L = 332 = T`, a similarity of
exactly 0.5, which is at least 0.5.

SPEC.md §11.4:

>   - an unmatched leaf with similarity to `k` of at least 0.5 and below 1:
>     `REFUSED(near-copy)`.

SPEC.md §11.3:

> | §11 states | compare |
> | --- | --- |
> | similarity at least 0.5 | `4·L ≥ T` |
> | similarity below 1 | `2·L < T` |
> | `2·L₁/T₁` exceeds `2·L₂/T₂` by at least 0.15 | `40·L₁·T₂ − 40·L₂·T₁ ≥ 3·T₁·T₂` |
