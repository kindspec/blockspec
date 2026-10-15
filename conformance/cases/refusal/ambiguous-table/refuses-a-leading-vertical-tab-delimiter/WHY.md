0002, Addendum (ambiguous tables), as widened on 2026-10-15: refused are
"a paragraph's last line, and the line under it in the same container, that
GitHub reads as a table header and delimiter row and that pandoc and
markdown-it do not both read as one". "GitHub's reading needs no pipe in
either line, and trims form feeds and vertical tabs from cells as well as
spaces and tabs. The reading pandoc and markdown-it share needs an
unescaped pipe in both lines, and trims spaces and tabs only."
As refusal/ambiguous-table/refuses-a-leading-form-feed-delimiter, with a
vertical tab (U+000B). pandoc 3.1.11.1 (`-f gfm`) and markdown-it-py 3.0.0
read one paragraph.
