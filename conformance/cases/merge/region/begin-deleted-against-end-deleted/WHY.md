# One branch deletes `:begin` and the other deletes `:end`

Each branch alone is refused as `unpaired-region` (0002 §3, Reading 3). Git
sees one deleted line on each side, with `Scoped text.` unchanged between them,
and merges cleanly. The merged document has neither marker, so it is accepted
with no name at all: the two half-removals combine into a complete removal.
Neither author's version would have been accepted, and the name is silently
gone; a reference to it would be `#REF!(r)`.

This is one of the silently wrong merges reported with this set.

SPEC.md §7.3:

> Both markers must be siblings in one container, or the pair is
> refused as `unpaired-region` (0002 §3).

SPEC.md §12, Reading 3 (`README.md`, *Readings*, 3):

> Whether a `:begin` with no `:end` anywhere, or an `:end`
> with no `:begin`, is `unpaired-region`. The suite says it is.
