# Both branches make the identical edit

Git takes an identical change once, so the edit appears a single time and the
document reads as either side's. This is the control for the branch cases of
`same-place/`, where the two sides add different text at one place.

SPEC.md §10, on what a `merge` case says:

> A case of the kind `merge` runs stock `git merge` over three versions of a
> document, checks what git reports and the merged bytes, and then reads the
> merged text as above.
