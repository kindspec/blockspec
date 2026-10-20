# apply: suggestions in leaves whose file holds U+0000

`tree/policy.md` holds a U+0000 at the end of its heading and at the end
of its second paragraph. The reader gives U+FFFD for each (SPEC.md §3), so
each leaf's text, and each record's stored `leaf.text`, holds U+FFFD
there. One suggestion replaces `4.2 sigma` in the paragraph, and the other
replaces `limits` in the heading. Each anchor resolves and is `open`, so
each applies, and its written file is the current file with only the
span's raw range replaced: the U+0000 outside the span is kept as it is in
the file.

SPEC.md §3:

> **U+0000 is replaced with U+FFFD**, as the pinned grammar requires
> (CommonMark 0.31.2 §2.3, "Insecure characters").

SPEC.md §11.7:

> **Write-back** (0003 Q11). Through the parse, each code point of the leaf's
> content comes from one raw character of its lines.

The U+FFFD in the content comes from the one raw U+0000, so the content
maps to the raw text code point for code point, and the span maps.

SPEC.md §11.7:

> 3. Replace the range with `replace`, written exactly as stored and never
>    normalised, except at its line breaks. Each `\n` in `replace` is written
>    as the line ending of the line it breaks (CRLF in a CRLF file, CR in a
>    bare-CR file), and each new line is preceded by the container prefixes
>    the parse gives the line it continues. Nothing outside the range
>    changes.

Provenance: written by the author of the resolver change it covers
(kindspec/blockspec#42), knowing that code, and so not an independent
case.
