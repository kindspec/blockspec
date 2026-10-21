# refusal/raw-html/refuses-an-unquoted-attribute-value-of-plain-letters

`input.md` is `<a b=x`, `z`, `y>`, then a line feed.

Refused: `raw-html`. `z` is none of the characters an unquoted attribute
value excludes, so `x`, `z`, `y` is an unquoted attribute value, the line
is a complete open tag alone on its line, and it starts an HTML block of
type 7, which is not a region marker.

CommonMark 0.31.2, *Raw HTML*:

> An [unquoted attribute value](@)
> is a nonempty string of characters not
> including spaces, tabs, line endings, `"`, `'`, `=`, `<`, `>`, or `` ` ``.

> An [open tag](@) consists of a `<` character, a [tag name],
> zero or more [attributes], optional spaces, tabs, and up to one line ending,
> an optional `/` character, and a `>` character.

CommonMark 0.31.2, *HTML blocks*, start condition 7:

> line begins with a complete [open tag]
> (with any [tag name] other than `pre`, `script`,
> `style`, or `textarea`) or a complete [closing tag],
> followed by zero or more spaces and tabs, followed by the end of the line.

`a` is none of type 6's tag names, and the line does not start with `<!`,
`<?` or `<pre`/`<script`/`<style`/`<textarea`.

SPEC.md §9, item 4: "`raw-html`: an HTML block that is not a region marker".

Control: `refusal/raw-html/accepts-a-double-quote-in-an-unquoted-attribute-value`, the same line with `"` in place of `z`. The
`refuses-*` cases for U+0001, U+001F and plain letters differ only in that
byte, and are refused alike.

Files read (sha256, as computed before writing):
- SPEC.md 9635b4a43bff3d7d16497e8cbfae7863d65597ac9941aa9769a634fa14537a09
- cases-README.md ccc2999df3d77cfaea2a1340475cd38fc1261bd8d63262d20dc6a1018c284289
- case-body.schema.json 9512b41c957f0acae91c2ae84e7b1948e574bc06ea600e039991605152b3dcc8
- CASE-TREE.md ae9ef062966f380ebdbcdf3223d2d1d8f9ca5e294bc199166ce3c755493e7a8d
- CommonMark 0.31.2 spec.txt, from `npm pack commonmark-spec@0.31.2`
