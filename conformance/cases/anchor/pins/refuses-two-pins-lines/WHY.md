# REFUSED(record-inconsistent): two `pins:` lines

Each target is pinned once, under a `pins:` line of its own.

SPEC.md §11.9:

> **Every transclusion in the
> referrer is `REFUSED(record-inconsistent)`** when the frontmatter has more
> than one line that begins with `pins:`, a line that begins with `pins:` and
> is not exactly `pins:`, a pin line not in the canonical form, pins out of
> order, one `path` twice, or such a `  - ` line after the pins have
> ended.
