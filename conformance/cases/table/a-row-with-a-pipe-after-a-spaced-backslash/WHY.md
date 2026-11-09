# A line below with an unescaped pipe after a backslash

Control: a space separates the backslash from the pipe, so the pipe is
unescaped and the line is a row.

docs/adjudications/0005-closing-draft-0s-gaps.md, item 1:

> A `|` is escaped when the character directly before it is a backslash,
> however many backslashes come before that one.

docs/adjudications/0005-closing-draft-0s-gaps.md, item 3:

> A non-blank line directly below a table's rows is another row when it
> holds an unescaped pipe, starts no other block, and is not only `|`
> with spaces around it. A line that is a row in markdown-it's reading
> and not by this rule stays `table-not-blank-below`.
