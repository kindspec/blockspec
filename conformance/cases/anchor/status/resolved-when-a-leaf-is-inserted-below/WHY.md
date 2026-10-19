# RESOLVED: an unlike leaf inserted directly below

A short new paragraph sits directly below the anchored one. It is
unmatched, but its similarity to the anchored paragraph is far below 0.5,
so `EXACT`'s near-copy rule does not fire. 0003 §8: a new leaf, unlike the
anchored one, inserted directly above or below it, `RESOLVED`.

**Under 0004** the near-copy rule compares the word similarity. The
anchored paragraph has 34 words (`p` and 33 pieces of text); `See the
annex.` has `p`, `See`, `the`, `annex.`, of which `p` and `the` are
common, so `L = 2`, `T = 38`: `2·2/38`, below 0.5 (`4·2 = 8 < 38`). The
outcome is unchanged.

SPEC.md §11.4:

> - **`EXACT`**:
>   [...]
>   - an unmatched leaf that is not a copy of `k`, with word similarity to
>     `k` of at least 0.5: `REFUSED(near-copy)`. A leaf that differs from `k`
>     only in whitespace has word similarity 1 and is not a copy, so it
>     refuses (0004).

SPEC.md §11.6:

> | `RESOLVED` | `EXACT`, and the span found | the anchor |
