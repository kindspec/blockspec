# An edit before the context

The opening of the paragraph is rewritten further than 32 code points before
the span, so both sides of the context hold and the anchor is `EDITED`. The
text before the span is not the stored text. Reading it from the record
finds no position and makes the suggestion stale.
`anchor/suggestion/stale-with-one-side-of-its-context` is the other side: an
edit inside the context.

docs/adjudications/0005-closing-draft-0s-gaps.md, item 9:

> The content before the span is read from the leaf the anchor is paired
> with in the current document, not from the record's stored base text.
