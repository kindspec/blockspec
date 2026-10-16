# RESOLVED: another leaf was edited

Only the paragraph after the anchored one changed. The anchored paragraph's
key is unique in both snapshots and stays on the chain, and no unmatched leaf
is similar to it: the edited paragraph pairs as `EDITED` with its own base
leaf. 0003 §8's first row: other leaves edited, `RESOLVED`.

SPEC.md §11.3:

> 1. **The chain.** Take each key that occurs exactly once in `base` and
>    exactly once in the current text, as a pair of positions. The longest
>    subsequence of those pairs, in base order, whose current positions
>    increase is the **chain**. Its pairs are `EXACT`. Every other such pair
>    is `MOVED`.

SPEC.md §11.6:

> | `RESOLVED` | `EXACT`, and the span found | the anchor |
