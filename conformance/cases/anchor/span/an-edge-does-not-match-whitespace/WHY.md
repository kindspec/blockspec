# DETACHED: the span's neighbour was a space and is now the leaf's start

A comment on `restart every replica`, stored with the short prefix `Note: `
and the short suffix ` now.`. `Note: ` was deleted, so the paragraph pairs
as `EDITED` and the span now opens it. The suffix holds, at the leaf's
end, but the code point before the occurrence is the text's start, where
the span followed a space. A text's start compares equal only to a start,
so it is not a hit. `context/a-short-prefix-must-sit-at-the-leaf-start` is
the other direction: a span that opened its leaf, with text now before it.

SPEC.md §11.5:

> 1. **Its neighbours are unchanged.** The code point just before the
>    occurrence in the paired leaf's text compares equal to the code point
>    just before the span in `leaf.text`, and the code point just after it to
>    the one just after the span. U+0009, U+000A, U+000D and U+0020 compare
>    equal to one another; a text's start or end compares equal only to a
>    start or end; any other code point only to itself.
