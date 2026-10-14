The owner's decision of 2026-10-14 (0002, addendum): a leading YAML block,
opened by `---` on line 1 and closed by `---`, is opaque metadata. It is not
a block, has no leaves and takes no names. `frontmatter` is its line range. Opaque means not parsed as markdown, so raw HTML, an indented line and
a link-reference-definition shape inside it are not refused.
