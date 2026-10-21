# refusal/link-reference-definition/accepts-an-unclosed-angle-destination-holding-a-u0000

`input.md` is `[a]: <x`, U+0000, `y`, then a line feed: the twin of
`refuses-an-angle-destination-holding-a-u0000` without its closing `>`.

Accepted: one paragraph, content `[a]: <x`, U+FFFD, `y` (§3). With no closing
`>` the angle form does not apply, and a bare destination "does not start
with `<`", so there is no link destination and no link reference definition.

SPEC.md §3:

> A link
> destination not in angle brackets does: it holds no ASCII control
> character (CommonMark §4.7, with §6.3's link destination), so it takes
> U+FFFD and not U+0000. With the replacement, the one line `[a]: x`,
> U+0000, `y` is refused as `link-reference-definition` [...]; without it, each
> would be a plain paragraph.

CommonMark 0.31.2, *Link reference definitions* and *Links*:

> A [link destination](@) consists of either
>
> - a sequence of zero or more characters between an opening `<` and a
>   closing `>` that contains no line endings or unescaped
>   `<` or `>` characters, or
>
> - a nonempty sequence of characters that does not start with `<`,
>   does not include [ASCII control characters][ASCII control character]
>   or [space] character, [...]

> An [ASCII control character](@) is a character between `U+0000–1F` (both
> including) or `U+007F`.

SPEC.md §4.1 refuses "a link reference definition (`link-reference-definition`)".

Files read (sha256, as computed before writing):
- SPEC.md 9635b4a43bff3d7d16497e8cbfae7863d65597ac9941aa9769a634fa14537a09
- cases-README.md ccc2999df3d77cfaea2a1340475cd38fc1261bd8d63262d20dc6a1018c284289
- case-body.schema.json 9512b41c957f0acae91c2ae84e7b1948e574bc06ea600e039991605152b3dcc8
- CASE-TREE.md ae9ef062966f380ebdbcdf3223d2d1d8f9ca5e294bc199166ce3c755493e7a8d
- CommonMark 0.31.2 spec.txt, from `npm pack commonmark-spec@0.31.2`
