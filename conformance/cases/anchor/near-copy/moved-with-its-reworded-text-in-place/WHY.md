# REFUSED(near-copy): reworded in place, the old wording quoted at the end

`spike/LOG.md` §9's shape: the paragraph is reworded where it stands, and
its original wording is quoted at the end of the document. The quote is
unique in both snapshots and off the chain, so the anchor's pair is
`MOVED`, and the reworded paragraph is unmatched with a similarity of at
least 0.5. The refilled-gap rule would also apply; near-copy comes first.

**Under 0004** the near-copy rule compares the word similarity. The
anchored paragraph has 34 words (`p` and 33 pieces of text); the rewording
replaces two of them (`rolling 30-second` with `sliding half-minute`), so
`L = 32`, `T = 68`: `2·32/68`, at least 0.5 (`4·32 = 128 ≥ 68`). The
outcome is unchanged.

SPEC.md §11.4:

> - **`MOVED`**:
>   - an unmatched leaf with word similarity to `k` of at least 0.5:
>     `REFUSED(near-copy)`;
>   - an unmatched leaf in `k`'s gap on the current side:
>     `REFUSED(refilled-gap)`.
>
> [...] the first rule that applies decides
