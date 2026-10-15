0002, Addendum (ambiguous tables): refused are "a paragraph's last line,
and the line under it in the same container, that GitHub reads as a table
header and delimiter row and that pandoc and markdown-it do not both read
as one". "GitHub's reading needs no pipe in either line", so it reads `a
\| b` over `|---|` as a one-cell table; "The reading pandoc and
markdown-it share needs an unescaped pipe in both lines", and `a \| b`
holds only an escaped one. markdown-it-py 3.0.0
reads a one-cell table with the cell `a | b`, and pandoc 3.1.11.1
(`-f gfm`) a paragraph.
