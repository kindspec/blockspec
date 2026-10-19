# EDITED: a short suffix that still ends at the leaf's end

The span closes the paragraph, so its stored `suffix` is empty and its
prefix is the full 32 code points. The paragraph gained `In short: ` in
front, far from the span. The one occurrence has its empty suffix ending at
the paired leaf's end, so it is a hit, ten code points later than before.

SPEC.md §11.5:

> 2. **One side of its context holds.** Write each text with every run of
>    U+0009, U+000A, U+000D and U+0020 as one U+0020: the paired leaf's text
>    before the occurrence and after it, each taken on its own, and `prefix`
>    and `suffix`. The prefix holds when the text before the occurrence, so
>    written, ends with `prefix` so written; when `prefix` is shorter than
>    32 code points, counted as stored, it must be all of that text (0003,
>    addendum, detail 6: a short context sits at the leaf's edge). The suffix holds in the same way, after the
>    occurrence and at the leaf's end. A hit needs the prefix or the suffix
>    to hold.

SPEC.md §11.6:

> | `EDITED` | `EDITED`, and the span found | the anchor, marked changed |
