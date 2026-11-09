# Each branch adds the same name far apart

The two markers are different insertions at different places, so stock git
merges them. The merged document declares the name twice.

SPEC.md §7.4:

> **A name declared twice in one document is refused** (`duplicate-name`;
> 0001, *What draft 0 carries*). A name is declared by a one-line marker or by
> a `:begin`.
