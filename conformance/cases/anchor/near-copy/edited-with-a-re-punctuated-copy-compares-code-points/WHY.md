# REFUSED(near-copy): edited, with a re-punctuated variant elsewhere, by code points

The anchored paragraph's last setting changed (`backoff=2.` to
`backoff=3.`), and it pairs as `EDITED` in its gap. A re-punctuated variant
of its old text is added after the next paragraph, in another gap, so
neither `exact-copy` nor `crowded-gap` applies. Its word similarity to the
anchored leaf is 0.25, but `EDITED` keeps 0003's code-point check, where it
is above 0.9 (`L = 36`, `T = 78`): `REFUSED(near-copy)`. 0004 gives this
shape as the reason words are not used for `MOVED` and `EDITED`.

SPEC.md §11.4:

> - **`EDITED`**:
>   - an unmatched copy of `k`: `REFUSED(exact-copy)`. A copy that is some
>     base leaf's pair does not count (0003 Q12);
>   - another unmatched leaf in `k`'s gap on the current side:
>     `REFUSED(crowded-gap)`;
>   - an unmatched leaf with similarity to `k` of at least 0.5:
>     `REFUSED(near-copy)`.

0004, *Why each*:

> For `MOVED` and `EDITED` leaves words are not safe: a descendant
> re-punctuated (`Set timeout=30, retries=5, backoff=2.` becoming
> `Set timeout=30; retries=5; backoff=2;`) has word similarity 0.25 and
> code-point similarity above 0.9, and comparing words would let the comment
> follow a sibling. Those checks stay
> as 0003 wrote them.
