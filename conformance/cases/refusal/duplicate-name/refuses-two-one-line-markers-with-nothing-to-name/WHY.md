# One name on two one-line markers, naming nothing

`dangling-marker` also applies: the first marker's next sibling is a marker
and the second has no next sibling. §9 reports it after `duplicate-name`.

SPEC.md, §7.4:

> A name is declared by a one-line marker or by a `:begin`.

SPEC.md, §9:

> when `duplicate-name` and `unpaired-region` both apply, the refusal is
> `duplicate-name`, and `dangling-marker` is reported after both: a
> document that also has a duplicate or unpaired name is refused for
> that;
