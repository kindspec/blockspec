# REFUSED(span-ambiguous): the span and its contexts occur twice

The span `rolling 30-second window` has full 32-code-point contexts. The
paragraph gained a sentence that repeats the span with both contexts, so
the paired leaf holds two hits.

SPEC.md §11.5:

> For `EDITED`, the span is searched **inside the paired leaf only**. A hit is
> an occurrence of `span` with `prefix` ending where it starts and `suffix`
> starting where it ends. [...] With no hit the anchor is
> `DETACHED`; with more than one, `REFUSED(span-ambiguous)`.
