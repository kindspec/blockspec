Control: 0002, Addendum (ambiguous tables): "A candidate with a pipe in
both lines is a table." `a|` over `---|` is a one-cell candidate with an
unescaped pipe in each line and no form feed, so it is a table. pandoc
3.1.11.1 (`-f gfm`) and markdown-it-py 3.0.0 read the same one-cell table.
