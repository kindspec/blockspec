Control: 0002, Addendum (ambiguous tables): "A delimiter line and the
paragraph line over it, in the same container, are judged as two lines".
Here the line over `---` and a form feed is an ATX heading, not a
paragraph line, so there is no header line and nothing to judge. `---`
and a form feed is not a thematic break (CommonMark 0.31.2 §4.1, §2.1),
so it opens a paragraph of its own, the form feed kept. pandoc 3.1.11.1
(`-f gfm`) and markdown-it-py 3.0.0 read a heading and a paragraph.
