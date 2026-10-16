# REFUSED(crowded-gap): edited while its gap gained a leaf

The anchored paragraph was edited, and a short new paragraph was added
after it, in the same gap. The new paragraph is unlike it, so the edit
still pairs as `EDITED`, and the new one is left unmatched in the gap.
0003 §8: the anchored leaf's gap gains leaves while it is edited.

SPEC.md §11.4:

> - **`EDITED`**:
>   - an unmatched copy of `k`: `REFUSED(exact-copy)`. A copy that is some
>     base leaf's pair does not count (0003 Q12);
>   - another unmatched leaf in `k`'s gap on the current side:
>     `REFUSED(crowded-gap)`;
>   - an unmatched leaf with similarity to `k` of at least 0.5:
>     `REFUSED(near-copy)`.
