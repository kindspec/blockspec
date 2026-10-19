# REFUSED(span-ambiguous): the span and its contexts occur twice

The span `rolling 30-second window` has full 32-code-point contexts. The
paragraph gained a sentence that repeats the span with both contexts, so
the paired leaf holds two hits.

**Under 0004** a hit needs one side of its context, and each occurrence
here has both; both start after a space and end before one, as the span
does in `base`, so both are still hits. The outcome is unchanged.

SPEC.md §11.5:

> For `EDITED`, the span is searched **inside the paired leaf only**. A hit is
> an occurrence of `span` that meets both of these (0004, which replaces
> 0003 Q13's requirement of both sides):
> [...]
> 2. **One side of its context holds.** [...] A hit needs the prefix or the suffix
>    to hold.
>
> Hits are counted by start position, overlapping ones included (§11.1). With no hit the anchor is
> `DETACHED`; with more than one, `REFUSED(span-ambiguous)`.
