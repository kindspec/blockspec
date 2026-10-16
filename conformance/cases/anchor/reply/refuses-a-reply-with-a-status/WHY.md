# REFUSED(record-inconsistent): a reply with a status line

A reply's lines are `reply-to:` and `kind: comment`, and nothing else.

SPEC.md §11.1:

> - a reply: `reply-to: ` followed by the parent's id as a JSON string, then
>   `kind: comment`.

0003, addendum:

> - **`reply-to` as a JSON string, and a reply carrying `kind: comment` and no
>   `status`**
