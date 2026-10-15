0002, Addendum (three defaults): "**Frontmatter is closed by a line of
`---` followed only by spaces or tabs**, as pandoc reads a YAML metadata
block, and never by YAML's `...` document end marker. The opening line is
exactly `---`."
Line 3 is `---` followed by U+000C, a form feed, which is not a space or a
tab, so it does not close the frontmatter, and the document parses as in
frontmatter/a-no-break-space-does-not-close-it: a thematic break, then
one paragraph of lines 2 to 4 with the form feed kept. CommonMark 0.31.2
§2.1 counts a form feed as Unicode whitespace but not as a space, and its
line endings are only LF, CR and CRLF, so the form feed does not end line
3 either. A reader that split lines with Python's `str.splitlines()`,
which breaks at a form feed, would count five lines. pandoc 3.1.11.1
(`-f commonmark`) and markdown-it-py 3.0.0 read the same as this case.
