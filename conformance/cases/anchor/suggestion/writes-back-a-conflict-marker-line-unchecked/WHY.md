# The result would hold a conflict-marker line

Written as stored. The result would be refused as `conflict-marker` if it
were read again, and it is not read again.

docs/adjudications/0005-closing-draft-0s-gaps.md, item 7:

> On a table, a suggestion is stale with the reason `unmappable-offset`.
> A `\n` in `replace` breaks the line where the span starts, and the
> result is not re-checked against the profile when it is written.
