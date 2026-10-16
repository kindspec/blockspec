# RESOLVED: the file re-saved in NFD

`base` writes `café` in NFC and the current file in NFD (`e` and U+0301).
Leaf text is normalised to NFC, so the keys are equal and the offsets, in
NFC code points, do not move. 0003 §8: the file re-saved in another
normalisation form, as if unchanged.

0003 §3:

> Two saves of
> the same paragraph, one in NFC and one in NFD, or one with LF and one with
> CRLF, give the same leaf.

SPEC.md §11.1:

> **Offsets are code points of `leaf.text`**, the NFC-normalised parsed
> content, never offsets into the file.
