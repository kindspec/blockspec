# A lone pipe over a delimiter row is a paragraph

A `|` alone has no cells, so it cannot match a delimiter row of one cell, and
the two lines are a paragraph. GFM tables, "the header row must match the
delimiter row in the number of cells". markdown-it-py 3.0.0 reads it
that way. A second implementation read it as a table, which found this
gap in the tree.
