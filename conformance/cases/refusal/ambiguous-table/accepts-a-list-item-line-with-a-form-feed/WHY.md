Control: 0002, Addendum (ambiguous tables): "the delimiter row must not
already be a setext underline, a thematic break or a list item, which are
tried first." `- - -` and a form feed is not a thematic break, since a
form feed is not a space or tab (CommonMark 0.31.2 §4.1, §2.1). It is a
bullet item holding a bullet item whose content is `-` and the form feed
(§5.2: `-` with no space after it is not a marker), and a non-empty item
may interrupt a paragraph. So it is no table to any reader: a paragraph
`a`, then one list block. The paragraph keeps its final form feed, since
only spaces or tabs are stripped (README, leaf table); pandoc 3.1.11.1
(`-f gfm`) reads the same tree and keeps it, while markdown-it-py 3.0.0
drops it from the inline text.
