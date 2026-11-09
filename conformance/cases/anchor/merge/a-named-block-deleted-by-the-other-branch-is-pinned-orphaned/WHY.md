# `REFUSED(pinned-orphaned)`: the other branch deletes the named paragraph

Theirs deletes the named paragraph and leaves the marker, which now binds the
next paragraph. Ours edits a third paragraph. The merge is clean. §11.9's step
3 finds no pair for the pinned leaf, so the transclusion is refused. The name
still binding something does not help: §11.9 runs against the pinned leaves.

SPEC.md §11.9, step 3:

> 3. For each text-bearing leaf the name binds in the pinned blob, §11.3 and
>    §11.4 run with that blob as `base`. A refusal, or no pair, refuses the
>    transclusion, as `REFUSED(pinned-<reason>)`, where `<reason>` is §11.4's
>    reason or `orphaned`.

0003 §8 lists it as the anchored leaf deleted:

> | the anchored leaf deleted | `ORPHANED` | stale | refused |
