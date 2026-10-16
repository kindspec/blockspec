# EDITED: two branches edit different lines of the anchored paragraph

The anchored paragraph spans five lines. One branch edits its first line
and the other its last, with three unchanged lines between, so stock git
merges them cleanly. The span and its contexts lie on the middle lines, so
the comment is `EDITED` against the merged text, and the open suggestion
applies to it.

0003 §8:

> | edit | comment | suggestion | transclusion |
> |---|---|---|---|
> | two branches edit different lines of the anchored leaf and merge cleanly | as the edit of the merged text | as the edit of the merged text | resolves |

SPEC.md §11.6:

> | `EDITED` | `EDITED`, and the span found | the anchor, marked changed |
