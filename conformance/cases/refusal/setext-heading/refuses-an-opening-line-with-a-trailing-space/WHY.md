0002, Addendum (three defaults): "The opening line is exactly `---`."
Line 1 is `---` and a space, so frontmatter does not open, and the lines
parse as CommonMark 0.31.2: line 1 is a thematic break (§4.1 allows
trailing spaces), and line 3, `---`, is a setext underline under line 2
(§4.3), which 0001 refuses. markdown-it-py 3.0.0 and pandoc 3.1.11.1
(`-f commonmark`) read a thematic break and a level 2 heading. pandoc's
`gfm` reader takes the lines as YAML metadata, which this ruling does not
follow.
