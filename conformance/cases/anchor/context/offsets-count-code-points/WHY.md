# EDITED: offsets in code points, with a character outside the BMP

The span `4.2 𝜎` ends in U+1D70E, one code point, two UTF-16 code units
and four UTF-8 bytes. The span is five code points long, at offsets 29 to
34, and its suffix is the 32 code points after the `𝜎`.

SPEC.md §11.1:

> **Offsets are code points of `leaf.text`**, the NFC-normalised parsed
> content, never offsets into the file.
