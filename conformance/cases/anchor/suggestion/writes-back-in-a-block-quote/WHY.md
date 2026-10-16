# apply: a line break in `replace`, inside a block quote

The quoted paragraph's second line is `> measured over a rolling ...`. The
span is on that line, and `replace` breaks it, so the new line starts with
the prefix the parse gives the line it continues, `> `.

SPEC.md §11.7:

> 3. Replace the range with `replace`, written exactly as stored and never
>    normalised, except at its line breaks. Each `\n` in `replace` is written
>    as the line ending of the line it breaks (CRLF in a CRLF file, CR in a
>    bare-CR file), and each new line is preceded by the container prefixes
>    the parse gives the line it continues. Nothing outside the range
>    changes.
