# One name on a `:begin` and a one-line marker

Each declares `b`. The `:begin` has no `:end`, which reading 3 makes
`unpaired-region`, and the one-line marker has no next sibling, which is
`dangling-marker`. §9's order makes the refusal `duplicate-name` either way.

SPEC.md, §7.4:

> A name is declared by a one-line marker or by a `:begin`.

SPEC.md, §9:

> when `duplicate-name` and `unpaired-region` both apply, the refusal is
> `duplicate-name`, and `dangling-marker` is reported after both: a
> document that also has a duplicate or unpaired name is refused for
> that;
