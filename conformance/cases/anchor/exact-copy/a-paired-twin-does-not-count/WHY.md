# EDITED and RESOLVED: one of two identical paragraphs edited

`base` holds the paragraph twice, separated by `B`. The first copy was
edited. The second still pairs, through its gap's alignment, with the copy
that remains, so that copy is accounted for: it does not refuse the edited
one, and the edited one, paired, is not a near-copy of the other. 0003 Q12.

SPEC.md §11.4:

> - **`EDITED`**:
>   - an unmatched copy of `k`: `REFUSED(exact-copy)`. A copy that is some
>     base leaf's pair does not count (0003 Q12);
>   - another unmatched leaf in `k`'s gap on the current side:
>     `REFUSED(crowded-gap)`;
>   - an unmatched leaf with similarity to `k` of at least 0.5:
>     `REFUSED(near-copy)`.

SPEC.md §11.4:

> - **`EXACT`**:
>   - if `base` or the current text holds more than one copy of `k`, the
>     number of copies in `k`'s gap must be equal on both sides, or
>     `REFUSED(repeat)`. The pair always lies in the gap: a repeated key is
>     never on the chain, so `k`'s `EXACT` pair comes from §11.3 step 2's
>     alignment inside `k`'s own gap (0003, second addendum of 2026-10-16,
>     item 9);
