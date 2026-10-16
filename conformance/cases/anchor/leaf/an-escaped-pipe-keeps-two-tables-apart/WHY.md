# DETACHED: a one-column table and a two-column table are not copies

`base` has a one-column table whose cells hold a pipe, and the current
text a two-column table with the same characters. With the `\|` escape
their texts differ (`Vote \| Rule` against `Vote | Rule`), so they are not
copies and do not pair on the chain. They pair as `EDITED`, and the span's
short prefix, `Vote \| Rule\n`, is not in the new text, so there is no hit.
Without the escape the two would be copies and the anchor `RESOLVED`.

SPEC.md §11.2:

> **A table's text** is one string (0003, addendum, detail 3). Its cells, as
> the suite's reading 8 normalises them (header row first, each cell trimmed
> of spaces and tabs, `\|` read as `|`, a short row padded with `""`, cells past
> the header's width dropped), each have every `|` written as `\|`; they are
> joined by ` | ` within a row and the rows by `\n`; and the result is
> normalised to NFC. The escape keeps the string unambiguous: a `|` from a
> cell follows a `\`, and a separator's follows a space, which a trimmed cell
> never ends in. Without it, a one-cell row `a | b` and a two-cell row `a`,
> `b` would be copies.

SPEC.md §11.5:

> With no hit the anchor is
> `DETACHED`

SPEC.md §11.6:

> | `DETACHED` | the leaf has a pair, and the span does not survive in it | on the paired leaf, flagged, with the text as it stood at `base` |
