# RESOLVED: a re-anchoring and a status change merge cleanly

One branch re-anchors the record onto the current blob of `policy.md`,
rewriting its `anchor:` line. The other sets `status: resolved`. The
`kind:` line between them is unchanged, so stock git merges the record
cleanly, and the merged record, consistent and canonical, resolves.

SPEC.md §11.1:

> - **The anchor is one line**, `anchor:` followed by a JSON object, and **at
>   least one line that is not edited freely separates it from any line that
>   is**, such as `kind:` before `status:`.

0003 §3:

> - **At least one unchanging line separates the anchor from any field edited
>   freely**, here `kind` before `status`. Git conflicts on edits to adjacent
>   lines, so without the spacer a status change and a re-anchoring on two
>   branches would conflict for no reason.
