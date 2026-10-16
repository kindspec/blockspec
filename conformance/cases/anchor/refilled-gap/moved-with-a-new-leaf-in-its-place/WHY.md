# REFUSED(refilled-gap): moved, and its old place holds a new leaf

The anchored paragraph is unchanged at the end of the document, `MOVED`.
Where it was, between `I` and `B`, the current text holds a short new
paragraph, unmatched and unlike it. 0003 Q6 keeps this rule, at the cost
of refusing a real move whose old place gained a paragraph.

SPEC.md §11.4:

> - **`MOVED`**:
>   - an unmatched leaf with similarity to `k` of at least 0.5:
>     `REFUSED(near-copy)`;
>   - an unmatched leaf in `k`'s gap on the current side:
>     `REFUSED(refilled-gap)`.

SPEC.md §11.4:

> The anchored leaf `k` is the leaf of `base` with key `leaf.type` and
> `leaf.text`, at ordinal `nth`. Its **gap** is bounded by the nearest chain
> pair before `k` and the nearest after it, in base order, or by a snapshot's
> edge where there is none. On the base side the gap is the leaves strictly
> between those two pairs' base positions, and on the current side the leaves
> strictly between their current positions.
