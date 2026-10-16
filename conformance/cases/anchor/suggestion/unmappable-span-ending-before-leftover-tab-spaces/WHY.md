# stale, `unmappable-offset`: a span that ends right before leftover tab spaces

The same code block. The span `= 4.2\n` ends with the first line's `\n`,
right before the two spaces left from the second line's tab, so its end
maps into the tab, not to a raw position.

SPEC.md §11.7:

> **Two spans that cannot be written back** (0003, third addendum of
> 2026-10-16, items 3 and 4). The suggestion is stale, as `unmappable-offset`,
> when:
>
> - a code point of the span comes from no single raw character, or the
>   span ends right before one: the rest of a tab only partly consumed by
>   indentation, which CommonMark keeps as spaces in the content. That is
>   container indentation (item 3) or any other, such as a fenced code
>   block's own indentation (the addendum's precision, extending item 3). A
>   span that begins right after such a character maps; one that ends right
>   before it ends with a `\n`, and step 2 carries `b` into the tab (the
>   addendum's precision);
> - the span's last code point is the `\n` that ends a code block's last
>   content line. That `\n` marks where the block's content ends: writing
>   over it would join the closing fence to the line before it, and in a
>   fence left unclosed at the end of its container or the file it may come
>   from no raw character. That holds whatever `replace` ends with (the
>   addendum's precision).
