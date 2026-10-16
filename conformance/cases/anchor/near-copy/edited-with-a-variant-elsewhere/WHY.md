# REFUSED(near-copy): edited, with another variant of it elsewhere

The anchored paragraph pairs as `EDITED` in its gap. Another variant of
it, unmatched and in another gap, has a similarity of at least 0.5 to it.
It is not a copy and not in the anchored leaf's gap, so the first two
`EDITED` rules do not apply.

SPEC.md §11.4:

> - **`EDITED`**:
>   - an unmatched copy of `k`: `REFUSED(exact-copy)`. A copy that is some
>     base leaf's pair does not count (0003 Q12);
>   - another unmatched leaf in `k`'s gap on the current side:
>     `REFUSED(crowded-gap)`;
>   - an unmatched leaf with similarity to `k` of at least 0.5:
>     `REFUSED(near-copy)`.
