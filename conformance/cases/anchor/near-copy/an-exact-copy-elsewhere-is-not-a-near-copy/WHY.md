# RESOLVED: an unmatched copy outside the gap

`R` is unique in `base`, and the current text adds a second copy after the
last paragraph. `R` pairs as `EXACT` in its gap between `I` and `B`, where
both sides hold one copy, so the repeat rule passes. The new copy is
unmatched, but it is a copy of `R`, and the near-copy rule for `EXACT`
takes only a leaf that is not a copy.

**Under 0004** the near-copy rule compares the word similarity, and for
`EXACT` 0003's "below 1" became "not a copy". The copy's words equal
`R`'s seven (`p`, `Repeat`, `the`, `check`, `after`, `every`, `trip.`), so
its word similarity is `2·7/14 = 1`; what keeps it out of the rule is that
its key equals `R`'s. The outcome is unchanged.
`near-copy/a-whitespace-variant-of-an-exact-leaf-is-a-near-copy` is the
other side of that line: word similarity 1, not a copy, refused.

SPEC.md §11.4:

> - **`EXACT`**:
>   - if `base` or the current text holds more than one copy of `k`, the
>     number of copies in `k`'s gap must be equal on both sides, or
>     `REFUSED(repeat)`. The pair always lies in the gap: a repeated key is
>     never on the chain, so `k`'s `EXACT` pair comes from §11.3 step 2's
>     alignment inside `k`'s own gap (0003, second addendum of 2026-10-16,
>     item 9);
>   - an unmatched leaf that is not a copy of `k`, with word similarity to
>     `k` of at least 0.5: `REFUSED(near-copy)`. A leaf that differs from `k`
>     only in whitespace has word similarity 1 and is not a copy, so it
>     refuses (0004).

SPEC.md §11.3:

> | §11 states | compare |
> | --- | --- |
> | similarity at least 0.5 | `4·L ≥ T` |
> | similarity at least 0.3 | `20·L ≥ 3·T` |
> | similarity below 1 | `2·L < T` |
> | `2·L₁/T₁` exceeds `2·L₂/T₂` by at least 0.15 | `40·L₁·T₂ − 40·L₂·T₁ ≥ 3·T₁·T₂` |
