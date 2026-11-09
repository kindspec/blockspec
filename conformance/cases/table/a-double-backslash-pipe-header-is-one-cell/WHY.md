# A double-backslash pipe does not split a header

The header's only pipe is escaped, so it is one cell over a two-cell
delimiter row. The lines are no table candidate, and they are a paragraph.
Counting the backslashes would make two cells and a table.

docs/adjudications/0005-closing-draft-0s-gaps.md, item 1:

> A `|` is escaped when the character directly before it is a backslash,
> however many backslashes come before that one.

SPEC.md, §4.3:

> are each `:?-+:?`, and the header line splits into as many cells.
