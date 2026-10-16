# RESOLVED: U+0080 written `\u0080`

The anchored paragraph holds U+0080, a C1 control, and the anchor writes
it as `\u0080`, the canonical form.

SPEC.md §11.1:

> - **Strings.** Each `S`, and the `reply-to` id, is `"`, its code points, then
>   `"`. `"` is written `\"`, `\` is written `\\`, and a line feed is written
>   `\n`. Every other code point in U+0000 to U+001F, in U+007F to U+009F, and
>   U+2028, U+2029, U+FEFF, U+FFFE and U+FFFF is written `\u` followed by four
>   lower-case hex digits. Every other code point is written as itself, in
>   UTF-8. No other escape is used.
> - **Spacing.** One space after each `:` and after each `,` between members,
>   and none anywhere else.
