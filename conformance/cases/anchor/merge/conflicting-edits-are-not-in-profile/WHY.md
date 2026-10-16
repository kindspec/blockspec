# REFUSED(not-in-profile): a conflicted merge committed with its markers

Both branches change the anchored paragraph's last line, so stock git
conflicts, and the merged file holds its conflict markers. The profile
refuses it (`conflict-marker`), so the comment is refused and the
suggestion stale.

0003 §8:

> | two branches edit the same lines | a git conflict; committed with its markers, the document is refused (`conflict-marker`) and the anchor is `REFUSED(not-in-profile)` | stale | `REFUSED(not-in-profile)` |

SPEC.md §11.10:

> | `not-in-profile` | `base`, the current text, a pinned blob or a transclusion's current target is refused under §9, a file committed with conflict markers included; or the referrer is, which refuses it as a whole (§11.9, step 0) |
