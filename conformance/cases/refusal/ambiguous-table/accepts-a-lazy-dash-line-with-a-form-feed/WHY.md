Control: 0002, Addendum (ambiguous tables): "A delimiter line and the
paragraph line over it, in the same container, are judged as two lines".
`---` and a form feed is neither a setext underline nor a thematic break
(CommonMark 0.31.2 §4.3, §4.1), so it joins the quoted paragraph only as a
lazy continuation line (§5.1). It carries no `>`, so it is not a line in
the block quote's container, and the rule does not reach it. The
addendum's earlier wording (at `a123bbc`) said so outright ("A line that reaches its
container only lazily is not under the paragraph's last line in its
container"); the rewrite speaks only of lazy header lines. pandoc
3.1.11.1 (`-f gfm`) and markdown-it-py 3.0.0 read one block quote holding
one paragraph.
