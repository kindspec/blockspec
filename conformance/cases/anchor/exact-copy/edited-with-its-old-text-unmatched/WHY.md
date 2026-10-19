# REFUSED(exact-copy): edited, with its old text unpaired elsewhere

`base` holds the paragraph twice. The first copy (`nth` 0) pairs as
`EDITED` in its gap. The second was deleted, and a verbatim copy of the
old text now sits after the last paragraph, where no base leaf pairs with
it. That copy is unmatched.

SPEC.md §11.4:

> - **`EDITED`**:
>   - an unmatched copy of `k`: `REFUSED(exact-copy)`. A copy that is some
>     base leaf's pair does not count (0003 Q12);
>   - another unmatched leaf in `k`'s gap on the current side, with word
>     similarity to `k` of at least 0.3: `REFUSED(crowded-gap)` (0004);
>   - an unmatched leaf with word similarity to `k` of at least 0.5:
>     `REFUSED(near-copy)`.
