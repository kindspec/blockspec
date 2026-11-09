# A list item deleted on one side and edited on the other

A list is one block (§6.1), but git merges by lines, so the deletion of the item
line conflicts with an edit of the same line.

SPEC.md §4.4:

> **A file holding a git conflict-marker line is refused** (`conflict-marker`),
> as a line scan before any block parsing

`conformance/cases/README.md`, *The kind `merge`*:

> A conflicted merge leaves markers in the text, so its reading is the refusal
> `conflict-marker`.
