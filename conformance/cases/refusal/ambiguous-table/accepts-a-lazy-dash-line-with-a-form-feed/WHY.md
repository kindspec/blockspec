Control: 0002, Addendum (ambiguous tables): "A line that reaches its
container only lazily is not under the paragraph's last line in its
container, so `> a` over an unprefixed `---` and a form feed is not a
table to any of the three, and is not refused." `---` with a form feed is
neither a setext underline nor a thematic break (CommonMark 0.31.2 §4.3,
§4.1), so it is a lazy continuation line of the quoted paragraph (§5.1),
and the block quote covers both lines. pandoc 3.1.11.1 (`-f gfm`) and
markdown-it-py 3.0.0 read the same.
