# REFUSED(near-copy): the heading's text as a paragraph

The anchor is on the `h2` heading `Limits`, unchanged, `EXACT`. A new
paragraph `Limits` is added below. It is not a copy (its type is `p`), and
it is unmatched; its one word is the heading's one word, word similarity 1.

SPEC.md §11.4:

> - **`EXACT`**:
>   [...]
>   - an unmatched leaf that is not a copy of `k`, with word similarity to
>     `k` of at least 0.5: `REFUSED(near-copy)` (0004). When `k` has words,
>     a leaf that differs from it only in runs of U+0009, U+000A, U+000D and
>     U+0020 has word similarity 1 and is not a copy, so it refuses; when `k`
>     has none, no leaf reaches 0.5. Words leave out the type, so a heading
>     with `k`'s text at another level, or a paragraph, refuses.
