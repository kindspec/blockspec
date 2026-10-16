# apply: the last line with no ending, and no line break in `replace`

The control for
`suggestion/unmappable-line-break-on-a-last-line-with-no-ending`: the same
span, with a `replace` that holds no `\n`.

SPEC.md §11.7:

> **A line break that cannot be written back** (0003, second addendum of
> 2026-10-16, item 4). A `\n` in `replace` makes the suggestion stale, as
> `unmappable-offset`, when the line it breaks is a list item's first line,
> whose container prefix is the list marker; a lazy line, which has no
> container prefix; a line whose container prefix holds a tab; or the file's
> last line, when the file has no final line ending.
