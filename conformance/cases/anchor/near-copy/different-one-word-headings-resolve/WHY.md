# RESOLVED: an unchanged one-word heading beside a new one

The anchor is on the `h2` heading `Limits`, unchanged, `EXACT`. A new `h2`
heading `Channels` is added below the paragraph, unmatched. The two share
no word, so their word similarity is 0. A word similarity that counted the
type as a word would find `h2` in both, `L = 1`, `T = 4`, exactly 0.5, and
refuse: this is the last row of 0004's first table.

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
