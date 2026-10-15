Owner's ruling of 2026-10-14, replacing README reading 9's "exactly
`---`": a closing line of `---` followed only by spaces or tabs closes the
frontmatter, as pandoc reads a YAML metadata block. Line 3 is `---` and two
spaces, so the frontmatter is lines 1 to 3, and line 4 is a paragraph.

This case was first written under the older reading, at
refusal/setext-heading/refuses-a-closing-line-with-trailing-spaces, where
the same input was refused. The owner reversed that reading, so the case
moved here and its expectation changed.
