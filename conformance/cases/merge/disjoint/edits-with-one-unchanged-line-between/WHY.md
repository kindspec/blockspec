# Two branches edit different blocks, one blank line between the edits

Ours edits the named paragraph, theirs the next paragraph. Only the blank line
between them is unchanged, which is enough for stock git to merge cleanly. Every
block and the name survive, and the name stays on its paragraph, read as §7.2
reads it.

SPEC.md §7.2:

> **`<!-- #name -->` binds `name` to the next sibling node in its container**,
> at any depth (0001; 0002 §3).
