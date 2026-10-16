# REFUSED(record-inconsistent): a malformed `reply-to`, and no document

The reply's `reply-to` is a lower-case ULID, and `policy.md` does not
exist. The reply's grammar is step 1, before `document-missing`.

SPEC.md §11.10:

> **A reply is a record** (0003, third addendum of 2026-10-16, item 2): a
> reply whose document is missing, or refused by the profile, is
> `REFUSED(document-missing)` or `REFUSED(not-in-profile)`. It goes through
> steps 1 to 3; steps 4 to 6 read an anchor, which a reply does not have. Only
> a reply that passes steps 1 to 3 is looked up by its `reply-to`, and renders
> `#REF!(reply-to)` when that names no record. (Where the reply sits in the
> order is the addendum's precision.)

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
