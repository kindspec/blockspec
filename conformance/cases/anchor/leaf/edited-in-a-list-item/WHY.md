# EDITED: a paragraph inside a list item

The anchored paragraph is the second item's, node `[1, 1, 0]`. Its key is
its parsed content, without the list marker, so the item's edit pairs it as
`EDITED` like a paragraph at top level.

SPEC.md §6.2:

> **Stage 1 of every anchor resolves a leaf**, with no fallback to the
> enclosing block

SPEC.md §11.1:

> | `leaf.text` | the leaf's content (§6.3), normalised to Unicode NFC, with `\n` line endings; for a table, the string §11.2 defines |
