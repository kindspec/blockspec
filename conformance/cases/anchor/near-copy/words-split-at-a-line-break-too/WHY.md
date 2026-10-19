# REFUSED(near-copy): a line break separates words as a space does

Added under 0004. The anchored paragraph `k`,

    Every channel trips whenever it reads high on two successive scans of the window.

is unchanged and `EXACT` on the chain. A new paragraph follows it, written
on two lines:

    Every channel reads high
    on its own scans.

so its text is `Every channel reads high\non its own scans.`, with a line
feed between `high` and `on`.

**Split at every run of tab, LF, CR and space**, as §11.2 says, the new
paragraph's words are `p`, `Every`, `channel`, `reads`, `high`, `on`,
`its`, `own`, `scans.`: 9. `k` has 15 (`p` and 14 pieces of
text). The first six are common, in order, so `L = 6`,
`T = 15 + 9 = 24`, and the word similarity is
`2·6/24`, exactly 0.5: `4·6 = 24 ≥ 24`. The paragraph is
not a copy of `k`, so the `EXACT` near-copy rule refuses.

**Split at spaces only**, `high` and `on` stay one word, `high\non`,
which `k` does not have. The new paragraph would have 8 words,
of which `p`, `Every`, `channel` and `reads` are common: `L = 4`,
`T = 23`, `2·4/23`, below 0.5 (`4·4 = 16 < 23`), and the anchor would
resolve. So an implementation that splits at spaces only reports
`RESOLVED` here.

`near-copy/exact-with-an-unmatched-leaf-at-one-half` is the same paragraph
on one line, also refused; `near-copy/exact-with-an-unmatched-leaf-just-below-one-half`
is the control below the threshold.

SPEC.md §11.2:

> The **word similarity** of two leaves is the same formula over words
> (0004): a leaf's **words** are its `leaf.type`, then its `leaf.text` split
> at each run of U+0009, U+000A, U+000D and U+0020, empty pieces left out.
> `m` and `n` count words, which are compared exactly, and `L` is the length
> of a longest common subsequence of the two word sequences.

SPEC.md §11.4:

> - **`EXACT`**:
>   [...]
>   - an unmatched leaf that is not a copy of `k`, with word similarity to
>     `k` of at least 0.5: `REFUSED(near-copy)`.

SPEC.md §11.3:

> | similarity at least 0.5 | `4·L ≥ T` |
