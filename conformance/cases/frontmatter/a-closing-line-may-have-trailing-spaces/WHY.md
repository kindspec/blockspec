0002, Addendum (three defaults): "**Frontmatter is closed by a line of
`---` followed only by spaces or tabs**, as pandoc reads a YAML metadata
block, and never by YAML's `...` document end marker. The opening line is
exactly `---`."
This replaced README reading 9's earlier "exactly `---`". Line 3 is `---` and two
spaces, so the frontmatter is lines 1 to 3, and line 4 is a paragraph.

This case was first written under the older reading, at
refusal/setext-heading/refuses-a-closing-line-with-trailing-spaces, where
the same input was refused. The owner reversed that reading, so the case
moved here and its expectation changed.
