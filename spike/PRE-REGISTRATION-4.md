<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Pre-registration 4: the anchor resolver's refusals on real history

**Status: draft, for the owner's approval.** "Committed" means merged to
`main`. No verdict arm below runs before this document merges.

**The question.** Adjudication 0003 §12, item 1, names first among what
would reverse its anchor design "A replay over real history that prices the
refusals". The resolver adds refusals (the near-copy, refilled-gap,
crowded-gap, twin and context rules, and the alignment) whose rate on real
edits is unknown: "If it is too high, the crowded-gap rule and the
near-copy rule on `EDITED` leaves are the likeliest costs, and the first to
revisit." This document fixes, before the replay runs, what is measured, on
what, and what result means what.

**Citations.** A blockspec path means its content at `d38a6bc` on `main`.
The harness is kindspec/research `experiments/D8-anchor-replay/`, at the
commit that merges research#19, pinned in §2 when this document is
approved. Every figure below is given with the command that produced it.

---

## 0. Choices the owner is approving

Approving the document approves each of these, as written.

1. **The bar for refusals (§4).** At gap 5, pooled over the verdict arms, at
   most **5%** of comments whose span survived are refused (`loud`). Above
   it, the rule that refuses most is revisited first, as 0003 §12 says.
   *Alternatives:* 2%, about the lowest D8 figure for its own resolver at
   gap 5 (2.1%, rust-book), which would make any cost of the added rules a failure; or
   10%, which tolerates one refusal in ten of text that is still there.
2. **The bar for wrong resolutions (§4).** Every `WRONG` is examined by
   hand and classified (§5). A single `WRONG` that is a resolver defect,
   not one of `SPEC.md` §11.12's R1 to R4 and not an oracle error, fails
   the run. *Alternative:* a rate, such as 0.1%. 0003's guarantee is that
   the format resolves silently wrong only in R1 to R4, so any other wrong
   resolution contradicts it, however rare.
3. **The verdict arms (§2).** rust-book, obsidian-help, k8s-en and
   cncf-toc, at the pins of research `experiments/D8-block-definitions/arms.json`.
   *Alternatives:* add k8s-l10n (other languages, where the profile and
   the oracle may behave differently); or D8's three arms only.
4. **Gap 5 decides; gaps 1 and 25 are reported.** Gap 5 is where D8
   reported its figures for two arms. Gap 1 is nearly every edit a single
   commit makes, and gap 25 is where D8's oracle is confident about fewest
   blocks (38% on rust-book, D8 §3), so neither decides. *Alternative:*
   decide on every gap.

## 1. What is measured

`experiments/D8-anchor-replay/replay.py`, as its README describes. In
brief, for each arm, each of 60 sampled files, and up to three pairs of
versions GAP commits apart in that file's history:

- a comment on three words from the middle of every paragraph of the
  earlier version with at least 20 characters, made as `SPEC.md` §11.1
  creates one;
- resolved by the reference resolver against the later version;
- graded by D8's line oracle, applied to paragraphs: `correct`; `loud`, a
  comment refused, `DETACHED` or `ORPHANED` though its span survived in
  the paragraph the oracle maps it to; or `WRONG`, a comment that resolves
  somewhere the oracle does not put it, or resolves though its span or
  paragraph is gone. A span the oracle cannot place, or that occurs more
  than once in its target, is not counted.

The measure for choice 1 is `loud` divided by comments whose span survived,
pooled over the verdict arms at gap 5. Each `loud` is reported with its
status and refusal reason.

## 2. Arms, sample and pins

| arm | pin | pathspec |
| --- | --- | --- |
| rust-book | `1500248d8f23` | `src/*.md` |
| obsidian-help | `327a782e9048` | `en/*.md` |
| k8s-en | `6b27baef1e44` | `content/en/*.md` |
| cncf-toc | `144c2e321588` | `*.md :(exclude).github/` |

The pins and pathspecs are `arms.json`'s. The sample is `replay.py`'s: 60
files per arm, up to three pairs per file, seed 7, gaps 1, 5 and 25. The
harness pin is filled in when this document is approved.

**Not verdict arms:** site-policy is the rehearsal arm (§6). cmspec is
excluded: the profile refuses both of its documents (one holds a
conflict-marker line, the other an indented code block), so it yields no
comments.

## 3. What is published

`replay.py`'s full stdout for every verdict arm and gap, committed under
research `experiments/D8-anchor-replay/`, with every `WRONG` listed and
classified (§5). The verdict, one of §4's, is recorded in blockspec beside
0003. It is published whatever it is.

## 4. Verdicts

- **Pass:** the loud rate at gap 5 is within choice 1's bar, and no
  `WRONG` is a resolver defect.
- **Refusals too high:** the loud rate at gap 5 is above the bar. The
  refusal reason with the most `loud` comments is revisited first. This
  reverses no rule by itself: a change to a rule is its own adjudication.
- **Resolver defect:** a `WRONG` is classified as a resolver defect. It is
  filed as a bug against the reference resolver, with the file, the pair
  and the comment, and the run fails until the defect is decided.

Both of the last two can hold at once.

## 5. Classifying a WRONG

Each `WRONG` is read by hand, with the two versions side by side, and
classified as one of:

- **R1 to R4**, the residual `SPEC.md` §11.12 names, which the format
  documents and does not prevent;
- **oracle error**, where reading the two versions shows the resolver was
  right and the line oracle placed the paragraph wrongly;
- **resolver defect**, anything else.

The classification and its reason are written beside each one.

## 6. Disclosure: what was seen before this draft

- **The rehearsal arm, site-policy,** was run at gaps 1 and 5 to show the
  harness works (`rehearsal-site-policy.txt`): 9 of 3,882 surviving spans
  refused at gap 1 (0.2%), 16 of 1,701 at gap 5 (0.9%, all `near-copy`),
  and no `WRONG`.
- **red_states.py** was run on site-policy at gap 1, with 5 files.
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
