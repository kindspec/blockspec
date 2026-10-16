# #REF!(reply-to): the parent record is gone

The reply names an id with no record file in `policy.md.notes/`, as after
the parent was deleted on one branch while the reply was added on another.

SPEC.md §11.8:

> - **A reply whose `reply-to` names no record in its directory** renders as
>   `#REF!(reply-to)`, once its document checks pass (§11.10).

SPEC.md §11.10:

> A reply with no parent renders `#REF!(reply-to)`, once its document
> checks pass (above; §11.8).
