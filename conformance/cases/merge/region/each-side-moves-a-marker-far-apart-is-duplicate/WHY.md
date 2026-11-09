# Each branch moves the same marker, to different places

Both sides delete the marker line, so git takes that once, and each side's
insertion lands somewhere else. Each branch alone holds one marker, and is
accepted. The merged document holds two.

SPEC.md §7.4:

> **A name declared twice in one document is refused** (`duplicate-name`;
> 0001, *What draft 0 carries*). A name is declared by a one-line marker or by
> a `:begin`.
