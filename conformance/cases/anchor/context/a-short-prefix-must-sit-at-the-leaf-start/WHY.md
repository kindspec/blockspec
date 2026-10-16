# DETACHED: a short prefix whose occurrence is not at the leaf's start

The span opens the paragraph, so its stored `prefix` is empty. The current
paragraph gained `In short: ` in front. The span and its suffix still
occur, at code point 10, but a short prefix must start at the start of the
paired leaf's text, and this one would start at 10. That occurrence is not
a hit, so there is none.

SPEC.md §11.5:

> **A short context must sit at the leaf's edge**
> (0003, addendum, detail 6): when `prefix` is shorter than 32 code points,
> the hit's `prefix` starts at the start of the paired leaf's text, and when
> `suffix` is shorter than 32, the hit's `suffix` ends at its end. An
> occurrence that does not is not a hit.

0003, addendum, detail 6:

> Without the rule, a span at a leaf's start,
> stored with an empty `prefix`, could land on a later occurrence of it that
> the same `suffix` follows.
