# EDITED for the comment, DETACHED for the suggestion: an edit beside a comment on prose

SPEC.md §11.12's own example. A comment and a suggestion on `4.2` in
"Unit A: trip at 4.2 sigma.", which became "Unit B: trip at 4.2 sigma.".
The paragraph pairs as `EDITED`. The short prefix, `Unit A: trip at `, no
longer holds; the short suffix, ` sigma.`, does, and the span still has a
space on each side. A comment needs one side: `EDITED`, on the same `4.2`,
though it now belongs to unit B. A suggestion needs both sides:
`DETACHED`, and stale.

**This outcome is a documented residual, not a defect.** §11.12 names an
edit beside a comment on prose, which 0004 accepts, so the case pins the
resolution the rules give for the comment, which may be wrong for the
history described here, and right where the edit beside it did not
change what the span means.

SPEC.md §11.12:

> **An edit beside a comment** is not in the table, and 0004 accepts it.
> Where a leaf and its pair are both `p` or headings, a comment follows its
> span through a change on one side of it while its neighbouring code points
> and the other side of its context hold: a comment on `4.2` in "Unit A: trip
> at 4.2 sigma" becoming "Unit B: trip at 4.2 sigma", or on `restart` in
> "should restart every replica" becoming "should not restart every
> replica". It lands on the same span, not on a copy of it as in R3,
> and it is `EDITED`, shown as changed (§11.6), but the text around it may
> now mean something else. A suggestion is not affected: it needs both
> sides.

0004, *What it gives up*:

> - **On prose, a comment follows its span through an edit beside it** while
>   one side of its context and its neighbours hold: a comment on `4.2` in
>   "Unit A: trip at 4.2 sigma" becoming "Unit B: trip at 4.2 sigma", or on
>   `restart` in "should restart every replica" becoming "should not restart
>   every replica". The comment lands
>   `EDITED`, shown as changed (SPEC.md §11.6), but the words around it may
>   now mean something else; SPEC.md §11.12 names it. This was 0003 Q13's
>   cost, kept on purpose, and is now traded the other way for comments on
>   prose only.
