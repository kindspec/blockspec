# A name deleted on one side and a reference to it edited on the other

Ours deletes the marker and the block it names. Theirs edits a paragraph
that links to the name. Stock git merges cleanly: nothing connects the two
lines. Inline content is opaque, so the link is characters of a paragraph
and the merged document is accepted. `limit` resolves to `#REF!(limit)`, but
the merged text carries no sign of it: the link renders, dead.

This is one of the silently wrong merges reported with this set.

SPEC.md §4.2:

> **Inline content is opaque text** (0001, *What
> draft 0 carries*)

SPEC.md §8.1:

> **A name that matches zero
> targets, or more than one, is `#REF!(name)`.**

**Changed by 0005:** this was accepted before adjudication 0005, which refuses it as `dangling-link`.
