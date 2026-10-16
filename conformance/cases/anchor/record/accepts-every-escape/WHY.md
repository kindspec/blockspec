# RESOLVED: a canonical anchor that uses every kind of escape

The anchored paragraph holds `"`, `\`, a tab, a line break, U+2028,
U+007F and `é`. The anchor writes them as `\"`, `\\`, `\u0009`, `\n`,
`\u2028`, `\u007f` and `é` itself, which is the canonical form, so the
record is consistent and resolves.

SPEC.md §11.1:

> - **Strings.** Each `S`, and the `reply-to` id, is `"`, its code points, then
>   `"`. `"` is written `\"`, `\` is written `\\`, and a line feed is written
>   `\n`. Every other code point in U+0000 to U+001F, in U+007F to U+009F, and
>   U+2028, U+2029, U+FEFF, U+FFFE and U+FFFF is written `\u` followed by four
>   lower-case hex digits. Every other code point is written as itself, in
>   UTF-8. No other escape is used.
> - **Spacing.** One space after each `:` and after each `,` between members,
>   and none anywhere else.

SPEC.md §11.6:

> | `RESOLVED` | `EXACT`, and the span found | the anchor |
