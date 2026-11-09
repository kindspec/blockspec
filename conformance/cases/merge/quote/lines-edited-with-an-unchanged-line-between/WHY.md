# Each branch edits a different line of a block quote

The quote's first and last lines change; the unchanged middle line keeps
them apart. The merged block quote has one paragraph whose content is the three
lines with their `>` prefixes removed.

0002 §1 is the partition rule this case relies on (SPEC.md §6.1):

> **A block is a top-level node.** A document is a sequence of blocks. A list
> is one block, and so are a block quote and a table.

SPEC.md §6.3:

> **A leaf's content is its parsed content, as CommonMark parses it, with
> container prefixes removed**
