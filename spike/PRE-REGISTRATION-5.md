<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Pre-registration 5: adjudication 0004's resolver on held-out history

**Status: draft, for the owner's approval.** "Committed" means merged to
`main`. No verdict arm below runs before this document merges.

**The question.** Pre-registration 4 found 0003's resolver refusing too
much: 17.0% (16.3% to 18.7%) of comments whose text survived five commits
(`docs/adjudications/0003-anchors/replay-verdict.md`). Adjudication 0004
narrowed two rules, choosing them on pre-registration 4's arms and
site-policy, where it measures 4.8% at gap 5 with the oracle for truth. This document fixes, before it runs, the test of
0004's resolver on repositories that played no part in choosing it.

**Citations.** A blockspec path means its content at `ae1d274`, the merge
of #57, which landed 0004's resolver with its cases after #55 landed its
text. The harness is kindspec/research
`experiments/D8-anchor-replay/` at `8ecb0e7` (research#23, which adds
§2's arms in `heldout-arms.json`).

---

## 0. Choices the owner is approving

Approving the document approves each of these, as written.

1. **The bar (§4)** is pre-registration 4's: at gap 5, pooled over the
   verdict arms, among comments on versions the profile accepts, at most
   **5%** of comments whose span survived are refused, with the labelled
   sample for truth. Comments on versions the profile refuses are
   reported beside the rate, not counted in it. Above the bar, refusals
   are reported by cause, and what to revisit is the following
   adjudication's. *Alternative:* a stricter bar, such as 3%, which 0004 does not
   meet with the oracle on the arms it was tuned on (4.8%).
2. **Reading the bar (§4)** is pre-registration 4's: pass if the whole
   range is within it, fail if the whole range is above, otherwise
   inconclusive.
3. **Wrong resolutions (§4, §5)** are pre-registration 4's: any `WRONG` at
   any gap, or a resolving comment the labels put elsewhere, that is a
   resolver defect fails the run. 0004's widened R2 and R3 (`SPEC.md`
   §11.12) are residuals, not defects.
4. **The verdict arms (§2) are chosen by a rule fixed before any of them
   was resolved:** from this list, in this order, the first four that meet
   every criterion below at the pin:

   | candidate | pathspec |
   | --- | --- |
   | github/docs | `content/*.md` |
   | microsoft/vscode-docs | `docs/*.md` |
   | docker/docs | `content/*.md` |
   | mdn/content | `files/en-us/*.md` |
   | dotnet/docs | `docs/*.md` |

   The criteria: English prose; at least 200 Markdown files in the
   pathspec; at least 1,000 commits and 50 distinct author addresses
   touching them; a licence that permits quoting excerpts with
   attribution; and Markdown that no kindspec anchor experiment has
   used. The pin is
   the default branch's first-parent commit at or before
   2026-10-18T00:00:00Z. The list was written from well-known
   documentation repositories before any was cloned; no anchor was
   resolved on any of them before this document. *Alternative:* a
   different list, or more arms.
5. **Gap 5 decides the bar; gaps 1 and 25 are reported**, as in
   pre-registration 4. A resolver defect at any gap fails the run.
6. **The labelled sample (§1)** is pre-registration 4's choice 6, with one
   change: pass B deals the key's packets in contiguous runs of the key's
   order, not round-robin, so that no pass-B batch repeats a pass-A batch
   (pre-registration 4's rotation could not separate them when the number
   of labellers divided the number of packets). *Alternative:*
   pre-registration 4's dealing unchanged.
7. **Pre-registration 4's arms are reported, not deciding.** The same
   commands are run on them at 0004's resolver and published; 0004 was
   tuned on them, so they are a regression check, not a test.

## 1. What is measured

As pre-registration 4 §1, unchanged: `replay.py` comments on three words
from the middle of every paragraph of at least 20 characters in 60 sampled
files per arm, up to three pairs per file, resolves each against the later
version with the reference resolver, and grades it with the word oracle;
`sample.py` stratifies the gap-5 comments and writes blind packets;
`score.py` scales the labelled shares to each stratum and gives the range
with every stratum at the end of its exact 95% interval least and most
favourable to the bar; `kinds.py` sorts the refusals by cause.

