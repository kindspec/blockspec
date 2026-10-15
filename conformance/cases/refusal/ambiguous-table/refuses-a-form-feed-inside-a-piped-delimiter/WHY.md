0002, Addendum (ambiguous tables), as widened on 2026-10-15: refused are
"a paragraph's last line, and the line under it in the same container, that
GitHub reads as a table header and delimiter row and that pandoc and
markdown-it do not both read as one". "GitHub's reading needs no pipe in
either line, and trims form feeds and vertical tabs from cells as well as
spaces and tabs. The reading pandoc and markdown-it share needs an
unescaped pipe in both lines, and trims spaces and tabs only."
GitHub trims the form feed from the delimiter cell `---` and the form feed,
and reads a one-cell table. pandoc 3.1.11.1 (`-f gfm`) and markdown-it-py
3.0.0 trim only spaces and tabs, so the cell is not a delimiter, and both
read one paragraph.
