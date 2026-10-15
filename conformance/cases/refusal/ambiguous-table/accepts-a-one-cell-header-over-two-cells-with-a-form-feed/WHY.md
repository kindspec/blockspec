Control: 0002, Addendum (ambiguous tables): "Either way, the header's cells
must be as many as the delimiter row's", and "A one-cell header over a
delimiter row of two or more cells is a table to none of them, and is not
refused." The form feed would make the delimiter row valid to GitHub, but
the header has one cell against two. pandoc 3.1.11.1 (`-f gfm`) and
markdown-it-py 3.0.0 read one paragraph.
