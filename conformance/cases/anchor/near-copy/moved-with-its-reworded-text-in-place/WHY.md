# REFUSED(near-copy): reworded in place, the old wording quoted at the end

`spike/LOG.md` §9's shape: the paragraph is reworded where it stands, and
its original wording is quoted at the end of the document. The quote is
unique in both snapshots and off the chain, so the anchor's pair is
`MOVED`, and the reworded paragraph is unmatched with a similarity of at
least 0.5. The refilled-gap rule would also apply; near-copy comes first.

SPEC.md §11.4:

> - **`MOVED`**:
>   - an unmatched leaf with similarity to `k` of at least 0.5:
>     `REFUSED(near-copy)`;
>   - an unmatched leaf in `k`'s gap on the current side:
>     `REFUSED(refilled-gap)`.
>
> [...] the first rule that applies decides
