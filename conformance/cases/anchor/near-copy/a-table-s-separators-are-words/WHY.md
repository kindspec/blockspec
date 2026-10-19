# REFUSED(near-copy): a table's separators are words

The anchored table is unchanged, `EXACT`. A new table at the end has three
columns too, a header of other words and three rows of empty cells. A
table's text joins its cells with ` | `, so each separator is a word `|`,
and an empty-celled row's text, ` |  | `, is the two words `|` and `|`.
The anchored table's text is twenty words (a header and three rows of five
words each), eight of them `|`; the new table's is eleven, also eight `|`.
They share only the separators: `L = 8`, `T = 31`, and `4·L = 32 ≥ 31`. By
code points the two are below 0.5 (`L = 35`, `T = 144`), and 0003 resolved
this.

The words follow from §11.2's definitions as written: a table's
`leaf.text` is the string §11.2 builds, and words split it at spaces
only.

SPEC.md §11.2:

> **A table's text** is one string (0003, addendum, detail 3). Its cells, as
> the suite's reading 8 normalises them (header row first, each cell trimmed
> of spaces and tabs, `\|` read as `|`, a short row padded with `""`, cells past
> the header's width dropped), each have every `|` written as `\|`; they are
> joined by ` | ` within a row and the rows by `\n`; and the result is
> normalised to NFC. The escape keeps the string unambiguous: a `|` from a

SPEC.md §11.2:

> The **word similarity** of two leaves (0004) is the same formula over
> words. A leaf's **words** are its `leaf.text` split at each run of U+0009,
> U+000A, U+000D and U+0020, empty pieces left out; `m` and `n` count words,
> which are compared exactly, and `L` is the length of a longest common
> subsequence of the two word sequences. It is 0 when either leaf has no
> words. Only §11.4's near-copy check on an `EXACT` leaf uses it, including
> where §11.9 runs §11.4 for a transclusion.

SPEC.md §11.4:

> - **`EXACT`**:
>   [...]
>   - an unmatched leaf that is not a copy of `k`, with word similarity to
>     `k` of at least 0.5: `REFUSED(near-copy)` (0004). When `k` has words,
>     a leaf that differs from it only in runs of U+0009, U+000A, U+000D and
>     U+0020 has word similarity 1 and is not a copy, so it refuses; when `k`
>     has none, no leaf reaches 0.5. Words leave out the type, so a heading
>     with `k`'s text at another level, or a paragraph, refuses.
