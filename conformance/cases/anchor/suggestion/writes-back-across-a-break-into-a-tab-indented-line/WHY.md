# apply: a span that crosses into a tab-indented continuation line

The span `baseline,\nmeasured` runs from the item's first line across the
break into its tab-indented second line. Its raw range runs from `b` to
`d` and so holds the line ending and the tab between them, and the
replacement, which has no line break, joins the two lines.

SPEC.md §11.7:

> **Write-back** (0003 Q11). Through the parse, each code point of the leaf's
> content comes from one raw character of its lines. Container prefixes (`>`
> markers and list-item indentation), the indentation a paragraph line loses,
> and line endings, carriage returns included, are raw characters no content
> code point comes from; a `\n` in the content stands for the line ending,
> whichever it is. In a file whose lines end in a bare CR, that `\n` comes
> from the CR.

SPEC.md §11.7:

> 2. Map `a` and `b` through the parse to raw positions, skipping the
>    characters above. The raw text between them is the span's raw range.
