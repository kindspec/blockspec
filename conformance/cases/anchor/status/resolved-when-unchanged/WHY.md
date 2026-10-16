# RESOLVED: the document is unchanged

The record's `base` is the current blob of `policy.md`. Every leaf pairs
with itself on the chain, so the anchored paragraph is `EXACT` and the span
keeps its offset, code points 31 to 40 of the paragraph's text.

SPEC.md §11.3:

> 1. **The chain.** Take each key that occurs exactly once in `base` and
>    exactly once in the current text, as a pair of positions. The longest
>    subsequence of those pairs, in base order, whose current positions
>    increase is the **chain**. Its pairs are `EXACT`. Every other such pair
>    is `MOVED`.

SPEC.md §11.5:

> For `EXACT` and `MOVED`, the span keeps its offset in the paired leaf, whose
> text is unchanged.

SPEC.md §11.6:

> | `RESOLVED` | `EXACT`, and the span found | the anchor |
