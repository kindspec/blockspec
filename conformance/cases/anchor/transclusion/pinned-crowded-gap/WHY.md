# REFUSED(pinned-crowded-gap): a pinned leaf edited while its gap grew

Inside the region, the first paragraph was edited and a short paragraph
added after it. The edit pairs as `EDITED`, and the new paragraph is
unmatched in the same gap.

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

0003 §7:

> An edit
> that leaves a pinned leaf with no pair (`pinned-orphaned`), or that adds
> leaves around one while editing it (`pinned-crowded-gap`), still refuses
> until a re-pin
