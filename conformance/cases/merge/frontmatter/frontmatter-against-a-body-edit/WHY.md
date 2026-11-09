# One branch edits the frontmatter, the other the body

Frontmatter lines and body lines are lines to git, and the unchanged lines
between keep them apart. The frontmatter still ends at the first closing line,
and is not a block.

SPEC.md §5:

> **Frontmatter is allowed** (0002, addendum on frontmatter). A leading YAML
> block is opaque metadata. It is not a block, has no leaves and takes no
> names. Its lines are in no block.
