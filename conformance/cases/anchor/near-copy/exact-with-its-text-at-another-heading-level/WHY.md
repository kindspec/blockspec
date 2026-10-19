# REFUSED(near-copy): the same text as a heading of another level

The anchor is on the `h2` heading `Limits`, unchanged, `EXACT`. A new `h3`
heading `Limits` is added below the paragraph. Its key differs, so it is
not a copy, and it is unmatched. Words leave out the type: both headings
are the one word `Limits`, word similarity 1. A word similarity that
counted the type as a word (`h2` against `h3`) would give `L = 1`, `T = 4`,
which still refuses; `near-copy/different-one-word-headings-resolve` is
where that difference shows.

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
