# REFUSED(record-inconsistent): `policy.md` pinned twice

The same pin line appears twice.

SPEC.md §11.9:

> - The pins end at the first frontmatter line that does not begin with
>   `  - `. They are sorted by `path`, ascending, code point by code point, and
>   no `path` appears twice.
> - A line that begins with `  - ` after the pins have ended is refused when
>   every line between them is blank or begins with a space or `#`: a YAML
>   reader would read it as one more pin, across a blank or comment line.

SPEC.md §11.9:

> **Every transclusion in the
> referrer is `REFUSED(record-inconsistent)`** when the frontmatter has more
> than one line that begins with `pins:`, a line that begins with `pins:` and
> is not exactly `pins:`, a pin line not in the canonical form, pins out of
> order, one `path` twice, or such a `  - ` line after the pins have
> ended.
