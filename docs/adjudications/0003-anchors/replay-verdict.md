<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# 0003 §12, item 1: the replay's verdict

**Verdict: refusals too high.** The resolver-defect verdict does not
hold. This is the verdict of `spike/PRE-REGISTRATION-4.md` (merged as
`08ef724`, amended as `80ef549`), recorded here as its §3 requires. It
reverses no rule by itself (§4): which rule to revisit is the following
adjudication's.

**Pins.** The reference resolver at `d38a6bc` (the header of each
`replay-ARM.txt`), and the harness at kindspec/research `735091e`, as
pre-registration §2 and amendment 1 fix it; the outputs name the resolver,
and the research README names the harness. The arms are rust-book,
obsidian-help, k8s-en and cncf-toc at the pins of research
`experiments/D8-block-definitions/arms.json`. The outputs are research
`experiments/D8-anchor-replay/prereg4/`, merged as `a0ea138`
(research#22); every figure below is from a file there.

## The refusal bar

With labels for truth, the refusal rate at gap 5, pooled over the four
arms, is **17.0%**, from 16.3% to 18.7% with every stratum at the end of
its interval, among comments on versions the profile accepts
(`score.txt`). The whole range is above the 5% bar of choice 1, as §4
reads it, so the verdict is refusals too high.

| arm | refusal rate | range |
| --- | --: | --: |
| rust-book | 22.1% | 21.1% to 22.8% |
| obsidian-help | 17.6% | 16.8% to 19.7% |
| k8s-en | 8.1% | 8.1% to 8.1% |
| cncf-toc | 10.4% | 10.4% to 11.5% |

The per-arm rates rest on few pairs at gap 5: 23 on rust-book, 101 on
obsidian-help, 3 on k8s-en and 6 on cncf-toc, and 37 of cncf-toc's 56
refusals are on one pair (`README.md` there). The ranges treat comments
as independent, which comments in one pair are not, and a stratum
labelled in full gets no interval, so k8s-en's zero-width range is not
precision. The pooled range is above the bar by more than eleven points.

Outside the rate, as choice 1 sets it: 595 comments on versions the
profile refuses, every one `REFUSED(not-in-profile)`; counting each as a
refusal of surviving text, the pooled rate is 29.1%.

## Wrong resolutions

No comment at any gap is `WRONG` (`wrongs.txt`), and the labels put no
resolving comment anywhere other than where it resolved (`score.txt`). So
there is nothing for §5 to classify, and the resolver-defect verdict does
not hold. Fifteen resolving comments the oracle does not count, at gaps 1
and 25 (the dump's rows with no verdict that resolve), are outside both
checks.

## What refuses

The rate counts 597 refusals of surviving text: the 570 the oracle places
and the resolver refuses, and 27 more on obsidian-help that the oracle does
not place and the labels find surviving. By status and refusal reason,
the 570 the oracle places, per arm (each `replay-ARM.txt` at gap 5) and
pooled (`kinds-gap5.txt`):

| cause | rust-book | obsidian-help | k8s-en | cncf-toc | pooled |
| --- | --: | --: | --: | --: | --: |
| `REFUSED(near-copy)` | 57 | 174 | 1 | 43 | 275 |
| `DETACHED` | 38 | 119 | 2 | 9 | 168 |
| `REFUSED(crowded-gap)` | 13 | 80 | 0 | 1 | 94 |
| `ORPHANED` | 2 | 26 | 0 | 3 | 31 |
| `REFUSED(repeat)` | 0 | 2 | 0 | 0 | 2 |

Of the pooled near-copy refusals, 268 are on a paragraph whose text is
unchanged; of the `DETACHED`, 154 are where the span's stored context
changed (`kinds-gap5.txt`).

These bear on two items of 0003 §12. Item 1 names the crowded-gap rule and
the near-copy rule on `EDITED` leaves as the likeliest costs. Here
near-copy is the first cause, and 268 of its 275 are on paragraphs whose
text is unchanged; crowded-gap is the third, with 94. Item 3 asks whether
detachments from edits next to a span dominate; `DETACHED` is the second
cause, 154 of its 168 with the context changed. Neither is decided here.

## How the run went

A first attempt at research `c26bba1` stopped: three arms on a harness
defect, and cncf-toc stopped by hand, before any figure was printed.
Amendment 1 moved the pin to `735091e` and records what was seen. The run
then followed the document: all twelve arm and gap sections, and the
gap-5 sample of 629 packets labelled twice, the two passes agreeing on
every packet. Choice 6 meant the two passes' batches to differ; with 629
packets and 37 labellers of 17 they could not, so each pass-B batch holds
one pass-A batch's packets in another order (`README.md` there).
