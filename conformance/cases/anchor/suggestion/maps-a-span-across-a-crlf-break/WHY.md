# apply: a span that crosses a CRLF line break

The paragraph breaks after `threshold is`, with CRLF. The span
`threshold is\n4.2` crosses the break: its `\n` comes from the CRLF, so the
raw range holds both characters, and the replacement joins the two lines.

SPEC.md §11.7:

> **Write-back** (0003 Q11). Through the parse, each code point of the leaf's
> content comes from one raw character of its lines. Container prefixes (`>`
> markers and list-item indentation), the indentation a paragraph line loses,
> and line endings, carriage returns included, are raw characters no content
> code point comes from; a `\n` in the content stands for the line ending,
> whichever it is. In a file whose lines end in a bare CR, that `\n` comes
> from the CR.

SPEC.md §11.7:

> Only the span's own text must match after NFC; the rest of the leaf may be
> in any normalisation form and may span several prefixed or CRLF lines.
