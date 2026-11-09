# Stale on a table, `RESOLVED`

The table is unchanged and the record is open, so only the leaf's type makes
it stale. `anchor/suggestion/applies-on-resolved` is the same gate on a
paragraph.

docs/adjudications/0005-closing-draft-0s-gaps.md, item 7:

> On a table, a suggestion is stale with the reason `unmappable-offset`.
> A `\n` in `replace` breaks the line where the span starts, and the
> result is not re-checked against the profile when it is written.
