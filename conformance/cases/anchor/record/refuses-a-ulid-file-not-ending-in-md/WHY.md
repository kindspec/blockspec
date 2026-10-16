# REFUSED(record-inconsistent): The file name is a ULID followed by `.txt`, not `.md`

The file holds a consistent, canonical comment that would resolve. The file name is a ULID followed by `.txt`, not `.md`.
Everything in a notes directory is a record, so the file is refused.

SPEC.md §11.1:

> - **A record's file name is `<id>.md`**, where `<id>` is a ULID (D8 §7.4):
>   26 characters of Crockford's base 32 in upper case, `[0-9A-HJKMNP-TV-Z]`,
>   the first of them `0` to `7`. Ids are unique within a notes directory. An
>   id is never written into the document.
> - **Everything in a notes directory is a record.** A file whose name is not
>   `<id>.md` in that form, and a subfolder, are each
>   `REFUSED(record-inconsistent)` (0003, second addendum of 2026-10-16,
>   item 5).
