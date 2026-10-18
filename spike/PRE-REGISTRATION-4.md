<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Pre-registration 4: the anchor resolver's refusals on real history

**Status: approved by the owner on 2026-10-17; choices 1, 3, 5 and 6
re-approved on 2026-10-18 as they now read.** Between the two, review
changed what the first approval left open: choice 1 no longer orders what
is revisited, choice 3 and 5 make a resolver defect at any gap fail the
run, and choice 6 names the labellers. It also fixed the commands and the
resolver's pin (§2), what is published (§3), how the range is read and
that a defect is not a pass (§4), the exclusions §1 lists, and an
attribution to 0003. Amendment 1 (§7, 2026-10-18) moves the harness pin
after a first attempt stopped on a harness defect. "Committed" means
merged to `main`. No verdict arm below runs before this document merges.

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
   the labelled sample for truth (§1). Above it, the refusals are reported
   by cause (§4), and which rule to revisit is the following adjudication's
   to decide; 0003 §12 names the crowded-gap rule and the near-copy rule on
   `EDITED` leaves as the likeliest costs. *Alternatives:* 2%, about the
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
   not one of `SPEC.md` §11.12's R1 to R4 and not an oracle error, at any
   gap, fails the run; so does a resolving comment the labels put
   elsewhere, classified as a resolver defect (§5). *Alternative:* a rate,
   such as 0.1%. 0003's guarantee is that the format resolves silently
   wrong only in R1 to R4, so any other wrong resolution contradicts it,
   however rare, at whatever gap.
4. **The verdict arms (§2).** rust-book, obsidian-help, k8s-en and
   cncf-toc, at the pins of research `experiments/D8-block-definitions/arms.json`.
   *Alternatives:* add k8s-l10n (other languages, where the profile and
   the oracle may behave differently); or D8's three arms only.
5. **Gap 5 decides the refusal bar; gaps 1 and 25 are reported.** Gap 5
   is where D8 reported its figures for two arms. Gap 1 is nearly every
   edit a single commit makes, and gap 25 is where D8's oracle is
   confident about fewest blocks (38% on rust-book, D8 §3), so neither
   decides the bar. A resolver defect at any gap still fails the run
   (choice 3). *Alternative:* decide the bar on every gap.
6. **The labelled sample (§1).** At gap 5, each verdict arm's comments
   are sampled per stratum up to the caps in §2, with **100** for comments
   the oracle places and the resolver resolves (30 on the rehearsal arm,
   where the oracle's error, with every stratum at the upper end of its
   interval, was 11.4%). Each packet is labelled twice, independently, by
   automated labellers who see only the packet and `labelling-brief.md`,
   as on the rehearsal arm; a disagreement is settled by a third label
   from a fresh labeller given the same. Every labeller is a fresh
   instance of Claude Opus 5.5 (`claude-opus-5-5`) with no other context,
   given `labelling-brief.md` at the harness pin with its packet directory,
   its output file and its packet ids filled in. Pass A deals the key's
   packets, in `key.jsonl`'s order, round-robin to as many labellers as
   keep each at 17 or fewer; pass B does the same from the key's middle
   onward, wrapping round, so a labeller's batch differs between the
   passes.
   *Alternatives:* people label, which no arm has tried and for which the
   brief's instructions on writing the output would change; or the
   rehearsal's caps, up to 70 fewer packets per arm and a wider range.

## 1. What is measured

`experiments/D8-anchor-replay/replay.py`, as its README describes. In
brief, for each arm, each of 60 sampled files, and up to three pairs of
versions GAP commits apart in that file's history:

- a comment on three words from the middle of every paragraph of the
  earlier version with at least 20 characters, made as `SPEC.md` §11.1
  creates one (a paragraph where no window's span and context are unique
  gets none);
- resolved by the reference resolver against the later version;
- graded by the word oracle: difflib matches the earlier version's
  paragraph words onto the later's, and the span survives in the paragraph
  its three words map to, adjacent and in order; it is gone when its
  words occur, in order and adjacent, in no later paragraph; otherwise (a
  move, a copy) it is not counted, nor is a surviving span whose words
  occur more than once in its target. A pair whose earlier version the
  profile refuses gets no comments; `replay.py` reports how many there
  are. A comment is `correct`; `loud`, refused, `DETACHED` or
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

The harness runs at research `735091e` (amendment 1, §7; it was
`c26bba1`), against the reference resolver at
blockspec `d38a6bc` (`--blockspec` a checkout of that commit). From
`experiments/D8-anchor-replay/`, with each clone at its pin:

    python3 -I replay.py --blockspec BLOCKSPEC \
        --clone rust-book=CLONE --clone obsidian-help=CLONE \
        --clone kubernetes-website=CLONE --clone cncf-toc=CLONE \
        --arm rust-book --arm obsidian-help --arm k8s-en --arm cncf-toc \
        --dump DUMP
    python3 -I sample.py --blockspec BLOCKSPEC --clone ... --dump DUMP --gap 5 \
        --cap placed/resolves=100 --packets PACKETS --keydir KEY
    python3 -I score.py --keydir KEY --labels A.jsonl --labels B.jsonl [--adjudicated C.jsonl]
    python3 -I kinds.py --blockspec BLOCKSPEC --clone ... --dump DUMP --gap 5

