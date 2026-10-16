# REFUSED(record-inconsistent): an anchor that is a JSON array

The `anchor:` line holds `[1]`, valid JSON but not an object, let alone
the canonical one.

SPEC.md §11.1:

> The anchor is a JSON object (RFC 8259), which is also a YAML 1.2 flow
> mapping, written in one canonical form:

SPEC.md §11.1:

> It is also `REFUSED(record-inconsistent)` (0003,
> addendum, detail 1) when it has no frontmatter; when the frontmatter's lines
> are not exactly those above, in that order, with nothing added; when the
> anchor or the `reply-to` id is not in the canonical form, including a value
> that is valid JSON or YAML and reads to the same values written another way
> (other spacing, key order or escapes, a duplicate key, an unquoted key);
> when `B` or `T` is not a value the list above allows; or when `replace` is
> present on a comment or missing on a suggestion.
