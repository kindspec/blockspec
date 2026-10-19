# DETACHED: a short prefix whose occurrence is not at the leaf's start

The span opens the paragraph, so its stored `prefix` is empty. The current
paragraph gained `In short: ` in front. The span and its full suffix still
occur, at code point 10, and the suffix holds. But the code point before
the occurrence is a space, where the span began at the leaf's start, and a
text's start compares equal only to a start: the neighbours are not
unchanged, so the occurrence is not a hit, and there is none. (The empty
prefix, not all of the text before the occurrence, does not hold either,
and as an empty side it would not count.)

Under 0003 this detached because the short prefix had to sit at the
leaf's start; under 0004 the neighbour rule detaches it, which is the case
0004 names: "a span at the leaf's start still needs its suffix", and with
text added at that edge the neighbour rule still detaches it.
`span/an-edge-does-not-match-whitespace` is the other direction.

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

0003, addendum, detail 6:

> Without the rule, a span at a leaf's start,
> stored with an empty `prefix`, could land on a later occurrence of it that
> the same `suffix` follows.

0004, *What it gives up*:

> - **A short context away from the leaf's edge** no longer detaches a
>   comment when the other side holds. The neighbour rule still detaches it
>   when a code point was added at that edge and the context there was
>   empty; with a short context there, as a comment on `restart every
>   replica` in "Note: restart every replica now." becoming "Urgent note:
>   restart every replica now.", the comment follows on the other side.
