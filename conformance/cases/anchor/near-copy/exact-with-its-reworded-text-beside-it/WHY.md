# REFUSED(near-copy): the old wording kept in place, a rewording beside it

The anchored paragraph was reworded, and its old wording survives
verbatim in its old place. The verbatim copy pairs on the chain as
`EXACT`, and the reworded paragraph, the real descendant, is unmatched and
not a copy. It keeps most of the old paragraph's words: `L = 31` of the two
paragraphs' 66 words, so its word similarity is at least 0.5. This is the
shape 0004 keeps the rule for: "a reworded paragraph keeps most of its
words, so the shape the rule is for still refuses".

SPEC.md §11.4:

> - **`EXACT`**:
>   [...]
>   - an unmatched leaf that is not a copy of `k`, with word similarity to
>     `k` of at least 0.5: `REFUSED(near-copy)` (0004). When `k` has words,
>     a leaf that differs from it only in runs of U+0009, U+000A, U+000D and
>     U+0020 has word similarity 1 and is not a copy, so it refuses; when `k`
>     has none, no leaf reaches 0.5. Words leave out the type, so a heading
>     with `k`'s text at another level, or a paragraph, refuses.

0003 §4:

> This is `spike/LOG.md` §9's shape when
>   the verbatim copy keeps the paragraph's place in the order
