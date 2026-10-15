0002, Addendum (ambiguous tables): "a header line with no unescaped pipe,
directly over a delimiter row of one cell (`a` over `|---|`, `---|` or
`:-:|`), in any container" is refused as `ambiguous-table`. GitHub reads a
one-column table there, and pandoc and markdown-it read a paragraph.
The same addendum: "Where the shape also follows a non-blank line in its
container, it is `ambiguous-table`, not `table-not-blank-above`: the table
exists in only one of the readings."
