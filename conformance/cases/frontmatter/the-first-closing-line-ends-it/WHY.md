The owner's decision of 2026-10-14 (0002, addendum): a leading YAML block,
opened by `---` on line 1 and closed by `---`, is opaque metadata. It is not
a block, has no leaves and takes no names. `frontmatter` is its line range. READING: frontmatter ends at the first later line that is exactly `---`,
whatever lies between. So a document whose first line is a thematic break
and which has another `---` line later opens with frontmatter. Without the
owner's rule this would be a thematic break, a paragraph, a thematic break
and a paragraph.
