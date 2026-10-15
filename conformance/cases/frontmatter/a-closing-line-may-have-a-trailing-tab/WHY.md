0002, Addendum (three defaults): "**Frontmatter is closed by a line of
`---` followed only by spaces or tabs**, as pandoc reads a YAML metadata
block, and never by YAML's `...` document end marker. The opening line is
exactly `---`."
Line 3 is `---`
and a tab, so the frontmatter is lines 1 to 3. Line 6 is a later exact
`---`, which, after a blank line, is a thematic break (CommonMark 0.31.2
§4.1); a reader that still wanted an exact `---` would close the
frontmatter there instead and lose the paragraph on line 4. pandoc
3.1.11.1 (`-f markdown`) reads the same.
