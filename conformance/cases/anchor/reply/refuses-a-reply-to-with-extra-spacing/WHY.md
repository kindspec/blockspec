# REFUSED(record-inconsistent): a `reply-to` line not in canonical form

The `reply-to` line names the parent's id, written with two spaces after the colon. The
line is not `reply-to: ` followed by the id as a canonical JSON string.

SPEC.md §11.1:

> - a reply: `reply-to: ` followed by the parent's id as a JSON string, then
>   `kind: comment`.

SPEC.md §11.1:

> - **Strings.** Each `S`, and the `reply-to` id, is `"`, its code points, then
>   `"`. `"` is written `\"`, `\` is written `\\`, and a line feed is written
>   `\n`. Every other code point in U+0000 to U+001F, in U+007F to U+009F, and
>   U+2028, U+2029, U+FEFF, U+FFFE and U+FFFF is written `\u` followed by four
>   lower-case hex digits. Every other code point is written as itself, in
>   UTF-8. No other escape is used.
> - **Spacing.** One space after each `:` and after each `,` between members,
>   and none anywhere else.

SPEC.md §11.1:

> It is also `REFUSED(record-inconsistent)` (0003,
> addendum, detail 1) when it has no frontmatter; when the frontmatter's lines
> are not exactly those above, in that order, with nothing added; when the
> anchor or the `reply-to` id is not in the canonical form, including a value
> that is valid JSON or YAML and reads to the same values written another way
> (other spacing, key order or escapes, a duplicate key, an unquoted key);
> when `B` or `T` is not a value the list above allows; or when `replace` is
> present on a comment or missing on a suggestion.
