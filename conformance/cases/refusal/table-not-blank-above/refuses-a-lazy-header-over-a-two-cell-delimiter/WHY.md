0002, Addendum (ambiguous tables): "A lazy header line is read as it
stands, as GitHub reads it. Whitespace before its leading pipe makes an
empty first cell, so `> x`, then an unprefixed ` | a |`, then `> :--` is
no candidate and no table, while `> --|--` under the same two lines is a
two-cell candidate."
Here the two lines are a two-cell candidate with a pipe in both, so they
are a table, and the addendum continues: "If the two lines alone are a
table, the paragraph line above them makes it `table-not-blank-above`."
`x` is that line. pandoc 3.1.11.1 (`-f gfm`) and markdown-it-py 3.0.0 read
one paragraph, since neither opens a table on a lazy header line; the
addendum follows GitHub's reading here.
