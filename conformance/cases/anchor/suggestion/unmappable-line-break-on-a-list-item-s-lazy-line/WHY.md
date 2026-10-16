# stale, `unmappable-offset`: a line break on a list item's lazy line

The second item's paragraph continues on a line with no indentation, a
lazy line with no container prefix. The span is on it.

SPEC.md §11.7:

> **A line break that cannot be written back** (0003, second addendum of
> 2026-10-16, item 4). A `\n` in `replace` makes the suggestion stale, as
> `unmappable-offset`, when the line it breaks is a list item's first line,
> whose container prefix is the list marker; a lazy line, which has no
> container prefix; a line whose container prefix holds a tab; or the file's
> last line, when the file has no final line ending.
