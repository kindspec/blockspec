# RESOLVED: the file re-saved with CRLF line endings

`base` has LF line endings and the current file CRLF. Leaf text uses `\n`
whatever the file uses, so every key is unchanged. 0003 §8: the file
re-saved with other line endings, as if unchanged.

0003 §3:

> Two saves of
> the same paragraph, one in NFC and one in NFD, or one with LF and one with
> CRLF, give the same leaf.

SPEC.md §3:

> **Leaf content uses `\n` as its line ending everywhere**
