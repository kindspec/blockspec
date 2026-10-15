Owner's ruling of 2026-10-14: a closing line of `---` followed only by
spaces or tabs closes the frontmatter, as pandoc reads it. Line 3 is `---`
and a tab, so the frontmatter is lines 1 to 3. Line 6 is a later exact
`---`, which, after a blank line, is a thematic break (CommonMark 0.31.2
§4.1); a reader that still wanted an exact `---` would close the
frontmatter there instead and lose the paragraph on line 4. pandoc
3.1.11.1 (`-f markdown`) reads the same.
