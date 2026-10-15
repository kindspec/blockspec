0002, Addendum (ambiguous tables): refused as `ambiguous-table` is "a
header line with no pipe over a one-cell delimiter row: `a` over `|---|`,
`---|` or `:-:|`", and "They are refused in a block quote and a list item
as at top level." GitHub reads a one-column table there, and pandoc and
markdown-it read a paragraph.
Here the shape is the content of a list item.
