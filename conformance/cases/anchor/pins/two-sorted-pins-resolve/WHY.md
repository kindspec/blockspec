# RESOLVED: two transclusions, two sorted pins

Each transclusion uses the pin whose `path` equals its own.

SPEC.md §11.9:

> **How pins are written** (0003, addendum, detail 2): a line of the
> referrer's frontmatter that is exactly `pins:`, directly followed by one
> line per pin, each `  - ` (two spaces, a hyphen and a space) followed by an
> object in §11.1's canonical form and string escaping:

SPEC.md §11.9:

> - The pins end at the first frontmatter line that does not begin with
>   `  - `. They are sorted by `path`, ascending, code point by code point, and
>   no `path` appears twice.
> - A line that begins with `  - ` after the pins have ended is refused when
>   every line between them is blank or begins with a space or `#`: a YAML
>   reader would read it as one more pin, across a blank or comment line.
