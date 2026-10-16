# RESOLVED: an unlike leaf inserted directly below

A short new paragraph sits directly below the anchored one. It is
unmatched, but its similarity to the anchored paragraph is far below 0.5,
so `EXACT`'s near-copy rule does not fire. 0003 §8: a new leaf, unlike the
anchored one, inserted directly above or below it, `RESOLVED`.

SPEC.md §11.4:

> - **`EXACT`**:
>   [...]
>   - an unmatched leaf with similarity to `k` of at least 0.5 and below 1:
>     `REFUSED(near-copy)`.

SPEC.md §11.6:

> | `RESOLVED` | `EXACT`, and the span found | the anchor |
