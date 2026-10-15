0002, Addendum (three defaults): frontmatter is closed by a line of `---`
followed only by spaces or tabs, "and never by YAML's `...` document end
marker." With no closing `---` the
block is not frontmatter (README reading 11): line 1 is a thematic break,
and lines 2 to 4 are one paragraph.
Note: pandoc 3.1.11.1 (`-f gfm`) reads `...` as the closing line,
as YAML does; the ruling does not follow it here.
