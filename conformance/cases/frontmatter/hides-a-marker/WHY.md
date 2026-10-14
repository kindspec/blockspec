The owner's decision of 2026-10-14 (0002, addendum): a leading YAML block,
opened by `---` on line 1 and closed by `---`, is opaque metadata. It is not
a block, has no leaves and takes no names. `frontmatter` is its line range. READING: frontmatter is opaque to the block rules, so a marker line
inside it declares no name: `names` is empty and nothing dangles.
READING: frontmatter content is not checked as YAML. Opaque means
unparsed, so text that is not valid YAML is still frontmatter.
