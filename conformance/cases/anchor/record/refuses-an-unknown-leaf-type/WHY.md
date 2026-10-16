# REFUSED(record-inconsistent): a `leaf.type` the list does not allow

`paragraph` is the tree's name for the node, not an allowed `T`.

This case cannot isolate the `T` check. No leaf of `base` has the key
`paragraph` and this text, so the rule that refuses a record whose `leaf`
at `nth` is not in `base` gives the same outcome. An implementation that
skipped the `T` check would still pass it.

SPEC.md §11.1:

> - `T` is a string, one of `p`, `h1` to `h6`, `code` and `table`.

SPEC.md §11.1:

> It is also `REFUSED(record-inconsistent)` (0003,
> addendum, detail 1) when it has no frontmatter; when the frontmatter's lines
> are not exactly those above, in that order, with nothing added; when the
> anchor or the `reply-to` id is not in the canonical form, including a value
> that is valid JSON or YAML and reads to the same values written another way
> (other spacing, key order or escapes, a duplicate key, an unquoted key);
> when `B` or `T` is not a value the list above allows; or when `replace` is
> present on a comment or missing on a suggestion.

SPEC.md §11.1:

> **Consistency.** A record is `REFUSED(record-inconsistent)` when `leaf` at
> `nth` is not in `base`; when `prefix + span + suffix` does not occur exactly
> once in `leaf.text`; when `prefix` or `suffix` is shorter than 32 code points
> while the leaf's edge is further away; or when `span` is empty (0003, the
> details it fixes).
