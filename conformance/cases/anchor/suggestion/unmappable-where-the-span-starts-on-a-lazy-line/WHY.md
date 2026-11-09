# A line break where the span starts, on a lazy line

The span starts on the lazy line and ends on a line with a prefix. The line
it breaks is the lazy one, so it cannot be written back.

docs/adjudications/0005-closing-draft-0s-gaps.md, item 7:

> On a table, a suggestion is stale with the reason `unmappable-offset`.
> A `\n` in `replace` breaks the line where the span starts, and the
> result is not re-checked against the profile when it is written.

SPEC.md, §11.7:

> A `\n` in `replace` makes the suggestion stale, as
> `unmappable-offset`, when the line it breaks is a list item's first
> line, whose container prefix is the list marker; a lazy line, which
> has no container prefix;
