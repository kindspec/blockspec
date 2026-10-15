Control: 0002, Addendum (ambiguous tables), as decided on 2026-10-15: "Otherwise the
lines are a table candidate when the delimiter row's cells, split on
unescaped pipes and trimmed of spaces and tabs, are each `:?-+:?`, and the
header line splits into as many cells. GitHub reads a candidate as a
table. A candidate with no unescaped pipe in one of its two lines is
`ambiguous-table`: `a` over `|---|`, `---|`, `:--` or `:-:`, and `| a |`
or `a|` over `:--`. A candidate with a pipe in both lines is a table."
`a` is one cell against the two of `:--|--:`, so the lines are no
candidate and no table: one paragraph. pandoc 3.1.11.1 (`-f gfm`) and markdown-it-py 3.0.0 read one paragraph.
