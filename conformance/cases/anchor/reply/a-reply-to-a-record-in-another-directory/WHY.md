# #REF!(reply-to): the parent is in another notes directory

A record with the reply's `reply-to` id exists, in `other.md.notes/`. The
reply is in `policy.md.notes/`, where no record has that id.

SPEC.md §11.1:

> - **A reply is its own record**, with a `reply-to` line naming a record in
>   the same directory, and no anchor.

SPEC.md §11.8:

> - **A reply whose `reply-to` names no record in its directory** renders as
>   `#REF!(reply-to)`.
