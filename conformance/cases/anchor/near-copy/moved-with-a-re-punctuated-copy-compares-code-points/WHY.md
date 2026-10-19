# REFUSED(near-copy): moved, with a re-punctuated variant, by code points

The anchored paragraph moved below the next two, so it pairs as `MOVED`. A
re-punctuated variant of it is added after it, unmatched. Its word
similarity is 0.25 (`Set` is the one word in common of eight), but `MOVED`
keeps 0003's code-point check, where the similarity is above 0.9
(`L = 36`, `T = 78`): `REFUSED(near-copy)`. A resolver that used words here
would report `MOVED`.

SPEC.md §11.4:

> - **`MOVED`**:
>   - an unmatched leaf with similarity to `k` of at least 0.5:
>     `REFUSED(near-copy)`;

0004, *Why each*:

> For `MOVED` and `EDITED` leaves words are not safe: a descendant
> re-punctuated (`Set timeout=30, retries=5, backoff=2.` becoming
> `Set timeout=30; retries=5; backoff=2;`) has word similarity 0.25 and
> code-point similarity above 0.9, and comparing words would let the comment
> follow a sibling. Those checks stay
> as 0003 wrote them.
