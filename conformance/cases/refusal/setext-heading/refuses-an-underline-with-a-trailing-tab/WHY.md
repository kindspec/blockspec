0001 refuses setext headings. CommonMark 0.31.2 §4.3: a setext underline
may have "any number of trailing spaces or tabs". 0002, Addendum (ambiguous
tables): "the delimiter row must not already be a setext underline, a
thematic break or a list item, which are tried first", so this is a setext
heading, not a table to GitHub. pandoc 3.1.11.1 (`-f gfm`) and
markdown-it-py 3.0.0 read a level 2 heading.
