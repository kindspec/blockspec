# A header whose only pipe follows two backslashes

That pipe is escaped, so the header has one cell and no unescaped pipe, over
a one-cell delimiter: a candidate with no unescaped pipe in one line.

docs/adjudications/0005-closing-draft-0s-gaps.md, item 1:

> A `|` is escaped when the character directly before it is a backslash,
> however many backslashes come before that one.

SPEC.md, §4.3:

> A candidate with no unescaped pipe in one of its two lines is refused
> as `ambiguous-table`.
