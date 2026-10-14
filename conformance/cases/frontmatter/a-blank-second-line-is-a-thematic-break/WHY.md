The owner's decision of 2026-10-14 (0002, addendum): a leading YAML block,
opened by `---` on line 1 and closed by `---`, is opaque metadata. It is not
a block, has no leaves and takes no names. `frontmatter` is its line range. The decision of 2026-10-14, as pandoc reads YAML metadata: frontmatter
also needs a non-blank line 2. Here line 2 is blank, so line 1 is a thematic
break, and the later `---`, which follows a blank line, is another. A document
that opens with a thematic break does not become frontmatter because a `---`
line appears further down.
