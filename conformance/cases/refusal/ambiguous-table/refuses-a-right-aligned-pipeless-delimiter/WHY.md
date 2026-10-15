0002, Addendum (ambiguous tables), as widened on 2026-10-15: refused are
"a paragraph's last line, and the line under it in the same container, that
GitHub reads as a table header and delimiter row and that pandoc and
markdown-it do not both read as one", among them "a one-cell header line,
with or without a pipe, over a delimiter row with no pipe that is not a
setext underline: `a` over `:--`, `--:` or `:-:`, `| a |` or `a|` over
`:--`", and "a delimiter row whose cells carry a form feed or a vertical
tab". "They are refused in a block quote and a list item as at top level."
`--:` is the right-aligned form. pandoc 3.1.11.1 (`-f gfm`) and markdown-it-py 3.0.0 read one paragraph.
