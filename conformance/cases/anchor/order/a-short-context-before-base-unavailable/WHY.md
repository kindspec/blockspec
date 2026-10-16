# REFUSED(record-inconsistent): a short suffix away from the edge, and base is unreadable

The suffix holds 31 code points while `leaf.text` runs on far past it, and
`base` cannot be read. The edge is checked in `leaf.text`, in step 1.

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

SPEC.md §11.10:

> Step 1 holds every check that reads only the record, `leaf.text` included:
> its file name and directory entry, its frontmatter, its body, an empty
> `span`, a context longer than 32 code points, `prefix + span + suffix` not
> occurring exactly once in `leaf.text`, and a short context whose edge in
> `leaf.text` is further away. Step 6 holds the one check that needs `base`'s
> leaves: no leaf of `base` with `leaf`'s type and text at ordinal `nth`.
