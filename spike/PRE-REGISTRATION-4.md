<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Pre-registration 4: the anchor resolver's refusals on real history

**Status: approved by the owner on 2026-10-17, as written, with each §0
choice as drafted.** "Committed" means merged to `main`. No verdict arm
below runs before this document merges.

**The question.** Adjudication 0003 §12, item 1, names first among what
would reverse its anchor design "A replay over real history that prices the
refusals". The resolver adds refusals (the near-copy, refilled-gap,
crowded-gap, twin and context rules, and the alignment) whose rate on real
edits is unknown: "If it is too high, the crowded-gap rule and the
near-copy rule on `EDITED` leaves are the likeliest costs, and the first to
revisit." This document fixes, before the replay runs, what is measured, on
what, and what result means what.

**Citations.** A blockspec path means its content at `d38a6bc` on `main`.
The harness is kindspec/research `experiments/D8-anchor-replay/`, with the
word oracle and the labelled sample of research#20, merged as `c26bba1`;
the commit it runs at is pinned in §2. Every figure below is given with
the file that holds it.

---

## 0. Choices the owner is approving

Approving the document approves each of these, as written.

1. **The bar for refusals (§4).** At gap 5, pooled over the verdict arms, at
   most **5%** of comments whose span survived are refused (`loud`), with
   the labelled sample for truth (§1). Above it, the rule that refuses most
   is revisited first, as 0003 §12 says. *Alternatives:* 2%, about the
   lowest D8 figure for its own resolver at gap 5 (2.1%, rust-book), which
   would make any cost of the added rules a failure; or 10%, which
   tolerates one refusal in ten of text that is still there. **The
   rehearsal arm is above 5%** (§6): this bar was drafted before that was
   known, and choosing it now is choosing with that known.

   The rate is over comments on pairs whose later version the profile
   accepts (`SPEC.md` §4). A comment on a version the profile refuses is
   `REFUSED(not-in-profile)` whatever its text: that is the profile's cost,
   not the anchor rules' 0003 §12 asks to price, and it is reported beside
   the rate (§3), not counted in it. *Alternative:* count each such comment
   as a refusal of surviving text, which on the rehearsal arm takes the
   rate from 6.6% to 27.3% (§6), every one of them from one profile rule.
2. **How the bar is read (§4).** The rate has a range (§1). It passes if
   the whole range is within the bar, fails if the whole range is above
   it, and is **inconclusive** otherwise. *Alternative:* read the point
   estimate alone, which always decides but can decide on noise.
3. **The bar for wrong resolutions (§4).** Every `WRONG` is examined by
   hand and classified (§5). A single `WRONG` that is a resolver defect,
   not one of `SPEC.md` §11.12's R1 to R4 and not an oracle error, fails
   the run. *Alternative:* a rate, such as 0.1%. 0003's guarantee is that
   the format resolves silently wrong only in R1 to R4, so any other wrong
   resolution contradicts it, however rare.
4. **The verdict arms (§2).** rust-book, obsidian-help, k8s-en and
   cncf-toc, at the pins of research `experiments/D8-block-definitions/arms.json`.
   *Alternatives:* add k8s-l10n (other languages, where the profile and
   the oracle may behave differently); or D8's three arms only.
5. **Gap 5 decides; gaps 1 and 25 are reported.** Gap 5 is where D8
   reported its figures for two arms. Gap 1 is nearly every edit a single
   commit makes, and gap 25 is where D8's oracle is confident about fewest
   blocks (38% on rust-book, D8 §3), so neither decides. *Alternative:*
   decide on every gap.
6. **The labelled sample (§1).** At gap 5, each verdict arm's comments
   are sampled per stratum up to the caps in §2, with **100** for comments
   the oracle places and the resolver resolves (30 on the rehearsal arm,
   where the oracle's error, with every stratum at the upper end of its
   interval, was 11.4%). Each
   packet is labelled twice, independently, by automated labellers who see
   only the packet and `labelling-brief.md`, as on the rehearsal arm; a
   disagreement is settled by a third label. *Alternatives:* people label,
   which no arm has tried and which the brief would need no change for; or
   the rehearsal's caps, up to 70 fewer packets per arm and a wider range.

## 1. What is measured

`experiments/D8-anchor-replay/replay.py`, as its README describes. In
brief, for each arm, each of 60 sampled files, and up to three pairs of
versions GAP commits apart in that file's history:

- a comment on three words from the middle of every paragraph of the
  earlier version with at least 20 characters, made as `SPEC.md` §11.1
  creates one;
- resolved by the reference resolver against the later version;
- graded by the word oracle: difflib matches the earlier version's
  paragraph words onto the later's, and the span survives in the paragraph
  its three words map to, adjacent and in order; it is gone when its
  words occur, in order and adjacent, in no later paragraph; otherwise (a
  move, a copy) it is not counted. A comment is `correct`; `loud`, refused, `DETACHED` or
  `ORPHANED` though its span survived; or `WRONG`, resolved somewhere the
  oracle does not put it, or resolved though its span is gone.

