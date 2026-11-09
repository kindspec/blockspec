# Stale on a table, `EDITED`

One cell changes, past the suffix's 32 code points, so the anchor is
`EDITED` with both sides exact. `anchor/suggestion/applies-on-edited` is the
same gate on a paragraph.

docs/adjudications/0005-closing-draft-0s-gaps.md, item 7:

> On a table, a suggestion is stale with the reason `unmappable-offset`.
> A `\n` in `replace` breaks the line where the span starts, and the
> result is not re-checked against the profile when it is written.
