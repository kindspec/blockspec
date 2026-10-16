# EDITED: a span in a table, with a row edited

The table's text is its rows joined by `\n` and its cells by ` | `. The span
`4.2 sigma` starts at code point 32, so its prefix is the full 32 code
points `Limit | Value\nscram threshold | `. The last row changed, beyond the
suffix, so the table pairs as `EDITED` and the span keeps offset 32.

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

SPEC.md §11.6:

> | `EDITED` | `EDITED`, and the span found | the anchor, marked changed |
