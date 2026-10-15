0002, Addendum (ambiguous tables), as widened on 2026-10-15: refused are
"a paragraph's last line, and the line under it in the same container, that
GitHub reads as a table header and delimiter row and that pandoc and
markdown-it do not both read as one". "GitHub's reading needs no pipe in
either line, and trims form feeds and vertical tabs from cells as well as
spaces and tabs. The reading pandoc and markdown-it share needs an
unescaped pipe in both lines, and trims spaces and tabs only."
A form feed is not indentation or a space (CommonMark 0.31.2 §2.1), so a
form feed and `---` is not a setext underline or a thematic break, and
pandoc 3.1.11.1 (`-f gfm`) and markdown-it-py 3.0.0 read one paragraph.
GitHub trims the form feed from the cell and reads a one-cell table.
