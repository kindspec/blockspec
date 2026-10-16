# RESOLVED: an unmatched copy outside the gap

`R` is unique in `base`, and the current text adds a second copy after the
last paragraph. `R` pairs as `EXACT` in its gap between `I` and `B`, where
both sides hold one copy, so the repeat rule passes. The new copy is
unmatched, but its similarity is 1, and the near-copy rule for `EXACT`
takes only a similarity below 1.

SPEC.md §11.4:

> - **`EXACT`**:
>   - if `base` or the current text holds more than one copy of `k`, the
>     number of copies in `k`'s gap must be equal on both sides, or
>     `REFUSED(repeat)`. The pair always lies in the gap: a repeated key is
>     never on the chain, so `k`'s `EXACT` pair comes from §11.3 step 2's
>     alignment inside `k`'s own gap (0003, second addendum of 2026-10-16,
>     item 9);
>   - an unmatched leaf with similarity to `k` of at least 0.5 and below 1:
>     `REFUSED(near-copy)`.

SPEC.md §11.3:

> | §11 states | compare |
> | --- | --- |
> | similarity at least 0.5 | `4·L ≥ T` |
> | similarity below 1 | `2·L < T` |
> | `2·L₁/T₁` exceeds `2·L₂/T₂` by at least 0.15 | `40·L₁·T₂ − 40·L₂·T₁ ≥ 3·T₁·T₂` |
