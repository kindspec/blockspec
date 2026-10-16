# MOVED: the unchanged leaf moved to the end

In base order the unique keys sit at current positions 0, 1, 4, 2, 3. The
longest increasing subsequence is 0, 1, 2, 3, so the anchored paragraph's
pair (base 2, current 4) is off the chain: `MOVED`. Its gap on the current
side, between the intro (current 1) and the next paragraph (current 2), is
empty, and nothing is unmatched, so neither `MOVED` rule fires.

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

> | `MOVED` | `MOVED`, and the span found | the anchor, marked moved |
