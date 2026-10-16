# RESOLVED: a `  - ` line after another key does not refuse

After the pins, a `tags:` key holds a list item `  - safety`. The line
between the pins and that item is neither blank nor begins with a space or
`#`, so the item is not refused, and both transclusions resolve.

SPEC.md §11.9:

> - The pins end at the first frontmatter line that does not begin with
>   `  - `. They are sorted by `path`, ascending, code point by code point, and
>   no `path` appears twice.
> - A line that begins with `  - ` after the pins have ended is refused when
>   every line between them is blank or begins with a space or `#`: a YAML
>   reader would read it as one more pin, across a blank or comment line.
