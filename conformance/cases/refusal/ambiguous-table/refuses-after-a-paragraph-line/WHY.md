0002, Addendum (ambiguous tables): refused as `ambiguous-table` is "a
header line with no pipe over a one-cell delimiter row: `a` over `|---|`,
`---|` or `:-:|`", and "They are refused in a block quote and a list item
as at top level." GitHub reads a one-column table there, and pandoc and
markdown-it read a paragraph.
The same addendum: "Where the shape also follows a non-blank line in its
container, it is `ambiguous-table`, not `table-not-blank-above`: the table
exists in only one of the readings."