`replay.py` may instead run once per arm (`--arm NAME`), with the dumps
concatenated in `arms.json`'s order: each arm and gap draws from its own
generator seeded 7, so the rows are the same. `sample.py`'s draw depends on the
dump's order, so it runs once, on the whole dump. k8s-l10n shares
k8s-en's clone and is never in the dump.

**Not verdict arms:** site-policy is the rehearsal arm (§6). cmspec is
excluded: the profile refuses both of its documents (one holds a
conflict-marker line, the other an indented code block), so it yields no
comments.

## 3. What is published

`replay.py`'s full stdout for every verdict arm and gap, its dump
(compressed), `kinds.py`'s stdout at gap 5, and the labelled sample
(`sample.py`'s stdout, key and `strata.json`, both passes of labels, any
adjudication, the model and brief they used, and `score.py`'s stdout),
committed under research `experiments/D8-anchor-replay/`. Every `WRONG`, at
every gap, is listed from the dump (each row whose `verdict` is `WRONG`)
and classified (§5). Every verdict of §4's that holds is recorded in
blockspec beside 0003. It is published whatever it is. `replay.py`'s
stdout must hold all twelve arm and gap sections, or the run is not
complete.

## 4. Verdicts

The range is `score.py`'s first pooled line, `refusal rate, labels for
truth, pooled over ...`, read as printed, to 0.1%: within the bar is an
upper end of at most 5.0%, above it a lower end of more than 5.0%.

- **Pass:** the pooled refusal rate's range at gap 5 is within choice 1's
  bar, and nothing is classified as a resolver defect.
- **Refusals too high:** the whole range is above the bar. The `loud`
  comments are reported by status and refusal reason, per arm from
  `replay.py`'s stdout and pooled from `kinds.py`'s; which rule to revisit
  is decided by the adjudication that follows, not here. This reverses no
  rule by itself: a change to a rule is its own adjudication.
- **Inconclusive:** the range spans the bar. It is reported as that, with
  the range; a larger sample is a new document, not an amendment.
- **Resolver defect:** a `WRONG` at any gap, or a resolving comment the
  labels put elsewhere, is classified as a resolver defect. It is
  filed as a bug against the reference resolver, with the file, the pair
  and the comment, and the run fails until the defect is decided.

A resolver defect can hold with refusals too high or inconclusive, and
both are recorded. With a range within the bar, it makes the verdict a
resolver defect, not a pass.

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
- No verdict arm had been run against the blockspec reference resolver
  when this draft was approved. The attempt amendment 1 (§7) records ran it
  on some gap-1 pairs and printed nothing.

## 7. Amendment rules

After this merges, a change to the bars, the arms, the sample or the
harness before the run is an amendment, committed and dated before the run.
After the run, nothing here changes; a different question gets its own
document.

### Amendment 1, 2026-10-18: the harness pin moves to research `735091e`

**Why.** An attempt was started at `c26bba1`, one `replay.py` per verdict
arm. rust-book, obsidian-help and k8s-en each stopped on the same defect,
after 1.2 s, 4.8 s and 31.6 s: a file's history from `git log -- FILE`
includes the commit that deletes it or moves it away, where `git show`
fails. cncf-toc, which holds no such pair, was stopped by hand. Before
stopping, the three had read and resolved 22, 37 and 55 gap-1 pairs, and
cncf-toc an unknown number; none printed any section, and no dump was
written, so no figure was seen. The attempt is not the run: §3 counts a
run only with all twelve sections, and the run, restarted at the new pin
after this amendment merges, starts from nothing.

**What changes** (research#21, merged as `735091e`). A file's history
starts after the last commit, in `git log`'s order, that does not hold it
as a file, as the history before a rename was already not followed.
Skipping only the deleting commit would have joined histories across a
move away and back: on rust-book, 36 sampled files left for
`second-edition/` in 2017 and returned in 2018. That, and a check that
stops the run if `git cat-file`'s answers do not line up, is the whole
change to the measurement; the rest of #21 adds self-checks (a red state,
sweep breaks, `histcheck.py`) and README text.

**Effect.** `histcheck.txt` counts the sampled files whose history this
changes: rust-book 36 of 60, obsidian-help 2, k8s-en 2, cncf-toc 1, and
site-policy 0, so the rehearsal's pairs, figures and labels (§6) are
unchanged. (It was made at research `7d5021e`, which differs from
`735091e` only in that file.) In the four verdict arms other files' pairs
can change too, since one generator draws every file's pairs in turn, and
three arms have fewer pairs, from shorter histories: rust-book 176, 160
and 88 at gaps 1, 5 and 25 become 172, 146 and 69; obsidian-help 104 at
gap 5 becomes 101; k8s-en 73 at gap 1 becomes 71, and 6 at gap 25
becomes 3.

**What was seen before this amendment**, besides §6: the three tracebacks;
`histcheck.txt`; a check that read every sampled pair's two versions with
`git show` and decoded them, at every arm and gap, which found none
unreadable and none not UTF-8 and gave each arm's number of pairs per gap;
and, in review, git-only counts of the pairs per arm and gap under each
harness version and of the pairs that crossed a deletion. None of these
read a document with the blockspec reader or ran the resolver.
