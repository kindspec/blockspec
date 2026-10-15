0002, Addendum (ambiguous tables), as decided on 2026-10-15: "A delimiter
line and the paragraph line over it, in the same container, are judged as
two lines, without the line above them."
0002, Addendum (ambiguous tables), as decided on 2026-10-15: "Otherwise the
lines are a table candidate when the delimiter row's cells, split on
unescaped pipes and trimmed of spaces and tabs, are each `:?-+:?`, and the
header line splits into as many cells. GitHub reads a candidate as a
table. A candidate with no unescaped pipe in one of its two lines is
`ambiguous-table`: `a` over `|---|`, `---|`, `:--` or `:-:`, and `| a |`
or `a|` over `:--`. A candidate with a pipe in both lines is a table."
"If the two lines alone are `ambiguous-table`, so is the document, which
takes precedence over `table-not-blank-above`." `a` over `:-:|`, judged
without `Intro.` above it, is a candidate with no pipe in its header line.
pandoc 3.1.11.1 (`-f gfm`) and markdown-it-py 3.0.0 read one paragraph.
