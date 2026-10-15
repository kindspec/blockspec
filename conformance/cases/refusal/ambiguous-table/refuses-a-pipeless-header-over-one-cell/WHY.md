0002, Addendum (ambiguous tables): "a header line with no unescaped pipe,
directly over a delimiter row of one cell (`a` over `|---|`, `---|` or
`:-:|`), in any container" is refused as `ambiguous-table`. GitHub reads a
one-column table there, and pandoc and markdown-it read a paragraph.
