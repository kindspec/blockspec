# The same `---` line, when it is not frontmatter

Control for item 4: after a blank line `---` is a thematic break, not
frontmatter's closing line, so it is a non-blank line directly above the
table.

docs/adjudications/0005-closing-draft-0s-gaps.md, item 4:

> **4. Frontmatter's closing line is an edge.** A table directly below
> it has its container's edge above it, and is not
> `table-not-blank-above`.

SPEC.md, §4.3:

> any non-blank line directly above or below a table in its container, a
> heading or a marker included, is refused
