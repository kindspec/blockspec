# apply: a span that starts right after a tab of list-item indentation

The second item's continuation line is indented by one tab. Two of its
columns are the item's content indentation, and the rest is indentation
the paragraph line loses, so no content code point comes from the tab.
The span starts at the line's first content code point, so its raw range
starts after the tab, and the tab is kept.

SPEC.md §11.7:

> **Write-back** (0003 Q11). Through the parse, each code point of the leaf's
> content comes from one raw character of its lines. Container prefixes (`>`
> markers and list-item indentation), the indentation a paragraph line loses,
> and line endings, carriage returns included, are raw characters no content
> code point comes from; a `\n` in the content stands for the line ending,
> whichever it is. In a file whose lines end in a bare CR, that `\n` comes
> from the CR.

SPEC.md §11.7:

> 3. Replace the range with `replace`, written exactly as stored and never
>    normalised, except at its line breaks. Each `\n` in `replace` is written
>    as the line ending of the line it breaks (CRLF in a CRLF file, CR in a
>    bare-CR file), and each new line is preceded by the container prefixes
>    the parse gives the line it continues. Nothing outside the range
>    changes.
