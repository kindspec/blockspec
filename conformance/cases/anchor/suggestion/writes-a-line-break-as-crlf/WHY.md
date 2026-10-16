# apply: a line break in `replace`, in a CRLF file

`replace` holds a `\n`. The paragraph is at top level, so the new line has
no container prefix, and the break is written as the line's own ending,
CRLF.

SPEC.md §11.7:

> 3. Replace the range with `replace`, written exactly as stored and never
>    normalised, except at its line breaks. Each `\n` in `replace` is written
>    as the line ending of the line it breaks (CRLF in a CRLF file, CR in a
>    bare-CR file), and each new line is preceded by the container prefixes
>    the parse gives the line it continues. Nothing outside the range
>    changes.
