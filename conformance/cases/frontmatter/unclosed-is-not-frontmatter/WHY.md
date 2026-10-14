The owner's decision of 2026-10-14 (0002, addendum): a leading YAML block,
opened by `---` on line 1 and closed by `---`, is opaque metadata. It is not
a block, has no leaves and takes no names. `frontmatter` is its line range. READING: with no closing `---` there is no frontmatter, and the lines
parse under the existing rules: a thematic break, then paragraphs. The
document is not refused for it. `frontmatter` is absent, which means none.
