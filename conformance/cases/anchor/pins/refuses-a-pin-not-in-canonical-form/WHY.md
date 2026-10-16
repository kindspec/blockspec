# REFUSED(record-inconsistent): a pin with no space after a colon

The first pin reads to the same values, written another way.

SPEC.md §11.9:

> **How pins are written** (0003, addendum, detail 2): a line of the
> referrer's frontmatter that is exactly `pins:`, directly followed by one
> line per pin, each `  - ` (two spaces, a hyphen and a space) followed by an
> object in §11.1's canonical form and string escaping:

SPEC.md §11.9:

> **Every transclusion in the
> referrer is `REFUSED(record-inconsistent)`** when the frontmatter has more
> than one line that begins with `pins:`, a line that begins with `pins:` and
> is not exactly `pins:`, a pin line not in the canonical form, pins out of
> order, one `path` twice, or such a `  - ` line after the pins have
> ended.
