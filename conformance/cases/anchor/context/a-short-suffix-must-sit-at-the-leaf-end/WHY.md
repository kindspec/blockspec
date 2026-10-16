# DETACHED: a short suffix whose occurrence is not at the leaf's end

The span closes the paragraph, so its stored `suffix` is empty. The current
paragraph gained a sentence after it. The span still occurs with its full
prefix, but a short suffix must end at the end of the paired leaf's text,
and this one would end 15 code points before it. That occurrence is not a
hit. `context/a-short-suffix-may-end-at-the-leaf-end` is the control.

SPEC.md §11.5:

> **A short context must sit at the leaf's edge**
> (0003, addendum, detail 6): when `prefix` is shorter than 32 code points,
> the hit's `prefix` starts at the start of the paired leaf's text, and when
> `suffix` is shorter than 32, the hit's `suffix` ends at its end. An
> occurrence that does not is not a hit.
