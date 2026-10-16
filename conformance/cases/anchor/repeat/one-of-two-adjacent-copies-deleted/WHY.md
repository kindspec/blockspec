# REFUSED(repeat) and REFUSED(unaccounted-copy): one of two twins deleted

`base` holds `R` twice between `I` and `B`; the current text once. The
gap's alignment pairs the first base copy with the remaining one, as
`EXACT`. For `nth` 0, `base` holds more than one copy, and the gap holds
two copies in `base` and one now: `REFUSED(repeat)`. For `nth` 1 there is
no pair, and a current leaf is a copy of it: `REFUSED(unaccounted-copy)`.

SPEC.md §11.4:

> - **`EXACT`**:
>   - if `base` or the current text holds more than one copy of `k`, the
>     number of copies in `k`'s gap must be equal on both sides, or
>     `REFUSED(repeat)`. The pair always lies in the gap: a repeated key is
>     never on the chain, so `k`'s `EXACT` pair comes from §11.3 step 2's
>     alignment inside `k`'s own gap (0003, second addendum of 2026-10-16,
>     item 9);

SPEC.md §11.4:

> - **No pair**: `REFUSED(unaccounted-copy)` if any current leaf is a copy of
>   `k`, and `ORPHANED` otherwise.
