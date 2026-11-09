# A code fence holding a pipe, directly below a table

The info string holds an unescaped pipe, but the line starts a fenced code
block, so it is not a row.

docs/adjudications/0005-closing-draft-0s-gaps.md, item 3:

> A non-blank line directly below a table's rows is another row when it
> holds an unescaped pipe, starts no other block, and is not only `|`
> with spaces around it. A line that is a row in markdown-it's reading
> and not by this rule stays `table-not-blank-below`.
