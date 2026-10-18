<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# 0003 §12, item 1: the replay's verdict

**Verdict: refusals too high. No resolver defect.** This is the verdict of
`spike/PRE-REGISTRATION-4.md` (merged as `08ef724`, amended as `80ef549`),
recorded here as its §3 requires. It reverses no rule by itself (§4): which
rule to revisit is the following adjudication's.

**Pins.** The harness at kindspec/research `735091e`, against the reference
resolver at `d38a6bc`, on rust-book, obsidian-help, k8s-en and cncf-toc at
the pins of research `experiments/D8-block-definitions/arms.json`. The
outputs are research `experiments/D8-anchor-replay/prereg4/`, merged as
`a0ea138` (research#22); every figure below is from a file there.

## The refusal bar

With labels for truth, the refusal rate at gap 5, pooled over the four
arms, is **17.0%**, from 16.3% to 18.7% with every stratum at the end of
its interval, among comments on versions the profile accepts
(`score.txt`). The whole range is above the 5% bar of choice 1, so the
verdict is refusals too high.

| arm | refusal rate | range |
| --- | --: | --: |
| rust-book | 22.1% | 21.1% to 22.8% |
| obsidian-help | 17.6% | 16.8% to 19.7% |
| k8s-en | 8.1% | 8.1% to 8.1% |
| cncf-toc | 10.4% | 10.4% to 11.5% |

The per-arm rates rest on few pairs at gap 5: 23 on rust-book, 101 on
obsidian-help, 3 on k8s-en and 6 on cncf-toc (`README.md` there). The
pooled range is above the bar by more than eleven points.

Outside the rate, as choice 1 sets it: 595 comments on versions the
profile refuses, every one `REFUSED(not-in-profile)`; counting each as a
refusal of surviving text, the pooled rate is 29.1%.

## Wrong resolutions

No comment at any gap is `WRONG` (`wrongs.txt`), and the labels put no
resolving comment anywhere other than where it resolved (`score.txt`). So
there is nothing for §5 to classify, and no resolver defect.

## What refuses

Of the 570 comments refused at gap 5 though their span survived, pooled
over the four arms (`kinds-gap5.txt`):

| cause | comments | of which |
| --- | --: | --- |
| `REFUSED(near-copy)` | 275 | 268 on a paragraph whose text is unchanged |
| `DETACHED` | 168 | 154 where the span's stored context changed |
| `REFUSED(crowded-gap)` | 94 | |
| `ORPHANED` | 31 | |
| `REFUSED(repeat)` | 2 | |

These bear on two items of 0003 §12. Item 1 names the crowded-gap rule and
the near-copy rule on `EDITED` leaves as the likeliest costs; here
near-copy refuses most, and almost all of it on unchanged paragraphs, not
`EDITED` ones. Item 3 asks whether detachments from edits next to a span
dominate; `DETACHED`, almost all of it with the context changed, is the
second cause. Neither is decided here.

## How the run went

A first attempt at research `c26bba1` stopped on a harness defect before
printing any figure; amendment 1 moved the pin to `735091e` and records
what was seen. The run then followed the document: all twelve arm and gap
sections, the gap-5 sample of 629 packets labelled twice, with the two
passes agreeing on every packet. Choice 6 meant the two passes' batches to
differ; with 629 packets and 37 labellers of 17 they could not, so each
pass-B batch holds one pass-A batch's packets in another order
(`README.md` there).
