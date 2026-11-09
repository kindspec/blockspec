# Edits to two different blocks conflict when no line separates them

A heading and the paragraph directly under it are two blocks, but their lines
touch, so stock git conflicts even though no block was edited twice. A
different block is not the unit git merges by; a line is. The case's control
edits two blocks with one blank line between them, and merges cleanly.

SPEC.md §4.4:

> **A file holding a git conflict-marker line is refused** (`conflict-marker`),
> as a line scan before any block parsing

`conformance/cases/README.md`, *The kind `merge`*:

> A conflicted merge leaves markers in the text, so its reading is the refusal
> `conflict-marker`.
