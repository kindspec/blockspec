# apply: a span in the middle of a tab-indented continuation line

The span lies inside the tab-indented second line, well after the tab.
The code points before it map through the parse past the tab, which no
content code point comes from, so only the span's raw range changes.

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
