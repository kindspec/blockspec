# REFUSED(record-inconsistent): a record whose body is raw HTML

The anchor and the frontmatter are canonical, and the body is an HTML
block the profile refuses (`raw-html`). A record is a blockspec document,
so its body must pass the profile.

SPEC.md §11.1:

> And it is
> `REFUSED(record-inconsistent)` (0003, second addendum of 2026-10-16) when
> `prefix` or `suffix` is longer than 32 code points (item 1); when its
> `reply-to` string is not a ULID in the form above (item 5); or when the
> profile refuses its body (item 8), since a record is a blockspec document.
