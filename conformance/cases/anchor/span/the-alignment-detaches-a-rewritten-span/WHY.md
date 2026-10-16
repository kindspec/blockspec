# DETACHED: the span's sentence rewritten, re-added after a long tail

The sentence holding the span was rewritten in place, and the old sentence
re-added at the paragraph's end, with the span's contexts, which lie
inside that sentence. There is one hit, in the re-added sentence. The
longest common subsequence of the old text onto the new runs through the
long sentence after the rewritten one, so it pairs the span's code points
with the rewritten sentence, not with the hit. 0003 §8: the span
rewritten, where the alignment does not carry the span onto it,
`DETACHED`. `residual/r3-a-sentence-rewritten-and-re-added` is the same
edit after a short tail, where the alignment does carry it.

SPEC.md §11.5:

> With one hit, the
> longest common subsequence alignment (§11.2) of the base leaf's text onto
> the paired leaf's text must pair every code point of the span with the code
> point at the same position in the hit, or the anchor is `DETACHED` (0003
> §5).

SPEC.md §11.2:

> A **longest common subsequence alignment** of two sequences pairs elements
> from the start: when the two elements under consideration are equal they
> are paired;
> otherwise the element of the first sequence is skipped if that does not
> shorten the longest common subsequence of what remains, and the element of
> the second is skipped if it does.
