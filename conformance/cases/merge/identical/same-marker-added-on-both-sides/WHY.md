# Both branches add the same marker at the same place

Git merges the identical insertion once, so there is one marker and no
duplicate name. Compare `region/same-name-added-far-apart-is-duplicate`,
where the same text added in two places is a duplicate.

SPEC.md §7.4:

> **A name declared twice in one document is refused** (`duplicate-name`;
> 0001, *What draft 0 carries*). A name is declared by a one-line marker or by
> a `:begin`.
