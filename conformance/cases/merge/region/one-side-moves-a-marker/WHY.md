# One branch moves a marker while the other edits a paragraph

Ours moves the marker to the last paragraph; theirs edits an unrelated
paragraph. The name now binds the paragraph ours moved it to. The merge is
clean and the name's move is ours's own change.

SPEC.md §7.2:

> **`<!-- #name -->` binds `name` to the next sibling node in its container**,
> at any depth (0001; 0002 §3).
