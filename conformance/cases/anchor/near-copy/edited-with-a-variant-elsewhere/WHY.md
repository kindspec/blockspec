# REFUSED(near-copy): edited, with another variant of it elsewhere

The anchored paragraph pairs as `EDITED` in its gap. Another variant of
it, unmatched and in another gap, has a similarity of at least 0.5 to it.
It is not a copy and not in the anchored leaf's gap, so the first two
`EDITED` rules do not apply.

**Under 0004** the near-copy rule compares the word similarity. The
anchored paragraph has 34 words (`p` and 33 pieces of text), and the
variant has the same 34 but for `four` and `redundant` in place of `three`
and `independent`, so `L = 32`, `T = 68`: `2·32/68`, at least 0.5 (`4·32 =
128 ≥ 68`). The variant is outside the anchored leaf's gap, so crowded-gap
does not reach it. The outcome is unchanged.

SPEC.md §11.4:

> - **`EDITED`**:
>   - an unmatched copy of `k`: `REFUSED(exact-copy)`. A copy that is some
>     base leaf's pair does not count (0003 Q12);
>   - another unmatched leaf in `k`'s gap on the current side, with word
>     similarity to `k` of at least 0.3: `REFUSED(crowded-gap)` (0004);
>   - an unmatched leaf with word similarity to `k` of at least 0.5:
>     `REFUSED(near-copy)`.
