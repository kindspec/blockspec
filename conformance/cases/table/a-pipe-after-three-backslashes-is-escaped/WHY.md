# A pipe after three backslashes is escaped

The count of backslashes does not matter: the pipe is escaped, and one
backslash goes with it when the cell is read.

docs/adjudications/0005-closing-draft-0s-gaps.md, item 1:

> A `|` is escaped when the character directly before it is a backslash,
> however many backslashes come before that one.
