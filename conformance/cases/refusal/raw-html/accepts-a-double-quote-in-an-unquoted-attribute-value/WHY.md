# refusal/raw-html/accepts-a-double-quote-in-an-unquoted-attribute-value

`input.md` is `<a b=x"y>`, then a line feed: the twin of the three
`refuses-an-unquoted-attribute-value-*` cases with `"` as the byte under test.

Accepted: one paragraph, content `<a b=x"y>`. An unquoted attribute value
excludes `"`, so the value is `x`, after which an open tag needs spaces or
tabs before another attribute, an optional `/`, or `>`; `"` is none of them.
The line is no complete open tag, meets no HTML block start condition, and
is a paragraph. Its inline content is opaque (SPEC.md §4.2), and `raw-html`
is block-level (SPEC.md §12, reading 6).

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

Files read (sha256, as computed before writing):
- SPEC.md 9635b4a43bff3d7d16497e8cbfae7863d65597ac9941aa9769a634fa14537a09
- cases-README.md ccc2999df3d77cfaea2a1340475cd38fc1261bd8d63262d20dc6a1018c284289
- case-body.schema.json 9512b41c957f0acae91c2ae84e7b1948e574bc06ea600e039991605152b3dcc8
- CASE-TREE.md ae9ef062966f380ebdbcdf3223d2d1d8f9ca5e294bc199166ce3c755493e7a8d
- CommonMark 0.31.2 spec.txt, from `npm pack commonmark-spec@0.31.2`
