# Each branch edits a different frontmatter key

The title and status lines change on different branches, and the owner line
between them does not. Stock git merges them.

SPEC.md §5:

> **Frontmatter is allowed** (0002, addendum on frontmatter). A leading YAML
> block is opaque metadata. It is not a block, has no leaves and takes no
> names. Its lines are in no block.