The oracle is difflib's, not a reader's, and does not follow a moved
paragraph. So the measure for choice 1 is taken with labels for truth:
`sample.py` stratifies the verdict arms' gap-5 comments by arm, the
oracle's class and the resolver's, and writes blind packets; `score.py`
scales each stratum's labelled shares to its size, which counts the
comments the oracle does not place and corrects for its errors where it
does, and prints each arm's rate beside the pooled one. Its range puts every
stratum at the end of its exact 95% interval (Clopper-Pearson) least and
most favourable to the bar. Each `loud` is reported with its status and
refusal reason, and `kinds.py` sorts them by how much their paragraph
changed.

## 2. Arms, sample and pins

| arm | pin | pathspec |
| --- | --- | --- |
| rust-book | `1500248d8f23` | `src/*.md` |
| obsidian-help | `327a782e9048` | `en/*.md` |
| k8s-en | `6b27baef1e44` | `content/en/*.md` |
| cncf-toc | `144c2e321588` | `*.md :(exclude).github/` |

The pins and pathspecs are `arms.json`'s. The replay's sample is
`replay.py`'s: 60 files per arm, up to three pairs per file, seed 7, gaps
1, 5 and 25. The labelled sample is `sample.py`'s at gap 5, per arm, seed
11, with these caps:

| stratum | cap |
| --- | --: |
| placed, loud | 60 |
| placed, resolves | 100 |
| gone, loud | 25 |
| gone, resolves | 25 |
| unplaced, loud | 60 |
| unplaced, resolves | 30 |

The harness runs at research `c26bba1`, its gap-5 sample with
`--cap placed/resolves=100`.

**Not verdict arms:** site-policy is the rehearsal arm (§6). cmspec is
excluded: the profile refuses both of its documents (one holds a
conflict-marker line, the other an indented code block), so it yields no
comments.

## 3. What is published

`replay.py`'s full stdout for every verdict arm and gap, `kinds.py`'s at
gap 5, and every labelled sample (`sample.py`'s key and stdout, both passes
of labels, any adjudication, and `score.py`'s stdout), committed under
research `experiments/D8-anchor-replay/`, with every `WRONG` listed and
classified (§5). The verdict, one of §4's, is recorded in blockspec beside
0003. It is published whatever it is.

## 4. Verdicts

- **Pass:** the pooled refusal rate's range at gap 5 is within choice 1's
  bar, and no `WRONG` is a resolver defect.
- **Refusals too high:** the whole range is above the bar. The refusal
  reason with the most `loud` comments is revisited first. This reverses
  no rule by itself: a change to a rule is its own adjudication.
- **Inconclusive:** the range spans the bar. It is reported as that, with
  the range; a larger sample is a new document, not an amendment.
- **Resolver defect:** a `WRONG` is classified as a resolver defect. It is
  filed as a bug against the reference resolver, with the file, the pair
  and the comment, and the run fails until the defect is decided.

A resolver defect can hold with any of the first three.

## 5. Classifying a WRONG

Each `WRONG` is read by hand, with the two versions side by side, and
classified as one of:

- **R1 to R4**, the residual `SPEC.md` §11.12 names, which the format
  documents and does not prevent;
- **oracle error**, where reading the two versions shows the resolver was
  right and the oracle placed the span wrongly;
- **resolver defect**, anything else.

The classification and its reason are written beside each one. A
resolving comment the labels put somewhere other than where it resolved is
classified the same way.

## 6. Disclosure: what was seen before this draft

- **The rehearsal arm, site-policy,** was run at gaps 1 and 5 with the
  word oracle (`rehearsal-site-policy.txt`) and labelled at gap 5
  (`labels/site-policy-gap5/`). At gap 5, the oracle does not count 10 of
  2,989 comments; among those it places, 182 of 2,809 surviving spans are
  refused (6.5%), with no `WRONG`. The two passes of labels agree on all
  125 packets, and no label contradicts the oracle where it places a
  comment. With labels for truth the refusal rate is **6.6%, from 6.3% to
  8.3%**, among comments on versions the profile accepts: above choice
  1's bar, so the rehearsal arm, read as a verdict arm, would fail it.
  Besides those, 800 comments sit on 11 pairs whose later version the
  profile refuses, every one for `raw-html`; counting each as a refusal of
  surviving text, the rate is 27.3%. 117 of the 125 labels were made on an
  earlier draw of the same comments and carried over by comment.
- **What refuses** (`kinds-site-policy-gap5.txt`): of the 182, 90 are
  `DETACHED`, 65 `REFUSED(crowded-gap)`, 19 `REFUSED(near-copy)` and 8
  `ORPHANED`. 18 of the near-copy refusals are on paragraphs whose text is
  unchanged, and 11 of the `DETACHED` on paragraphs changed only in
  whitespace, within the span's stored context.
- **The line oracle's figures** for the same arm came first (research#19),
  and are superseded: it did not count 1,275 of the 2,989 comments at gap
  5, and gave 0.9% among those it placed.
- **red_states.py and red_sweep.py** were run on their own fixture.
- **D8's figures** for its own resolver were known: 7.1% loud on rust-book
  at gap 25, 3.1% on obsidian-help and 2.1% on rust-book at gap 5 (0003
  §12). They measure a different resolver and are not comparable as
  numbers.
- No verdict arm has been run against the blockspec reference resolver.

## 7. Amendment rules

After this merges, a change to the bars, the arms, the sample or the
harness before the run is an amendment, committed and dated before the run.
After the run, nothing here changes; a different question gets its own
document.
