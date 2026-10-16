# RESOLVED: two branches re-pin different targets

`guide.md` pins `a.md`, `b.md` and `c.md`, one line each. One branch
re-pins `a.md` and the other `c.md`. The `b.md` line between them is
unchanged, so stock git merges the referrer cleanly, and all three
transclusions resolve: `b.md`'s older pin still resolves, since only a
paragraph outside its name changed.

SPEC.md §11.9:

> Two branches that add or re-pin different targets merge cleanly when an
> unchanged line lies between their changes, and conflict when the changes
> touch (0003, addendum, detail 2).
