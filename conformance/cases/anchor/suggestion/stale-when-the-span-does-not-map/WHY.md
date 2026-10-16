# stale, `unmappable-offset`: the span ends inside a reordered character

The file writes `ẹ́` as `e`, U+0301, U+0323, which is not canonical order.
Its NFC form is U+1EB9 (`ẹ`) then U+0301, so `leaf.text` begins
`The ẹ` followed by the acute, and the span is `The ẹ`. No raw position
`b` gives a piece of content whose NFC form is `The ẹ`: the content up to
the `e` normalises to `The e`, up to U+0301 to `The é`, and up to U+0323
to `The ẹ́`. The anchor resolves and the suggestion is open, so it is
stale with the reason `unmappable-offset`.

SPEC.md §11.7:

> 1. Let `a` and `b` be the positions in the leaf's content, before NFC, such
>    that the NFC form of the content before `a` is `leaf.text` before the
>    span, and the NFC form of the content from `a` to `b` is `span`. If there
>    are no such positions, the span does not map.

SPEC.md §11.7:

> Where the span does not map, the suggestion is stale, with the reason
> `unmappable-offset`.
