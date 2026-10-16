# REFUSED(not-in-profile): a base with a setext heading

The record's `base` opens with a setext heading, which the profile
refuses, so `base` has no leaves. Step 5 of the order reports it before
step 6's leaf check, which would otherwise find no leaf at `nth`.

SPEC.md §11.10:

> **Which reason is reported** (0003, second addendum of 2026-10-16, item 2).
> When a record has several input problems, the first in data-dependency order
> is reported:
>
> 1. the record's grammar (`record-inconsistent`);
> 2. `document-missing`;
> 3. the current document refused under the profile (`not-in-profile`);
> 4. `base-unavailable`;
> 5. `base` refused under the profile (`not-in-profile`);
> 6. the leaf at `nth` inconsistent with `base` (`record-inconsistent`).
