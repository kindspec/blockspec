# REFUSED(unresolvable-path): a `..` above the repository's root

`guide.md` is at the repository's root, so `..` would leave it. The referrer pins the same path text, and `policy.md` exists at the
root.

SPEC.md §11.9:

> **The path** (0003, addendum, detail 7) is the destination's part before the
> `#` (CommonMark 0.31.2, *Links*), **as raw text**: character for character
> as the file writes it, with no backslash escape, entity reference or
> percent-encoding decoded. That is also the text a pin's `path` holds, and
> this definition governs both. So `my%20doc.md` names a file called
> `my%20doc.md`. It resolves relative to the directory that
> holds the referrer, as a renderer resolves a relative link, in the tree of
> the snapshot being resolved: it is split at `/`, a `.` segment is dropped,
> and a `..` segment removes the segment before it.
>
> - A path that begins with `/`, or whose first segment holds a `:`, is
>   absolute, and is `REFUSED(unresolvable-path)`.
> - A `..` that would go above the repository's root is
>   `REFUSED(unresolvable-path)`.
> - A path that names no file in that tree is `REFUSED(document-missing)`.
>   Names compare exactly, case included.
