# Both branches edit the same frontmatter key

The merge conflicts, and the markers land inside the frontmatter. The
frontmatter's opacity does not hide them: the conflict scan runs before anything
else (0001 §4).

**READING** 12 (SPEC.md §12):

> That frontmatter is opaque to the block rules but not to
> the conflict-marker scan, read, as reading 4 is, from 0001 §4's line scan
> before any block parsing.

SPEC.md §4.4:

> **A file holding a git conflict-marker line is refused** (`conflict-marker`),
> as a line scan before any block parsing

`conformance/cases/README.md`, *The kind `merge`*:

> A conflicted merge leaves markers in the text, so its reading is the refusal
> `conflict-marker`.
