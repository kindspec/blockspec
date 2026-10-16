# REFUSED(record-inconsistent): `suffix` before `prefix`

The anchor holds the same members, with `suffix` written before `prefix`.

SPEC.md §11.1:

>     {"base": B, "leaf": {"type": T, "nth": N, "text": S}, "span": S, "prefix": S, "suffix": S}
>
> with `, "replace": S` before the final `}` for a suggestion, and never for a
> comment. The keys are in the order shown.

SPEC.md §11.1:

> It is also `REFUSED(record-inconsistent)` (0003,
> addendum, detail 1) when it has no frontmatter; when the frontmatter's lines
> are not exactly those above, in that order, with nothing added; when the
> anchor or the `reply-to` id is not in the canonical form, including a value
> that is valid JSON or YAML and reads to the same values written another way
> (other spacing, key order or escapes, a duplicate key, an unquoted key);
> when `B` or `T` is not a value the list above allows; or when `replace` is
> present on a comment or missing on a suggestion.
