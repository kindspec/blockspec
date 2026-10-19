# RESOLVED: short unrelated leaves that reach 0.5 only by code points

0004's own example. The anchored paragraph, one link, is unchanged,
`EXACT`, and a new paragraph with another link is added below it. By code
points their keys are similar (`L = 24`, `T = 78`, about 0.62), which 0003
refused as a near-copy. They share no word (`[The`, `Slice`,
`Type](ch04-03-slices.md)` against `[Generic`, `Data`,
`Types](ch10-01-syntax.md)`), so the word similarity §11.4 now uses for an
`EXACT` leaf is 0.

SPEC.md §11.4:

> - **`EXACT`**:
>   [...]
>   - an unmatched leaf that is not a copy of `k`, with word similarity to
>     `k` of at least 0.5: `REFUSED(near-copy)` (0004). When `k` has words,
>     a leaf that differs from it only in runs of U+0009, U+000A, U+000D and
>     U+0020 has word similarity 1 and is not a copy, so it refuses; when `k`
>     has none, no leaf reaches 0.5. Words leave out the type, so a heading
>     with `k`'s text at another level, or a paragraph, refuses.

0004, *Why each*:

> leaves reach 0.5 by code points: `[The Slice Type](ch04-03-slices.md)` and
> `[Generic Data Types](ch10-01-syntax.md)` score 0.62, and share no word. A
> reworded paragraph keeps most of its words, so the shape the rule is for
> still refuses. Words leave out the leaf's type, so two one-word headings
> with different words are not near-copies of each other; the same word at
> another heading level still is.
