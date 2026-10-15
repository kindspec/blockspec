0002, Addendum (ambiguous tables): "A lazy header line is read as it
stands, as GitHub reads it. Whitespace before its leading pipe makes an
empty first cell, so `> x`, then an unprefixed ` | a |`, then `> :--` is
no candidate and no table, while `> --|--` under the same two lines is a
two-cell candidate."
The lazy line ` | a |` splits into two cells, an empty one and `a`,
against the one cell of `:--`, so the lines are no candidate: one
paragraph in the block quote. Its content drops the lazy line's initial
space (README, leaf table). pandoc 3.1.11.1 (`-f gfm`) and markdown-it-py
3.0.0 read the same.
