# EDITED: a short suffix that still ends at the leaf's end

The span closes the paragraph, so its stored `suffix` is empty and its
prefix is the full 32 code points. The paragraph gained `In short: ` in
front, far from the span. The one occurrence has its empty suffix ending at
the paired leaf's end, so it is a hit, ten code points later than before.

SPEC.md §11.5:

> **A short context must sit at the leaf's edge**
> (0003, addendum, detail 6): when `prefix` is shorter than 32 code points,
> the hit's `prefix` starts at the start of the paired leaf's text, and when
> `suffix` is shorter than 32, the hit's `suffix` ends at its end. An
> occurrence that does not is not a hit.

SPEC.md §11.6:

> | `EDITED` | `EDITED`, and the span found | the anchor, marked changed |
