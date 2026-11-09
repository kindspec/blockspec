# A paragraph deleted on one side and edited on the other

Ours deletes the paragraph, theirs edits it. Stock git conflicts, and the
conflict's text is refused for its markers. Neither branch's edit is lost
silently.

SPEC.md §4.4:

> **A file holding a git conflict-marker line is refused** (`conflict-marker`),
> as a line scan before any block parsing

`conformance/cases/README.md`, *The kind `merge`*:

> A conflicted merge leaves markers in the text, so its reading is the refusal
> `conflict-marker`.
