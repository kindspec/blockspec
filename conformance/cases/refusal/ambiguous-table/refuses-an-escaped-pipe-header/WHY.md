0002, Addendum (ambiguous tables): "a header line with no unescaped
pipe, directly over a delimiter row of one cell" is refused. `a \| b`
holds only an escaped pipe, so it is such a line. markdown-it-py 3.0.0
reads a one-cell table with the cell `a | b`, and pandoc 3.1.11.1
(`-f gfm`) a paragraph.
