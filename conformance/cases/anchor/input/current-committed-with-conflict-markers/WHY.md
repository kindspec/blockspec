# REFUSED(not-in-profile): a file committed with conflict markers

The current file holds a conflict on another paragraph, committed as it
stood. The profile refuses it (`conflict-marker`). 0003 §8: two branches
edit the same lines, committed with its markers, `REFUSED(not-in-profile)`.

SPEC.md §11.10:

> | `not-in-profile` | `base`, the current text, a pinned blob or a transclusion's current target is refused under §9, a file committed with conflict markers included; or the referrer is, which refuses it as a whole (§11.9, step 0) |
