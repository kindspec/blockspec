# A marker that names a block neither author's branch named

Ours deletes `One.` and theirs deletes `Two.`. On ours the name binds `Two.`,
on theirs it binds `One.`, and each deletion is one line with a blank line
between the two, so stock git merges cleanly. In the merged text the name binds
`Three.`, which neither branch named. The format reads it as §7.2 says; nothing
in the merged text shows that the binding moved. The reader of this document
has no way to tell.

This is one of the silently wrong merges reported with this set.

SPEC.md §7.2:

> **`<!-- #name -->` binds `name` to the next sibling node in its container**,
> at any depth (0001; 0002 §3).

Blank lines between the marker and its node do not matter (SPEC.md §7.2):

> A blank line between the marker and the node does not matter.
