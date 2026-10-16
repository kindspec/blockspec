# REFUSED(record-inconsistent): a grammar fault, and no document

The anchor lacks a space after one colon, and `policy.md` does not exist.
The record's grammar comes first.

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
