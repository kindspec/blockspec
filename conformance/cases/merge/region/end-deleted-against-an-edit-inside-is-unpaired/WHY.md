# A region's `:end` deleted on one side, and its content edited on the other

Ours deletes the `:end` marker. Theirs edits a paragraph inside the region.
The merge is clean and the merged text keeps a `:begin` with no `:end`:
`unpaired-region`, Reading 3.

**READING** 3 (`README.md`, *Readings*): `:begin` with no `:end`, which SPEC.md §12
lists as open:

> Whether a `:begin` with no `:end` anywhere, or an `:end`
> with no `:begin`, is `unpaired-region`. The suite says it is.
