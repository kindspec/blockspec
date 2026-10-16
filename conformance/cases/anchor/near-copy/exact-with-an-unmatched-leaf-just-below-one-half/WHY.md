# RESOLVED: an unmatched leaf at a similarity just below 0.5

As `near-copy/exact-with-an-unmatched-leaf-at-one-half`, with 167
digits, so the new paragraph's similarity is below 0.5.

SPEC.md §11.4:

>   - an unmatched leaf with similarity to `k` of at least 0.5 and below 1:
>     `REFUSED(near-copy)`.

SPEC.md §11.3:

> | §11 states | compare |
> | --- | --- |
> | similarity at least 0.5 | `4·L ≥ T` |
> | similarity below 1 | `2·L < T` |
> | `2·L₁/T₁` exceeds `2·L₂/T₂` by at least 0.15 | `40·L₁·T₂ − 40·L₂·T₁ ≥ 3·T₁·T₂` |
