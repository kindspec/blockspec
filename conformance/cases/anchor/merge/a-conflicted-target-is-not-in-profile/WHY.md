# REFUSED(not-in-profile): the target is a conflicted merge

Both branches change the same line of the target, outside the named
paragraph. The merged target holds conflict markers, so the profile
refuses it. 0003 §8: two branches edit the same lines, the transclusion
`REFUSED(not-in-profile)`.

0003 §8:

> | edit | comment | suggestion | transclusion |
> |---|---|---|---|
> | two branches edit the same lines | a git conflict; committed with its markers, the document is refused (`conflict-marker`) and the anchor is `REFUSED(not-in-profile)` | stale | `REFUSED(not-in-profile)` |

SPEC.md §11.9:

> **Resolution**, against the target's current text:
>
> 0. The path must resolve, or `REFUSED(unresolvable-path)`. The target
>    document must exist, or `REFUSED(document-missing)`, and the
>    pinned blob must be readable, or `REFUSED(base-unavailable)`. Both the
>    pinned blob and the current target must pass the profile, or
>    `REFUSED(not-in-profile)`. The name must bind in the pinned blob, or
>    `REFUSED(record-inconsistent)`.
> 1. The name resolves as §8.1 says, against markers only. Zero matches, or
>    more than one, is `#REF!(name)`.
> 2. For each text-bearing leaf the name bound in the pinned blob, §11.3 and
>    §11.4 run with that blob as `base`. A refusal, or no pair, refuses the
>    transclusion, as `REFUSED(pinned-<reason>)`, where `<reason>` is §11.4's
>    reason or `orphaned`.
> 3. Each pair must lie inside what the name binds now. Otherwise the
>    transclusion is `REFUSED(name-rebound)`.
