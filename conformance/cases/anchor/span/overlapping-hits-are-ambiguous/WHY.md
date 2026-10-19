# REFUSED(span-ambiguous): two hits that overlap

The span `ip tri` straddles the two words of `trip trip` in

    When a channel faults, the alarm sequence is trip trip and then the reactor scrams at once.

at 47 to 53, with the prefix `faults, the alarm sequence is tr` and the
suffix `p and then the reactor scrams at`. The current paragraph says
`trip trip trip`, so the span occurs at 47 and at 52, five code points
apart: the two occurrences share the `i` at 52, so they overlap.

- At 47: the text before ends with the prefix, so the prefix holds; the
  text after begins `p trip and`, so the suffix does not.
- At 52: the text before ends `is trip tr`, so the prefix does not hold;
  the text after begins `p and then the reactor scrams at`, so the suffix
  does.
- Word boundaries: in `leaf.text` the span starts between `r` and `i` and
  ends between `i` and `p`, neither a word boundary; at both occurrences
  the same holds.

Each occurrence has one side of its context and matching boundaries, so
both are hits. Hits are counted by start position, so there are two. A
search that resumed after each match, and so never saw an overlapping one,
would find only the occurrence at 47 and report `EDITED`.

**What 0004 changed.** Under 0003 the paragraph held `trip ` fourteen
times, and the span with both its contexts occurred at two overlapping
positions. Under 0004 one side is enough, and the same input has a hit at
every one of its 14 occurrences: still ambiguous, but no longer only
through counting an overlap, since a search that skips overlaps also
finds seven. The input is now one where exactly two hits exist and they
overlap.

The paragraph's similarity to its base text is `2·93/191`
(`4·93 = 372 ≥ 191`). Every other leaf is unchanged and on the chain, so the anchored
paragraph and its edit are the only leftovers in their gap; they pair as
`EDITED` once their similarity is at least 0.5, and no unmatched leaf is
left for §11.4's `EDITED` rules.

SPEC.md §11.5:

> For `EDITED`, the span is searched **inside the paired leaf only**. A hit is
> an occurrence of `span` that meets both of these (0004, which replaces
> 0003 Q13's requirement of both sides):
>
> 1. **Its ends are word boundaries exactly where the base span's are.** A
>    position in a text is a word boundary when it is the text's start or
>    end, or when the code points on its two sides are not both letters or
>    numbers (general category L or N). The occurrence's start is a word
>    boundary in the paired leaf's text if and only if the span's start is
>    one in `leaf.text`, and the same for its end.
> 2. **One side of its context holds.** Write each text with every run of
>    U+0009, U+000A, U+000D and U+0020 as one U+0020: the paired leaf's text
>    before the occurrence and after it, each taken on its own, and `prefix`
>    and `suffix`. The prefix holds when the text before the occurrence, so
>    written, ends with `prefix` so written; when `prefix` is shorter than
>    32 code points, counted as stored, it must be all of that text (0003,
>    addendum, detail 6: a short context sits at the leaf's edge). The suffix holds in the same way, after the
>    occurrence and at the leaf's end. A hit needs the prefix or the suffix
>    to hold.
>
> Hits are counted by start position, overlapping ones included (§11.1). With no hit the anchor is
> `DETACHED`; with more than one, `REFUSED(span-ambiguous)`.

SPEC.md §11.1:

> **Occurrences are counted by start position** (0003, third addendum of
> 2026-10-16, item 1), here, in the consistency check below and in §11.5's
> hits alike: two occurrences that overlap are two.
