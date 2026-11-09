# One branch edits an item while the other splits it

Ours edits the item's text, theirs splits it into two items. Both change the
same line, so stock git conflicts.

SPEC.md §4.4:

> **A file holding a git conflict-marker line is refused** (`conflict-marker`),
> as a line scan before any block parsing

`conformance/cases/README.md`, *The kind `merge`*:

> A conflicted merge leaves markers in the text, so its reading is the refusal
> `conflict-marker`.
