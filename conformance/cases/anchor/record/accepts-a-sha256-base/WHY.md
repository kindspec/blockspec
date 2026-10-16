# RESOLVED: a 64-digit base in a SHA-256 repository

The repository uses SHA-256 object ids, so `base` is 64 lower-case hex
digits.

SPEC.md §11.1:

> - `B` is a string holding `base` in lower-case hex: 40 digits in a SHA-1
>   repository, 64 in a SHA-256 one.
