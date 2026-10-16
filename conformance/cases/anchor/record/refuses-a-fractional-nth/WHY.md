# REFUSED(record-inconsistent): `nth` written with a fraction

`"nth": 0.0` reads as zero, and is not decimal digits.

SPEC.md §11.1:

> - `N` is decimal digits, `0` or with no leading zero, and no sign, fraction
>   or exponent.

SPEC.md §11.1:

> It is also `REFUSED(record-inconsistent)` (0003,
> addendum, detail 1) when it has no frontmatter; when the frontmatter's lines
> are not exactly those above, in that order, with nothing added; when the
> anchor or the `reply-to` id is not in the canonical form, including a value
> that is valid JSON or YAML and reads to the same values written another way
> (other spacing, key order or escapes, a duplicate key, an unquoted key);
> when `B` or `T` is not a value the list above allows; or when `replace` is
> present on a comment or missing on a suggestion.
