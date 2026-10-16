# REFUSED(unaccounted-copy) and RESOLVED: the first of two twins deleted

`R` occurs between `I` and `B`, and between `B` and the last paragraph. The
first copy is deleted. The first gap now holds no copy, so `nth` 0 has no
pair while a copy of it survives: `REFUSED(unaccounted-copy)`. The second
gap holds one copy on both sides, so `nth` 1 pairs there and the counts
agree: `RESOLVED`.

SPEC.md §11.4:

> - **No pair**: `REFUSED(unaccounted-copy)` if any current leaf is a copy of
>   `k`, and `ORPHANED` otherwise.

SPEC.md §11.4:

> - **`EXACT`**:
>   - if `base` or the current text holds more than one copy of `k`, the
>     number of copies in `k`'s gap must be equal on both sides, and the pair
>     must lie in the gap, or `REFUSED(repeat)`;
