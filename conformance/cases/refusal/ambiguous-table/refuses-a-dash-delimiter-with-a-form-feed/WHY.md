0002, Addendum (ambiguous tables), as widened on 2026-10-15: refused are
"a paragraph's last line, and the line under it in the same container, that
GitHub reads as a table header and delimiter row and that pandoc and
markdown-it do not both read as one", among them "a one-cell header line,
with or without a pipe, over a delimiter row with no pipe that is not a
setext underline: `a` over `:--`, `--:` or `:-:`, `| a |` or `a|` over
`:--`", and "a delimiter row whose cells carry a form feed or a vertical
tab". "They are refused in a block quote and a list item as at top level."
A setext underline may be followed only by spaces or tabs (CommonMark
0.31.2 §4.3, and §2.1: a space is U+0020), so `---` followed by a form feed (U+000C) is not
one, nor a thematic break (§4.1), and CommonMark readers continue the
paragraph. GitHub's parser does not take it as an underline either, and
reads a one-cell delimiter row. pandoc 3.1.11.1 (`-f gfm`) and markdown-it-py 3.0.0 read one paragraph.
