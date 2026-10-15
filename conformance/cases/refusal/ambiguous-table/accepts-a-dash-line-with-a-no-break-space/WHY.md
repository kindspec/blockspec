Control: 0002, Addendum (ambiguous tables), as decided on 2026-10-15: "A form feed
or a vertical tab in either line refuses them. If either line holds one,
and the delimiter line holds nothing but `|`, `:`, `-`, spaces, tabs, form
feeds and vertical tabs, with at least one `-`, the lines are
`ambiguous-table`, whatever the header line holds."
0002, Addendum (ambiguous tables), as decided on 2026-10-15: "Otherwise the
lines are a table candidate when the delimiter row's cells, split on
unescaped pipes and trimmed of spaces and tabs, are each `:?-+:?`, and the
header line splits into as many cells. GitHub reads a candidate as a
table. A candidate with no unescaped pipe in one of its two lines is
`ambiguous-table`: `a` over `|---|`, `---|`, `:--` or `:-:`, and `| a |`
or `a|` over `:--`. A candidate with a pipe in both lines is a table."
`---` and a no-break space holds a character outside the form-feed rule's
list, and trimmed of spaces and tabs the cell is not `:?-+:?`, so the lines
are neither refused nor a candidate. Nor is the line a setext underline or
a thematic break (CommonMark 0.31.2 §4.3, §4.1, §2.1). The two lines are
one paragraph, the no-break space kept. pandoc 3.1.11.1 (`-f gfm`) and markdown-it-py 3.0.0 read one paragraph.
