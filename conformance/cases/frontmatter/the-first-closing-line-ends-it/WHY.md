The owner's decision of 2026-10-14 (0002, addendum): a leading YAML block,
opened by `---` on line 1 and closed by `---`, is opaque metadata. It is not
a block, has no leaves and takes no names. `frontmatter` is its line range. Line 2 must not be blank (see
frontmatter/a-blank-second-line-is-a-thematic-break). READING: once opened,
frontmatter ends at the first later line that is exactly `---`, whatever lies
between, blank lines and markdown-looking text included.
