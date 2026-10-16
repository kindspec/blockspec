# REPLY: a reply naming a record in its directory

The reply's `reply-to` is the id of the comment beside it.

SPEC.md §11.1:

> - **A reply is its own record**, with a `reply-to` line naming a record in
>   the same directory, and no anchor.

SPEC.md §11.1:

> - a reply: `reply-to: ` followed by the parent's id as a JSON string, then
>   `kind: comment`.
