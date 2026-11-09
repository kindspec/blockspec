# Two backslashes before a pipe, over a two-cell delimiter

The pipe is escaped, so the header has one cell over a two-cell delimiter
row. That is no table candidate. `-|-` is not a setext underline, a thematic
break or a list item, so both lines are paragraph text. Reading the two
backslashes as one escaped backslash and an open pipe would make this a
table.

docs/adjudications/0005-closing-draft-0s-gaps.md, item 1:

> A `|` is escaped when the character directly before it is a backslash,
> however many backslashes come before that one.

SPEC.md, §4.3:

> are each `:?-+:?`, and the header line splits into as many cells.
