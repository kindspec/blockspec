# EDITED: a short prefix no longer at the leaf's start, the suffix holding

0004's own example. The comment on `restart every replica` has the short
prefix `Note: ` and the short suffix ` now.`. `Note:` became `Urgent
note:`, so the prefix is no longer all of the text before the occurrence
and does not hold. The suffix is still all of the text after it, and the
span still has a space before it and after it: one side holds, so the
comment follows, `EDITED`. Under 0003 it detached.

SPEC.md §11.5:

> For `EDITED`, the span is searched **inside the paired leaf only**. A hit is
> an occurrence of `span` that meets both of these (0004, which amends 0003
> Q13):
>
> 1. **Its neighbours are unchanged.** The code point just before the
>    occurrence in the paired leaf's text compares equal to the code point
>    just before the span in `leaf.text`, and the code point just after it to
>    the one just after the span. U+0009, U+000A, U+000D and U+0020 compare
>    equal to one another; a text's start or end compares equal only to a
>    start or end; any other code point only to itself.
> 2. **Its context holds.** The prefix holds when the paired leaf's text
>    before the occurrence ends with `prefix`; when `prefix` is shorter than
>    32 code points, counted as stored, it must be all of that text (0003,
>    addendum, detail 6: a short context sits at the leaf's edge). The
>    suffix holds in the same way, after the occurrence and at the leaf's
>    end. Which sides must hold, and how they compare, depends on the types
>    of `leaf` and of the paired leaf:
>    - **either is `code` or `table`**: both sides, compared exactly, as
>      0003 Q13 decided, for a comment and a suggestion alike.
>    - **both are `p` or `h1` to `h6`**: each of the text before the occurrence, the
>      text after it, `prefix` and `suffix` is first written on its own with
>      every run of U+0009, U+000A, U+000D and U+0020 as one U+0020. **For a
>      comment**, one side must hold whose stored context is not empty; when
>      both are empty, the span is the whole leaf and both hold. **For a
>      suggestion**, both sides must hold.

0004, *What it gives up*:

> - **A short context away from the leaf's edge** no longer detaches a
>   comment when the other side holds. The neighbour rule still detaches it
>   when a code point was added at that edge and the context there was
>   empty; with a short context there, as a comment on `restart every
>   replica` in "Note: restart every replica now." becoming "Urgent note:
>   restart every replica now.", the comment follows on the other side.
