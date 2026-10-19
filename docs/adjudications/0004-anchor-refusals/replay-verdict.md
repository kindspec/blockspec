<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# 0004: the held-out replay's verdict

**Verdict: pass.** The resolver-defect verdict does not hold. This is the
verdict of `spike/PRE-REGISTRATION-5.md` (merged as `04a612f`), recorded
here as its §3 requires. 0004's first reversal condition, the held-out
replay failing the bar or finding a resolver defect, is not met.

**Pins.** The reference resolver at `ae1d274` (the header of each
`replay-ARM.txt`), and the harness at kindspec/research `8ecb0e7`, as
pre-registration §2 fixes them; the outputs name the resolver, and the
run's README names the harness. The verdict arms are github-docs,
vscode-docs, docker-docs and mdn-en at the pins of research
`experiments/D8-anchor-replay/heldout-arms.json`. The outputs are research
`experiments/D8-anchor-replay/prereg5/`, merged as `95bfc44`
(research#24); every figure below is from a file there.

## The refusal bar

With labels for truth, the refusal rate at gap 5, pooled over the four
verdict arms, is **2.9%**, from 2.8% to 4.2% with every stratum at the
end of its interval, among comments on versions the profile accepts
(`score.txt`). The whole range is within the 5% bar of choice 1, as
choice 2 reads it, so the verdict is pass.

| arm | refusal rate | range |
| --- | --: | --: |
| github-docs | 3.4% | 3.4% to 4.4% |
| vscode-docs | 3.2% | 3.0% to 4.7% |
| docker-docs | 1.8% | 1.8% to 2.4% |
| mdn-en | 2.9% | 2.9% to 4.4% |

The comments at gap 5 come from 101 pairs on github-docs, 160 on
vscode-docs, 31 on docker-docs and 113 on mdn-en, of which 5, 64, 4 and 26
have an earlier version the profile refuses and get no comments (each
`replay-ARM.txt`). The ranges treat comments as independent, which
comments in one pair are not. The pooled range's upper end is 0.8 points
under the bar.

Outside the rate, as choice 1 sets it: 33 comments on versions the
profile refuses, every one `REFUSED(not-in-profile)`; counting each as a
refusal of surviving text, the pooled rate is 3.3%, from 3.2% to 4.6%.

## Wrong resolutions

No comment at any gap is `WRONG` (`wrongs.txt`), and the labels put no
resolving comment anywhere other than where it resolved (`score.txt`). So
there is nothing for §5 to classify, and the resolver-defect verdict does
not hold. As pre-registration 5 §4 says, the test cannot see an edit beside
a span (`SPEC.md` §11.12) or R3 within one leaf: the oracle counts such a
comment correct, and the labels place it in the same paragraph. And 33
resolving comments the oracle does not count, 19 at gap 1 and 14 at gap
25, are outside both checks; the run's README gives them per arm.

## What refuses

The rate counts the refusals of surviving text: the 213 comments the oracle
places and the resolver refuses at gap 5, all of which the labels find
surviving where sampled but two of 60 on vscode-docs, and the refused
comments the oracle does not place that the labels find surviving (36 of
the 56 sampled). By status and refusal reason, the 213, per arm (each
`replay-ARM.txt`) and pooled (`kinds-gap5.txt`):

| cause | github-docs | vscode-docs | docker-docs | mdn-en | pooled |
| --- | --: | --: | --: | --: | --: |
| `REFUSED(crowded-gap)` | 22 | 59 | 9 | 6 | 96 |
| `REFUSED(near-copy)` | 18 | 21 | 6 | 7 | 52 |
| `ORPHANED` | 8 | 23 | 7 | 2 | 40 |
| `DETACHED` | 7 | 9 | 1 | 6 | 23 |
| `REFUSED(repeat)` | 0 | 0 | 0 | 1 | 1 |
| `REFUSED(unaccounted-copy)` | 0 | 1 | 0 | 0 | 1 |

Of the near-copy refusals, 22 are on a paragraph whose text is unchanged
(`kinds-gap5.txt`). Crowded-gap, which 0004 left as 0003 had it, is the
first cause, as it was on the arms 0004 was tuned on.

## The regression arms

The five arms 0004 was tuned on, run at the same resolver into their own
dump (choice 7, `regression/`): no comment at any gap is `WRONG`, and with
the oracle for truth 299 of 6,279 comments whose span survives are loud at
gap 5 (4.8%), the figure 0004 records. They are not part of the verdict.

## How the run went

The run followed the document: all twelve arm and gap sections for the
verdict arms and fifteen for the regression arms, and the gap-5 sample of
743 packets labelled twice by 44 labellers a pass, dealt as choice 6 says.
The passes agree on 738; a third label decides the other five. Labellers in
the same pass shared one scratch directory and could see each other's
helper scripts, which hold no labels; each pass's files were moved out of
reach before the next. Copies of pre-registration 4's labels were on the
same machine with 215 ids in common, for other comments: no label that
says the words survive gives the same later paragraph as one of those,
and three that say they do not survive match, about as chance gives
(`README.md` there).