## 2. Arms, sample and pins

Under choice 4's rule, measured at the pins with git alone (no anchor
resolved):

| arm | clone | pin | pathspec | Markdown files | commits | authors | licence |
| --- | --- | --- | --- | --: | --: | --: | --- |
| github-docs | github/docs | `dae83f7d28f3` | `content/*.md` | 3,760 | 20,547 | 2,879 | CC-BY-4.0 |
| vscode-docs | microsoft/vscode-docs | `ef0ca127806a` | `docs/*.md` | 364 | 8,135 | 937 | CC-BY-3.0 US |
| docker-docs | docker/docs | `31d174d090fd` | `content/*.md` | 1,095 | 5,196 | 568 | Apache-2.0 |
| mdn-en | mdn/content | `32eceacf42b6` | `files/en-us/*.md` | 14,703 | 23,282 | 4,884 | CC-BY-SA 2.5 (prose) |

dotnet/docs also meets every criterion and, fifth in order, is not an arm.

The replay's sample is `replay.py`'s, as in pre-registration 4: 60 files
per arm, up to three pairs per file, seed 7, gaps 1, 5 and 25. The labelled
sample is `sample.py`'s at gap 5, seed 11, with pre-registration 4's caps
(100 for placed comments that resolve).

The harness runs at research `8ecb0e7`, against the reference resolver at
blockspec `ae1d2740a90f36530d19fc2f026dc9b99710cac9`. Each clone is a full clone (no partial-clone filter), detached at
its pin with Git LFS files left as pointers
(`GIT_LFS_SKIP_SMUDGE=1 git checkout --detach PIN`), and
`git status --porcelain --untracked-files=no` prints nothing. The
commands are pre-registration 4 §2's with these four arms:

    python3 -I replay.py --blockspec BLOCKSPEC \
        --clone github-docs=CLONE --clone vscode-docs=CLONE \
        --clone docker-docs=CLONE --clone mdn-content=CLONE \
        --arm github-docs --arm vscode-docs --arm docker-docs --arm mdn-en \
        --dump DUMP
    python3 -I sample.py --blockspec BLOCKSPEC --clone ... --dump DUMP --gap 5 \
        --cap placed/resolves=100 --packets PACKETS --keydir KEY
    python3 -I score.py --keydir KEY --labels A.jsonl --labels B.jsonl [--adjudicated C.jsonl]
    python3 -I kinds.py --blockspec BLOCKSPEC --clone ... --dump DUMP --gap 5

Per-arm runs concatenated in `heldout-arms.json`'s order are allowed, as in
pre-registration 4.

## 3. What is published

As pre-registration 4 §3, for these arms and for choice 7's: each arm's
stdout with all twelve arm and gap sections for the verdict arms, the
dump, `kinds.py`'s stdout, the labelled sample with its batches, and every
`WRONG` at every gap with its classification. The verdict is recorded in
blockspec beside 0004.

## 4. Verdicts

Pre-registration 4 §4, unchanged: **pass**, **refusals too high**,
**inconclusive**, or **resolver defect**, read from `score.py`'s first
pooled line as printed to 0.1%.

## 5. Classifying a WRONG

Pre-registration 4 §5, with R1 to R4 as `SPEC.md` §11.12 now gives them
(0004 widens R2 and R3).

## 6. Disclosure: what was seen before this draft

- Everything pre-registration 4 §6 and its amendment 1 list.
- 0004's design measurements on pre-registration 4's arms and site-policy,
  with the oracle for truth: gap 5 4.8%, gap 1 0.9%, no `WRONG`
  (`0004-anchor-refusals.md`), repeated at `ae1d274`'s resolver with
  identical output (#57).
- 0004's reviews and its conformance cases (#55, #56, #57), all built on
  constructed inputs or the arms above.
- For the candidates: their clones, and the git counts in §2's table.
  No candidate's document was read with the blockspec reader, and no
  anchor was resolved on any of them.

## 7. Amendment rules

Pre-registration 4 §7: before the run, a change is an amendment, committed
and dated; after it, nothing here changes.
