# `REFUSED(not-in-profile)`: a merge that makes the target a refused document

Each branch adds a marker named `duty-window`, at different places. The
merge is clean and declares the name twice, so the current target is refused.
A transclusion of an unrelated name in that document is refused with it.

SPEC.md §11.9, step 1:

> 4. the current target must pass the profile, or
>       `REFUSED(not-in-profile)`;

SPEC.md §7.4:

> **A name declared twice in one document is refused** (`duplicate-name`;
> 0001, *What draft 0 carries*). A name is declared by a one-line marker or by
> a `:begin`.
