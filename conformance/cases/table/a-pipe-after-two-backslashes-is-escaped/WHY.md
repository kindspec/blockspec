# A pipe after two backslashes is escaped

The character directly before the third cell-looking pipe is a backslash, so
the row has two cells. Reading 8 reads `\|` as `|`, which removes only that
one backslash.

docs/adjudications/0005-closing-draft-0s-gaps.md, item 1:

> A `|` is escaped when the character directly before it is a backslash,
> however many backslashes come before that one.
