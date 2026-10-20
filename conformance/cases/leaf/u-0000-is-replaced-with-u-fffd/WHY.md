SPEC.md §3: "**U+0000 is replaced with U+FFFD**, as the pinned grammar
requires (CommonMark 0.31.2 §2.3, "Insecure characters")." CommonMark
0.31.2's `spec.txt` (tag `0.31.2`), *Insecure characters*: "For security
reasons, the Unicode character `U+0000` must be replaced with the
REPLACEMENT CHARACTER (`U+FFFD`)."

`input.md` holds a U+0000 in a heading, a paragraph and a fenced code
block. Each leaf's content holds U+FFFD where the file holds U+0000, and
the block structure is the one the file has with U+FFFD in its place.

Provenance: written by the author of the reader change it covers
(kindspec/blockspec#42), knowing that code, and so not an independent
case. The expected outcome comes from the passages above, and
markdown-it-py 3.0.0 (`commonmark` preset) renders `A�B`, `a�b` and
`c�d` from this input. pandoc 3.1.11.1 (`-f commonmark`, `-f gfm`) keeps
U+0000 in the heading and the paragraph, against the spec.
