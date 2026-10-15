0002, Addendum (three defaults): "**Frontmatter is closed by a line of
`---` followed only by spaces or tabs**, as pandoc reads a YAML metadata
block, and never by YAML's `...` document end marker. The opening line is
exactly `---`."
Line 3 is `---` and a form feed, so it does not close the frontmatter,
and with no other closing line this is not frontmatter (README reading
11). Line 1 is a thematic break and line 2 an ATX heading. Line 3 is not
a thematic break (CommonMark 0.31.2 §4.1, §2.1), and the line over it is
a heading, not a paragraph line, so the ambiguous-table rule ("A
delimiter line and the paragraph line over it") has nothing to judge:
lines 3 and 4 are one paragraph. pandoc 3.1.11.1 (`-f gfm`) and
markdown-it-py 3.0.0 read the same. A reader that let a form feed close
the frontmatter would report frontmatter on lines 1 to 3.

Line 2 is a heading because any paragraph line there would sit over the
form-feed line, which the addendum refuses as `ambiguous-table`.
