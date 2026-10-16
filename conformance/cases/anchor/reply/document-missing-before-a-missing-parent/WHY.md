# REFUSED(document-missing): no document, and no parent

The reply's `reply-to` names no record, and `policy.md` does not exist.
A reply is looked up by its `reply-to` only once its document checks
pass, so it is `REFUSED(document-missing)`, not `#REF!(reply-to)`.

SPEC.md §11.10:

> **A reply is a record** (0003, third addendum of 2026-10-16, item 2): a
> reply whose document is missing, or refused by the profile, is
> `REFUSED(document-missing)` or `REFUSED(not-in-profile)`. It goes through
> steps 1 to 3; steps 4 to 6 read an anchor, which a reply does not have. Only
> a reply that passes steps 1 to 3 is looked up by its `reply-to`, and renders
> `#REF!(reply-to)` when that names no record. (Where the reply sits in the
> order is the addendum's precision.)

SPEC.md §11.8:

> - **A reply whose `reply-to` names no record in its directory** renders as
>   `#REF!(reply-to)`, once its document checks pass (§11.10).
