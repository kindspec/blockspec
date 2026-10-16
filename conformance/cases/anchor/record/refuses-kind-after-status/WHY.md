# REFUSED(record-inconsistent): the lines out of order

`status:` comes before `kind:`.

SPEC.md §11.1:

> The
> lines between the record's opening and closing `---` (§5) are exactly these,
> in this order, each with nothing before or after it:
>
> - a comment or a suggestion: `anchor: ` followed by the anchor, then
>   `kind: comment` or `kind: suggestion`, then `status: ` followed by one of
>   the four statuses;

SPEC.md §11.1:

> It is also `REFUSED(record-inconsistent)` (0003,
> addendum, detail 1) when it has no frontmatter; when the frontmatter's lines
> are not exactly those above, in that order, with nothing added; when the
> anchor or the `reply-to` id is not in the canonical form, including a value
> that is valid JSON or YAML and reads to the same values written another way
> (other spacing, key order or escapes, a duplicate key, an unquoted key);
> when `B` or `T` is not a value the list above allows; or when `replace` is
> present on a comment or missing on a suggestion.
