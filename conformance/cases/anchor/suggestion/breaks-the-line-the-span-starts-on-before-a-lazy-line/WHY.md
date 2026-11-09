# A line break where the span starts, before a lazy line

The span starts on a line with the `> ` prefix and ends on a lazy line. The
`\n` breaks the line where the span starts, so the new line gets that line's
prefix. Reading it as the line where the span ends would make this stale.

docs/adjudications/0005-closing-draft-0s-gaps.md, item 7:

> On a table, a suggestion is stale with the reason `unmappable-offset`.
> A `\n` in `replace` breaks the line where the span starts, and the
> result is not re-checked against the profile when it is written.

SPEC.md, §11.7:

> Each `\n` in `replace` is written as the line ending of the line it
> breaks (CRLF in a CRLF file, CR in a bare-CR file), and each new line
> is preceded by the container prefixes the parse gives the line it
> continues.
