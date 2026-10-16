# REFUSED(repeat): the current text repeats a leaf that was unique

`R` is unique in `base` and occurs twice now, side by side. It pairs as
`EXACT` through the gap's alignment, and the current text holds more than
one copy, so the gap's copies are counted: one in `base`, two now.

SPEC.md §11.4:

> - **`EXACT`**:
>   - if `base` or the current text holds more than one copy of `k`, the
>     number of copies in `k`'s gap must be equal on both sides, or
>     `REFUSED(repeat)`. The pair always lies in the gap: a repeated key is
>     never on the chain, so `k`'s `EXACT` pair comes from §11.3 step 2's
>     alignment inside `k`'s own gap (0003, second addendum of 2026-10-16,
>     item 9);

0003 §4:

> The rule fires when *either* side is repeated
