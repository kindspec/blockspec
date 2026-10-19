# REFUSED(near-copy): the old wording kept in place, a rewording beside it

The anchored paragraph was reworded, and its old wording survives
verbatim in its old place. The verbatim copy pairs on the chain as
`EXACT`, and the reworded paragraph, the real descendant, is unmatched with
a similarity of at least 0.5, and it is not a copy.

**Under 0004** the near-copy rule compares the word similarity. The
anchored paragraph has 34 words (`p` and 33 pieces of text); the rewording
replaces `rolling 30-second` with `sliding half-minute`, two words of 34,
so `L = 32`, `T = 68`: `2·32/68`, at least 0.5 (`4·32 = 128 ≥ 68`), and its
key differs from the anchored paragraph's, so it is not a copy. The
outcome is unchanged.

SPEC.md §11.4:

> - **`EXACT`**:
>   [...]
>   - an unmatched leaf that is not a copy of `k`, with word similarity to
>     `k` of at least 0.5: `REFUSED(near-copy)`. A leaf that differs from `k`
>     only in whitespace has word similarity 1 and is not a copy, so it
>     refuses (0004).

0003 §4:

> This is `spike/LOG.md` §9's shape when
>   the verbatim copy keeps the paragraph's place in the order
