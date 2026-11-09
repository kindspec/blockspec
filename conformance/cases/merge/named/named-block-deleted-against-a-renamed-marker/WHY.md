# A named block deleted on one side and its marker edited on the other

Ours deletes the marker and the paragraph it names; theirs renames the marker.
The deletion overlaps the renamed line, so stock git conflicts: the name is
not lost silently.

SPEC.md §4.4:

> **A file holding a git conflict-marker line is refused** (`conflict-marker`),
> as a line scan before any block parsing

`conformance/cases/README.md`, *The kind `merge`*:

> A conflicted merge leaves markers in the text, so its reading is the refusal
> `conflict-marker`.
