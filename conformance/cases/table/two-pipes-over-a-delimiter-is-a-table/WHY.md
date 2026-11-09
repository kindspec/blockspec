# Two pipes over a delimiter row is a table of one empty cell

The control for `a-lone-pipe-over-a-delimiter-is-a-paragraph`. `||` has one
cell, empty, so it matches a delimiter row of one cell. markdown-it-py 3.0.0
reads it as a table.
