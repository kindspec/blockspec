# No transclusion: link text that holds a link

Link text cannot contain another link. CommonMark 0.31.2's example 518
reads `[foo [bar](/uri)](/uri)` as `[foo `, a link `bar`, and `](/uri)`.
Here, likewise, the inner `[b](c.md)` is a link, and the outer brackets are literal
text. The paragraph is text around one untitled link, and holds no link
titled `transclude`, so the referrer has no transclusion.

SPEC.md §11.9:

> **A transclusion is a paragraph whose content is exactly one inline link
> with the title `transclude`** (0003 Q5)

CommonMark 0.31.2, *Links*, before example 518:

> However, links may not contain other links, at any level of nesting.
