# apply: neither the leaf nor `replace` is normalised

The file writes `café` in NFD, before the span. The content before the
span maps to `leaf.text` before it once normalised, so the span maps.
`replace` holds `naïve` in NFD (`i` and U+0308), and is written exactly as
stored; `café` stays in NFD.

SPEC.md §11.7:

> 1. Let `a` and `b` be the positions in the leaf's content, before NFC, such
>    that the NFC form of the content before `a` is `leaf.text` before the
>    span, and the NFC form of the content from `a` to `b` is `span`. If there
>    are no such positions, the span does not map.

SPEC.md §11.7:

> 3. Replace the range with `replace`, written exactly as stored and never
>    normalised, except at its line breaks. Each `\n` in `replace` is written
>    as the line ending of the line it breaks (CRLF in a CRLF file, CR in a
>    bare-CR file), and each new line is preceded by the container prefixes
>    the parse gives the line it continues. Nothing outside the range
>    changes.
